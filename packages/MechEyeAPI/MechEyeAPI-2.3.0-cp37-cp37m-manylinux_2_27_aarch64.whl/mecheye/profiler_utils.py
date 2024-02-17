from mecheye.profiler import *
from mecheye.shared import *

def print_profiler_info(profiler_info: ProfilerInfo):
    print(".........................................")
    print("Profiler Model Name:           ", profiler_info.model, sep="")
    print("Controller Serial Number:      ", profiler_info.controller_sn, sep="")
    print("Sensor Serial Number:          ", profiler_info.sensor_sn, sep="")
    print("Profiler IP Address:           ", profiler_info.ip_address, sep="")
    print("Profiler IP Subnet Mask:       ", profiler_info.subnet_mask, sep="")
    print("Profiler IP Assignment Method: ", ip_assignment_method_to_string(profiler_info.ip_assignment_method), sep="")
    print("Hardware Version:              V", profiler_info.hardware_version.to_string(), sep="")
    print("Firmware Version:              V", profiler_info.firmware_version.to_string(), sep="")
    print(".........................................")
    print()

def find_and_connect(profiler: Profiler) -> bool:
    print("Find Mech-Eye 3D Laser Profilers...")
    profiler_infos = Profiler.discover_profilers()

    if len(profiler_infos) == 0:
        print("No Mech-Eye 3D Laser Profilers found.")
        return False

    for i in range(len(profiler_infos)):
        print("Mech-Eye device index :", i)
        print_profiler_info(profiler_infos[i])

    print("Please enter the device index you want to connect: ")
    input_index = 0

    while True:
        input_index = input()
        if input_index.isdigit() and 0 <= int(input_index) < len(profiler_infos):
            input_index = int(input_index)
            break
        print("Input invalid! Please enter the device index you want to connect: ")

    error_status = profiler.connect(profiler_infos[input_index])
    if not error_status.is_ok():
        show_error(error_status)
        return False

    print("Connect Mech-Eye 3D Laser Profiler Successfully.")
    return True

def confirm_capture() -> bool:
    print("Do you want the profiler to capture image ? Please input y/n to confirm: ")
    while True:
        input_str = input()
        if input_str == "y" or input_str == "Y":
            return True
        elif input_str == "n" or input_str == "N":
            return False
        else:
            print("Please input y/n again!")