class Version:
    def __init__(self, version=None):
        if version is None:
            self.patch = 0
            self.minor = 0
            self.major = 0

        elif isinstance(version, str):
            if "v" in version:
                version = version.replace("v", "")
            levels = version.split(".")
            self.major = int(levels[0])
            self.minor = int(levels[1])
            self.patch = int(levels[2])

    def to_str(self):
        version_str = (
            "v" + str(self.major) + "." + str(self.minor) + "." + str(self.patch)
        )
        return version_str

    def to_num(self):
        version_num = str(self.major) + "." + str(self.minor) + "." + str(self.patch)
        return version_num

    def bump(self, level="patch"):
        if level == "patch":
            self.patch += 1

        if level == "minor":
            self.minor += 1
            self.patch = 0

        if level == "major":
            self.major += 1
            self.minor = 0
            self.patch = 0
