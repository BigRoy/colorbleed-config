import os

import avalon.blender
import colorbleed.api


class ExtractBlenderAlembic(colorbleed.api.Extractor):
    """Produce an alembic of the instance."""

    label = "Extract Pointcache (Alembic)"
    hosts = ["maya"]
    families = ["colorbleed.pointcache",
                "colorbleed.model"]

    def process(self, instance):

        import bpy

        # Collect the start and end including handles
        start = instance.data.get("startFrame", 1)
        end = instance.data.get("endFrame", 1)
        handles = instance.data.get("handles", 0)
        if handles:
            start -= handles
            end += handles

        # attrs = instance.data.get("attr", "").split(";")
        # attrs = [value for value in attrs if value.strip()]
        # attrs += ["cbId"]
        #
        # attr_prefixes = instance.data.get("attrPrefix", "").split(";")
        # attr_prefixes = [value for value in attr_prefixes if value.strip()]

        # Get extra export arguments
        writeColorSets = instance.data.get("writeColorSets", False)

        self.log.info("Extracting pointcache..")
        dirname = self.staging_dir(instance)

        parent_dir = self.staging_dir(instance)
        filename = "{name}.abc".format(**instance.data)
        path = os.path.join(parent_dir, filename)

        # Parse options from the instance
        options = {
            # todo: test samples
            "xsamples": instance.data.get("step", 1.0),
            "gsamples": instance.data.get("step", 1.0),
            # todo: see if
            #"writeVisibility": True,
            #"writeCreases": True,
            "vcolors": writeColorSets,
            "renderable_only": instance.data["renderableOnly"],
            "visible_layers_only": instance.data["visibleOnly"],
            "flatten": not instance.data["includeParentHierarchy"]

        }

        with avalon.blender.maintained_selection():

            # Clear the selection
            for node in bpy.context.selected_objects:
                node.select_set(state=False)

            # Select only the instance nodes
            for node in instance:
                node.select_set(state=True)

            # Export to Alembic
            bpy.ops.wm.alembic_export(filepath=path,
                                      selected=True,
                                      start=start,
                                      end=end,
                                      uvs=True,
                                      packuv=True,
                                      renderable_only=False,
                                      normals=True,
                                      face_sets=True,
                                      compression_type="OGAWA",
                                      export_hair=True,
                                      export_particles=True,
                                      as_background_job=False,
                                      init_scene_frame_range=False,
                                      **options)

        if "files" not in instance.data:
            instance.data["files"] = list()

        instance.data["files"].append(filename)

        self.log.info("Extracted {} to {}".format(instance, dirname))
