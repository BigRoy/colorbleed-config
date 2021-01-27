import pyblish.api


class SaveCurrentScene(pyblish.api.ContextPlugin):
    """Save current scene before extraction.

    This will skip saving scene if the current file has no modified changes.

    """

    label = "Save current file"
    order = pyblish.api.ExtractorOrder - 0.49
    hosts = ["maya"]
    families = ["colorbleed.renderlayer"]

    def process(self, context):
        import maya.cmds as cmds

        current = cmds.file(query=True, sceneName=True)
        assert context.data['currentFile'] == current

        # If file has no modifications, skip forcing a file save
        if not cmds.file(query=True, modified=True):
            self.log.debug("Skipping file save as there "
                           "are no modifications..")
            return

        self.log.info("Saving current file..")
        cmds.file(save=True, force=True)
