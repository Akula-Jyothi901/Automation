import sys
import os
import time
import configparser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cfrfuelbdd.fuel_logging import logger
from enums.pump import MP_Lock


def before_all(context):
    logger.info("=== Test Execution started: ")
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "config.ini")
    config.read(config_path)

    context.config_data = config['DEFAULT']
    context.fuel_proxy_addr = context.config_data['fuel_PROXY_ADDRESS']
    context.fuel_proxy_port = context.config_data['fuel_PROXY_PORT']
    context.fcc_exe_path = context.config_data['fcc_exe_path']
    context.radio_service_name = context.config_data['radio_service_name']
    context.simpumps_exe_path = context.config_data['simpumps_exe_path']
    context.simpumps_msi_path = context.config_data['simpumps_msi_path']
    context.simpumps_dir = context.config_data['simpumps_dir'] ## INSTALLDIR
    context.radiant_dir = context.config_data['radiant_dir']
    context.temp = context.config_data['temp']
    context.fcc_system =context.config_data['fcc_system']
    context.temp_simpumps_folder = context.config_data['temp_simpumps_folder']
    context.simpumps_folder = context.config_data['simpumps_folder']
    context.radio_service_name = context.config_data['radio_service_name']
    context.load_config_filename = context.config_data['load_config_filename']

    context.dump_tool = context.config_data['dump_tool']
    context.dump_logfile_path = context.config_data['dump_logfile_path']
    context.radiant_dir = context.config_data['radiant_dir']
    context.pumpsrv_log = context.config_data['pump_srv_log']
    context.pumpsrv_ini = context.config_data['pump_srv_ini']
    context.disp_status_locked = context.config_data['disp_status_locked']
    context.dispenser_ready_msg = context.config_data['dispenser_ready_msg']
    

# Called before each feature
def before_feature(context, feature):
    logger.info(f"===> Starting feature: {feature.name}")
    # allure.dynamic.feature(feature.name)

# Called before each scenario
def before_scenario(context, scenario):
    logger.info(f"===> Starting scenario: {scenario.name}")
    context.execute_steps("""
        Given the test environment for retalix product
        And the application connects to socket
    """)
    # allure.dynamic.story(scenario.name)

# Called before each step
def before_step(context, step):
    logger.info(f"--> Step: {step.name}")

# Called after each step
def after_step(context, step):
    if step.status == "failed":
        logger.error(f"--> Step failed: {step.name}")

# Called after each scenario
def after_scenario(context, scenario):
    """
    Behave hook: Called after each scenario.
    Unlocks the pump if it was locked during the scenario.
    """
    time.sleep(5)
    logger.info(f"<=== Finished scenario: {scenario.name}")
    
    # Only unlock if this scenario locked the pump
    if hasattr(context, "pump") and "cashier can lock the pump" in scenario.name.lower():
        try:
            logger.debug(f"Auto-unlocking pump {context.pump} after scenario.")
            context.execute_steps(f'When Cashier attempts to unlock pump "{context.pump}"')
            logger.debug(f"Pump {context.pump} unlocked in after_scenario.")
        except Exception as e:
            logger.debug(f"Error unlocking pump in after_scenario: {e}")
            context.error = str(e)

# Called after each feature
def after_feature(context, feature):
    logger.info(f"<=== Finished feature: {feature.name}")

# Called once after all tests
def after_all(context):
    logger.info("===> Test execution finished")
    #Generate allure reports -- index.html file will be created.
    os.system('allure generate --single-file --clean')
