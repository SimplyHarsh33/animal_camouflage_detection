#!/usr/bin/python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

vel_msg = Twist()

class JoySubscriber(Node):

    def __init__(self):
        super().__init__('joy_subscriber')
        self.publisher_ = self.create_publisher(Twist, '/animal_robot/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.listener_callback,
            10)

    def listener_callback(self, data):
        vel_msg.linear.x = float(data.axes[1])
        vel_msg.linear.y = 0.0
        vel_msg.angular.z = float(data.axes[0])
        self.publisher_.publish(vel_msg)

def main(args=None):
    rclpy.init(args=args)
    joy_subscriber = JoySubscriber()
    rclpy.spin(joy_subscriber)
    joy_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
