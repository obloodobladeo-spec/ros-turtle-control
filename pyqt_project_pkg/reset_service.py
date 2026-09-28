import rclpy as rp
from rclpy.node import Node
from std_srvs.srv import Empty

class TurtlesimReset(Node):
    def __init__(self):
        super().__init__("reset_service")
        self.reset = self.create_client(Empty, '/reset')
        self.req_reset = Empty.Request()


def main(args=None):
    rp.init(args=args)

    tp = TurtlesimReset()
    rp.spin(tp)

    tp.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()