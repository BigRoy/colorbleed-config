"""Integration tests

These tests include external libraries in order to test
the integration between them.

"""

import os

from tests.lib import (
    setup,
    teardown,
    publish,
    ASSET_NAME,
    TASK_NAME,
    PROJECT_NAME
)

from nose.tools import (
    with_setup,
    assert_equals,
)

from avalon import io, api
import colorbleed.maya.lib

from maya import cmds


def clear():

    # Create and set the Maya workspace
    workdir = api.Session["AVALON_WORKDIR"]
    if not os.path.exists(workdir):
        cmds.workspace(workdir, newWorkspace=True)
    else:
        cmds.workspace(workdir, openWorkspace=True)

    cmds.file(new=True, force=True)
    _rename_scene("temp.ma")


@with_setup(clear)
def test_modeling():
    """Modeling workflow is functional"""
    transform, generator = cmds.polyCube(name="body_GEO")
    group = cmds.group(transform, name="hulk_GRP")

    cmds.select(group, replace=True)
    api.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="colorbleed.model",
        options={"useSelection": True}
    )

    # Comply with save validator
    cmds.file(save=True)

    publish()

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    assert asset

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "modelDefault"
    })

    assert subset

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
    })

    assert version

    assert io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "ma"
    }) is not None


@with_setup(clear)
def test_pointcache_export():
    """Exporting pointcache family to Alembic works"""

    transform, generator = cmds.polyCube(name="myCube_GEO")

    visibility_keys = [
        (10, True),
        (20, False),
        (30, True)
    ]

    for time, value in visibility_keys:
        cmds.setKeyframe(transform,
                         time=time,
                         attribute="visibility",
                         value=value)

    api.create(
        name="pointcacheDefault",
        asset=ASSET_NAME,
        family="colorbleed.pointcache",
        options={"useSelection": True}
    )

    cmds.file(save=True)

    publish()

    # Import and test result
    cmds.file(new=True, force=True)

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "pointcacheDefault"
    })

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
        "name": 1
    })

    assert version

    representation = io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "abc"
    })

    assert representation is not None

    loader = _get_loader_by_name(representation["_id"], "AbcLoader")
    container = api.load(loader, representation)
    nodes = cmds.sets(container, query=True)
    print("Nodes: %s" % nodes)
    cube = cmds.ls(nodes, type="mesh")
    transform = cmds.listRelatives(cube, parent=True)[0]

    for time, value in visibility_keys:
        cmds.currentTime(time, edit=True)
        assert cmds.getAttr(transform + ".visibility") == value, (
            "Cached visibility did not match original visibility")


@with_setup(clear)
def test_camera_export():
    """Exporting camera works with substeps with animated focal length"""

    transform, camera = cmds.camera(name="camera")
    group = cmds.group(empty=True, name="camera_GRP")

    # Apply animation
    animation = {
        (transform, "translateY"): ((10, 0), (20, 10), (30, -5)),
        (camera, "focalLength"): ((10, 35), (12.25, 70.25), (30, 10)),
        (group, "translateX"): ((10, 0), (20, 500), (30, -30.55))
    }
    for (node, attr), keys in animation.items():
        for time, value in keys:
            cmds.setKeyframe(node,
                             time=time,
                             attribute=attr,
                             value=value)

    cmds.parent(transform, group)

    cmds.select(group, replace=True)
    api.create(
        name="cameraDefault",
        asset=ASSET_NAME,
        family="colorbleed.camera",
        options={"useSelection": True}
    )

    # TODO(roy): This should be set using the api
    cmds.setAttr("cameraDefault.startFrame", 10)
    cmds.setAttr("cameraDefault.endFrame", 30)
    cmds.setAttr("cameraDefault.step", 0.25)

    cmds.file(save=True)

    publish()

    # Import and test result
    cmds.file(new=True, force=True)

    representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "cameraDefault", 1, "abc"
    ])

    assert representation is not None

    loader = _get_loader_by_name(representation, "CameraLoader")
    container = api.load(loader, representation)
    nodes = cmds.sets(container, query=True)
    print("Nodes: %s" % nodes)

    cameras = cmds.ls(nodes, type="camera")
    assert len(cameras) == 1
    camera = cameras[0]

    transform = cmds.listRelatives(camera, parent=True)[0]

    # Validate the animation on the camera matches to 2 decimals
    valid_animation = True
    for (_, attr), keys in animation.items():
        node = transform if attr in ["translateY", "translateX"] else camera
        for time, value in keys:
            cmds.currentTime(time, edit=True)

            plug = "{}.{}".format(node, attr)
            original = round(value, 3)
            current = round(cmds.getAttr(plug), 3)
            if original != current:
                print("Current value does not match original: {0} != {1} "
                      "({2} on time {3})".format(current, original,
                                                 attr, time))
                valid_animation = False

    assert valid_animation, "Camera animation not similar to original"


