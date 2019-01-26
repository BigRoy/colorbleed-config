import avalon.api as api

from avalon.blender import pipeline
from avalon.blender.pipeline import containerise
from avalon.blender import lib


def is_avalon_container(collection):
    # TODO: Accurately detect whether the collection is an avalon internal
    #  container (check attributes, etc.)
    if collection.name == pipeline.AVALON_CONTAINERS:
        return True

    return False


class AbcLoader(api.Loader):
    """Specific loader for Alembics"""

    families = ["colorbleed.model",
                "colorbleed.animation",
                "colorbleed.pointcache"]
    label = "Import Alembic"
    representations = ["abc"]
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self,
             context,
             name=None,
             namespace=None,
             data=None):

        import bpy

        # Ensure the currently active Collection is not an Avalon container
        # otherwise any loading operation will be loaded into that and
        # the selection will also not get caught correctly after import.
        collection = bpy.context.collection
        if is_avalon_container(collection):
            print("Import operation ignored as you are currently inside an "
                  "avalon collection. Please ensure you are active in the "
                  "scene collection you want to work in.")
            return

        import os
        assert os.path.exists(self.fname), "%s does not exist." % self.fname

        # TODO: figure out if there's some sort of namespacing in Blender?
        namespace = context['asset']['name']

        result = bpy.ops.wm.alembic_import(
            lib.get_override_context(),
            filepath=self.fname,
            set_frame_range=False,
            is_sequence=False,
            as_background_job=False,
            validate_meshes=False,
            scale=1
        )
        assert 'FINISHED' in result, "Alembic import did not finish.."

        # The new nodes are the ones that are selected directly after
        # the import
        nodes = lib.get_selected()

        # Only containerize if any nodes were loaded by the Loader
        if not nodes:
            print("No nodes selected after import Alembic?")
            return

        return containerise(
            name=name,
            namespace=namespace,
            nodes=nodes,
            context=context,
            loader=self.__class__.__name__)

    def update(self, container, representation):
        import os

        collection = container["node"]
        path = api.get_representation_path(representation)
        assert os.path.exists(path), "%s does not exist." % path

        # TODO: for each mesh in the container find the linked cache modifier
        #       to update the frames? But it should also add in the new
        #       objects? Or how do we update the loaded Alembic?
        raise NotImplemented("Update is not implemented")

        # Update metadata
        collection.data["representation"] = str(representation["_id"])

    def remove(self, container):
        """Remove an existing `container` from Maya scene

        Deprecated; this functionality is replaced by `api.remove()`

        Arguments:
            container (avalon-core:container-1.0): Which container
                to remove from scene.

        """

        collection = container["node"]
        self.log.info("Removing '%s' from Blender.." % container["name"])

        # TODO: Delete the collection and its members
        raise NotImplemented("Remove is not implemented")

    def switch(self, container, representation):
        self.update(container, representation)
