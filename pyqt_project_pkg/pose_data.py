import rclpy as rp
from rclpy.node import Node

from turtlesim.msg import Pose

class TurtlesimPose(Node):
    def __init__(self):
        super().__init__('Pose_sub')
        self.create_subscription(Pose, '/turtle1/pose', self.callback, 10)
        self.pose_x = 0
        self.pose_y = 0
        self.pose_theta = 0

    def callback(self, msg):
        self.pose = msg
        self.pose_x = msg.x
        self.pose_y = msg.y
        self.pose_theta = msg.theta

def main(args=None):
    rp.init(args=args)
    ts = TurtlesimPose()
    rp.spin()
    ts.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()