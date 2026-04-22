from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_dir = get_package_share_directory("my_pkg")

    yaml_path = pkg_dir + "/config/my_pkg.yaml"

    xarm_pkg_dir = get_package_share_directory("xarm_description")
    xarm_urdf_path = xarm_pkg_dir + "/urdf/xarm7_with_gripper_camera.urdf"

    xarm_urdf_str = open(xarm_urdf_path).read()

    return LaunchDescription(
        [
            Node(
                package="my_pkg",
                executable="talker",
                name="novi_talker",
                output="screen",

                parameters=[
                    yaml_path
                ]

            ),
            Node(
                package="my_pkg",
                executable="listener",
                name="novi_listener",
                output="screen",
                emulate_tty=True,
            ),

            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[
                    {
                        "robot_description": xarm_urdf_str
                    }
                ]
            ),

            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                parameters=[
                    {
                        "robot_description": xarm_urdf_str
                    }
                ]
            )

        ]

    )
