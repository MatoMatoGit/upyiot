from upyiot.middleware.StructFile import StructFile
from upyiot.system.ExtLogging import ExtLogging


class Version:

    VERSION_DATA_FMT = "<III"

    _Instance = None

    @staticmethod
    def Instance():
        """
        Get the Version instance.
        :return: Version instance
        :rtype: <Version> or None
        """
        return Version._Instance

    def __init__(self, dir, major, minor, patch):
        if Version._Instance is not None:
            raise Exception("An instance of the Version class already exists.")

        Version._Instance = self
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

    def SwVersionString(self):
        """
        Returns the current software version as a string.
        Format: Major.minor.patch
        :return: current software version
        :rtype: string
        """
        return "{}.{}.{}".format(self.Major, self.Minor, self.Patch)

    def SwVersionEncoded(self):
        """
        Returns the current software version encoded as an integer.
        Format: Major x 100 + minor x 10 + patch
        :return: current software version
        :rtype: int
        """
        return self.Major * 100 + self.Minor * 10 + self.Patch
