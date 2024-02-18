from __future__ import annotations

import json
import sys
import warnings
from functools import partial
from getpass import getpass
from pathlib import Path
from typing import IO, Any, List

import click
from pydantic.json import pydantic_encoder

from unfolded.data_sdk.auth import authenticate as _authenticate
from unfolded.data_sdk.data_sdk import DataSDK, RefreshToken
from unfolded.data_sdk.enums import ResourceType
from unfolded.data_sdk.environment import AuthEnvironment
from unfolded.data_sdk.errors import NON_ROTATING_TOKEN_WARNING, REFRESH_TOKEN_SAVED_MSG
from unfolded.data_sdk.models import CategorizedPermissions, MediaType


class PathType(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(self, value: Any, param: Any, ctx: Any) -> Any:
        return Path(super().convert(value, param, ctx))


@click.group()
def main() -> None:
    pass


@click.command()
@click.option(
    "--credentials-dir",
    type=PathType(dir_okay=True, file_okay=False, writable=True),
    help="A directory on disk to use for storing credentials. Only used if --store-credentials is passed.",
    default=Path("~/.config/unfolded/").expanduser(),
    show_default=True,
)
@click.option(
    "--non-rotating",
    is_flag=True,
    help="If passed, generate a non-rotating refresh token.",
    default=False,
    show_default=True,
)
@click.option(
    "--print/--no-print",
    "_print",
    default=False,
    show_default=True,
    help="If passed, print refresh token information to stdout.",
)
@click.option(
    "--store-credentials/--no-store-credentials",
    default=True,
    show_default=True,
    help="If passed, store generated credentials on disk to the location of --credentials-dir.",
)
def authenticate(
    credentials_dir: Path, non_rotating: bool, _print: bool, store_credentials: bool
) -> None:
    """Authenticate with the Unfolded backend using OAuth2"""
    auth_env = (
        AuthEnvironment.PRODUCTION_NO_ROTATE
        if non_rotating
        else AuthEnvironment.PRODUCTION
    )

    if non_rotating:
        sys.stderr.write("\n\x1b[1;33m" + NON_ROTATING_TOKEN_WARNING + "\x1b[0m\n")

    credentials = _authenticate(auth_env=auth_env)

    if store_credentials:
        data_sdk = DataSDK(
            access_token=credentials.access_token,
            credentials_dir=credentials_dir,
            store_credentials=store_credentials,
        )
        data_sdk.refresh_token = credentials.refresh_token
        sys.stderr.write(REFRESH_TOKEN_SAVED_MSG)

    if _print:
        click.echo(json.dumps(credentials, indent=4, default=pydantic_encoder))


@click.command()
@click.option(
    "--organization/--no-organization",
    default=False,
    help="If True, list datasets for organization of authenticated user. For non-enterprise users, passing this flag will cause the request to fail with a 403 error",
    show_default=True,
)
def list_datasets(organization: bool) -> None:
    """List datasets for authenticated user"""
    data_sdk = DataSDK()
    output_data = [
        dataset.dict() for dataset in data_sdk.list_datasets(organization=organization)
    ]
    click.echo(json.dumps(output_data, indent=4, default=pydantic_encoder))


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
def get_dataset(dataset_id: str) -> None:
    """Get dataset given its id"""
    data_sdk = DataSDK()
    dataset = data_sdk.get_dataset_by_id(dataset=dataset_id)
    click.echo(dataset.json(indent=4))


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
@click.option(
    "-o",
    "--output-file",
    type=PathType(file_okay=True, writable=True),
    required=True,
    help="Output file for dataset.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
def download_dataset(dataset_id: str, output_file: Path, progress: bool) -> None:
    """Download data for existing dataset to disk"""
    data_sdk = DataSDK()
    data_sdk.download_dataset(
        dataset=dataset_id, output_file=output_file, progress=progress
    )


@click.command()
@click.option(
    "-n", "--name", type=str, required=False, default=None, help="Dataset name."
)
@click.option(
    "--media-type",
    type=click.Choice([c.value for c in MediaType], case_sensitive=False),
    required=False,
    default=None,
    help="Dataset media type.",
)
@click.option(
    "--dataset-id",
    type=str,
    required=False,
    default=None,
    help="Dataset id. If provided, will update the existing dataset.",
)
@click.option(
    "--desc",
    type=str,
    required=False,
    default=None,
    show_default=True,
    help="Dataset description.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
@click.argument("file", type=PathType(readable=True, file_okay=True))
def upload_file(
    file: Path, name: str, media_type: str, dataset_id: str, desc: str, progress: bool
) -> None:
    """Upload new dataset to Unfolded Studio"""
    data_sdk = DataSDK()
    new_dataset = data_sdk.upload_file(
        file=file,
        name=name,
        media_type=media_type,
        description=desc,
        dataset=dataset_id,
        progress=progress,
    )
    click.echo(new_dataset.json())


@click.command()
@click.option(
    "--dataset-id",
    type=str,
    required=False,
    default=None,
    help="Dataset id. If provided, will update the existing dataset.",
)
@click.option(
    "--media-type",
    type=click.Choice([c.value for c in MediaType], case_sensitive=False),
    required=False,
    default=None,
    help="Dataset media type.",
)
@click.option(
    "--progress/--no-progress",
    default=True,
    help="Whether to show progress bar.",
    show_default=True,
)
@click.argument("file", type=PathType(readable=True, file_okay=True))
def update_dataset(
    file: Path, dataset_id: str, media_type: str, progress: bool
) -> None:
    """Update data for existing Unfolded Studio dataset"""
    warnings.warn(
        "update-dataset is deprecated. Use upload-file with a --dataset-id option.",
        DeprecationWarning,
    )

    data_sdk = DataSDK()
    updated_dataset = data_sdk.upload_file(
        file=file, dataset=dataset_id, media_type=media_type, progress=progress
    )
    click.echo(updated_dataset.json())


def abort_if_false(ctx: Any, param: Any, value: Any) -> None:
    # pylint: disable=unused-argument
    if not value:
        ctx.abort()


@click.command()
@click.option("--dataset-id", type=str, required=True, help="Dataset id.")
@click.option(
    "--force",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help="Delete dataset without prompting.",
    prompt="Are you sure you want to delete the dataset?",
)
def delete_dataset(dataset_id: str) -> None:
    """Delete dataset from Unfolded Studio

    Warning: This operation cannot be undone. If you delete a dataset currently
    used in one or more maps, the dataset will be removed from those maps,
    possibly causing them to render incorrectly.
    """
    data_sdk = DataSDK()
    data_sdk.delete_dataset(dataset=dataset_id)
    click.echo("Dataset deleted.", file=sys.stderr)


@click.command()
@click.argument("map_id", type=str)
@click.argument("dataset-to-replace-id", type=str)
@click.argument("dataset-to-use-id", type=str)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force replace dataset (even if not compatible)",
)
@click.option(
    "--strict",
    is_flag=True,
    default=True,
    help="Use strict type checking for datasets",
)
def replace_dataset(
    map_id: str,
    dataset_to_replace_id: str,
    dataset_to_use_id: str,
    force: bool = False,
    strict: bool = False,
) -> None:
    """Replace one dataset associated with a map with another"""
    data_sdk = DataSDK()
    map_object = data_sdk.replace_dataset(
        map_id,
        dataset_to_replace=dataset_to_replace_id,
        dataset_to_use=dataset_to_use_id,
        force=force,
        strict=strict,
    )
    click.echo(map_object.json())


@click.command()
@click.option(
    "--organization/--no-organization",
    default=False,
    help="If True, list map records for organization of authenticated user. For non-enterprise users, passing this flag will cause the request to fail with a 403 error",
    show_default=True,
)
def list_maps(organization: bool) -> None:
    """List map records for authenticated user"""
    data_sdk = DataSDK()
    output_data = [
        map.dict(exclude_none=True)
        for map in data_sdk.list_maps(organization=organization)
    ]
    click.echo(json.dumps(output_data, indent=4, default=pydantic_encoder))


@click.command()
@click.argument("map_id", type=str)
def get_map(map_id: str) -> None:
    """Get an Unfolded map record by its id, including associated datasets and map state"""
    data_sdk = DataSDK()
    map_object = data_sdk.get_map_by_id(map_id)
    click.echo(map_object.json())


@click.command()
@click.option("--name", type=str, required=True, help="The map name")
@click.option("--description", type=str, required=False, help="The map description")
@click.option(
    "--map-state",
    type=click.File(),
    required=False,
    help="The map state as a json file",
)
@click.option(
    "--dataset-ids",
    type=str,
    required=False,
    help="Comma separated list of dataset ids to add to the map",
)
def create_map(name: str, description: str, map_state: IO, dataset_ids: str) -> None:
    """Create an Unfolded Studio map"""
    data_sdk = DataSDK()
    datasets = (
        [dataset_id.strip() for dataset_id in dataset_ids.split(",")]
        if dataset_ids
        else None
    )

    map_object = data_sdk.create_map(
        name=name,
        description=description,
        map_state=json.load(map_state) if map_state else None,
        datasets=datasets,
    )

    click.echo(map_object.json())


@click.command()
@click.argument("map_id", type=str)
@click.option(
    "--copy-datasets/--no-copy-datasets",
    required=True,
    help="If True, will copy the map and copy its underlying datasets.",
)
@click.option(
    "--name",
    type=str,
    required=False,
    help="The name for the new copied map. Default: 'Copy of {source_map_name}'",
)
def copy_map(map_id: str, copy_datasets: bool, name: str) -> None:
    """Copy an Unfolded map"""
    data_sdk = DataSDK()
    map_object = data_sdk.copy_map(map_id, copy_datasets=copy_datasets, name=name)
    click.echo(map_object.json())


@click.command()
@click.option("--map-id", type=str, required=True, help="The map id")
@click.option("--name", type=str, required=False, help="The map name")
@click.option("--description", type=str, required=False, help="The map description")
@click.option(
    "--map-state",
    type=click.File(),
    required=False,
    help="The map state as a json file",
)
@click.option(
    "--dataset-ids",
    type=str,
    required=False,
    help="Comma separated list of dataset ids to add to the map",
)
def update_map(
    map_id: str, name: str, description: str, map_state: IO, dataset_ids: str
) -> None:
    """Update an Unfolded Studio map"""
    data_sdk = DataSDK()
    datasets = (
        [dataset_id.strip() for dataset_id in dataset_ids.split(",")]
        if dataset_ids
        else None
    )
    map_object = data_sdk.update_map(
        map_id=map_id,
        name=name,
        description=description,
        map_state=json.load(map_state) if map_state else None,
        datasets=datasets,
    )
    click.echo(map_object.json())


@click.command()
@click.option(
    "--force",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    help="Delete map without prompting.",
    prompt="Are you sure you want to delete this map?",
)
@click.argument("map_id", type=str)
def delete_map(map_id: str) -> None:
    """Delete map from Unfolded Studio

    Warning: This operation cannot be undone.
    """
    data_sdk = DataSDK()
    data_sdk.delete_map(map_id)
    click.echo("Map deleted.", file=sys.stderr)


@click.command()
@click.option(
    "--organization/--no-organization",
    default=False,
    help="If True, list data connectors for organization of authenticated user. For non-enterprise users, passing this flag will cause the request to fail with a 403 error",
    show_default=True,
)
def list_data_connectors(organization: bool) -> None:
    """List data connectors for authenticated user"""
    data_sdk = DataSDK()
    output_data = data_sdk.list_data_connectors(organization=organization)
    click.echo(json.dumps(output_data, indent=4, default=pydantic_encoder))


@click.command()
@click.option(
    "--connector-id", type=str, required=True, help="Id of Data Connector to use"
)
@click.option(
    "--query", type=str, required=True, help="SQL query to run against the connector"
)
@click.option("--output-file", type=str, help="The path to write the query output to")
@click.option(
    "--output-format", type=str, help="The format in which to write the output"
)
def execute_query(
    connector_id: str, query: str, output_file: str | None, output_format: str | None
) -> None:
    """Execute a query against a data connector (enterprise only)"""
    data_sdk = DataSDK()
    output_df = data_sdk.execute_query(
        connector=connector_id,
        query=query,
        output_file=output_file,
        output_format=output_format,
    )
    if output_file:
        click.echo(f"Query results written to: {output_file}")
    else:
        click.echo(repr(output_df))


@click.command()
@click.option(
    "--connector-id", type=str, required=True, help="Id of Data Connector to use"
)
@click.option("--query", type=str, required=True, help="SQL query to use")
@click.option(
    "--name", type=str, default=None, required=True, help="Name of the new SQL dataset"
)
@click.option(
    "--description",
    type=str,
    default=None,
    required=False,
    help="Description of the new SQL dataset",
)
def create_query_dataset(
    connector_id: str, query: str, name: str, description: str | None
) -> None:
    """Create a dataset from a query against a data connector (enterprise only)"""
    data_sdk = DataSDK()
    dataset = data_sdk.create_query_dataset(
        connector=connector_id, query=query, name=name, description=description
    )
    click.echo(dataset.json())


@click.command()
@click.option("--source", type=str, required=True, help="Source URL of the dataset")
@click.option(
    "--name", type=str, default=None, required=True, help="Name of the new dataset"
)
@click.option(
    "--description",
    type=str,
    default=None,
    required=False,
    help="Description of the new dataset",
)
@click.option(
    "--connector-id",
    type=str,
    required=False,
    help="Id of optional Data Connector to use",
)
def create_external_dataset(
    source: str, name: str, description: str | None, connector_id: str | None
) -> None:
    """Create a dataset from an external file"""
    data_sdk = DataSDK()
    dataset = data_sdk.create_external_dataset(
        connector=connector_id, source=source, name=name, description=description
    )
    click.echo(dataset.json())


@click.command()
@click.option("--source", type=str, required=True, help="Source dataset id.")
@click.option("--target", type=str, required=False, help="Target dataset id.")
@click.option(
    "--source-hex-column", type=str, required=False, help="Source hex column."
)
@click.option(
    "--source-lat-column", type=str, required=False, help="Source lat column."
)
@click.option(
    "--source-lng-column", type=str, required=False, help="Source lng column."
)
@click.option(
    "--source-time-column", type=str, required=False, help="Source time column."
)
@click.option(
    "--time-interval",
    type=str,
    multiple=True,
    required=False,
    help='Time granularities for hextile job input. Options are "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND". Supports multiple inputs',
)
@click.option(
    "--finest-resolution", type=int, required=False, help="Finest resolution."
)
@click.option(
    "--output-column",
    type=str,
    multiple=True,
    required=False,
    help="Output column config (JSON). Supports multiple inputs",
)
def generate_hextile(
    source: str,
    target: str | None,
    source_hex_column: str | None,
    source_lat_column: str | None,
    source_lng_column: str | None,
    source_time_column: str | None,
    time_interval: List[str],
    finest_resolution: int | None,
    output_column: List[str],
) -> None:
    """Generate a hextile dataset from a source dataset"""
    data_sdk = DataSDK()
    dataset = data_sdk.generate_hextile(
        source=source,
        target=target,
        source_hex_column=source_hex_column,
        source_lat_column=source_lat_column,
        source_lng_column=source_lng_column,
        source_time_column=source_time_column,
        time_intervals=list(time_interval) if time_interval else None,
        finest_resolution=finest_resolution,
        output_columns=list(map(json.loads, output_column)),
    )
    click.echo(dataset.json(indent=4))


@click.command()
@click.option("--source", type=str, required=True, help="Source dataset id.")
@click.option("--target", type=str, required=False, help="Target dataset id.")
@click.option(
    "--source-lat-column", type=str, required=False, help="Source lat column."
)
@click.option(
    "--source-lng-column", type=str, required=False, help="Source lng column."
)
@click.option(
    "-y",
    "--attributes",
    type=str,
    required=False,
    multiple=True,
    help="Attributes to keep.",
)
@click.option(
    "-X",
    "--exclude-all-attributes",
    type=str,
    required=False,
    is_flag=True,
    help="Whether to exclude all attributes.",
)
@click.option(
    "--tile-size-kb", type=int, required=False, help="Maximum tile size (in kilobytes)."
)
def generate_vectortile(
    source: str,
    target: str | None,
    source_lat_column: str | None,
    source_lng_column: str | None,
    attributes: List[str],
    exclude_all_attributes: bool,
    tile_size_kb: int | None,
) -> None:
    """Generate a vector tileset from a source dataset"""
    data_sdk = DataSDK()
    dataset = data_sdk.generate_vectortile(
        source=source,
        target=target,
        source_lat_column=source_lat_column,
        source_lng_column=source_lng_column,
        attributes=attributes,
        exclude_all_attributes=exclude_all_attributes,
        tile_size_kb=tile_size_kb,
    )
    click.echo(dataset.json(indent=4))


@click.command()
@click.option(
    "--refresh-token",
    type=str,
    help="Refresh Token. Retrieve from https://studio.foursquare.com/tokens.html",
    # Use getpass for password input
    # Ref https://github.com/pallets/click/issues/300#issuecomment-606105993
    default=partial(getpass, "Refresh Token: "),
)
@click.option(
    "--credentials-dir",
    type=PathType(dir_okay=True, file_okay=False, writable=True),
    help="A directory on disk to use for storing credentials.",
    default=Path("~/.config/unfolded/").expanduser(),
    show_default=True,
)
def store_refresh_token(refresh_token: RefreshToken, credentials_dir: Path) -> None:
    """Store refresh token to enable seamless future authentication

    Retrieve token from https://studio.foursquare.com/tokens.html
    """
    DataSDK(refresh_token=refresh_token, credentials_dir=credentials_dir)


@click.command()
@click.option(
    "--resource-type",
    type=click.Choice([c.value for c in ResourceType], case_sensitive=False),
    required=True,
    help="Resource type",
)
@click.option("--resource-id", type=str, required=True, help="Resource UUID")
def get_permissions(resource_type: ResourceType, resource_id: str) -> None:
    """Get permissions for a specific resource"""

    data_sdk = DataSDK()
    permissions = data_sdk.get_permissions(
        resource_type=resource_type, resource_id=resource_id
    )
    click.echo(permissions.json())


@click.command()
@click.option(
    "--resource-type",
    type=click.Choice([c.value for c in ResourceType], case_sensitive=False),
    required=True,
    help="Resource type",
)
@click.option("--resource-id", type=str, required=True, help="Resource UUID")
@click.option(
    "--organization",
    type=click.Choice(["viewer", "editor"]),
    required=False,
    help="Permissions for an organization",
)
@click.option(
    "viewers",
    "--viewer",
    type=str,
    required=False,
    multiple=True,
    help="Email address of user(s) who should have 'viewer' permissions",
)
@click.option(
    "editors",
    "--editor",
    type=str,
    required=False,
    multiple=True,
    help="Email address of user(s) who should have 'editor' permissions",
)
def set_permissions(
    resource_type: ResourceType,
    resource_id: str,
    organization: str | None,
    viewers: tuple[str],
    editors: tuple[str],
) -> None:
    """Set permissions for a specific resource"""

    data_sdk = DataSDK()

    user_permissions: list[dict] = []
    for viewer_email in viewers:
        user_permissions.append({"email": viewer_email, "permission": "viewer"})
    for editor_email in editors:
        user_permissions.append({"email": editor_email, "permission": "editor"})

    permissions = {"organization": organization, "users": user_permissions}

    data_sdk.set_permissions(
        resource_type=resource_type,
        resource_id=resource_id,
        permissions=CategorizedPermissions(**permissions),
    )


main.add_command(authenticate)
main.add_command(list_datasets)
main.add_command(get_dataset)
main.add_command(download_dataset)
main.add_command(upload_file)
main.add_command(update_dataset)
main.add_command(delete_dataset)
main.add_command(list_maps)
main.add_command(get_map)
main.add_command(create_map)
main.add_command(copy_map)
main.add_command(update_map)
main.add_command(delete_map)
main.add_command(list_data_connectors)
main.add_command(execute_query)
main.add_command(create_query_dataset)
main.add_command(create_external_dataset)
main.add_command(generate_hextile)
main.add_command(generate_vectortile)
main.add_command(store_refresh_token)
main.add_command(get_permissions)
main.add_command(set_permissions)

if __name__ == "__main__":
    main()
