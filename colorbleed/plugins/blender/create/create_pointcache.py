import avalon.api
from avalon.blender import lib

import bpy


class CreatePointcache(avalon.api.Creator):
    """Alembic pointcache for animated data"""

    name = "pointcache"
    label = "Point Cache"
    family = "colorbleed.pointcache"
    icon = "gears"

    def __init__(self, *args, **kwargs):
        super(CreatePointcache, self).__init__(*args, **kwargs)

        # Get current Blender frame range as initial values for start/end
        if bpy.context.scene.use_preview_range:
            start = bpy.context.scene.frame_preview_start
            end = bpy.context.scene.frame_preview_end
        else:
            start = bpy.context.scene.frame_start
            end = bpy.context.scene.frame_end

        self.data["startFrame"] = start
        self.data["endFrame"] = end
        self.data["handles"] = 1
        self.data["step"] = 1.0

        self.data["writeColorSets"] = False  # Vertex colors with the geometry.
        self.data["renderableOnly"] = False  # Only renderable visible shapes
        self.data["visibleOnly"] = False     # only nodes that are visible
        self.data["includeParentHierarchy"] = False  # Include parent groups

        # todo: implement custom data filter in export
        # Add options for custom attributes
        # self.data["attr"] = ""
        # self.data["attrPrefix"] = ""

    def process(self):

        collection = bpy.data.collections.new(self.name)

        # This is solely an Outliner collection
        collection.hide_viewport = True
        collection.hide_render = True
        collection.hide_select = True

        # Link the instance to the current scene
        bpy.context.scene.collection.children.link(collection)

        # TODO: Collections don't support custom data (dont have .data?)
        #lib.imprint(collection, self.data)

        # Link selection when option was passed
        if (self.options or {}).get("useSelection"):
            print("Use selection")
            selection = bpy.context.selected_objects
            for obj in selection:
                collection.objects.link(obj)

        return collection
