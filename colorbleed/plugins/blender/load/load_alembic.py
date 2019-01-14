import avalon.api as api
from avalon.blender.pipeline import containerise


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
        import os
        assert os.path.exists(self.fname), "%s does not exist." % self.fname

        # TODO: figure out if there's some sort of namespacing in Blender?
        # asset = context['asset']
        # namespace = namespace or lib.unique_namespace(
        #     asset["name"] + "_",
        #     prefix="_" if asset["name"][0].isdigit() else "",
        #     suffix="_",
        # )

        result = bpy.ops.wm.alembic_import(
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
        nodes = bpy.context.selected_objects

        # Only containerize if any nodes were loaded by the Loader
        if not nodes:
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
