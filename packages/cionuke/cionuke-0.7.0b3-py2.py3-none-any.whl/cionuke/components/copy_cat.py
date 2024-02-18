"""
Controls specific for CopyCat.
"""
import nuke
import os
import pathlib

import ciocore.loggeria
from cionuke.components import advanced

LOG = ciocore.loggeria.get_conductor_logger()

NODE_SYNC_SCRIPT_PATH = pathlib.Path(__file__).parent.with_name("node_sync.py")

COPY_CAT_MODE_TOOLTIP = """
Single Instance: Submit and train the CopyCat node on a single machine (support multiple GPUs). Training is not visible in Nuke. Training data will need to be downloaded.

Distributed (local Main): Submit and train the CopyCat node on multiple remote machines, communicating with directly with the main node running on your machine. Training is visible in Nuke. Training data does not need to be downloaded. Only available on Linux.

Distributed (remote Main): Submit and train the CopyCat node on multiple remote machines. Main node is remote as well. Training is not visible in Nuke. Training data will need to be downloaded.
"""

COPY_CAT_MODES = {'single_instance': 'Single Instance',
                  'distributed_local': 'Distributed (local Main)',
                  'distributed_remote':  'Distributed (remote Main)'}

def build(submitter):
    """
    Build the controls.
    """
    enabled_copy_cat_modes = (COPY_CAT_MODES['single_instance'], COPY_CAT_MODES['distributed_remote'])
    knob = nuke.Enumeration_Knob("cio_copycat_mode", "CopyCat Mode", enabled_copy_cat_modes)
    knob.setTooltip(COPY_CAT_MODE_TOOLTIP)
    submitter.addKnob(knob)
    knob.setValue(0)

    knob = nuke.String_Knob("cio_copycat_main_node_ip", "Main node IP", "0.0.0.0")
    knob.setTooltip("The public IP of the machine")
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.String_Knob("cio_copycat_main_node_port", "Main node port", "30000")
    knob.clearFlag(nuke.STARTLINE)
    submitter.addKnob(knob)
    knob.setVisible(False)

    knob = nuke.Int_Knob("cio_copycat_worker_size", "Worker size")
    knob.setValue(2)
    submitter.addKnob(knob)
    knob.setVisible(False)

def update_ui(node, copy_cat_mode):
    """
    Update the UI to reflect the different knobs needs for each copy cat mode
    """

    if copy_cat_mode == COPY_CAT_MODES["distributed_local"]:
        node.knob("cio_copycat_main_node_ip").setVisible(True)
        node.knob("cio_copycat_main_node_port").setVisible(True)

    else:
        node.knob("cio_copycat_main_node_ip").setVisible(False)
        node.knob("cio_copycat_main_node_port").setVisible(False)

    if copy_cat_mode != COPY_CAT_MODES['single_instance']:
        node.knob("cio_copycat_worker_size").setVisible(True)

    else:
        node.knob("cio_copycat_worker_size").setVisible(False)
        node.knob("cio_copycat_worker_size").setValue(1)

def knobChanged(node, knob):
    """
    Adjust the enabled/visible state of widgets in this component.
    """
    
    if knob.name() == "cio_copycat_mode":
        
        copy_cat_mode = knob.value()
        
        update_ui(node, copy_cat_mode)

        if copy_cat_mode == COPY_CAT_MODES["single_instance"]:
            task_cmd = 'nuke -V 2 --gpu --multigpu --remap "[value cio_pathmap]" -F 1 -X [python {",".join([n.name() for n in nuke.thisNode().dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)])}] "[regsub -nocase {^[A-Z]:} [value root.name] []]"'

        elif copy_cat_mode == COPY_CAT_MODES['distributed_local']:
            task_cmd = ""

        elif copy_cat_mode == COPY_CAT_MODES['distributed_remote']:
            
            if NODE_SYNC_SCRIPT_PATH.drive and NODE_SYNC_SCRIPT_PATH.drive[1] == ":":
                posix_node_sync_script_path = pathlib.Path(*(("/",) + NODE_SYNC_SCRIPT_PATH.parts[1:])).as_posix()

            else:
                posix_node_sync_script_path.as_posix()

            task_cmd = 'python3 {} [python {{",".join([n.name() for n in nuke.thisNode().dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)])}}] "[regsub -nocase {{^[A-Z]:}} [value root.name] []]"'.format(posix_node_sync_script_path)

        else:
            raise Exception("Unrecognized CopyCat mode chosen from menu: '{}'. Unable to update the submitter.".format(copy_cat_mode))
        
        node.knob("cio_task").setValue(task_cmd)


def resolve(submitter, **kwargs):
    """
    Resolve the part of the payload that is handled by this component.
    """

    result = {}

    if submitter.knob("cio_copycat_mode").value() == COPY_CAT_MODES['distributed_remote']:
        world_size = submitter.knob("cio_copycat_worker_size").value()
        result = {'upload_paths': [NODE_SYNC_SCRIPT_PATH.as_posix()],
                  'environment': {'CONDUCTOR_OUTPUT_PATH': advanced.resolve(submitter, **kwargs)['output_path'][2:],
                                  'COPYCAT_MAIN_PORT': "60000",
                                  'COPYCAT_WORLD_SIZE': world_size}
                  }

    return result

def affector_knobs():
    """
    Register knobs in this component that affect the payload.
    """
    return [
        "cio_copycat_main_node_ip",
        "cio_copycat_main_node_port",
        "cio_copycat_mode"
    ]
