from .proto.grpc_wrapper import *
from .proto.control_pb2_grpc import ControlStub
from .proto.device_pb2_grpc import DeviceStub
from .proto.config_pb2_grpc import ConfigStub
from .proto.rtde_pb2_grpc import RTDataExchangeStub

from .proto import common_msgs_pb2 as common_msgs
from .proto import control_msgs_pb2 as control_msgs
from .proto import config_msgs_pb2 as config_msgs
from .proto import device_msgs_pb2 as device_msgs
from .proto import rtde_msgs_pb2 as rtde_msgs

from .common import *

from operator import add
import json
import grpc
from google.protobuf import json_format
from google.protobuf.json_format import ParseDict
import math
import time

CONTROL_SOCKET_PORT = [20001, 30001]
DEVICE_SOCKET_PORT = [20002, 30002]
CONFIG_SOCKET_PORT = [20003, 30003]
RTDE_SOCKET_PORT = [20004, 30004]


def grpc_mapping_call(control_stub, func_name, arg_dict=None):
    if arg_dict is None:
        arg_dict = {}
    grpc_request = getattr(control_msgs, "{}Req".format(func_name))()
    ParseDict(arg_dict, grpc_request)
    try:
        grpc_response = getattr(control_stub, func_name)(grpc_request)

    except grpc.RpcError as rpc_error:
        print('Robot gRPC: ' + func_name + ': Connection unavailable')
        grpc_response = None

    except Exception as ex:
        print(func_name + 'Robot gRPC Exception: ' + str(ex))
        grpc_response = None

    return grpc_response

