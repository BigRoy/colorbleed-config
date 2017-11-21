import os
import sys
import tempfile
import shutil

import pyblish.util

from avalon import api, maya, io, inventory, schema, pipeline


IS_SILENT = bool(os.getenv("AVALON_SILENT"))
PROJECT_NAME = "hulk"
ASSET_NAME = "Bruce"
TASK_NAME = "modeling"

self = sys.modules[__name__]
self._tempdir = None
self._config = {
    "schema": "avalon-core:config-1.0",
    "apps": [
        {"name": "app1"},
    ],
    "tasks": [
        {"name": "task1"},
    ],
    "template": {
        "work":
            "{root}/{project}/{silo}/{asset}/work/{task}/{app}",
        "publish":
            "{root}/{project}/{silo}/{asset}/publish/"
            "{subset}/v{version:0>3}/{subset}.{representation}"
    },
    "copy": {}
}
self._inventory = {
    "schema": "avalon-core:inventory-1.0",
    "assets": [
        {"name": ASSET_NAME},
        {"name": "Claire"}
    ],
    "film": []
}


def setup():
    self._tempdir = tempfile.mkdtemp()

    # Setup environment
    api.Session["AVALON_PROJECTS"] = self._tempdir
    api.Session["AVALON_CONFIG"] = "colorbleed"
    api.Session["AVALON_PROJECT"] = PROJECT_NAME

    # TODO(roy): We should be able to install without the next settings set
    api.Session["AVALON_ASSET"] = ASSET_NAME
    api.Session["AVALON_SILO"] = "assets"
    api.Session["AVALON_TASK"] = TASK_NAME
    api.Session["AVALON_APP"] = "maya"
    workdir = pipeline._format_work_template(
        self._config["template"]["work"], api.Session)
    api.Session["AVALON_WORKDIR"] = workdir

    # Ensure the environment is set like the session prior to installing
    os.environ.update(api.Session)

    # Install maya host
    api.install(maya)

    # Create the project
    schema.validate(self._config)
    schema.validate(self._inventory)
    inventory.save(
        name=PROJECT_NAME,
        config=self._config,
        inventory=self._inventory
    )


def teardown():
    io.drop()
    api.uninstall()

    shutil.rmtree(self._tempdir)


def publish():
    context = pyblish.util.publish()

    if not IS_SILENT:

        header = "{:<10}{:<40} -> {}".format("Success", "Plug-in", "Instance")
        result = "{success:<10}{plugin.__name__:<40} -> {instance}"
        error = "{:<10}+-- EXCEPTION: {:<70} line {:<20}"
        record = "{:<10}+-- {level}: {message:<70}"

        results = list()
        for r in context.data["results"]:
            # Format summary
            results.append(result.format(**r))

            # Format log records
            for lr in r["records"]:
                results.append(
                    record.format(
                        "",
                        level=lr.levelname,
                        message=lr.msg))

            # Format exception (if any)
            if r["error"]:
                _, line, _, _ = r["error"].traceback
                results.append(error.format("", r["error"], line))

        report = """
{header}
{line}
{results}
        """

        print(report.format(header=header,
                            results="\n".join(results),
                            line="-" * 70))

    return context
