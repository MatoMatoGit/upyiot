from upyiot.middleware.StructFile import StructFile
from upyiot.system.ExtLogging import ExtLogging


class Version:

    VERSION_DATA_FMT = "<III"

    def __init__(self, dir, major, minor, patch):
        self.Log = ExtLogging.Create("Version")
        self.VersionSFile = StructFile.StructFile(dir + '/ver', self.VERSION_DATA_FMT)

        try:
            self.Major, self.Minor, self.Patch = self.VersionSFile.ReadData(0)
        except TypeError:
            self.Log.info("No stored version present.")
            self.Major = self.Minor = self.Patch = -1

        self.Log.info("Current version (major.minor.patch): {}.{}.{}".format(self.Major, self.Minor, self.Patch))

        if major is not self.Major or minor is not self.Minor \
                or patch is not self.Patch:
            self.Major = major
            self.Minor = minor
            self.Patch = patch
            self.VersionSFile.WriteData(0, self.Major, self.Minor, self.Patch)

            self.Log.info("New version: {}.{}.{}".format(self.Major, self.Minor, self.Patch))
