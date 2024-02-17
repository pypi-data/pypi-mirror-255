import json
from pathlib import Path

# from esi_releases.format import release_metadata

BASE_DIR = (Path(".").parent).resolve()
DATA_DIR = (Path(".").parent / "src" / "esi_releases" / "data").resolve()
TEST_DATA_DIR = (Path(".").parent / "tests" / "data").resolve()

JSON_FIELDS = [
    "name",
    "description",
    "version",
    "status",
    "organization",
    "vcs",
    "repositoryURL",
    "homepageURL",
    "downloadURL",
    "disclaimerURL",
    "permissions",
    "laborHours",
    "languages",
    "tags",
    "contact",
    "date",
]

JSON_URL_FIELDS = [
    "repositoryURL",
    "homepageURL",
    "downloadURL",
    "disclaimerURL",
    "permissions",
]

JSON_PKG_VERSION_FIELDS = [
    "downloadURL",
    "disclaimerURL",
    "permissions",
]


def load_code_json(filename):
    if not isinstance(filename, str):
        filename = str(filename)

    with open(filename, "r") as f:
        try:
            print("Loading json file: " + filename)
            code_json = json.load(f)

            return code_json

        except Exception as e:
            raise e


# def check_version_format():
#     # Check if version format includes a prepended 'v' or not
#     return


# def check_release_history():
#     # Print out all previous versions from code.json
#     return


# def validate_release_history():
#     # Check that release history entries are increasing in version #
#     return
