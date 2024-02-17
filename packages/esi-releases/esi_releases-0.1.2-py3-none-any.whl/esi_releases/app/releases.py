import json
import copy
import typer

# Local imports
from esi_releases.format import release_metadata
from esi_releases.utils.metadata_utils import load_code_json
from esi_releases.utils.metadata_utils import BASE_DIR, DATA_DIR

project_code_json = BASE_DIR / "code.json"
example_code_json = DATA_DIR / "example_code.json"
default_code_json = DATA_DIR / "default_code.json"

app = typer.Typer()


@app.command()
def bump_version(
    release_level: str = typer.Argument(
        default="patch", help="Version level to bump at i.e. 'major'.'minor'.'patch'"
    )
):
    # major: str = (typer.Option(None, help="Bump version at the major level aka N.0.0"),)
    # minor: str = (typer.Option(None, help="Bump version at the minor level aka 0.N.0"),)
    # patch: str = (typer.Option(None, help="Bump version at the patch level aka 0.0.N"),)

    try:
        # Load project code.json file
        code_json = load_code_json(project_code_json)

        # Instantiate new release_metadata obj
        current_release = release_metadata.ReleaseMetadata()
        current_release.fill_from_json(project_code_json)

        # Can improve if using above list
        new_release = copy.deepcopy(current_release)
        new_release.bump_version(release_level=release_level)

        # Update the "metadataLastUpdated" field to current time
        new_release.sync_time()

        # Prepend new release metadata and convert to JSON str
        bumped_release = [new_release.__dict__] + code_json
        bumped_release_json = json.dumps(bumped_release, indent=4)

        # Write to the code.json file
        with open(project_code_json, mode="w") as outfile:
            outfile.write(bumped_release_json)
    except Exception as e:
        return e


if __name__ == "__main__":
    # app()
    typer.run(bump_version)
