import rclpy
from rclpy.node import Node
from moveit.planning import MoveItPy
from moveit.core.robot_model import RobotModel
from geometry_msgs.msg import PoseStamped
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
import random


class RobotSubscriberNode(Node):
    def __init__(self, robot, arm, hand):
        super().__init__("robot_move_subscriber")
        self.robot: RobotModel = robot
        self.arm = arm
        self.hand = hand
        self.open = True

        self.sub = self.create_subscription(
            String, "/some_topic", self.callback, 10
        )

    def callback(self, msg):
        self.get_logger().info(f"Received: {msg.data}")
        self.hand.set_start_state_to_current_state()
        self.hand.set_goal_state("open" if self.open else "close")
        plan = self.hand.plan()
        if plan:
            self.robot.execute(plan.trajectory, controllers=[])
            self.open = not self.open

        pose_goal = PoseStamped()
        pose_goal.header.frame_id = "link_base"

        # Rotate 180 degrees around X to point Z down while keeping X facing forward
        pose_goal.pose.orientation.x = 1.0
        pose_goal.pose.orientation.y = 0.0
        pose_goal.pose.orientation.z = 0.0
        pose_goal.pose.orientation.w = 0.0  # Explicitly setting w=0.0 is good practice

        pose_goal.pose.position.x = 0.4
        pose_goal.pose.position.y = 0.0
        pose_goal.pose.position.z = random.uniform(0.2, 0.5)  # Random height between 0.2 and 0.5 meters
        self.arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="link_eef")

        plan = self.arm.plan()
        if plan:
            self.robot.execute(plan.trajectory, controllers=[])


def main():
    rclpy.init()

    # MoveItPy node_name must match the node name in the launch file
    # so it receives all the parameters
    robot = MoveItPy(node_name="robot_move_moveit")
    arm = robot.get_planning_component("arm")
    hand = robot.get_planning_component("hand")

    node = RobotSubscriberNode(robot, arm, hand)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()

    rclpy.shutdown()


if __name__ == "__main__":

    main()
