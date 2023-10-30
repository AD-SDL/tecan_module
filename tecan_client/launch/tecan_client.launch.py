from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    port = LaunchConfiguration('port')
    declare_use_port_cmd = DeclareLaunchArgument(
        name = "port",
        default_value= "/dev/ttyUSB0",
        description= "Flag to accept chemspeed port"
        )
    
    chemspeed_module_client = Node(
            package = 'chemspeed_module_client',
            namespace = 'chemspeed_module_client',
            executable = 'chemspeed_client',
            output = "screen",
            name='chemspeedNode',
            parameters = [{"port":port}],
            emulate_tty=True

    )
    launch_d = LaunchDescription()
    launch_d.add_action(declare_use_port_cmd)
    launch_d.add_action(chemspeed_module_client)
    return launch_d
    