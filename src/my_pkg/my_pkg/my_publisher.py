import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MyNode(Node):

    def __init__(self):
        super().__init__("naziv_nodea")
        self.pub = self.create_publisher(String, "/talker", 10)

        self.declare_parameter("publish_rate", 0.1)
        self.publish_rate = self.get_parameter("publish_rate").get_parameter_value().double_value

        self.timer = self.create_timer(self.publish_rate, self.talker_callback)

    def talker_callback(self):
        msg = String()
        msg.data = "Hello world!"
        self.pub.publish(msg)


def main():
    rclpy.init()
    my_node = MyNode()
    rclpy.spin(my_node)
    rclpy.shutdown()


if __name__ == "__main__":

    main()
