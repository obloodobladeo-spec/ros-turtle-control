# ROS2 Turtlesim Controller with PyQt5 & MySQL

ROS2 Humble 환경에서 `turtlesim`을 직접 만든 ROS2 노드와 PyQt5 GUI로 제어하고,
현재 거북이의 위치 데이터를 MySQL 데이터베이스에 저장하는 프로젝트입니다.

## 프로젝트 목표

다음 기능을 구현합니다.

- ROS2 사용자 정의 패키지 생성
- PyQt5 GUI를 이용한 turtlesim 제어
- 전진 / 후진 / 좌회전 / 우회전
- turtlesim Reset
- `/turtle1/pose`를 이용한 현재 위치 확인
- 현재 위치 `(x, y, theta)`를 MySQL에 저장
- WSL의 ROS2 프로그램에서 Windows MySQL Server 사용

---

# 개발 환경

- Windows + WSL2
- Ubuntu 22.04
- ROS2 Humble
- Python 3.10
- PyQt5
- MySQL 8.0
- MySQL Workbench
- turtlesim

ROS2 Package:

```text
pyqt_project_pkg
```

---

# 프로젝트 구조

```text
ros2_study/
└── src/
    └── pyqt_project_pkg/
        └── pyqt_project_pkg/
            ├── pyqt.py
            ├── publisher.py
            ├── reset_service.py
            ├── pose_data.py
            └── database.py
```

각 파일의 역할은 다음과 같습니다.

```text
publisher.py
    └─ /turtle1/cmd_vel Publisher

reset_service.py
    └─ /reset Service Client

pose_data.py
    └─ /turtle1/pose Subscriber

database.py
    └─ MySQL 연결 및 위치 데이터 저장

pyqt.py
    └─ PyQt5 GUI 및 전체 기능 연결
```

---

# 시스템 구성

전체적인 데이터 흐름은 다음과 같습니다.

```text
                 PyQt5 GUI
                     │
       ┌─────────────┼──────────────┐
       │             │              │
       ▼             ▼              ▼
  방향 버튼       Reset        Data Down
       │             │              │
       ▼             ▼              ▼
 /cmd_vel Pub    /reset Client   Pose Subscriber
       │             │              │
       ▼             ▼              │
             turtlesim_node         │
                    │               │
                    └─ /turtle1/pose
                                    │
                                    ▼
                             x, y, theta
                                    │
                                    ▼
                               MySQL DB
                                    │
                                    ▼
                         rosdb.turtlepos
```

---

# 1. Turtlesim Publisher

`publisher.py`에서는 `geometry_msgs/msg/Twist` 메시지를 이용하여
`/turtle1/cmd_vel` 토픽으로 이동 명령을 전송합니다.

사용 토픽:

```text
/turtle1/cmd_vel
```

메시지 타입:

```text
geometry_msgs/msg/Twist
```

GUI 버튼에 따라 다음 값이 사용됩니다.

```text
front
linear.x  =  1.0
angular.z =  0.0

backward
linear.x  = -1.0
angular.z =  0.0

turn_left
linear.x  =  0.0
angular.z =  1.0

turn_right
linear.x  =  0.0
angular.z = -1.0
```

---

# 2. Reset Service

turtlesim을 초기 상태로 되돌리기 위해 `/reset` 서비스를 사용합니다.

Service:

```text
/reset
```

Service Type:

```text
std_srvs/srv/Empty
```

PyQt의 `reset` 버튼을 누르면:

```python
self.client.reset.call_async(self.client.req_reset)
```

가 호출되어 turtlesim이 초기화됩니다.

---

# 3. Pose Subscriber

현재 거북이의 위치를 얻기 위해 다음 토픽을 구독합니다.

```text
/turtle1/pose
```

Message Type:

```text
turtlesim/msg/Pose
```

사용하는 데이터:

```text
x
y
theta
```

Subscriber가 받은 Pose 메시지에서 다음과 같이 데이터를 저장합니다.

```python
self.pose_x = msg.x
self.pose_y = msg.y
self.pose_theta = msg.theta
```

Pose 메시지 예:

```text
turtlesim.msg.Pose(
    x=7.960444450378418,
    y=5.544444561004639,
    theta=1.0080000162124634,
    linear_velocity=0.0,
    angular_velocity=0.0
)
```

---

# 4. PyQt5 GUI

GUI에는 총 6개의 버튼이 있습니다.

```text
              front

     turn_left     turn_right

             backward

         reset    data down
```

버튼 기능:

