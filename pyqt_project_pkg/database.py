import mysql.connector


class TurtleDB:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="172.17.176.1",
            port=3306,
            user="rosuser",
            password="1234",
            database="rosdb"
        )

        self.cursor = self.conn.cursor()

    def save_pose(self, x, y, theta):

        sql = """
        INSERT INTO turtlepos (x, y, theta)
        VALUES (%s, %s, %s)
        """

        data = (
            float(x),
            float(y),
            float(theta)
        )

        self.cursor.execute(sql, data)
        self.conn.commit()

        print(
            f"DB 저장 완료: "
            f"x={x}, y={y}, theta={theta}"
        )

    def close(self):
        self.cursor.close()
        self.conn.close()