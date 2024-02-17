import re
import json
from datetime import datetime

from esi_releases.utils.metadata_utils import JSON_FIELDS, DATA_DIR
from esi_releases.format.version import Version

example_code_json = DATA_DIR / "example_code.json"


class ReleaseMetadata:
    def __init__(self, version="v0.0.0") -> None:
        self.name = "usgs-package"
        self.description = "Description of functionality"
        self.version = str(version)
        self.status = "Development"
        self.organization = "U.S. Geological Survey"
        self.vcs = "git"
        self.repositoryURL = "https://code.usgs.gov/ghsc/esi/my-cool-package/.git"
        self.homepageURL = "https://code.usgs.gov/ghsc/esi/my-cool-packages/"
        self.downloadURL = ""
        self.disclaimerURL = {
            "https://code.usgs.gov/ghsc/esi/my-cool-package/-/tree/main/DISCLAIMER.md"
        }
        self.permissions = (
            {
                "licenses": {
                    "name": "Public Domain, CC0-1.0",
                    "URL": "https://code.usgs.gov/ghsc/esi/my-cool-package/-/tree/main/LICENSE.md",
                },
                "usageType": "openSource",
                "exemptionText": "null",
            },
        )
        self.laborHours = 1
        self.languages = ["python", "bash"]
        self.tags = [
            "releases",
            "utilities",
        ]
        self.contact = {"name": " Name Name", "email": "name@usgs.gov"}
        self.date = {"metadataLastUpdated": str(datetime.now()).split(" ", 1)[0]}

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_description(self):
        return self.name

    def set_description(self, description):
        self.description = description

    def get_version(
        self,
    ):
        return self.version

    def set_version(self, version):
        if "v" not in version:
            version = "v" + str(version)
        self.version = version

    def get_URLs(self):
        url_dict = {
            "repositoryURL": self.repositoryURL,
            "homepageURL": self.homepageURL,
            "downloadURL": self.downloadURL,
            "disclaimerURL": self.disclaimerURL,
            "licenseURL": self.permissions["licenses"][0]["URL"],
        }

        return url_dict

    def set_URLs(self, urls):
        self.repositoryURL = urls[0]
        self.homepageURL = urls[1]
        self.downloadURL = urls[2]
        self.disclaimerURL = urls[3]
        self.licenseURL = self.permissions["licenses"]["URL"]

    def update_URLs(self):
        # Update the version tags in relevant URLs
        version = self.get_version()

        old_URLs = self.get_URLs()

        REGEX_V = r"v[0-9]+\.[0-9]+\.[0-9]+"
        # REGEX_V = r"[0-9]+\.[0-9]+\.[0-9]+"

        new_urls = old_URLs.copy()
        for url in old_URLs:
            new_urls[url] = re.sub(REGEX_V, version, old_URLs[url], re.IGNORECASE)
            # print(new_urls)

        self.downloadURL = new_urls["downloadURL"]
        self.disclaimerURL = new_urls["disclaimerURL"]
        # self.licenseURL = new_urls["licenseURL"]
        self.permissions["licenses"][0]["URL"] = new_urls["licenseURL"]

    def get_metadata_fields(self):
        return JSON_FIELDS

    def fill_from_json(self, filename):
        filename = str(filename)

        with open(filename, "r") as f:
            try:
                print("json filename: " + filename)
                code_json = json.load(f)

                # Get most recent release entry in code.json file
                self.__dict__.update(code_json[0])

            except Exception as e:
                raise e

    def bump_version(self, release_level="patch"):
        old_version = self.get_version()

        new_version = Version(version=old_version)
        new_version.bump(level=release_level)

        self.set_version(new_version.to_str())
        self.update_URLs()

    # def bump_URLs(self):

    def sync_time(self):
        self.date = {"metadataLastUpdated": str(datetime.now()).split(" ", 1)[0]}
