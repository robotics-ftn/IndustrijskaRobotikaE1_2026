import os
import yaml

from launch import LaunchDescription
from launch.actions import TimerAction
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from xacro import process_file

# ============================================================
# ACTIVE PLANNING PIPELINE
# Change this value to switch the default planner.
# All four pipelines are loaded; this controls which one is used.
# Options: "ompl" | "pilz_industrial_motion_planner" | "chomp" | "stomp"
# ============================================================
DEFAULT_PLANNING_PIPELINE = "ompl"


def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def generate_launch_description():

    # ------------------------------------------------------------------
    # Package / config directories
    # ------------------------------------------------------------------
    xarm_moveit_dir = get_package_share_directory('xarm_moveit_config')
    robot_move_dir = get_package_share_directory('robot_move')

    xarm_cfg = os.path.join(xarm_moveit_dir, 'config')
    robot_move_cfg = os.path.join(robot_move_dir,  'config')

    # ==================================================================
    # MoveIt core parameters (replaces MoveItConfigsBuilder)
    # ==================================================================

    # --- robot_description  (URDF from xacro) -------------------------
    robot_description = {
        'robot_description': process_file(
            os.path.join(xarm_cfg, 'UF_ROBOT.urdf.xacro')
        ).toxml()
    }

    # --- robot_description_semantic  (SRDF) ---------------------------
    with open(os.path.join(xarm_cfg, 'UF_ROBOT.srdf'), 'r') as f:
        robot_description_semantic = {'robot_description_semantic': f.read()}

    # --- robot_description_kinematics ---------------------------------
    robot_description_kinematics = {
        'robot_description_kinematics': load_yaml(
            os.path.join(xarm_cfg, 'kinematics.yaml')
        )
    }

    # --- robot_description_planning  (joint limits + Pilz Cartesian) --
    joint_limits = load_yaml(os.path.join(xarm_cfg,       'joint_limits.yaml'))
    pilz_cart_limits = load_yaml(os.path.join(robot_move_cfg, 'pilz_cartesian_limits.yaml'))
    robot_description_planning = {
        'robot_description_planning': {**joint_limits, **pilz_cart_limits}
    }

    # --- MoveIt controller manager ------------------------------------
    moveit_controllers = load_yaml(os.path.join(xarm_cfg, 'moveit_controllers.yaml'))

    # ==================================================================
    # Planning pipelines
    # All four pipelines are registered and ready to use.
    # Switch between them by changing DEFAULT_PLANNING_PIPELINE above.
    # ==================================================================
    ompl_config = load_yaml(os.path.join(robot_move_cfg, 'ompl_planning.yaml'))
    pilz_config = load_yaml(os.path.join(robot_move_cfg, 'pilz_industrial_motion_planner_planning.yaml'))
    chomp_config = load_yaml(os.path.join(robot_move_cfg, 'chomp_planning.yaml'))
    stomp_config = load_yaml(os.path.join(robot_move_cfg, 'stomp_planning.yaml'))

    planning_pipeline_configs = {
        'ompl':                           ompl_config,
        'pilz_industrial_motion_planner': pilz_config,
        'chomp':                          chomp_config,
        'stomp':                          stomp_config,
    }

    # ==================================================================
    # MoveItCpp settings  (planning scene monitor + request defaults)
    # Active pipeline is injected from DEFAULT_PLANNING_PIPELINE.
    # ==================================================================
    moveit_cpp_params = load_yaml(
        os.path.join(robot_move_cfg, 'moveit_cpp.yaml')
    )['/**']['ros__parameters']

    moveit_cpp_params['planning_pipelines']['pipeline_names'] = [
        'ompl', 'pilz_industrial_motion_planner', 'chomp', 'stomp'
    ]
    moveit_cpp_params['plan_request_params']['planning_pipeline'] = DEFAULT_PLANNING_PIPELINE

    # ==================================================================
    # Nodes
    # ==================================================================

    # --- Robot State Publisher ----------------------------------------
    # Publishes /robot_description and TF frames.
    # ROS2 Control tags in the URDF are required for ros2_control_node.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

    # --- ROS2 fake / sim controllers ----------------------------------
    fake_controllers = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            os.path.join(xarm_cfg, 'ros2_controllers.yaml'),
        ],
        remappings=[
            ('/controller_manager/robot_description', '/robot_description'),
        ],
    )

    # --- Controller spawners ------------------------------------------
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller'],
    )

    hand_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['hand_controller'],
    )

    # --- RViz ---------------------------------------------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    # --- robot_move  (MoveItCpp action server) ------------------------
    robot_move_node = Node(
        package='robot_move',
        executable='robot_move',
        name='robot_move',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            moveit_controllers,
            planning_pipeline_configs,
            moveit_cpp_params,
        ],
    )

    return LaunchDescription([
        robot_state_publisher_node,
        fake_controllers,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        hand_controller_spawner,
        rviz,
        # Delay robot_move until RViz is fully initialised
        TimerAction(period=2.0, actions=[robot_move_node]),
    ])
