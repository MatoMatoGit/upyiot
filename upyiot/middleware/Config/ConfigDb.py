import btree


class ConfigDbException(Exception):

    def __init__(self):
        return


class ConfigDbExceptionUpdateFailed(ConfigDbException):

    def __init__(self):
        return


class ConfigDef:

    def __init__(self, name, file_path):
        return


class ConfigLoader:

    def __init__(self, cfg_file_path):
        # Check if the config file exists,
        # open it if it does.

        # Deserialize the JSON contents.

        # Verify that required keys are present.
        return


class ConfigUpdater:

    def __init__(self, cfg_def_obj):
        # cfg_def_obj = config to update.

        # Create a config loader object to load the
        # config file.

        # Create a backup of the old config (overwrite the previous backup)

        # Overwrite the config
        return 0


class ConfigDb:

    def __init__(self):
        # Create / open internal db.

        # Create user db (if it does not exist).

        return

    def Add(self, cfg_def_obj):
        # Add the config def to the internal db.
        return

    def Remove(self, cfg_def_obj):
        # Remove the config def to the internal db.
        return

    def Update(self, cfg_def_obj):
        return

    def UpdateAll(self):
        # Loop over all configs and create a ConfigUpdater
        # for each one.
        return

    def Read(self, *keys):
        #
        return

    def Write(self, *keys, data):
        return