| 버튼 | 기능 |
|---|---|
| front | 앞으로 이동 |
| backward | 뒤로 이동 |
| turn_left | 왼쪽 회전 |
| turn_right | 오른쪽 회전 |
| reset | turtlesim 초기화 |
| data down | 현재 x, y, theta를 DB에 저장 |

GUI 창 크기는 다음과 같이 고정되어 있습니다.

```text
400 x 300
```

### 방향키로 거북이 조종하기

PyQt GUI 창이 활성화된 상태에서 방향키를 누르면 해당 이동 버튼을 클릭한 것과 같은 동작을 합니다.

| 키 | 실행되는 버튼 | 동작 |
|---|---|---|
| `↑` | `front` | 앞으로 이동 |
| `↓` | `backward` | 뒤로 이동 |
| `←` | `turn_left` | 왼쪽으로 회전 |
| `→` | `turn_right` | 오른쪽으로 회전 |

`pyqt.py`는 각 방향키를 `QShortcut`으로 등록하고, 단축키가 실행되면 기존 버튼의 `click()`을 호출합니다. 따라서 마우스로 버튼을 눌렀을 때와 동일한 ROS2 이동 명령을 전송합니다.

`data down` 버튼을 누르면 현재 Pose 데이터를 한 번 받아온 후
MySQL 데이터베이스에 저장합니다.

```text
data down
    ↓
/turtle1/pose 확인
    ↓
x, y, theta
    ↓
INSERT
    ↓
rosdb.turtlepos
```

---

# 5. MySQL 데이터베이스

요구사항에 따라 다음 데이터베이스를 사용합니다.

Schema:

```text
rosdb
```

Table:

```text
turtlepos
```

테이블 구성:

```text
id
x
y
theta
time
```

MySQL Workbench에서 다음 SQL을 실행합니다.

```sql
CREATE DATABASE IF NOT EXISTS rosdb;

USE rosdb;

CREATE TABLE turtlepos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    theta FLOAT NOT NULL,
    time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

`id`는 자동 증가하고 `time`은 데이터가 저장되는 현재 시간이 자동으로 기록됩니다.

따라서 Python에서는 다음 세 값만 INSERT 합니다.

```text
x
y
theta
```

INSERT SQL:

```sql
INSERT INTO turtlepos (x, y, theta)
VALUES (%s, %s, %s);
```

---

# 6. WSL에서 Windows MySQL 사용하기

이 프로젝트에서는 ROS2와 Python을 WSL에서 실행하고,
MySQL Server는 Windows에서 실행할 수 있습니다.

구조:

```text
WSL Ubuntu
    │
    │ TCP/IP : 3306
    ▼
Windows MySQL Server
    │
    ▼
rosdb.turtlepos
```

## Windows MySQL Server 확인

MySQL Workbench의 기본 Windows MySQL 연결은 일반적으로:

```text
Hostname : 127.0.0.1
Port     : 3306
```

형태입니다.

하지만 WSL에서 Windows의 `127.0.0.1`을 사용하는 대신
Windows 호스트 IP를 확인하여 사용하는 방법이 있습니다.

WSL에서:

```bash
ip route | grep default
```

예:

```text
default via 172.17.176.1 dev eth0 proto kernel
```

이 경우 Windows 호스트 주소는:

```text
172.17.176.1
```

입니다.

> WSL을 다시 시작하면 IP가 변경될 수 있으므로 접속이 되지 않을 경우
> `ip route | grep default`로 다시 확인합니다.

---

# 7. Windows MySQL에 WSL 접속 계정 만들기

Windows MySQL의 `root` 계정은 외부 호스트에서의 접속이 제한될 수 있습니다.

예를 들어 다음 오류가 발생할 수 있습니다.

```text
ERROR 1130 (HY000):
Host '172.x.x.x' is not allowed to connect to this MySQL server
```

또는:

```text
ERROR 1045 (28000):
Access denied for user 'root'@'172.x.x.x'
```

따라서 `root`를 직접 사용하는 대신 WSL 접속용 사용자를 별도로 생성합니다.

Windows MySQL Workbench에서 실행:

```sql
CREATE USER 'rosuser'@'%' IDENTIFIED BY 'YOUR_PASSWORD';

GRANT ALL PRIVILEGES ON rosdb.* TO 'rosuser'@'%';

FLUSH PRIVILEGES;
```

`%`는 여러 호스트에서 해당 계정으로 접속할 수 있도록 허용합니다.

교육용 로컬 환경에서는 편리하지만 실제 서비스 환경에서는
허용할 IP 범위를 제한하는 것이 좋습니다.

---

# 8. WSL에서 Windows MySQL 접속 테스트

Windows IP가 다음이라고 가정합니다.

```text
172.17.176.1
```

WSL 터미널에서:

```bash
mysql -h 172.17.176.1 -P 3306 -u rosuser -p
```

비밀번호를 입력합니다.

접속에 성공하면:

```sql
USE rosdb;

