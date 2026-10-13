# ros2_system_status_monitor

基于 ROS2 Humble 的系统状态监视器：一个节点采集本机系统状态并发布，另一个节点用 Qt 小窗口实时显示。

## 功能

`status_publisher` 节点周期采样以下信息，封装为自定义消息发布到 `/sys_status`：

| 字段 | 类型 | 说明 |
|---|---|---|
| `stamp` | `builtin_interfaces/Time` | 采样时间戳 |
| `hostname` | `string` | 主机名 |
| `cpu_percent` | `float32` | CPU 使用率（%） |
| `memory_percent` | `float32` | 内存使用率（%） |
| `memory_total` | `float32` | 内存总大小（GB） |
| `memory_available` | `float32` | 可用内存（GB） |
| `net_sent` | `float32` | 周期内发送量（MB） |
| `net_recv` | `float32` | 周期内接收量（MB） |

同时提供一个 PyQt5 窗口订阅该话题，用于可视化展示。

## 目录结构

```
src/
├── status_interfaces/          # 接口包 (ament_cmake)
│   ├── CMakeLists.txt
│   ├── package.xml
│   ├── LICENSE
│   └── msg/
│       └── SystemStatus.msg
└── status_publisher/           # Python 功能包 (ament_python)
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── LICENSE
    ├── resource/
    │   └── status_publisher
    ├── status_publisher/
    │   ├── __init__.py
    │   ├── sys_status_pub.py       # 发布节点
    │   └── sys_status_display.py   # Qt 显示节点
    └── test/
        ├── test_copyright.py
        ├── test_flake8.py
        └── test_pep257.py
```

## 环境要求

- Ubuntu 22.04
- ROS2 Humble
- Python 3.10+
- `psutil`、`PyQt5`

```bash
sudo apt update
sudo apt install -y python3-psutil python3-pyqt5
```

> 若使用 pip：`pip install psutil PyQt5`

## 编译

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
# 将本仓库的两个包放入 src/ 下，或直接 clone 后再处理
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

> `--symlink-install` 是可选的，对 Python 包开发比较方便。接口包属于 C++ 包，改动 `.msg` 后需要重新 `colcon build`。

## 运行

打开三个终端（每个都先 `source /opt/ros/humble/setup.bash` 与 `source ~/ros2_ws/install/setup.bash`）。

**1. 启动发布节点**

```bash
ros2 run status_publisher sys_status_pub
```

**2. 启动 Qt 显示窗口**

```bash
ros2 run status_publisher sys_status_display
```

**3. 命令行查看话题（可选）**

```bash
ros2 topic echo /sys_status
ros2 interface show status_interfaces/msg/SystemStatus
```

## 参数

`sys_status_pub` 支持一个 `interval` 参数，用于调整发布周期（秒），默认 `1.0`：

```bash
ros2 run status_publisher sys_status_pub --ros-args -p interval:=0.5
```

## 说明

- 网络收发量是**增量**值（相邻两次采样的差值），不是系统累计值。
- CPU 使用率取自 `psutil.cpu_percent(interval=None)`，为非阻塞采样，首次调用结果可能为 `0.0`。
- 该节点设计为在**目标机器本地**运行，采集的是运行节点的那台机器的状态。
- 内存与网络单位分别为 GB、MB，接口字段已按此换算。

## 许可证

Apache-2.0
