import sys
import os

generated_files_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(generated_files_path)

from control_pb2_grpc import *
from device_pb2_grpc import *
from config_pb2_grpc import *
from rtde_pb2_grpc import *

from ethercat_pb2_grpc import *
from moby_pb2_grpc import *