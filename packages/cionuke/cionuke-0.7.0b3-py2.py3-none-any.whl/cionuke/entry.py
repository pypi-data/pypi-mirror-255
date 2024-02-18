"""Entry point for the Submitter."""

import datetime
import os
import sys

import nuke

from cionuke import utils
from cionuke.components import (
    actions,
    advanced,
    autosave,
    copy_cat,
    environment,
    assets,
    frames,
    instance_type,
    metadata,
    preview,
    project,
    software,
    title,
)


# SAFE_KNOB_CHANGED calls entry.knobChanged() in a try block
# because the node is present on the render node but the
# Python module is not.
SAFE_KNOB_CHANGED = """
try:
    entry.knobChanged()
except NameError:
    pass
"""

def add_to_nodes():
    """
    Add a Conductor submitter node to the project.

    Connect selected Write nodes to the selected submitter nodes.
    If no submitter exists, build a new one.
    """

    submitters = [n for n in nuke.selectedNodes("Group") if n.knob("cio_title")]

    if nuke.selectedNodes("Write") and nuke.selectedNodes("CopyCat"):
        raise Exception("Write nodes and CopyCat nodes have both been selected. Please only select one type.")
    
    else:
        # We can query for both node types since only a single node type can be selected
        render_nodes = [n for n in (nuke.selectedNodes("Write") + nuke.selectedNodes("CopyCat"))]

    if not render_nodes:
        print("Select at least one Write node.")
        return

    build_new = False
    if not submitters:
        build_new = True
        submitter = nuke.createNode("Group")
        submitter.setName("Conductor")
        submitters = [submitter]

    for submitter in submitters:
        inputs = submitter.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)
        i = len(inputs)
        for render_node in render_nodes:
            if render_node not in inputs:
                render_node.knob("selected").setValue(False)
                submitter.setInput(i, render_node)
                i += 1

    if build_new:
        build_tabs(submitter)
        submitter.knob("selected").setValue(True)
        nuke.show(submitter)
        submitter.knob("Configure").setFlag(0)


def build_tabs(submitter):
    """
    Add Conductor controls to the submitter.

    Args:
        submitter (Group node): The submitter node
    """
    config_tab = nuke.Tab_Knob("Configure")
    submitter.addKnob(config_tab)

    actions.build(submitter)
    title.build(submitter)
    project.build(submitter)
    instance_type.build(submitter)
    utils.divider(submitter, "div_1")
    software.build(submitter)
    utils.divider(submitter, "div_2")

    if submitter.input(0).Class() == "CopyCat":
        copy_cat.build(submitter)

    else:
        frames.build(submitter)
    
    utils.divider(submitter, "div_3")
    advanced.build(submitter)
    environment.build(submitter)
    utils.divider(submitter, "div_4")
    assets.build(submitter)
    utils.divider(submitter, "div_5")
    metadata.build(submitter)
    utils.divider(submitter, "div_6")
    autosave.build(submitter)

    preview_tab = nuke.Tab_Knob("Preview")
    submitter.addKnob(preview_tab)
    preview.build(submitter)

    submitter.knob("knobChanged").setValue(SAFE_KNOB_CHANGED)

COMPONENTS = (
    actions,
    project,
    title,
    instance_type,
    software,
    environment,
    metadata,
    assets,
    frames,
    advanced,
    autosave,
    preview,
    copy_cat
)

def knobChanged():
    """
    Notify all component modules when a knob changes.
    """
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    for component in COMPONENTS:
        try:
            component.knobChanged(node, knob)
        except AttributeError:
            pass
