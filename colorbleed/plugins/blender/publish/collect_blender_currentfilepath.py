import bpy

import pyblish.api


class CollectBlenderCurrentFile(pyblish.api.ContextPlugin):
    """Inject the current working file into context"""

    label = "Blender Current File"
    order = pyblish.api.CollectorOrder - 0.5
    hosts = ['blender']

    def process(self, context):
        """Inject the current working file"""
        current_file = bpy.data.filepath
        context.data['currentFile'] = current_file
