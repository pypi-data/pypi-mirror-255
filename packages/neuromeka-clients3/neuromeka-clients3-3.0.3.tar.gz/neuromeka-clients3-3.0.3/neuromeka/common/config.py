import os
from .utils import get_abs_path, load_json
from .singleton_meta import SingletonMeta

class ConfigLibrary(metaclass=SingletonMeta):
    DEPLOY_JSON_DEFAULT = 'indyDeploy.json'
    CONFIG_JSON_DEFAULT = 'configPath.json'
    CONTROL_TASK_BIN_DEFAULT = 'IndyControlTask'
    PROGRAM_DIR = ''
    ## SET DEFAULT PORTS FOR CLIENTS
    ETHERCAT_SOCKET_PORT = 20000
    CONTROL_SOCKET_PORT = [20001, 30001]
    DEVICE_SOCKET_PORT = [20002, 30002]
    CONFIG_SOCKET_PORT = [20003, 30003]
    RTDE_SOCKET_PORT = [20004, 30004]
    MOBY_SOCKET_PORT = 20200
    CONTY_SOCKET_PORT = [20131, 30131]
    LINEAR_SOCKET_PORT = 30132
    MOBY_V2_PORT = 50051

    SW_UPDATE_FILE_NAME = 'indy_sw.zip'

    # deploy_json_abs = get_abs_path(DEPLOY_JSON_DEFAULT)
    # deploy_config = load_json(deploy_json_abs)
    # deploy_config

    ############################
    #    Exit Code             #
    ############################
    EXIT_NORMAL = 0
    EXIT_REBOOT = 1
    EXIT_UPDATE = 2

    def __init__(self):
        self.VERSION_INFO = '3.1.0'
        self.VERSION_DETAIL = ''
        self.VERSION_DATE = "2024.01.04"

    ##
    # @return list of names of tasks of which binary file is task_bin
    def get_robot_tasks(self, deploy_json=DEPLOY_JSON_DEFAULT, task_bin=CONTROL_TASK_BIN_DEFAULT):
        deploy_json_abs = get_abs_path(deploy_json)
        deploy_config = load_json(deploy_json_abs)
        task_names = []
        for task_name, task_config in deploy_config["RTTasks"].items():
            if task_name == task_bin:
                task_names.append(task_name)
        return task_names

    ##
    # @return relative path for config json file
    def get_task_config(self, deploy_json=DEPLOY_JSON_DEFAULT, task_name=CONTROL_TASK_BIN_DEFAULT):
        deploy_json_abs = get_abs_path(deploy_json)
        deploy_config = load_json(deploy_json_abs)
        return deploy_config["RTTasks"][task_name]["ConfigFile"]

    def load_config(self, deploy_json=DEPLOY_JSON_DEFAULT, config_json=CONFIG_JSON_DEFAULT):
        deploy_json_abs = get_abs_path(deploy_json)
        deploy_config = load_json(deploy_json_abs)
        self.task_order = deploy_config["RTTasks"]["IndyControlTask"]["Order"]

        config_dict = load_json(get_abs_path(config_json))
        robot_configs = load_json(get_abs_path(config_dict["Config"]))
        bot_type = "Cobot"
        robot_config = robot_configs[bot_type][self.task_order]
        mobile_key = "MobileRobot"
        bridge_key = "use_v2_bridge"
        self.USE_V2_BRIDGE = False
        if mobile_key in robot_configs:
            mobile_config = robot_configs[mobile_key]
            if bridge_key in mobile_config:
                self.USE_V2_BRIDGE = mobile_config[bridge_key]

        self.ROBOT_MODEL = f"NRMK-{robot_config['robot_name']}"
        self.ROBOT_DOF = robot_config['DOF']

        # self.CONTROLLER_IP_ADDRESS = '192.168.6.138'
        # self.CONTROLLER_IP_ADDRESS = '192.168.1.8'
        self.CONTROLLER_IP_ADDRESS = '127.0.0.1'

        port_config = load_json(get_abs_path(config_dict["Ports"]))
        self.ETHERCAT_SOCKET_PORT = port_config["EtherCAT"]
        self.CONTROL_SOCKET_PORT = port_config["Control"][self.task_order]
        self.DEVICE_SOCKET_PORT = port_config["Device"][self.task_order]
        self.CONFIG_SOCKET_PORT = port_config["Config"][self.task_order]
        self.RTDE_SOCKET_PORT = port_config["RTDE"][self.task_order]
        if "Moby" in port_config:
            self.MOBY_SOCKET_PORT = port_config["Moby"]
        if "Linear" in port_config:
            self.LINEAR_SOCKET_PORT = port_config["Linear"]
        if "Conty" in port_config:
            self.CONTY_SOCKET_PORT = port_config["Conty"][self.task_order]

        ############################
        #    Configuration Files   #
        ############################
        self.CONTROL_GAIN_DIR = get_abs_path(config_dict["ControlGain"])
        self.COLLISION_DEFAULT_DIR = get_abs_path(config_dict["DefaultCollisionGain"])
        self.COLLISION_CUSTOM_DIR = get_abs_path(config_dict["CollisionGain"])
        self.FRICTION_PARAMETER_DIR = get_abs_path(config_dict["FrictionParameter"])

        self.SYSTEM_INFO_DIR = get_abs_path(config_dict["SerialNumber"])

        self.FRICTION_CONFIG_DIR = get_abs_path(config_dict["FrictionConfig"])
        self.SAFETY_CONFIG_DIR = get_abs_path(config_dict["SafetyConfig"])
        self.COLLISION_CONFIG_DIR = get_abs_path(config_dict["CollisionConfig"])

        self.HOME_POS_DIR = get_abs_path(config_dict["HomePos"])
        self.CUSTOM_POS_DIR = get_abs_path(config_dict["CustomPos"])
        self.TOOL_DIR = get_abs_path(config_dict["ToolList"])
        self.TOOL_PROPERTY_DIR = get_abs_path(config_dict["ToolProperty"])
        self.MOUNT_ANGLE_DIR = get_abs_path(config_dict["MountingAngle"])
        self.AUTO_SERVO_OFF_DIR = get_abs_path(config_dict["AutoServoOff"])
        self.DI_CONFIG_DIR = get_abs_path(config_dict["DIConfig"])
        self.DO_CONFIG_DIR = get_abs_path(config_dict["DOConfig"])
        self.TOOL_FRAME_DIR = get_abs_path(config_dict["ToolFrameConfig"])
        self.REF_FRAME_DIR = get_abs_path(config_dict["RefFrameConfig"])
        self.VISION_DIR = get_abs_path(config_dict["VisionConfig"])
        self.ON_START_PROGRAM_CONFIG_DIR = get_abs_path(config_dict["OnStartProgram"])

        ############################
        #    Configuration Paths   #
        ############################
        self.ROBOT_CONFIG_PATH = os.path.dirname(self.HOME_POS_DIR)+"/"

        self.PROGRAM_DIR = get_abs_path('ProgramScripts')
        self.INDEX_PROGRAM_DIR = self.PROGRAM_DIR + '/index'

        self.LOG_PATH = get_abs_path("LogData/")
        self.SERVER_LOG_PATH = self.LOG_PATH + "Server/"
        self.FRICTION_LOG_PATH = self.LOG_PATH + "Friction/"

        ######################
        #    Derived Paths   #
        ######################
        self.MODBUS_DIR = self.ROBOT_CONFIG_PATH + "Modbus.json"
        self.PALLET_MAKER_DIR = self.ROBOT_CONFIG_PATH + "Pallet.json"

        self.FRICTION_LOG_DIR = self.FRICTION_LOG_PATH + "FrictionData.csv"

        self.WELDING_MACHINE_DIR = self.ROBOT_CONFIG_PATH + "WeldingMachineConfig.json"
        self.WELDING_LINES_DIR = self.ROBOT_CONFIG_PATH + "WeldingLinesInfo.json"
        self.DETECTED_WELDING_LINES_DIR = self.ROBOT_CONFIG_PATH + "DetectedWeldingLinesInfo.json"