@with_setup(clear)
def test_model_update():
    """Updating model works"""

    transform, generator = cmds.polyCube(name="body_GEO")
    group = cmds.group(transform, name="hulk_GRP")

    cmds.select(group, replace=True)
    api.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="colorbleed.model",
        options={"useSelection": True}
    )

    # Comply with save validator
    cmds.file(save=True)

    publish()
    publish()
    publish()  # Version 3

    cmds.file(new=True, force=True)

    asset = io.find_one({
        "type": "asset",
        "name": ASSET_NAME
    })

    subset = io.find_one({
        "parent": asset["_id"],
        "type": "subset",
        "name": "modelDefault"
    })

    version = io.find_one({
        "parent": subset["_id"],
        "type": "version",
        "name": 2
    })

    assert version

    representation = io.find_one({
        "parent": version["_id"],
        "type": "representation",
        "name": "ma"
    })

    # Load version 2 and update to 3
    loader = _get_loader_by_name(representation["_id"], "ModelLoader")
    api.load(loader, representation["_id"])
    host = api.registered_host()
    container = next(host.ls())
    api.update(container, version=3)


@with_setup(clear)
def test_modeling_to_rigging():
    """Test modeling to rigging

    This generates a model publish that gets loaded in in a rig and
    then gets published as rig.

    """
    transform, generator = cmds.polyCube(name="body_GEO")
    group = cmds.group(transform, name="hulk_GRP")

    cmds.select(group, replace=True)
    api.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="colorbleed.model",
        options={"useSelection": True})

    # Comply with save validator
    cmds.file(save=True)

    publish()

    cmds.file(new=True, force=True)

    representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "modelDefault", 1, "ma"
    ])

    # Get ModelLoader
    loader = _get_loader_by_name(representation, "ModelLoader")

    container = api.load(loader, representation)
    nodes = cmds.sets(container, query=True)
    assembly = cmds.ls(nodes, assemblies=True)[0]
    assert_equals(assembly, "Bruce_01_:modelDefault")

    # Rig it
    mesh = cmds.ls(nodes, type="mesh")
    transform = cmds.listRelatives(mesh, parent=True)[0]
    ctrl = cmds.circle(name="main_CTL")[0]
    cmds.parentConstraint(ctrl, transform)

    # Rig rule: Controls must have visibility locked
    cmds.setAttr(ctrl + ".visibility", lock=True)

    # Rig rule: Everything must be under a single group
    group = cmds.group([assembly, ctrl], name="rig_GRP")

    cmds.select([group], noExpand=True)
    api.create(
        name="rigDefault",
        asset=os.environ["AVALON_ASSET"],
        family="colorbleed.rig",
        options={"useSelection": True},
    )

    assert cmds.objExists("out_SET"), "out_SET does not exist"
    assert cmds.objExists("controls_SET"), "controls_SET does not exist"

    # Rig rule: Add out geometry to `out_SET` and controls to `controls_SET`
    cmds.sets(mesh, forceElement="out_SET")
    cmds.sets(ctrl, forceElement="controls_SET")

    _rename_scene("temp.ma")
    cmds.file(save=True)

    publish()

    cmds.file(new=True, force=True)

    representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "rigDefault", 1, "ma"
    ])

    # Load the rig with RigLoader
    loader = _get_loader_by_name(representation, "RigLoader")
    container = api.load(loader, representation)
    nodes = cmds.sets(container, query=True)
    assembly = cmds.ls(nodes, assemblies=True)[0]
    assert_equals(assembly, "Bruce_01_:rigDefault")