class IndyDCP3:
    ABSOLUTE_JOINT = control_msgs.ABSOLUTE_JOINT
    RELATIVE_JOINT = control_msgs.RELATIVE_JOINT
    ABSOLUTE_TASK = control_msgs.ABSOLUTE_TASK
    RELATIVE_TASK = control_msgs.RELATIVE_TASK
    TCP_TASK = control_msgs.TCP_TASK
    CIRCLE_POINT_SET = control_msgs.POINT_SET
    CIRCLE_CENTER_AXIS = control_msgs.CENTER_AXIS
    CIRCLE_CONSTANT = control_msgs.CONSTANT
    CIRCLE_RADIAL = control_msgs.RADIAL
    CIRCLE_SMOOTH = control_msgs.SMOOTH
    STOP_IMMEDIATE_BRAKE = 0
    STOP_SMOOTH_BRAKE = 1
    STOP_SMOOTH_ONLY = 2
    NO_BLENDING = 0
    OVERRIDE_BLENDING = 1
    DUPLICATE_BLENDING = 2

    COLLISION_NO_DETECT = common_msgs.COLL_NO_DETECT
    COLLISION_PAUSE = common_msgs.COLL_PAUSE
    COLLISION_RESUME_AFTER_SLEEP = common_msgs.COLL_RESUME_AFTER_SLEEP
    COLLISION_STOP = common_msgs.COLL_STOP
    STOPCAT_IMMEDIATE_BRAKE = common_msgs.IMMEDIATE_BRAKE
    STOPCAT_SMOOTH_BRAKE = common_msgs.SMOOTH_BRAKE
    STOPCAT_SMOOTH_ONLY = common_msgs.SMOOTH_ONLY

    def __init__(self, robot_ip='127.0.0.1', index=0):
        self.control_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, CONTROL_SOCKET_PORT[index]))
        self.device_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, DEVICE_SOCKET_PORT[index]))
        self.config_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, CONFIG_SOCKET_PORT[index]))
        self.rtde_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, RTDE_SOCKET_PORT[index]))

        self.control = ControlStub(self.control_channel)
        self.device = DeviceStub(self.device_channel)
        self.config = ConfigStub(self.config_channel)
        self.rtde = RTDataExchangeStub(self.rtde_channel)



    def __del__(self):
        if self.control_channel is not None:
            self.control_channel.close()
        if self.device_channel is not None:
            self.device_channel.close()
        if self.config_channel is not None:
            self.config_channel.close()
        if self.rede_channel is not None:
            self.rede_channel.close()

    def __to_digital_request_list__(self, digital_signal_list) -> list:
        request_list = []
        if digital_signal_list is not None:
            for signal in digital_signal_list:
                request_list.append(device_msgs.DigitalSignal(address=signal['address'], state=signal['state']))
        return request_list

    def __to_analog_request_list__(self, analog_signal_list) -> list:
        request_list = []
        if analog_signal_list is not None:
            for signal in analog_signal_list:
                request_list.append(device_msgs.AnalogSignal(address=signal['address'], voltage=signal['voltage']))
        return request_list

    ############################
    # RTDE
    ############################
    def get_motion_data(self):
        """
        Motion Data:
            traj_state   -> TrajState
            traj_progress   -> int32
            is_in_motion  -> bool
            is_target_reached  -> bool
            is_pausing  -> bool
            is_stopping  -> bool
            has_motion  -> bool
            speed_ratio  -> int32
            motion_id  -> int32
            remain_distance  -> float
            motion_queue_size  -> uint32
            cur_traj_progress  -> int32
            response  -> Response
        """
        response = self.rtde.GetMotionData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_control_data(self):
        """
        Control Data:
            running_hours   -> uint32
            running_mins   -> uint32
            running_secs  -> uint32
            op_state  -> OpState
            sim_mode  -> bool
            q  -> float[6]
            qdot  -> float[6]
            p  -> float[6]
            pdot  -> float[6]
            ref_frame  -> float[6]
            tool_frame  -> float[6]
            response  -> Response
        """
        response = self.rtde.GetControlData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_io_data(self):
        """
        IO Data:
            di   -> DigitalSignal[]
            do   -> DigitalSignal[]
            ai  -> AnalogSignal[]
            ao  -> AnalogSignal[]
            end_di  -> EndtoolSignal[]
            end_do  -> EndtoolSignal[]
            end_ai  -> AnalogSignal[]
            end_ao  -> AnalogSignal[]
            response  -> Response
        """
        response = self.rtde.GetIOData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_servo_data(self):
        """
        Servo Data:
            status_codes   -> string[]
            temperatures   -> float[]
            voltages  -> float[]
            currents  -> float[]
            servo_actives  -> bool[]
            brake_actives  -> bool[]
            response  -> Response
        """
        response = self.rtde.GetServoData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_violation_data(self):
        """
        Violation Data:
            violation_code   -> uint64
            j_index   -> uint32
            i_args  -> int32[]
            f_args  -> float[]
            violation_str  -> string
            response  -> Response
        """
        response = self.rtde.GetViolationData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_program_data(self):
        """
        Program Data:
            program_state   -> ProgramState
            cmd_id   -> int32
            sub_cmd_id  -> int32
            running_hours  -> int32
            running_mins  -> int32
            running_secs  -> int32
            program_name  -> string
            program_alarm  -> string
            program_annotation  -> string
            response  -> Response
        """
        response = self.rtde.GetProgramData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Device
    ############################
    def get_di(self) -> list:
        """
        address = uint32
        state = DigitalState
        """
        response = self.device.GetDI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_do(self) -> list:
        """
        signals = index
        address = uint32
        state = DigitalState
        """
        response = self.device.GetDO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_do(self, do_signal_list: list):
        """
        do_list = [(int_addr1, True/False), (int_addr1, True/False), ...]
        """
        response = self.device.SetDO(device_msgs.DigitalList(
            signals=do_signal_list,
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ai(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetAI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ao(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetAO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ao(self, ao_signal_list: list):
        response = self.device.SetAO(device_msgs.AnalogList(
            signals=ao_signal_list,
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_di(self) -> list:
        """
        state = EndtoolState
        port = char value [A,B,C]
        """
        response = self.device.GetEndDI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_do(self) -> list:
        """
        state = EndtoolState
        port = char value [A,B,C]
        """
        response = self.device.GetEndDO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_do(self, end_do_signal_list: list):
        response = self.device.SetEndDO(device_msgs.EndtoolSignalList(
            signals=end_do_signal_list,
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_ai(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetEndAI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_ao(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetEndAO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_ao(self, end_ao_signal_list: list):
        response = self.device.SetEndAO(device_msgs.AnalogList(
            signals=end_ao_signal_list,
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_device_info(self):
        """
        Device Info:
            num_joints   -> uint32
            robot_serial   -> string
            io_board_fw_ver  -> string
            core_board_fw_vers  -> string[6]
            endtool_board_fw_ver  -> string
            endtool_port_type  -> EndToolPortType
            response  -> {code: int64, msg: string}
        """
        response = self.device.GetDeviceInfo(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ft_sensor_data(self):
        """
        Device Info:
            num_joints   -> uint32
            robot_serial   -> string
            io_board_fw_ver  -> string
            core_board_fw_vers  -> string[6]
            endtool_board_fw_ver  -> string
            endtool_port_type  -> EndToolPortType
            response  -> {code: int64, msg: string}
        """
        response = self.device.GetFTSensorData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)



    ############################
    # Motion Control (Move)
    ############################
    def stop_motion(self, stop_category=STOP_IMMEDIATE_BRAKE) -> dict:
        """
         stop motion element:
            IMMEDIATE_BRAKE = 0
            SMOOTH_BRAKE = 1
            SMOOTH_ONLY = 2
        """
        response = self.control.StopMotion(common_msgs.StopCat(category=stop_category))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movej(self, jtarget,
              blending_type=NO_BLENDING,
              base_type=ABSOLUTE_JOINT,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=Property.PostCondition(),
              teaching_mode=False) -> dict:
        jtarget = control_msgs.TargetJ(j_start=[], j_target=list(jtarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveJ(control_msgs.MoveJReq(
            target=jtarget,
            blending=blending,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movej_time(self, jtarget,
                   blending_type=NO_BLENDING,
                   base_type=ABSOLUTE_JOINT,
                   blending_radius=0.0,
                   move_time=2.0,
                   post_condition=Property.PostCondition()) -> dict:
        """
        jtarget = [deg, deg, deg, deg, deg, deg]
        move_time = seconds
        """
        jtarget = control_msgs.TargetJ(j_start=[], j_target=list(jtarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveJT(control_msgs.MoveJTReq(
            target=jtarget,
            blending=blending,
            time=move_time,
            post_condition=post_cond
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movel(self, ttarget,
              blending_type=NO_BLENDING,
              base_type=ABSOLUTE_TASK,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=Property.PostCondition(),
              teaching_mode=False) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]
         Recover from violation
        """
        ptarget = control_msgs.TargetP(t_start=[], t_target=list(ttarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveL(control_msgs.MoveLReq(
            target=ptarget,
            blending=blending,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movec(self, tpos0, tpos1,
              blending_type=NO_BLENDING,
              base_type=ABSOLUTE_TASK,
              angle=90.0,
              setting_type=CIRCLE_POINT_SET,
              move_type=control_msgs.CONSTANT,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=Property.PostCondition(),
              teaching_mode=False) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]
         Recover from violation
        """
        ctarget = control_msgs.TargetC(t_start=[], t_pos0=list(tpos0), t_pos1=list(tpos1),
                                       base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveC(control_msgs.MoveCReq(
            target=ctarget,
            blending=blending,
            angle=angle,
            setting_type=setting_type,
            move_type=move_type,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)


    ############################
    # Motion Control (Teleoperation)
    ############################
    def start_teleop(self, method, mode=control_msgs.TeleMode.TELE_RAW):
        """
        Start tele op
        """
        response = self.control.StartTeleOp(control_msgs.TeleOpState(mode=mode,method=method))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def stop_teleop(self):
        """
        Stop tele op
        """
        response = self.control.StopTeleOp(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelej(self, jpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        MoveteleJ
        jpos = [deg, deg, deg, deg, deg, deg]
        """
        response = self.control.MoveTeleJ(control_msgs.MoveTeleJReq(jpos=jpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelel(self, tpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        MoveteleL
        jpos = [mm, mm, mm, deg, deg, deg]
        """
        response = self.control.MoveTeleL(control_msgs.MoveTeleLReq(tpos=tpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Control - Additional
    ############################
    def inverse_kin(self, tpos, init_jpos) -> dict:
        """
        :param tpos:
        :param init_jpos:
        :return:
            'jpos': []
        """
        response = self.control.InverseKinematics(control_msgs.InverseKinematicsReq(
            tpos=list(tpos),
            init_jpos=list(init_jpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_direct_teaching(self, enable=True) -> dict:
        """
         enable = True | False
        """
        response = self.control.SetDirectTeaching(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_simulation_mode(self, enable=True) -> dict:
        """
         Set simulation mode = True | False
        """
        response = self.control.SetSimulationMode(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def recover(self) -> dict:
        """
         Recover from violation
        """
        response = self.control.Recover(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_manual_recovery(self, enable=True) -> dict:
        """
         Set manual recovery = True | False
        """
        response = self.control.SetManualRecovery(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Program control
    ############################
    def play_program(self, prog_name: str = '', prog_idx: int = -1):
        """
         Play program
        """
        response = self.control.PlayProgram(control_msgs.Program(
            prog_name=prog_name,
            prog_idx=prog_idx
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def pause_program(self):
        """
         Pause program
        """
        response = self.control.PauseProgram(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def stop_program(self):
        """
         Stop program
        """
        response = self.control.StopProgram(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def play_tuning_program(self, prog_name: str = '', prog_idx: int = -1,
                            tuning_space=common_msgs.TUNE_ALL, precision=common_msgs.HIGH_PRECISION,
                            vel_level_max=9):
        """
        Play tuning program
        """
        tuning_prog_dict = dict(
            program=dict(
                prog_name=prog_name,
                prog_idx=prog_idx),
            tuning_space=tuning_space,
            precision=precision,
            vel_level_max=vel_level_max
        )
        tuning_req = control_msgs.TuningProgram()

        # json_format.ParseDict(tuning_prog_dict, tuning_req)
        ParseDict(tuning_prog_dict, tuning_req)
        response = self.control.PlayTuningProgram(tuning_req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Variables
    ############################
    def get_bool_variable(self):
        """
        Bool Variables:
            [
                addr -> int32
                value -> bool
            ]
        """
        response = self.control.GetBoolVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_int_variable(self):
        """
        Integer Variables:
            [
                addr -> int32
                value -> int32
            ]
        """
        response = self.control.GetIntVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_float_variable(self):
        """
        Float Variables:
            [
                addr -> int32
                value -> float
            ]
        """
        response = self.control.GetFloatVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_jpos_variable(self):
        """
        JPos Variables:
            [
                addr -> int32
                jpos -> float[]
            ]
        """
        response = self.control.GetJPosVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)['variables']

    def get_tpos_variable(self):
        """
        TPos Variables:
            [
                addr -> int32
                tpos -> float[]
            ]
        """
        response = self.control.GetTPosVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_bool_variable(self, bool_variables: list):
        """
        Bool Variables:
            [
                addr -> int32
                value -> bool
            ]
        """
        variable_list = []
        for bool_var in bool_variables:
            variable_list.append(control_msgs.BoolVariable(addr=bool_var['addr'], value=bool_var['value']))

        response = self.control.SetBoolVariable(
            control_msgs.BoolVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_int_variable(self, int_variables: list):
        """
        Integer Variables:
            [
                addr -> int32
                value -> int64
            ]
        """
        variable_list = []
        for int_var in int_variables:
            variable_list.append(control_msgs.IntVariable(addr=int_var['addr'], value=int_var['value']))

        response = self.control.SetIntVariable(
            control_msgs.IntVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_float_variable(self, float_variables: list):
        """
        Float Variables:
            [
                addr -> int32
                value -> float
            ]
        """
        variable_list = []
        for float_var in float_variables:
            variable_list.append(control_msgs.FloatVariable(addr=float_var['addr'], value=float_var['value']))

        response = self.control.SetFloatVariable(
            control_msgs.FloatVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_jpos_variable(self, jpos_variables: list):
        """
        JPos Variables:
            [
                addr -> int32
                jpos -> float[]
            ]
        """
        variable_list = []
        for jpos in jpos_variables:
            variable_list.append(control_msgs.JPosVariable(addr=jpos['addr'], jpos=jpos['jpos']))

        response = self.control.SetJPosVariable(
            control_msgs.JPosVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tpos_variable(self, tpos_variables: list):
        """
        TPos Variables:
            [
                addr -> int32
                tpos -> float[]
            ]
        """
        variable_list = []
        for tpos in tpos_variables:
            variable_list.append(control_msgs.TPosVariable(addr=tpos['addr'], tpos=tpos['tpos']))

        response = self.control.SetTPosVariable(
            control_msgs.TPosVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)


    ############################
    # Config
    ############################
    def set_ref_frame(self, fpos: list):
        """
        Ref Frame
            fpos -> float[6]
        """
        response = self.config.SetRefFrame(config_msgs.Frame(
            fpos=list(fpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ref_frame_planar(self, fpos0: list, fpos1: list, fpos2: list):
        """
        Ref Frame
            fpos -> float[6]
        """
        response = self.config.SetRefFramePlanar(config_msgs.PlanarFrame(
            fpos0=list(fpos0), fpos1=list(fpos1), fpos2=list(fpos2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_frame(self, fpos: list):
        """
        Tool Frame
            fpos -> float[6]
        """
        response = self.config.SetToolFrame(config_msgs.Frame(
            fpos=list(fpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_speed_ratio(self, speed_ratio: int):
        """
        Speed Ratio
            ratio -> uint32 {0 ~ 100}
        """
        response = self.config.SetSpeedRatio(config_msgs.Ratio(
            ratio=speed_ratio
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_home_pos(self, home_jpos: list):
        """
        Joint Home Position
            jpos -> double[]
        """
        response = self.config.SetHomePosition(config_msgs.JointPos(
            jpos=home_jpos
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_home_pos(self):
        """
        Joint Home Position
            jpos -> double[]
        """
        response = self.config.GetHomePosition(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_di_config_list(self, di_config_list: dict):
        """
        DI Configuration List
            {
                'di_configs': [
                    {
                        'function_code': 2,
                        'function_name': "name",
                        'triggerSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                        'successSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                        'failureSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        di_list_request = config_msgs.DIConfigList()
        # json_format.ParseDict(di_config_list, di_list_request)
        ParseDict(di_config_list, di_list_request)
        response = self.config.SetDIConfigList(di_list_request)

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_di_config_list(self):
        """
        DI Configuration List
            {
                'di_configs': [
                    {
                        'function_code': 2,
                        'function_name': "name",
                        'triggerSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'successSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'failureSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        response = self.config.GetDIConfigList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_do_config_list(self, do_config_list: dict):
        """
        DO Configuration List
            {
                'do_configs': [
                    {
                        'state_code': 2,
                        'state_name': "name",
                        'onSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'offSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        do_list_request = config_msgs.DOConfigList()
        json_format.ParseDict(do_config_list, do_list_request)

        response = self.config.SetDOConfigList(do_list_request)

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_do_config_list(self):
        """
        DO Configuration List
            {
                'do_configs': [
                    {
                        'state_code': 2,
                        'state_name': "name",
                        'onSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'offSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        response = self.config.GetDOConfigList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_auto_servo_Off(self, enable: bool, time: float):
        """
        Auto Servo-Off Config
            enable -> bool
            time -> float
        """
        response = self.config.SetAutoServoOff(config_msgs.AutoServoOffConfig(
            enable=enable, time=time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_auto_servo_off(self):
        """
        Auto Servo-Off Config
            enable -> bool
            time -> float
        """
        response = self.config.GetAutoServoOff(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_joint_control_gain(self, kp: list, kv: list, kl2: list):
        """
        Joint Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetJointControlGain(config_msgs.JointGainSet(
            kp=list(kp), kv=list(kv), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_joint_control_gain(self):
        """
        Joint Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetJointControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_task_control_gain(self, kp, kv, kl2):
        """
        Task Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetTaskControlGain(config_msgs.TaskGainSet(
            kp=list(kp), kv=list(kv), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_task_control_gain(self):
        """
        Task Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetTaskControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_impedance_control_gain(self, mass, damping, stiffness, kl2):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetImpedanceControlGain(config_msgs.ImpedanceGainSet(
            mass=list(mass), damping=list(damping), stiffness=list(stiffness), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_impedance_control_gain(self):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetImpedanceControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_friction_comp(self, control_comp: bool, control_comp_levels: list,
                          dt_comp: bool, dt_comp_levels: list):
        """
        Friction Compensation Set:
            joint_idx   -> uint32
            control_comp_enable   -> bool
            control_comp_levels   -> int32[6]
            teaching_comp_enable   -> bool
            teaching_comp_levels   -> int32[6]
        """
        response = self.config.SetFrictionComp(config_msgs.FrictionCompSet(
            control_comp_enable=control_comp, control_comp_levels=list(control_comp_levels),
            teaching_comp_enable=dt_comp, teaching_comp_levels=list(dt_comp_levels)
        ))

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_friction_comp(self):
        """
        Friction Compensation Set:
            joint_idx   -> uint32
            control_comp_enable   -> bool
            control_comp_levels   -> int32[6]
            teaching_comp_enable   -> bool
            teaching_comp_levels   -> int32[6]
        """
        response = self.config.GetFrictionComp(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_mount_pos(self, rot_y=0.0, rot_z=0.0):
        """
        Mounting Angles:
            rot_y   -> float
            rot_z   -> float
        """
        response = self.config.SetMountPos(config_msgs.MountingAngles(
            ry=rot_y, rz=rot_z
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_mount_pos(self):
        """
        Mounting Angles:
            rot_y   -> float
            rot_z   -> float
        """
        response = self.config.GetMountPos(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_property(self, mass: float, center_of_mass: list, inertia: list):
        """
        Tool Properties:
            mass   -> float
            center_of_mass   -> float[3]
            inertia   -> float[6]
        """
        response = self.config.SetToolProperty(config_msgs.ToolProperties(
            mass=mass, center_of_mass=list(center_of_mass), inertia=list(inertia)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tool_property(self):
        """
        Tool Properties:
            mass   -> float
            center_of_mass   -> float[3]
            inertia   -> float[6]
        """
        response = self.config.GetToolProperty(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_sens_level(self, level: int):
        """
        Collision Sensitivity Level:
            level -> uint32
        """
        response = self.config.SetCollSensLevel(config_msgs.CollisionSensLevel(
            level=level
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_sens_level(self):
        """
        Collision Sensitivity Level:
            level -> uint32
        """
        response = self.config.GetCollSensLevel(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_sens_param(self, j_torque_bases, j_torque_tangents,
                            t_torque_bases, t_torque_tangents,
                            t_constvel_torque_bases, t_constvel_torque_tangents,
                            t_conveyor_torque_bases, t_conveyor_torque_tangents,
                            error_bases, error_tangents):
        """
        Collision Params:
            j_torque_bases                  -> double[6]
            j_torque_tangents               -> double[6]
            t_torque_bases                  -> double[6]
            t_torque_tangents               -> double[6]
            error_bases                     -> double[6]
            error_tangents                  -> double[6]
            t_constvel_torque_bases         -> double[6]
            t_constvel_torque_tangents      -> double[6]
            t_conveyor_torque_bases         -> double[6]
            t_conveyor_torque_tangents      -> double[6]
        """
        response = self.config.SetCollSensParam(config_msgs.CollisionThresholds(
            j_torque_bases=list(j_torque_bases), j_torque_tangents=list(j_torque_tangents),
            t_torque_bases=list(t_torque_bases), t_torque_tangents=list(t_torque_tangents),
            error_bases=list(error_bases), error_tangents=list(error_tangents),
            t_constvel_torque_bases=list(t_constvel_torque_bases),
            t_constvel_torque_tangents=list(t_constvel_torque_tangents),
            t_conveyor_torque_bases=list(t_conveyor_torque_bases),
            t_conveyor_torque_tangents=list(t_conveyor_torque_tangents)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_sens_param(self):
        """
        Collision Params:
            j_torque_bases                  -> double[6]
            j_torque_tangents               -> double[6]
            t_torque_bases                  -> double[6]
            t_torque_tangents               -> double[6]
            error_bases                     -> double[6]
            error_tangents                  -> double[6]
            t_constvel_torque_bases         -> double[6]
            t_constvel_torque_tangents      -> double[6]
            t_conveyor_torque_bases         -> double[6]
            t_conveyor_torque_tangents      -> double[6]
        """
        response = self.config.GetCollSensParam(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_policy(self, policy=COLLISION_NO_DETECT,
                        sleep_time=0, gravity_time=0.1):
        """
        Collision Policies:
            policy -> uint32
            sleep_time -> float
            gravity_time -> float
        """
        response = self.config.SetCollPolicy(config_msgs.CollisionPolicy(
            policy=policy, sleep_time=sleep_time, gravity_time=gravity_time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_policy(self):
        """
        Collision Policy:
            policy -> uint32
            sleep_time -> float
            gravity_time -> float
        """
        response = self.config.GetCollPolicy(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_safety_limits(self, power_limit: float, power_limit_ratio: float,
                          tcp_force_limit: float, tcp_force_limit_ratio: float,
                          tcp_speed_limit: float, tcp_speed_limit_ratio: float):
        # joint_limits: list):
        """
        Safety Limits:
            power_limit             -> float
            power_limit_ratio       -> float
            tcp_force_limit         -> float
            tcp_force_limit_ratio   -> float
            tcp_speed_limit         -> float
            tcp_speed_limit_ratio   -> float
            # joint_limits   -> float[]
        """
        response = self.config.SetSafetyLimits(config_msgs.SafetyLimits(
            power_limit=power_limit, power_limit_ratio=power_limit_ratio,
            tcp_force_limit=tcp_force_limit, tcp_force_limit_ratio=tcp_force_limit_ratio,
            tcp_speed_limit=tcp_speed_limit, tcp_speed_limit_ratio=tcp_speed_limit_ratio  # ,
            # joint_limits=list(joint_limits)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_limits(self):
        """
        Safety Limits:
            power_limit             -> float
            power_limit_ratio       -> float
            tcp_force_limit         -> float
            tcp_force_limit_ratio   -> float
            tcp_speed_limit         -> float
            tcp_speed_limit_ratio   -> float
            joint_limits   -> float[]
        """
        response = self.config.GetSafetyLimits(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_safety_stop_config(self, jpos_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE,
                               jvel_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE,
                               jtau_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE,
                               tvel_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE,
                               tforce_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE,
                               power_limit_stop_cat=STOPCAT_IMMEDIATE_BRAKE):
        """
        Safety Stop Category:
            jpos_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            jvel_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            jtau_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tvel_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tforce_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            power_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
        """
        response = self.config.SetSafetyStopConfig(config_msgs.SafetyStopConfig(
            joint_position_limit_stop_cat=jpos_limit_stop_cat,
            joint_speed_limit_stop_cat=jvel_limit_stop_cat,
            joint_torque_limit_stop_cat=jtau_limit_stop_cat,
            tcp_speed_limit_stop_cat=tvel_limit_stop_cat,
            tcp_force_limit_stop_cat=tforce_limit_stop_cat,
            power_limit_stop_cat=power_limit_stop_cat
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_stop_config(self):
        """
        Safety Stop Category:
            joint_position_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            joint_speed_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            joint_torque_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tcp_speed_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tcp_force_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            power_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
        """
        response = self.config.GetSafetyStopConfig(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_tuning(self, precision=config_msgs.CollTuningConfig.MIDDLE_TUNE,
                        tuning_space=config_msgs.CollTuningConfig.ALL_TUNE,
                        vel_level_max=3):
        """
        Safety Stop Category:
            precision = LOW(0) | MIDDLE(1) | HIGH(2)
            tuning_space = NONE(0) | JOINT(1) | TASK(2) | ALL(3)
            vel_level_max = 1..5
        """
        response = self.config.SetCollTuning(config_msgs.CollTuningConfig(
            precision=precision,
            tuning_space=tuning_space,
            vel_level_max=vel_level_max
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # NOT Yet Released
    ############################
    def wait_time(self, time: float,
                  set_do_signal_list=None, set_end_do_signal_list=None,
                  set_ao_signal_list=None, set_end_ao_signal_list=None):
        """
         Wait time [s]
        """
        response = self.control.WaitTime(control_msgs.WaitTimeReq(
            time=time,
            set_do_list=self.__to_digital_request_list__(set_do_signal_list),
            set_end_do_list=self.__to_digital_request_list__(set_end_do_signal_list),
            set_ao_list=self.__to_analog_request_list__(set_ao_signal_list),
            set_end_ao_list=self.__to_analog_request_list__(set_end_ao_signal_list)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_progress(self, progress: int,
                      set_do_signal_list=None, set_end_do_signal_list=None,
                      set_ao_signal_list=None, set_end_ao_signal_list=None):
        """
         Wait progress [s]
        """
        response = self.control.WaitProgress(control_msgs.WaitProgressReq(
            progress=progress,
            set_do_list=self.__to_digital_request_list__(set_do_signal_list),
            set_end_do_list=self.__to_digital_request_list__(set_end_do_signal_list),
            set_ao_list=self.__to_analog_request_list__(set_ao_signal_list),
            set_end_ao_list=self.__to_analog_request_list__(set_end_ao_signal_list)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_traj(self, traj_condition,
                  set_do_signal_list=None, set_end_do_signal_list=None,
                  set_ao_signal_list=None, set_end_ao_signal_list=None):
        """
         Wait trajectory
        """
        response = self.control.WaitTraj(control_msgs.WaitTrajReq(
            traj_condition=traj_condition,
            set_do_list=self.__to_digital_request_list__(set_do_signal_list),
            set_end_do_list=self.__to_digital_request_list__(set_end_do_signal_list),
            set_ao_list=self.__to_analog_request_list__(set_ao_signal_list),
            set_end_ao_list=self.__to_analog_request_list__(set_end_ao_signal_list)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_radius(self, radius: int,
                    set_do_signal_list=None, set_end_do_signal_list=None,
                    set_ao_signal_list=None, set_end_ao_signal_list=None):
        """
         Wait radius [mm]
        """
        response = self.control.WaitRadius(control_msgs.WaitRadiusReq(
            radius=radius,
            set_do_list=self.__to_digital_request_list__(set_do_signal_list),
            set_end_do_list=self.__to_digital_request_list__(set_end_do_signal_list),
            set_ao_list=self.__to_analog_request_list__(set_ao_signal_list),
            set_end_ao_list=self.__to_analog_request_list__(set_end_ao_signal_list)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def move_recover_joint(self, jtarget,
                           base_type=ABSOLUTE_JOINT) -> dict:
        """
         Move recover joint
         jtarget = [deg, deg, deg, deg, deg, deg]
        """
        response = self.control.MoveRecoverJoint(
            control_msgs.TargetJ(j_target=list(jtarget), base_type=base_type)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_control_info(self):
        response = self.control.GetControlInfo(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def ping_from_conty(self):
        response = self.control.PingFromConty(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def check_aproach_retract_valid(self, tpos, init_jpos, pre_tpos, post_tpos):
        """
        Check aproach retract valid
        """
        response = self.control.CheckAproachRetractValid(control_msgs.CheckAproachRetractValidReq(
            tpos=list(tpos),
            init_jpos=list(init_jpos),
            pre_tpos=list(pre_tpos),
            post_tpos=list(post_tpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_pallet_point_list(self, tpos, jpos, pre_tpos, post_tpos, pallet_pattern, width, height):
        """
        Get pallet point list
        """
        response = self.control.GetPalletPointList(control_msgs.GetPalletPointListReq(
            tpos=list(tpos),
            jpos=list(jpos),
            pre_tpos=list(pre_tpos),
            post_tpos=list(post_tpos),
            pallet_pattern=pallet_pattern,
            width=width,
            height=height
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def calculate_relative_pose(self, start_pos, end_pos,
                                base_type=ABSOLUTE_TASK):
        """
        Calculate relative pose
        """
        response = self.control.CalculateRelativePose(control_msgs.CalculateRelativePoseReq(
            start_pos=list(start_pos),
            end_pos=list(end_pos),
            base_type=base_type
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def calculate_current_pose_rel(self, current_pos, relative_pos,
                                   base_type=ABSOLUTE_TASK):
        """
        Calculate current pos rel
        """
        response = self.control.CalculateCurrentPoseRel(control_msgs.CalculateCurrentPoseRelReq(
            current_pos=list(current_pos),
            relative_pos=list(relative_pos),
            base_type=base_type
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)



