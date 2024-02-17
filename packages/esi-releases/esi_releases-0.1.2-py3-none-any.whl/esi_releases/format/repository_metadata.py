# TODO: Eventually break out associated info (URLS) into a new class


class RepositoryMetadata(object):
    def __init__(self, urls, permissions) -> None:
        self.repositoryURL = urls[0]
        self.homepageURL = urls[1]
        self.downloadURL = urls[2]
        self.disclaimerURL = urls[3]
        self.licenseURL = self.permissions["licenses"]["URL"]
