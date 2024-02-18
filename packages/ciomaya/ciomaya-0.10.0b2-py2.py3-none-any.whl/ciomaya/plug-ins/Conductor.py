import sys
import os

CIODIR = os.environ.get("MAYA_CIODIR")
sys.path.append(CIODIR)


import maya.api.OpenMaya as om

import ciocore.loggeria
from ciocore import data as coredata
import maya.cmds as mc


def maya_useNewAPI():
    pass


def initializePlugin(obj):
    # Use "0.10.0-beta.2 to cause the version to be replaced at build time."
 
    # if not check_pymel():
    #     return

    plugin = om.MFnPlugin(obj, "Conductor", "0.10.0-beta.2", "Any")
    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.registerNode(
            "conductorRender",
            conductorRender.id,
            conductorRender.creator,
            conductorRender.initialize,
            om.MPxNode.kDependNode,
        )
    except:
        sys.stderr.write("Failed to register conductorRender\n")
        raise

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib import conductor_menu
    conductor_menu.load()

    coredata.init("maya-io")


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.deregisterNode(conductorRender.id)
    except:
        sys.stderr.write("Failed to deregister conductorRender\n")
        raise

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib import conductor_menu
    conductor_menu.unload()
