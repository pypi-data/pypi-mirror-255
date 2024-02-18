'''
This script synchronizes instances within a single CopyCat job to allow for distributed workloads.

CopyCat (i.e.: PyTorch) requires one worker to be the primary worker. All other workers connect
to the primary worker. The primary worker is responsible for writing out all the files.

We take advantage that on CoreWeave, all the tasks within a job use shared storage for the output
path.

The first task to start running creates a .lock file in the output path that contains its IP.

As other tasks spin-up, if they see the .lock file, they read the IP and then use it to connect to the
primary worker.
'''

import logging
import os
import os.path
import pathlib
import stat
import subprocess
import sys

print("Running worker sync script...")

ROOT_PATH = pathlib.Path(__file__)
LOCK_FILE = pathlib.Path(ROOT_PATH.parent, ".lock")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

primary_node_ip = None

def get_ip_address():
    ip_address = os.environ['AGENT_POD_IP']
    logger.info("Found IP of instance: {}".format(ip_address))
    return ip_address

if LOCK_FILE.exists():
    
    logger.info("Lock file ({}) exists. Reading IP address of primary render node".format(LOCK_FILE))
    
    with open(LOCK_FILE, 'r') as fh:
        data = fh.readlines()
        logger.debug("Contents of lock file:\n{}".format(data))
    
    primary_node_ip = data[0].strip()
    logger.info("Using %s as IP address of primary render instance", primary_node_ip)
    
    # Loop through the lock files to figure out the worker rank
    lock_file_suffix = 1
    while True:
        try:
            worker_lock_file = LOCK_FILE.with_suffix(f'.{lock_file_suffix}')
            worker_lock_file.touch(exist_ok=False)
            logger.info("Touched (%s). Setting rank to %s.", worker_lock_file, lock_file_suffix)
            copycat_rank = lock_file_suffix
            break
        except FileExistsError:
            lock_file_suffix += 1
            continue

else:
    logger.info("Lock file (%s) doesn't exist. Writing IP into lock file.", LOCK_FILE)
    
    primary_node_ip = get_ip_address()
    
    with open(LOCK_FILE, 'a') as fh:
        fh.write("{}".format(get_ip_address()))

    copycat_rank = "0"

os.environ['COPYCAT_RANK'] = str(copycat_rank)
os.environ['COPYCAT_MAIN_ADDR'] = primary_node_ip

cmd_script = ["nuke", "-F", "1", "-X", sys.argv[1], "--multigpu", "--gpu", sys.argv[2]]

logger.info("Starting Nuke: %s", " ".join(cmd_script))
p = subprocess.run(cmd_script, check=False, shell=False)
logger.info("Process completed. Return code: %s", p.returncode)
