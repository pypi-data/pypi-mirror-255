from __future__ import unicode_literals

"""
Handle the UI for ScoutFrames:

when the useScoutFrames checkbox is unchecked,
the field is hidden. 
"""

import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI."""

    with AEcommon.ae_template():
        pm.checkBoxGrp("frameSpecCheckbox", label="Use Scout Frames")
        pm.frameLayout("frameSpecFrame", visible=False, lv=False, cl=False, cll=False)

        pm.textFieldGrp("frameSpecField", label="Scout Frames")

        pm.setParent("..")  # out of frameLayout
        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""

    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()

    bool_attr = attr.node().attr("useScoutFrames")
    bool_val = bool_attr.get()
    val = attr.get()

    pm.checkBoxGrp(
        widgets["checkbox"],
        edit=True,
        value1=bool_val,
        changeCommand=pm.Callback(_on_bool_changed, bool_attr, **widgets),
    )

    pm.textFieldGrp(
        widgets["field"],
        edit=True,
        text=val,
        changeCommand=pm.Callback(_on_text_changed, attr, **widgets),
    )
    _on_bool_changed(bool_attr, **widgets)


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "checkbox": AEcommon.find_ui("frameSpecCheckbox", parent),
        "frame": AEcommon.find_ui("frameSpecFrame", parent),
        "field": AEcommon.find_ui("frameSpecField", parent),
    }


def _on_bool_changed(attr, **widgets):
    checkbox = widgets["checkbox"]
    frame = widgets["frame"]
    val = pm.checkBoxGrp(checkbox, q=True, value1=True)
    attr.set(val)
    pm.frameLayout(frame, edit=True, enable=True, visible=val)
    AEcommon.print_setAttr_cmd(attr)


def _on_text_changed(attr, **widgets):
    attr.set(pm.textFieldGrp(widgets["field"], q=True, text=True))
    AEcommon.print_setAttr_cmd(attr)
