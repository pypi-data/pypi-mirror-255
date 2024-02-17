###############################################################
####### INITIALIZE THE BEC CLIENT - DO NOT MODIFY #############
###############################################################
import os
import sys

from bec_lib import RedisConnector, ServiceConfig, bec_logger

from bec_client import BECIPythonClient

# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=unused-import
# pylint: disable=ungrouped-imports


logger = bec_logger.logger

if __name__ == "__main__":
    try:
        from bec_plugins.bec_client import startup
    except ImportError:
        startup = None

    args = sys.argv[1:]

    if "--config" in args:
        config_file = args[args.index("--config") + 1]
        if not os.path.isfile(config_file):
            raise FileNotFoundError("Config file not found.")
        print("Using config file: ", config_file)
        config = ServiceConfig(config_file)
        args.remove("--config")
        args.remove(config_file)

    if startup and not "config" in locals():
        # check if pre-startup.py script exists
        file_name = os.path.join(os.path.dirname(startup.__file__), "pre_startup.py")
        if os.path.isfile(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                # exec the pre-startup.py script and pass the arguments
                # pylint: disable=exec-used
                exec(file.read(), globals(), locals())

    # check if config was defined in pre-startup.py
    if not "config" in locals():
        config = ServiceConfig()

    bec = BECIPythonClient()
    bec.initialize(config, RedisConnector)
    bec.load_high_level_interface("spec_hli")
    bec.start()

    dev = bec.device_manager.devices
    scans = bec.scans

    ####################### END OF INIT #############################
    #################################################################

    # MODIFY THE SECTIONS BELOW TO CUSTOMIZE THE BEC

    ################################################################
    ################################################################
    import numpy as np  # not needed but always nice to have

    bec._ip.prompts.status = 1

    # SETUP BEAMLINE INFO
    # from bec_client.plugins.cSAXS.beamline_info import BeamlineInfo
    from bec_client.plugins.SLS.sls_info import OperatorInfo, SLSInfo

    # bec._beamline_mixin._bl_info_register(BeamlineInfo)
    bec._beamline_mixin._bl_info_register(SLSInfo)
    bec._beamline_mixin._bl_info_register(OperatorInfo)

    if startup:
        # check if post-startup.py script exists
        file_name = os.path.join(os.path.dirname(startup.__file__), "post_startup.py")
        if os.path.isfile(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                # pylint: disable=exec-used
                exec(file.read())
