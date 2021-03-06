import pyblish.api
import colorbleed.api
import colorbleed.maya.action


class ValidateAnimationContent(pyblish.api.InstancePlugin):
    """Adheres to the content of 'animation' family

    - Must have collected `outMembersHierarchy` data.
    - All nodes in `outMembersHierarchy` must be in the instance.

    """

    order = colorbleed.api.ValidateContentsOrder
    hosts = ["maya"]
    families = ["colorbleed.animation"]
    label = "Animation Content"
    actions = [colorbleed.maya.action.SelectInvalidAction]

    @classmethod
    def get_invalid(cls, instance):

        out_set = next((i for i in instance.data["setMembers"] if
                        i.endswith("out_SET")), None)

        assert out_set, ("Instance '%s' has no objectSet named: `OUT_set`. "
                         "If this instance is an unloaded reference, "
                         "please deactivate by toggling the 'Active' attribute"
                         % instance.name)

        assert 'outMembersHierarchy' in instance.data, \
            "Missing `outMembersHierarchy` data"

        # All nodes in the `outMembersHierarchy` must be among the nodes that
        # are in the instance. The nodes in the instance are found from the top
        # group, as such this tests whether all nodes are under that top group.

        lookup = set(instance[:])
        invalid = [node for node in instance.data['outMembersHierarchy'] if
                   node not in lookup]

        return invalid

    def process(self, instance):
        invalid = self.get_invalid(instance)
        if invalid:
            raise RuntimeError("Animation content is invalid. See log.")