@with_setup(clear)
def test_modeling_to_lookdev():
    """Model to lookdev to model assignment works

    This will publish a new model, it will load it and then assign a shader
    and publish that as look. Then it will load the model in a new scene and
    assign the default shader, validating it is the shader we just created.

    """

    transform, generator = cmds.polyCube(name="head_GES")
    group = cmds.group(transform, name="hulk_GRP")

    cmds.select(group, replace=True)
    api.create(
        name="modelDefault",
        asset=ASSET_NAME,
        family="colorbleed.model",
        options={"useSelection": True}
    )

    # Comply with save validator
    cmds.file(save=True)

    publish()

    cmds.file(force=True, new=True)
    _rename_scene("lookdev_temp.ma")

    # Load the published model
    model_representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "modelDefault", 1, "ma"
    ])
    model_loader = _get_loader_by_name(model_representation, "ModelLoader")
    container = api.load(model_loader, model_representation)
    members = cmds.sets(container, query=True)
    mesh = cmds.ls(members, type="mesh")[0]

    # Create a material and shading engine
    material = cmds.shadingNode("blinn", name="my_shader", asShader=True)
    sg = cmds.sets(empty=True, renderable=True,
                   noSurfaceShader=True, name="my_shaderSG")
    cmds.connectAttr(material + ".outColor", sg + ".surfaceShader")

    # Assign the shaders
    cmds.sets([mesh], forceElement=sg)

    assembly = cmds.ls(members, assemblies=True, long=True)[0]
    cmds.select(assembly)
    api.create(
        name="lookDefault",
        asset=ASSET_NAME,
        family="colorbleed.look",
        options={"useSelection": True}
    )

    cmds.file(save=True)

    publish()

    # Test look assignment
    cmds.file(new=True, force=True)
    container = api.load(model_loader, model_representation)
    members = cmds.sets(container, query=True)
    colorbleed.maya.lib.assign_look(members, "lookDefault")

    # Ensure this look is loaded
    look_representation = io.locate([
        PROJECT_NAME, ASSET_NAME, "lookDefault", 1, "ma"
    ])
    host = api.registered_host()
    assert any(True for container in host.ls() if
               container["representation"] == str(look_representation))

    # Ensure look is correctly assigned
    mesh = cmds.ls(members, type="mesh")[0]
    sets = cmds.listSets(o=mesh)
    assert sets[0].endswith("my_shaderSG")


def _get_loader_by_name(representation_id, loader_name):
    """Get a loader for representation id by name"""
    loaders = api.discover(api.Loader)

    # Get the loader by name
    loader = next((x for x in loaders if x.__name__ == loader_name), None)
    if not loader:
        raise RuntimeError("Can't find loader with name: "
                           "{}".format(loader_name))

    # Get the loader by compatibility
    loaders = api.loaders_from_representation([loader], representation_id)
    if not loaders:
        raise RuntimeError("Loader is not compatible: "
                           "{}".format(loader_name))

    return loaders[0]


def _rename_scene(name):
    """Rename maya scene with relative name to Session's workdir

    To save run `cmds.file(save=True)` afterwards.

    """
    workdir = api.Session["AVALON_WORKDIR"]
    path = os.path.join(workdir, name)
    cmds.file(rename=path)
