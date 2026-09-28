import sys
import rclpy as rp

from PyQt5.QtWidgets import *
from pyqt_project_pkg.publisher import TurtlesimPublisher
from pyqt_project_pkg.reset_service import TurtlesimReset
from pyqt_project_pkg.pose_data import TurtlesimPose

from pyqt_project_pkg.database import TurtleDB

class Window(QMainWindow):
    def __init__(self, Publisher, reset_client, Pose, db):
        super().__init__()
        self.setFixedSize(400, 300)

        self.pub = Publisher
        self.client = reset_client
        self.pose = Pose
        self.db = db

        window = QWidget()

        main_layout = QVBoxLayout()

        grid_layout = QGridLayout()
        self.front_btn = QPushButton("front")
        self.left_btn = QPushButton("turn_left")
        self.right_btn = QPushButton("turn_right")
        self.backward_btn = QPushButton("backward")

        grid_layout.addWidget(self.front_btn, 0, 1)
        grid_layout.addWidget(self.left_btn, 1, 0)
        grid_layout.addWidget(self.right_btn, 1, 2)
        grid_layout.addWidget(self.backward_btn, 2, 1)

        QHlayout = QHBoxLayout()
        self.reset_btn = QPushButton("reset")
        self.pose_btn = QPushButton("data down")
        QHlayout.addWidget(self.reset_btn)
        QHlayout.addWidget(self.pose_btn)

        main_layout.addLayout(grid_layout)
        main_layout.setSpacing(20)
        main_layout.addLayout(QHlayout)

        self.front_btn.clicked.connect(self.front)
        self.left_btn.clicked.connect(self.left)
        self.right_btn.clicked.connect(self.right)
        self.backward_btn.clicked.connect(self.backward)

        self.reset_btn.clicked.connect(self.reset)
        self.pose_btn.clicked.connect(self.get_data)

        window.setLayout(main_layout)
        self.setCentralWidget(window)

    def front(self):
        print("front")
        self.pub.msg.linear.x = 1.
        self.pub.msg.angular.z = 0.
        self.pub.publisher.publish(self.pub.msg)

    def backward(self):
        print("backward")
        self.pub.msg.linear.x = -1.
        self.pub.msg.angular.z = 0.
        self.pub.publisher.publish(self.pub.msg)

    def left(self):
        print("turn_left")
        self.pub.msg.linear.x = 0.
        self.pub.msg.angular.z = 1.
        self.pub.publisher.publish(self.pub.msg)

    def right(self):
        print("turn_right")
        self.pub.msg.linear.x = 0.
        self.pub.msg.angular.z = -1.
        self.pub.publisher.publish(self.pub.msg)

    def reset(self):
        print('reset')
        self.client.reset.call_async(self.client.req_reset)

    def get_data(self):
        print('get_data')
        rp.spin_once(self.pose)
        print(self.pose.pose)

        self.db.save_pose(
            self.pose.pose.x,
            self.pose.pose.y,
            self.pose.pose.theta
        )

def main():
    rp.init()

    tp = TurtlesimPublisher()
    rs = TurtlesimReset()
    ps = TurtlesimPose()
    db = TurtleDB()

    app = QApplication(sys.argv)

    myWindow = Window(tp, rs, ps, db)
    myWindow.show()

    app.exec_()

    db.close()

    tp.destroy_node()
    rs.destroy_node()
    ps.destroy_node()

if __name__=='__main__':
    main()