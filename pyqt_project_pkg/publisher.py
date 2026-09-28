import rclpy as rp
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtlesimPublisher(Node):
    def __init__(self):
        super().__init__("cmd_vel_publisher")
        self.msg = Twist()
        timer_period = 0.5
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        print(self.msg)

def main(args=None):
    rp.init(args=args)

    tp = TurtlesimPublisher()
    rp.spin(tp)

    tp.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()