import os
import sys
import logging

import bpy

from avalon import api as avalon
from pyblish import api as pyblish


log = logging.getLogger("colorbleed.blender")

PARENT_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.dirname(PARENT_DIR)
PLUGINS_DIR = os.path.join(PACKAGE_DIR, "plugins")

PUBLISH_PATH = os.path.join(PLUGINS_DIR, "blender", "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "blender", "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "blender", "create")


def install():
    pyblish.register_plugin_path(PUBLISH_PATH)
    avalon.register_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.register_plugin_path(avalon.Creator, CREATE_PATH)

    # Callbacks below are not required for headless mode, the `init` however
    # is important to load referenced Alembics correctly at rendertime.
    if bpy.app.background:
        log.info("Running in headless mode, skipping Colorbleed Blender "
                 "save/open/new callback installation..")
        return

    # Initialize a QApplication without exec_() that can keep running
    # in the background. By having an instance created already this also
    # ensures the Avalon tools will not trigger exec_() as they will assume
    # the current QApplication instance is already executing.
    from avalon.vendor.Qt import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Somehow this instance gets closed after this script finished running.
    # Probably because Blender 'cleans up' and garbage collects the finished
    # script. So we need to instead register this as an addon to open up
    # the QApplication, maybe?
    # See: https://raw.githubusercontent.com/RichardFrangenberg/Prism/development/Prism/Plugins/Apps/Blender/Integration/PrismInit.py


    #avalon.on("save", on_save)
    #avalon.on("open", on_open)
    #avalon.on("new", on_new)
    #avalon.before("save", on_before_save)

    #log.info("Overriding existing event 'taskChanged'")
    #override_event("taskChanged", on_task_changed)

    #log.info("Setting default family states for loader..")
    #avalon.data["familiesStateToggled"] = ["colorbleed.imagesequence"]


def uninstall():
    pyblish.deregister_plugin_path(PUBLISH_PATH)
    avalon.deregister_plugin_path(avalon.Loader, LOAD_PATH)
    avalon.deregister_plugin_path(avalon.Creator, CREATE_PATH)
