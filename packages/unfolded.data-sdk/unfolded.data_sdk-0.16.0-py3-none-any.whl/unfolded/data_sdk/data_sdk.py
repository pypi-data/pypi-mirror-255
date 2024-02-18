from __future__ import annotations

import json
import os
import sys
import warnings
from contextlib import ExitStack
from datetime import datetime, timedelta
from io import BufferedReader, BufferedWriter, BytesIO
from pathlib import Path
from tempfile import TemporaryFile
from typing import IO, Any, BinaryIO, Dict, Iterable, List, Sequence, Tuple, overload
from uuid import UUID

import click
import jwt
import requests

from unfolded.data_sdk._query import Query
from unfolded.data_sdk.enums import (
    DatasetType,
    MediaType,
    QueryOutputType,
    ResourceType,
    TileMode,
    TimeInterval,
)
from unfolded.data_sdk.errors import (
    CREDENTIALS_NOT_WRITABLE_MSG,
    REFRESH_TOKEN_SAVED_MSG,
    AuthenticationError,
    DataFrameParsingError,
    DataSDKError,
    UnknownDatasetNameError,
    UnknownMediaTypeError,
)
from unfolded.data_sdk.models import (
    CategorizedPermissions,
    ConnectorQuery,
    DataConnector,
    Dataset,
    HexTileConfig,
    HexTileMetadata,
    HexTileOutputColumnConfig,
    Map,
    MapState,
    MapUpdateParams,
    PermissionsConfig,
    VectorTileConfig,
)
from unfolded.data_sdk.types import AccessToken, RefreshToken
from unfolded.data_sdk.utils import (
    compress_fileobj,
    get_fileobj_length,
    get_gzip_length,
    is_gzipped,
    raise_for_status,
    read_fileobj_chunks,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import geopandas as gpd
except ImportError:
    gpd = None

try:
    import pyarrow as pa
    import pyarrow.csv as pa_csv
    import pyarrow.parquet as pa_parquet
except ImportError:
    pa = None
    pa_csv = None
    pa_parquet = None

REFRESH_BUFFER = timedelta(minutes=1)


class DataSDK:
    """Manage datasets and maps through the Unfolded Cloud."""

    client_id: str = "v970dpbcqmRtr3y9XwlAB3dycpsvNRZF"
    base_url: str = "https://data-api.foursquare.com"
    auth_url: str = "https://auth.studio.foursquare.com/oauth/token"

    credentials_dir: Path | None
    store_credentials: bool
    _token: AccessToken | None
    _refresh_token: RefreshToken | None

    def __init__(
        self,
        refresh_token: RefreshToken | str | None = None,
        *,
        access_token: AccessToken | str | None = None,
        credentials_dir: Path | str | None = Path("~/.config/unfolded/").expanduser(),
        store_credentials: bool | None = None,
    ):
        """Constructor for DataSDK

        Args:
            refresh_token (optional, str): a refresh token for interacting with
                Unfolded Studio.

                If `store_credentials` is True, this only needs to be provided once; the
                DataSDK class will automatically load and refresh authentication
                credentials in the future.

                If `store_credentials` is False, a refresh token or access token will
                need to be provided every time the DataSDK class is used.

                Default: loads refresh token from saved file path on disk.

        Kwargs:
            access_token (optional, str): an access token for interacting with Unfolded Studio.

                This is necessary if a refresh token is not provided and if a refresh
                token has not previously been saved. An access token provides temporary,
                ephemeral access to your Unfolded account, so it may need to be updated
                the next time you create the DataSDK class.

                If you are using a secure, personal computer, it is easier to provide a
                refresh_token once, along with `store_credentials=True`, so that the
                `DataSDK` class can handle authentication on its own, without needing an
                `access_token` argument.

            credentials_dir (optional, Union[str, pathlib.Path]): a path to a directory
                on disk to use for storing credentials. Default: $HOME/.config/unfolded.

                If this path isn't writable, you can either make that path writable or
                define a custom credentials directory. If you use a custom directory,
                you'll need to include that every time you use the DataSDK class.

            store_credentials (optional, bool): Whether to save refresh token and/or
                access token on disk for future usage. It's recommended to pass `True`
                for this when used on a personal computer or other secure, single-user
                machine. This should be set to `False` on any multi-user systems where
                the `credentials_dir` is accessible by multiple users.

                Default: True except when run as the ROOT user.
        """
        self.credentials_dir = Path(credentials_dir) if credentials_dir else None
        self.store_credentials = (
            self._store_credentials_heuristic()
            if store_credentials is None
            else store_credentials
        )
        self._token = None
        self._refresh_token = None
        self._credentials_written = False

        if refresh_token:
            # Call _refresh_access_token directly so that we can verify that we can create an access
            # token before saving anything to disk.
            self._refresh_access_token(refresh_token=RefreshToken(refresh_token))

            # Check this in the constructor so that we only inform about a saved refresh token once,
            # not every time an access token is refreshed
            if self._credentials_written:
                sys.stderr.write(REFRESH_TOKEN_SAVED_MSG)
        elif access_token:
            self.token = AccessToken(access_token)

        # Test that we can create an access token
        _ = self.token

    def list_datasets(self, *, organization: bool = False) -> List[Dataset]:
        """List datasets for authenticated user or organization

        Kwargs:
            organization: if True, list datasets for organization of authenticated user. For non-enterprise users, organization=True will cause the request to fail with a 403 error.

        Returns:
            List of dataset objects.
        """
        if organization:
            url = f"{self.base_url}/v1/datasets/for-organization"
        else:
            url = f"{self.base_url}/v1/datasets"

        r = requests.get(url, headers=self._headers)
        raise_for_status(r)

        return [Dataset(**item) for item in r.json().get("items", [])]

    def get_dataset_by_id(self, dataset: Dataset | str | UUID) -> Dataset:
        """Get dataset given its id

        Args:
            dataset: dataset record to retrieve.

        Returns:
            Retrieved dataset record.
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        url = f"{self.base_url}/v1/datasets/{dataset}"
        r = requests.get(url, headers=self._headers)
        raise_for_status(r)

        return Dataset(**r.json())

    def download_dataset(
        self,
        dataset: Dataset | str | UUID,
        output_file: BinaryIO | str | Path | None = None,
        **kwargs: Any,
    ) -> bytes | None:
        """Download data for dataset

        Args:
            dataset: identifier for dataset whose data should be downloaded.
            output_file: if provided, a path or file object to write dataset's data to.

        Kwargs:
            chunk_size: number of bytes to download at a time. Used for progressbar.
            progress: if True, show progress bar.

        Returns:
            If output_file is None, returns bytes containing dataset's data.
            Otherwise, returns None and writes dataset's data to output_file.
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        url = f"{self.base_url}/v1/ingest/datasets/{dataset}/data"
        buf, _ = self._download_url(url=url, output_file=output_file, **kwargs)
        return buf

    # We use typing overloads here to make clear that a `None` response happens
    # when `None` is not passed as `output_file`
    @overload
    def _download_url(
        self, url: str, output_file: Literal[None] = None, **kwargs: Any
    ) -> Tuple[bytes, requests.Response]:
        ...

    @overload
    def _download_url(
        self, url: str, output_file: BinaryIO | str | Path, **kwargs: Any
    ) -> Tuple[None, requests.Response]:
        ...

    def _download_url(
        self,
        url: str,
        output_file: BinaryIO | BufferedWriter | str | Path | None = None,
        **kwargs: Any,
    ) -> Tuple[bytes | None, requests.Response]:
        """Low-level helper to download an arbitrary URL"""
        if not output_file:
            return self._download_dataset_to_bytes(url=url, **kwargs)

        opened_file: BinaryIO | BufferedWriter
        with ExitStack() as ctx:
            if isinstance(output_file, (str, Path)):
                # Open file if it isn't already open
                opened_file = ctx.enter_context(open(output_file, "wb"))
            else:
                opened_file = output_file

            r = self._download_dataset_to_fileobj(
                url=url, fileobj=opened_file, **kwargs
            )

        return None, r

    def _download_dataset_to_fileobj(
        self,
        url: str,
        fileobj: BinaryIO | BufferedWriter,
        chunk_size: int = 256 * 1024,
        progress: bool = False,
    ) -> requests.Response:
        """Download dataset to file object"""
        with ExitStack() as ctx:
            r = ctx.enter_context(requests.get(url, headers=self._headers, stream=True))
            raise_for_status(r)

            content_length = r.headers.get("Content-Length")

            fout = sys.stderr if progress else ctx.enter_context(open(os.devnull, "w"))

            # Don't fail when the content-length header doesn't exist
            if content_length:
                with click.progressbar(
                    length=int(content_length), label="Downloading data", file=fout
                ) as bar:
                    for data in r.iter_content(chunk_size=chunk_size):
                        fileobj.write(data)
                        bar.update(chunk_size)

            else:
                for data in r.iter_content(chunk_size=chunk_size):
                    fileobj.write(data)

            return r

    def _download_dataset_to_bytes(
        self, url: str, **kwargs: Any
    ) -> Tuple[bytes, requests.Response]:
        """Download dataset to bytes object"""
        with BytesIO() as bio:
            r = self._download_dataset_to_fileobj(url=url, fileobj=bio, **kwargs)
            bio.seek(0)
            return bio.read(), r

    def download_dataframe(
        self, dataset: Dataset | str | UUID, **kwargs: Any
    ) -> pd.DataFrame | gpd.GeoDataFrame:
        """Download dataset to pandas DataFrame or geopandas GeoDataFrame

        Args:
            dataset: identifier for dataset whose data should be downloaded.

        Kwargs:
            chunk_size: number of bytes to download at a time. Used for progressbar.
            progress: if True, show progress bar.

        Returns:
            Either a pandas DataFrame or a geopandas GeoDataFrame. If the
            dataset is a CSV file, a pandas DataFrame will be returned. If it is
            a GeoJSON file, a geopandas GeoDataFrame will be returned.
        """
        if pd is None:
            raise ImportError("Pandas required to load DataFrame object.")

        if isinstance(dataset, Dataset):
            dataset = dataset.id

        url = f"{self.base_url}/v1/ingest/datasets/{dataset}/data"
        buf, r = self._download_url(url=url, output_file=None, **kwargs)
        content_type = r.headers["Content-Type"]

        with BytesIO(buf) as bio:
            if content_type == MediaType.CSV:
                return pd.read_csv(bio)

            if content_type == MediaType.GEOJSON:
                if gpd is None:
                    raise ImportError(
                        "GeoPandas required to load GeoJSON response to DataFrame object."
                    )

                return gpd.read_file(bio)

            # Unfortunately, Studio doesn't put the correct content type on
            # GeoJSON files and saves all JSON data as application/json. Here
            # we'll try to parse as GeoJSON, then fall back to attempting JSON
            # parsing
            if content_type == MediaType.JSON:
                if gpd is not None:
                    try:
                        return gpd.read_file(bio)
                    except:
                        pass

                try:
                    return pd.read_json(bio, orient="records")
                except:
                    pass

                # Unable to parse JSON
                msg = "Unable to parse JSON data. If a GeoJSON, GeoPandas must be installed to parse GeoJSON to a DataFrame. Otherwise, the JSON file must be an array of records."
                raise DataFrameParsingError(msg)

            raise UnknownMediaTypeError(f"Unknown Media Type {content_type}")

    def upload_file(
        self,
        file: BinaryIO | str | Path,
        name: str | None = None,
        *,
        dataset: Dataset | str | UUID | None = None,
        media_type: str | MediaType | None = None,
        description: str | None = None,
        chunk_size: int = 256 * 1024,
        progress: bool = False,
    ) -> Dataset:
        """Upload dataset to Unfolded Studio

        To create a new dataset record, don't pass a dataset parameter. If a
        dataset parameter is passed, that dataset will be updated.

        Args:
            file: path or file object to use for uploading data.
            name: name for dataset record.

        Kwargs:
            dataset: If provided, dataset whose data should be updated. Otherwise, creates a new dataset.
            media_type: media type of data. By default, tries to infer media type from file name.
            description: description for dataset record.

        Kwargs:
            chunk_size: number of bytes to upload at a time. Used for progressbar.
            progress: if True, show progress bar.

        Returns:
            Updated dataset record
        """
        # Name not necessary for updating a dataset
        if not name and not dataset:
            name = self._infer_new_dataset_name(file)

        if not media_type:
            media_type = self._infer_media_type(file=file)

        if isinstance(media_type, MediaType):
            media_type = media_type.value

        if dataset and isinstance(dataset, Dataset):
            dataset = dataset.id

        if dataset:
            url = f"{self.base_url}/v1/ingest/datasets/{dataset}/data"
        else:
            url = f"{self.base_url}/v1/datasets/data"

        with ExitStack() as ctx:
            # Open file if it isn't already open

            opened_file: BufferedReader | IO[bytes]

            if isinstance(file, (str, Path)):
                opened_file = ctx.enter_context(open(file, "rb"))
            else:
                opened_file = file

            if media_type == MediaType.PMTILES:
                click.echo("PMTiles file detected, calculating the length", err=True)
                uncompressed_file_length = get_fileobj_length(opened_file)
                compressed_file_length = uncompressed_file_length
            elif is_gzipped(opened_file):
                click.echo(
                    "Gzipped file detected, calculating uncompressed length", err=True
                )
                compressed_file_length = get_fileobj_length(opened_file)
                uncompressed_file_length = get_gzip_length(opened_file)
            else:
                click.echo("Compressing file", err=True)
                uncompressed_file_length = get_fileobj_length(opened_file)

                # Create temporary file to write compressed bytes to
                tmpf = ctx.enter_context(TemporaryFile())
                compress_fileobj(opened_file, tmpf)
                tmpf.seek(0)
                opened_file = tmpf

                # Get compressed file length (used for progress bar)
                compressed_file_length = get_fileobj_length(tmpf)

            headers: Dict[str, str] = {
                **self._headers,
                "Content-Type": media_type,
            }

            if media_type != MediaType.PMTILES:
                headers["Content-Encoding"] = "gzip"
                headers["Content-Length-Uncompressed"] = str(uncompressed_file_length)

            fout = sys.stderr if progress else ctx.enter_context(open(os.devnull, "w"))

            # Enter progressbar context manager
            bar = ctx.enter_context(
                click.progressbar(
                    label="Uploading file", length=compressed_file_length, file=fout
                )
            )

            # Create iterator for file object (default file iterator uses
            # newlines, not a byte length)
            iterator = read_fileobj_chunks(
                opened_file, chunk_size=chunk_size, callback=bar.update
            )

            # Upload using iterator
            if dataset:
                # TODO: can updating a dataset also using name and description
                # params?
                r = requests.put(url, data=iterator, headers=headers)
            else:
                params = {"name": name}
                if description:
                    params["description"] = description
                r = requests.post(url, data=iterator, params=params, headers=headers)

        raise_for_status(r)
        return Dataset(**r.json())

    def upload_dataframe(
        self,
        df: pd.DataFrame | gpd.GeoDataFrame,
        name: str | None = None,
        index: bool = True,
        **kwargs: Any,
    ) -> Dataset:
        """Upload DataFrame or GeoDataFrame to Unfolded Studio

        Args:
            df: Either a pandas DataFrame or a geopandas GeoDataFrame to upload to Unfolded Studio.
            name: Name of dataset record. Required if creating a new dataset record.
            index (optional): if True, include row names in output. Default: True.
            **kwargs: keyword arguments to pass on to DataSDK.upload_file

        Returns:
            Dataset record of new data.
        """
        with BytesIO(df.to_csv(index=index).encode("utf-8")) as bio:
            return self.upload_file(
                file=bio, name=name, media_type=MediaType.CSV, **kwargs
            )

    def update_dataset(
        self,
        file: BinaryIO | str | Path,
        dataset: Dataset | str | UUID,
        media_type: str | MediaType | None = None,
        **kwargs: Any,
    ) -> Dataset:
        """Update data for existing Unfolded Studio dataset

        Note that this overwrites any existing data attached to the dataset.

        Args:
            file: path or file object to use for uploading data.
            dataset: dataset whose data should be updated.
            media_type: media type of data. By default, tries to infer media type from file name.

        Kwargs:
            chunk_size: number of bytes to upload at a time. Used for progress bar.
            progress: if True, show progress bar.

        Returns:
            Updated dataset record
        """
        warnings.warn(
            "update_dataset is deprecated. Use upload_file with a dataset argument.",
            DeprecationWarning,
        )

        return self.upload_file(
            file=file, dataset=dataset, media_type=media_type, **kwargs
        )

    def delete_dataset(self, dataset: Dataset | str | UUID) -> None:
        """Delete dataset from Unfolded Studio

        Warning: This operation cannot be undone. If you delete a dataset
        currently used in one or more maps, the dataset will be removed from
        those maps, possibly causing them to render incorrectly.

        Args:
            dataset: dataset to delete from Unfolded Studio.

        Returns:
            None
        """
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        url = f"{self.base_url}/v1/datasets/{dataset}"
        r = requests.delete(url, headers=self._headers)
        raise_for_status(r)

    def replace_dataset(
        self,
        # pylint:disable = redefined-builtin
        map: Map | str | UUID,
        dataset_to_replace: Dataset | str | UUID,
        dataset_to_use: Dataset | str | UUID,
        *,
        force: bool = False,
        strict: bool = True,
    ) -> Map:
        """Replace a dataset within a Map with another one

        This does not delete any datasets, it simply swaps one for another in a map.
        Will error if the new dataset is not compatible with the old one (override with the force option).

        Args:
            map: the map to change. Can be a Map object or a string/UUID id.
            dataset_to_replace: the dataset currently being used to be swapped out. Can be a Dataset object or a string/UUID id.
            dataset_to_use: the new dataset to be added to the map. Can be a Dataset object or a string/UUID id.

        Kwargs:
            force: skip compatibility check and force replacement of datasets.
            strict: check every field in the datasets to make sure types are an exact match

        Returns:
            The Map object that was operated upon.
        """

        if isinstance(map, Map):
            map = map.id
        if isinstance(dataset_to_replace, Dataset):
            dataset_to_replace = dataset_to_replace.id
        if isinstance(dataset_to_use, Dataset):
            dataset_to_use = dataset_to_use.id

        url = f"{self.base_url}/v1/maps/{map}/datasets/replace"
        replace_dataset_payload = {
            "datasetToReplaceId": str(dataset_to_replace),
            "datasetToUseId": str(dataset_to_use),
            "force": force,
            "strict": strict,
        }
        r = requests.post(url, headers=self._headers, json=replace_dataset_payload)
        raise_for_status(r)
        return Map(**r.json())

    def list_maps(self, *, organization: bool = False) -> List[Map]:
        """List maps for authenticated user or organization

        Gets the Map records for the current user, without dataset associations and map state. To get
        the full record with the associations, please use `get_map_by_id` after retrieving map identifiers.

        Kwargs:
            organization: if True, list map records for organization of authenticated user. For non-enterprise users, organization=True will cause the request to fail with a 403 error.

        Returns:
            List of map objects.
        """

        if organization:
            url = f"{self.base_url}/v1/maps/for-organization"
        else:
            url = f"{self.base_url}/v1/maps"

        r = requests.get(url, headers=self._headers)
        raise_for_status(r)
        return [Map(**item) for item in r.json().get("items", [])]

    def get_map_by_id(
        self,
        # pylint:disable = redefined-builtin
        map: Map | str | UUID,
    ) -> Map:
        """Get an Unfolded map given its id

        Gets a full Unfolded map record, which includes the associated dataset records as well the
        latest saved map state.

        Args:
            map: the map record to retrieve. Can be either a shallow record or a string/UUID id.

        Returns:
            Retrieved map record.
        """
        if isinstance(map, Map):
            map = map.id

        url = f"{self.base_url}/v1/maps/{map}"
        r = requests.get(url, headers=self._headers)
        raise_for_status(r)
        return Map(**r.json())

    def create_map(
        self,
        *,
        name: str,
        description: str | None = None,
        map_state: MapState | None = None,
        datasets: Iterable[Dataset | UUID | str] | None = None,
    ) -> Map:
        """Create an Unfolded Map record

        Args:
            name: the name of the map record (required).
            description: map description (optional).
            map_state: the map state/configuration (optional).
            datasets: list of datasets (records or ids) to add to the map (optional).

        Returns:
            New map record.
        """

        dataset_ids = None
        if datasets:
            dataset_ids = [
                str(dataset.id) if isinstance(dataset, Dataset) else dataset
                for dataset in datasets
            ]
        map_params = MapUpdateParams(
            name=name,
            description=description,
            latest_state=map_state,
            datasets=dataset_ids,
        )

        url = f"{self.base_url}/v1/maps"
        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url, data=map_params.json(exclude_none=True, by_alias=True), headers=headers
        )
        raise_for_status(r)
        return Map(**r.json())

    def copy_map(
        self,
        # pylint:disable = redefined-builtin
        map: Map | str | UUID,
        *,
        copy_datasets: bool,
        name: str | None = None,
    ) -> Map:
        """Copy a map

        Creates a copy of the specified map and returns the Map record for the new map.
        Can optionally make copies of the datasets used for the map as well.

        Args:
            map: the map record to copy. Can be a Map object representing a created map or a string/UUID id.

        Kwargs:
            copy_datasets (required): whether or not to make copyies of the underlying datasets
            name: the name to give the new copied map. Defaults to "Copy of {source_map_name}"
        Returns:
            Copied map record.
        """
        if isinstance(map, Map):
            map = map.id

        url = f"{self.base_url}/v1/maps/{map}/copy"
        copy_attrs: Dict[str, Any] = {"copyDatasets": copy_datasets}
        if name:
            copy_attrs["name"] = name
        r = requests.post(url, headers=self._headers, json=copy_attrs)
        raise_for_status(r)
        return Map(**r.json())

    def update_map(
        self,
        *,
        map_id: Map | UUID | str,
        name: str | None = None,
        description: str | None = None,
        map_state: MapState | None = None,
        datasets: Iterable[Dataset | UUID | str] | None = None,
    ) -> Map:
        """Update fields of an Unfolded Map record

        Args:
            map: the map record to update with the new field.

        Returns:
            The updated map record.
        """
        if isinstance(map_id, Map):
            map_id = map_id.id

        if not map_id:
            raise DataSDKError("Map id is required to perform the update")

        dataset_ids = None
        if datasets:
            dataset_ids = [
                str(dataset.id) if isinstance(dataset, Dataset) else dataset
                for dataset in datasets
            ]

        update_params = MapUpdateParams(
            name=name,
            description=description,
            latest_state=map_state,
            datasets=dataset_ids,
        )

        url = f"{self.base_url}/v1/maps/{map_id}"
        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.put(
            url,
            data=update_params.json(exclude_none=True, by_alias=True),
            headers=headers,
        )
        raise_for_status(r)
        return Map(**r.json())

    def delete_map(self, map_id: Map | UUID | str) -> None:
        """Delete an Unfolded Map record

        Args:
            map: the map record or id to delete.
        """
        if isinstance(map_id, Map):
            map_id = map_id.id

        url = f"{self.base_url}/v1/maps/{map_id}"
        r = requests.delete(url, headers=self._headers)
        raise_for_status(r)

    def list_data_connectors(
        self, *, organization: bool = False
    ) -> List[DataConnector]:
        """List data connectors for authenticated user or organization

        Gets the Data Connection records for the current user.

        Kwargs:
            organization: if True, list data connection records for organization of authenticated user. For non-enterprise users, organization=True will cause the request to fail with a 403 error.

        Returns:
            List of data connector objects.
        """

        if organization:
            url = f"{self.base_url}/v1/data-connections/for-organization"
        else:
            url = f"{self.base_url}/v1/data-connections"

        r = requests.get(url, headers=self._headers)
        raise_for_status(r)
        return [DataConnector(**item) for item in r.json().get("items", [])]

    def execute_query(
        self,
        connector: DataConnector | UUID | str,
        query: str,
        output_file: str | None = None,
        output_format: QueryOutputType | str | None = None,
    ) -> pd.DataFrame | None:
        """Execute a query against a data connector (enterprise only)

        Args:
            connector: the data connector record to use, or its id.
            query: the text of the query.
            output_file: the path to write the query output to (optional).
            output_format: the format in which to write the output (optional).

        Returns:
            A dataframe containing the results of the query
            or None if the output was written to a file.
        """
        if pa is None:
            raise ImportError("PyArrow required to load DataFrame object.")

        url = f"{self.base_url}/v1/data-queries"

        if isinstance(connector, DataConnector):
            connector = connector.id

        connector_query = ConnectorQuery(connector_id=connector, query=query)

        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url,
            data=connector_query.json(exclude_none=True, by_alias=True),
            headers=headers,
            stream=True,
        )
        raise_for_status(r)

        with pa.ipc.open_stream(r.raw) as reader:
            table = reader.read_all()

        if output_file:
            if output_format is None:
                raise ValueError("Must specify a file output format")
            elif output_format == QueryOutputType.CSV:
                if pa_csv is None:
                    raise ImportError("Could not import pyarrow.csv")
                pa_csv.write_csv(table, output_file)
            elif output_format == QueryOutputType.PARQUET:
                if pa_parquet is None:
                    raise ImportError("Could not import pyarrow.parquet")
                pa_parquet.write_table(table, output_file)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        else:
            if pd is None:
                raise ImportError("Pandas required to return as DataFrame.")
            return table.to_pandas()

    def create_query_dataset(
        self,
        connector: DataConnector | UUID | str,
        query: str,
        name: str,
        description: str | None = None,
    ) -> Dataset:
        """Create a dataset from a query (enterprise only)

        Args:
            connector: the data connector record to use, or its id.
            query: the text of the query.
            name: the name of the map record (optional).
            description: map description (optional).

        Returns:
            The newly created dataset
        """

        url = f"{self.base_url}/v1/datasets/data-query"

        if isinstance(connector, DataConnector):
            connector = connector.id

        create_params = {
            "name": name,
            "dataConnectionId": str(connector),
            "query": query,
        }
        if description:
            create_params["description"] = description

        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url,
            json=create_params,
            headers=headers,
        )
        raise_for_status(r)

        return Dataset(**r.json())

    def create_external_dataset(
        self,
        *,
        name: str,
        description: str | None = None,
        source: str,
        connector: DataConnector | UUID | str | None = None,
    ) -> Dataset:
        """Create an external dataset record referencing a dataset by URL. External datasets
        will be loaded from source every time, and will not be stored in our system.

        If the URL references a cloud storage object, e.g. with the s3:// or gcs:// protocol,
        and that URL requires authentication, you can include a data connector id referencing
        a connector with appropriate privileges to read that object. Note that this feature
        is in beta and may not work for all datasets.

        Args:
            name: the name of the dataset record (required).
            description: dataset description (optional).
            source: the source URL of the dataset (required).
            data_connector_id: id of associated data connector, for cloud storage URLs (optional).

        Returns:
            New dataset record.
        """

        url = f"{self.base_url}/v1/datasets"

        if isinstance(connector, DataConnector):
            connector = connector.id

        create_params = {
            "name": name,
            "type": DatasetType.EXTERNALLY_HOSTED,
            "dataConnectionId": str(connector),
            "metadata": {"source": source},
        }
        if description:
            create_params["description"] = description

        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url,
            json=create_params,
            headers=headers,
        )
        raise_for_status(r)

        return Dataset(**r.json())

    def get_hextile_metadata(
        self,
        dataset: Dataset | str | UUID,
    ) -> HexTileMetadata:
        """Download metadata for a hextile dataset"""
        if isinstance(dataset, Dataset):
            dataset = dataset.id

        url = f"{self.base_url}/v1/tileset/{dataset}/metadata"
        r = requests.get(url, headers=self._headers)
        raise_for_status(r)

        return HexTileMetadata(**r.json())

    def enrich(
        self,
        dataset: pd.DataFrame | Dataset | UUID | str,
        source_id: UUID,
        source_column: str | List[str],
        *,
        h3_column: str | None = None,
        lat_column: str | None = None,
        lng_column: str | None = None,
        time_column: str | None = None,
    ) -> pd.DataFrame:
        """Enriches a dataset with a given enrichment source

        Enriches a dataset with a given enrichment source and column based on either a h3_column
        or a combination of lat_column and lng_column

        Args:
            dataset: the dataset to enrich, could be in one of the following shapes:
                DataFrame: a Pandas DataFrame (inline data)
                Dataset: an Unfolded dataset record
                UUID, str: an Unfolded dataset uuid
            source_id: the uuid of the EnrichmentDataset to enrich with.
            source_column: the EnrichmentColumn(s) to enrich with.
            h3_column: the dataset h3 column to use for enrichment (enrichment by h3).
            lat_column: the dataset latitude column to use for enrichment (enrichment by lat/lng).
            lng_column: the dataset longitude column to use for enrichment (enrichment by lat/lng).
            time_column: the dataset time column to use for temporal enrichment.

        Returns:
            A pandas data frame with the resulting enriched dataset.
        """
        if pd is None:
            raise ImportError("Pandas required to use the enrich method.")

        if h3_column:
            index_columns = [h3_column]
        elif lat_column and lng_column:
            index_columns = [lat_column, lng_column]
        else:
            raise DataSDKError(
                "You need to either supply h3_column or both lat_column and lng_column to run enrichment"
            )

        if time_column:
            index_columns.append(time_column)

        # Construct the dataset node based on its type
        query = Query()
        if isinstance(dataset, pd.DataFrame):
            # Only upload the index column(s) for datasets passed as a dataframe
            # We use reset_index to allow for one or more of the index columns to be
            # stored as a pandas DataFrame index.
            query = query.inline_data(
                dataset.reset_index()[index_columns]
                .to_csv(index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
                .strip()
            )
        elif isinstance(dataset, Dataset):
            query = query.dataset(dataset.id)
        else:
            query = query.dataset(dataset)

        # Build and run the enrichment query
        query = query.enrich(
            source_id=source_id,
            source_column=source_column,
            h3_column=h3_column,
            lat_column=lat_column,
            lng_column=lng_column,
            time_column=time_column,
        )

        result_df = self._query(query)

        # For datasets passed as a dataframe, stitch out the result
        if isinstance(dataset, pd.DataFrame):
            if isinstance(source_column, str):
                result_source_cols = [source_column]
            else:
                result_source_cols = source_column
            result_df = pd.concat([dataset, result_df[result_source_cols]], axis=1)

        return result_df

    def tile_extract(
        self,
        source_id: str | UUID,
        geojson: Dict,
        *,
        source_column: str | List[str] | None = None,
        res: int | None = None,
        h3_column: str | None = None,
        time_column: str | None = None,
        time_interval: Dict | TimeInterval | None = None,
    ) -> pd.DataFrame:
        """Extract data from a HexTile dataset

        Args:
            source_id: the uuid of the EnrichmentDataset to enrich with.
            geojson: the GeoJSON geometry of the area to extract

        Kwargs:
            source_column: the EnrichmentColumn(s) to enrich with.
            res: the resolution of data to extract
            h3_column: name of column for h3 index
            time_column: name of column for time index
            time_interval: time interval of data to extract

        Returns:
            A pandas data frame with the extracted dataset.
        """
        if pd is None:
            raise ImportError("Pandas required to use the tile_extract method.")

        # Build and run the enrichment query
        query = Query()
        query = query.tile_extract(
            source_id=source_id,
            geojson=geojson,
            source_column=source_column,
            res=res,
            h3_column=h3_column,
            time_column=time_column,
            time_interval=time_interval,
        )

        result_df = self._query(query)
        return result_df

    def create_hextile(self, *args: Any, **kwargs: Any) -> Dataset:
        warnings.warn(
            "Function create_hextile is deprecated and will be removed in a future release. Use generate_hextile instead",
            DeprecationWarning,
        )
        return self.generate_hextile(*args, **kwargs)

    def generate_hextile(
        self,
        source: Dataset | str | UUID,
        *,
        target: Dataset | str | UUID | None = None,
        source_hex_column: str | None = None,
        source_lat_column: str | None = None,
        source_lng_column: str | None = None,
        source_time_column: str | None = None,
        time_intervals: Sequence[TimeInterval | str] | None = None,
        target_res_offset: int | None = None,
        finest_resolution: int | None = None,
        _tile_mode: TileMode | str | None = None,
        output_columns: Sequence[dict | HexTileOutputColumnConfig] | None = None,
        _positional_indexes: bool | None = None,
    ) -> Dataset:
        """Start hextiling process on dataset"""

        if target_res_offset:
            warnings.warn(
                "Option target_res_offset is deprecated and will be removed in a future release.",
                DeprecationWarning,
            )
        if _tile_mode:
            warnings.warn(
                "Option _tile_mode is deprecated and will be removed in a future release.",
                DeprecationWarning,
            )
        if _positional_indexes:
            warnings.warn(
                "Option _positional_indexes is deprecated and will be removed in a future release.",
                DeprecationWarning,
            )

        config = HexTileConfig(
            source=source,
            target=target,
            source_hex_column=source_hex_column,
            source_lat_column=source_lat_column,
            source_lng_column=source_lng_column,
            source_time_column=source_time_column,
            time_intervals=time_intervals,
            target_res_offset=target_res_offset,
            finest_resolution=finest_resolution,
            _tile_mode=_tile_mode,
            output_columns=output_columns,
            _positional_indexes=_positional_indexes,
        )

        url = f"{self.base_url}/v1/datasets/hextile"
        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url,
            data=config.json(exclude_none=True, by_alias=True),
            headers=headers,
        )
        raise_for_status(r)

        return Dataset(**r.json())

    def generate_vectortile(
        self,
        source: Dataset | str | UUID,
        *,
        target: Dataset | str | UUID | None = None,
        source_lat_column: str | None = None,
        source_lng_column: str | None = None,
        attributes: List[str] | None = None,
        exclude_all_attributes: bool | None = None,
        tile_size_kb: int | None = None,
    ) -> Dataset:
        """Start vector tiling process on dataset"""
        config = VectorTileConfig(
            source=source,
            target=target,
            source_lat_column=source_lat_column,
            source_lng_column=source_lng_column,
            attributes=attributes,
            exclude_all_attributes=exclude_all_attributes,
            tile_size_kb=tile_size_kb,
        )

        url = f"{self.base_url}/v1/datasets/vectortile"
        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(
            url,
            data=config.json(exclude_none=True, by_alias=True),
            headers=headers,
        )
        raise_for_status(r)

        return Dataset(**r.json())

    def get_permissions(
        self,
        *,
        resource_type: ResourceType,
        resource_id: UUID | str,
    ) -> CategorizedPermissions:
        """Get permissions for a resource specified by its id and type (enterprise only)

        Args:
            resource_type: the type of the resource
            resource_id: the uuid of the resource

        Returns:
            Permissions per user (email) and the organization (if the user belongs to one)
        """

        headers = {**self._headers, "Content-Type": "application/json"}
        url = f"{self.base_url}/v1/permissions/{resource_type}/{resource_id}"

        r = requests.get(url, headers=headers)
        raise_for_status(r)

        return CategorizedPermissions(**r.json())

    def set_permissions(
        self,
        *,
        resource_type: ResourceType,
        resource_id: UUID | str,
        permissions: CategorizedPermissions | Dict,
    ) -> None:
        """Sets permissions for a resource specified by its id and type (enterprise only)

        For every user and organization:
        - if the permission didn't exist before, but now does - it creates a new one
        - if the permission existed, but is now different - it's updated
        - if the permission existed, but is now omitted - it's removed

        Args:
            resource_type: the type of the resource
            resource_id: the uuid of the resource
            permissions: permission type per user email and for the organization
        """

        config = PermissionsConfig(
            resource_type=resource_type,
            resource_id=resource_id,
            permissions=permissions,
        )

        headers = {**self._headers, "Content-Type": "application/json"}
        url = f"{self.base_url}/v1/permissions"

        # we coerce the value to the right one that backend understands
        if config.resource_type == ResourceType.DATA_CONNECTOR:
            config.resource_type = "data-connection"

        r = requests.post(
            url, data=config.json(exclude_none=True, by_alias=True), headers=headers
        )
        raise_for_status(r)

    def _query(self, query: Query) -> pd.DataFrame:
        """Runs a query using the Unfolded Query API

        Args:
            query: the Query describing the operations to run

        Returns:
            A pandas data frame with the result of the query.
        """
        if pd is None:
            raise ImportError("Pandas required to use the _query method.")

        url = f"{self.base_url}/v1/query"
        headers = {**self._headers, "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, data=query.json())
        raise_for_status(r)

        with BytesIO(r.content) as buf:
            return pd.read_csv(buf)

    def _infer_new_dataset_name(self, file: BinaryIO | str | Path) -> str:
        general_msg = "Please supply an explicit name for the dataset."
        if not isinstance(file, (str, Path)):
            raise UnknownDatasetNameError(
                f"Cannot infer dataset name from binary stream.\n{general_msg}"
            )

        if isinstance(file, Path):
            return file.name

        return Path(file).name

    def _infer_media_type(self, file: BinaryIO | str | Path) -> MediaType:
        general_msg = "Please supply an explicit Media Type for the file."
        if not isinstance(file, (str, Path)):
            raise UnknownMediaTypeError(
                f"Cannot infer Media Type from binary stream.\n{general_msg}"
            )

        media_type = self._infer_media_type_from_path(file)

        if not media_type:
            raise UnknownMediaTypeError(
                f"Could not infer file's Media Type.\n{general_msg}"
            )

        return media_type

    @staticmethod
    def _infer_media_type_from_path(path: str | Path) -> MediaType | None:
        suffix = Path(path).suffix.lstrip(".").upper()

        try:
            return MediaType[suffix]
        except KeyError:
            return None

    @property
    def _headers(self) -> Dict[str, str]:
        """Default headers to send with each request"""
        return {"Authorization": f"Bearer {self.token}"}

    @property
    def refresh_token(self) -> RefreshToken | None:
        """Refresh token for generating new access tokens"""
        if self._refresh_token:
            return self._refresh_token

        try:
            self._refresh_token = self._load_refresh_token_from_disk()
        except OSError:
            raise AuthenticationError(
                "refresh_token was not provided and was not previously saved."
            )

        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value: RefreshToken) -> None:
        # Handle storing the refresh token on disk in the setter
        self._refresh_token = value

        if self.store_credentials and self._refresh_token_path:
            self._write_token({"refresh_token": value}, self._refresh_token_path)
            self._credentials_written = True

    @property
    def token(self) -> AccessToken:
        """Valid access token for interacting with Unfolded Studio's backend"""
        # If no token in memory, try to load saved access token if one exists
        if not self._token:
            try:
                self._token = self._load_access_token_from_disk()
            except (FileNotFoundError, KeyError):
                pass

        # If token is expired, refresh it
        if not self._token or (
            datetime.now() >= self._token_expiration - REFRESH_BUFFER
        ):
            self._refresh_access_token(self.refresh_token)

        if not self._token:
            raise AuthenticationError("Could not refresh access token.")

        return self._token

    @token.setter
    def token(self, value: AccessToken) -> None:
        self._token = value

        if self.store_credentials and self._access_token_path:
            self._write_token({"access_token": value}, self._access_token_path)

    def _store_credentials_heuristic(self) -> bool:
        """Heuristic for whether to store credentials

        Returns:
            if True, should store credentials
        """
        # See discussion in https://github.com/foursquare/studio-monorepo/pull/2017 and
        # related Jira ticket. In order to not break backwards compatibility, we need to
        # default existing users to `store_credentials=True`, or cycled refresh tokens
        # will not be persisted to disk. On the other hand, we want to default insecure
        # environments to not storing credentials.
        if os.getenv("USER", "").lower() == "root":
            return False

        return True

    @property
    def _token_expiration(self) -> datetime:
        # Use _token to bypass logic that depends on token_expiration to avoid
        # recursion error
        token = self._token

        # If token doesn't exist, provide timestamp in the past to trigger token
        # refresh
        if not token:
            return datetime.now() - timedelta(seconds=1)

        decoded = jwt.decode(token, options={"verify_signature": False})
        return datetime.fromtimestamp(decoded["exp"])

    @property
    def _refresh_token_path(self) -> Path | None:
        if not self.credentials_dir:
            return None

        return self.credentials_dir / "credentials.json"

    @property
    def _access_token_path(self) -> Path | None:
        if not self.credentials_dir:
            return None

        return self.credentials_dir / "access_token.json"

    def _load_refresh_token_from_disk(self) -> RefreshToken | None:
        """Load saved refresh token"""
        path = self._refresh_token_path

        if not path:
            return None

        with open(path, encoding="utf-8") as f:
            return json.load(f)["refresh_token"]

    def _load_access_token_from_disk(self) -> AccessToken | None:
        """Load saved access token"""
        path = self._access_token_path

        if not path:
            return None

        with open(path, encoding="utf-8") as f:
            return json.load(f)["access_token"]

    def _write_token(
        self, body: Dict[str, AccessToken | RefreshToken], path: Path
    ) -> None:
        """Write access token or refresh token to credentials_dir"""
        assert (
            self.store_credentials
        ), "Cannot write token when store_credentials is False"

        try:
            # Create credentials directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(body, f)
        except OSError as e:
            raise DataSDKError(CREDENTIALS_NOT_WRITABLE_MSG) from e

    def _refresh_access_token(self, refresh_token: RefreshToken | None) -> None:
        if not refresh_token:
            raise AuthenticationError(
                "Unable to retrieve access token without a refresh token."
            )

        post_data: Dict[str, str | RefreshToken] = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token,
        }

        r = requests.post(self.auth_url, json=post_data)
        raise_for_status(r)
        auth_data = r.json()

        if "refresh_token" in auth_data:
            self.refresh_token = auth_data["refresh_token"]

        self.token = auth_data["access_token"]