SHOW TABLES;
```

`turtlepos` 테이블 확인:

```sql
SELECT * FROM turtlepos;
```

---

# 9. Python MySQL 연결

필요한 Python 패키지를 설치합니다.

```bash
python3 -m pip install mysql-connector-python
```

`database.py`에서는 다음과 같은 방식으로 Windows MySQL에 접속합니다.

```python
self.conn = mysql.connector.connect(
    host="WINDOWS_HOST_IP",
    port=3306,
    user="rosuser",
    password="YOUR_PASSWORD",
    database="rosdb"
)
```

예:

```python
self.conn = mysql.connector.connect(
    host="172.17.176.1",
    port=3306,
    user="rosuser",
    password="YOUR_PASSWORD",
    database="rosdb"
)
```

현재 위치 저장 함수에서는:

```python
sql = """
INSERT INTO turtlepos (x, y, theta)
VALUES (%s, %s, %s)
"""
```

을 실행하고:

```python
self.conn.commit()
```

하여 실제 DB에 반영합니다.

---

# 10. ROS2 패키지 Build

Workspace로 이동합니다.

```bash
cd ~/ros2_study
```

Build:

```bash
colcon build --packages-select pyqt_project_pkg
```

환경 적용:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_study/install/setup.bash
```

---

# 11. 실행 방법

## Terminal 1 - turtlesim 실행

```bash
ros2 run turtlesim turtlesim_node
```

과제 조건에 따라 `turtlesim_node`를 제외한 이동/Reset/Pose 처리 기능은
직접 작성한 패키지의 코드에서 수행합니다.

## Terminal 2 - PyQt 프로그램 실행

Workspace 환경을 적용합니다.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_study/install/setup.bash
```

PyQt 프로그램을 실행합니다.

```bash
python3 ~/ros2_study/src/pyqt_project_pkg/pyqt_project_pkg/pyqt.py
```

`setup.py`에 console script가 등록되어 있다면 해당 ROS2 실행 명령으로
실행할 수도 있습니다.

---

# 12. 데이터 저장 확인

turtlesim을 이동시킨 후 GUI에서:

```text
data down
```

버튼을 누릅니다.

터미널에는 다음과 같은 Pose 정보가 출력됩니다.

```text
get_data
turtlesim.msg.Pose(
    x=7.960444450378418,
    y=5.544444561004639,
    theta=1.0080000162124634,
    linear_velocity=0.0,
    angular_velocity=0.0
)
```

이후:

```text
DB 저장 완료:
x=7.960444450378418,
y=5.544444561004639,
theta=1.0080000162124634
```

형태로 출력됩니다.

Windows MySQL Workbench에서:

```sql
USE rosdb;

SELECT * FROM turtlepos;
```

를 실행하면 저장된 데이터를 확인할 수 있습니다.

예:

```text
+----+----------+----------+-------+---------------------+
| id | x        | y        | theta | time                |
+----+----------+----------+-------+---------------------+
| 1  | 7.960444 | 5.544445 | 1.008 | 2026-09-28 16:20:10 |
+----+----------+----------+-------+---------------------+
```

---

# 사용한 ROS2 통신

| 기능 | ROS2 통신 | 이름 | 타입 |
|---|---|---|---|
| 거북이 이동 | Publisher | `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` |
| 거북이 초기화 | Service Client | `/reset` | `std_srvs/srv/Empty` |
| 위치 확인 | Subscriber | `/turtle1/pose` | `turtlesim/msg/Pose` |

---

# 실행 흐름 요약

```text
1. Windows MySQL Server 실행
           ↓
2. WSL에서 ROS2 환경 적용
           ↓
3. turtlesim_node 실행
           ↓
4. 직접 만든 PyQt 프로그램 실행
           ↓
5. 방향 버튼으로 turtlesim 제어
           ↓
6. data down 클릭
           ↓
7. /turtle1/pose 메시지 수신
           ↓
8. x, y, theta 추출
           ↓
9. Windows MySQL의 rosdb.turtlepos에 저장
```

---

# 주의사항

Windows 호스트 IP는 WSL 실행 환경에 따라 변경될 수 있습니다.

현재 Windows IP 확인:

```bash
ip route | grep default
```

따라서 MySQL 연결에 실패하는 경우 `database.py`의 `host` 값을
현재 Windows 호스트 IP로 수정해야 합니다.

또한 GitHub 공개 저장소에는 실제 MySQL 비밀번호를 직접 업로드하지 않는 것을 권장합니다.
