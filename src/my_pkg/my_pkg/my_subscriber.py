import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MySub(Node):

    def __init__(self):

        super().__init__("listener")

        self.sub = self.create_subscription(String, "/talker", self.talker_cb, 10)

    def talker_cb(self, msg: String):

        self.get_logger().error(f"I've got: {msg.data}")


def main():
    rclpy.init()

    node = MySub()

    rclpy.spin(node)

    rclpy.shutdown()
