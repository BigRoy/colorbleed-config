import re

import pyblish.api
import colorbleed.api

from avalon import io


class ValidateUSDShadeModelExists(pyblish.api.InstancePlugin):
    """Validate the Instance has no current cooking errors."""

    order = colorbleed.api.ValidateContentsOrder
    hosts = ['houdini']
    families = ["usdShade"]
    label = 'USD Shade model exists'

    def process(self, instance):

        asset = instance.data["asset"]
        subset = instance.data["subset"]

        # Assume shading variation starts after a dot separator
        shade_subset = subset.split(".", 1)[0]
        model_subset = re.sub("^usdShade", "usdModel", shade_subset)

        asset_doc = io.find_one({"name": asset,
                                 "type": "asset"})
        if not asset_doc:
            raise RuntimeError("Asset does not exist: %s" % asset)

        subset_doc = io.find_one({"name": model_subset,
                                  "type": "subset",
                                  "parent": asset_doc["_id"]})
        if not subset_doc:
            raise RuntimeError("USD Model subset not found: "
                               "%s (%s)" % (model_subset, asset))
