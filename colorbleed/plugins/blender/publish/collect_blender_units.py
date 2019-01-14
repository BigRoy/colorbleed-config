import bpy

import pyblish.api


class CollectBlenderUnits(pyblish.api.ContextPlugin):
    """Collect Blender's scene units."""

    label = "Blender Units"
    order = pyblish.api.CollectorOrder
    hosts = ["blender"]

    def process(self, context):

        unit_settings = bpy.context.scene.unit_settings

        context.data['linearUnits'] = unit_settings.system
        context.data['angularUnits'] = unit_settings.system_rotation
        context.data['fps'] = bpy.context.scene.render.fps
