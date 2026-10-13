#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""系统状态显示节点（Qt 界面）。

订阅 /sys_status 话题，把收到的系统状态消息渲染到一个简单的
PyQt5 小窗口中，包括采样时间、主机名、CPU、内存与网络收发量。
"""

import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from status_interfaces.msg import SystemStatus

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StatusSubscriber(Node, QObject):
    """订阅系统状态话题，并通过 Qt 信号转发到界面线程。

    同时继承 Node 与 QObject：前者负责 rclpy 通信，后者用于跨线程
    发射信号，保证界面刷新在主线程执行。
    """

    #: 收到新状态消息时发射，携带 SystemStatus 消息
    status_received = pyqtSignal(object)

    def __init__(self):
        Node.__init__(self, 'sys_status_sub')
        QObject.__init__(self)

        # 使用可靠传输，避免高频状态下丢包
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.subscription = self.create_subscription(
            SystemStatus,
            'sys_status',
            self.status_callback,
            qos,
        )
        self.get_logger().info('sys_status_sub 已启动，订阅话题 /sys_status')

    def status_callback(self, msg: SystemStatus):
        """话题回调：仅转发信号，实际刷新交给界面线程。"""
        self.status_received.emit(msg)


class StatusWindow(QWidget):
    """展示系统状态的 Qt 窗口。"""

    def __init__(self, subscriber: StatusSubscriber):
        super().__init__()

        self.subscriber = subscriber
        self.subscriber.status_received.connect(self.update_ui)

        self.setWindowTitle('ROS2 系统状态监视器')
        self.resize(420, 320)

        self._build_ui()

    def _build_ui(self):
        """构建界面控件并填充占位文本。"""
        root_layout = QVBoxLayout(self)

        group = QGroupBox('实时系统状态')
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        value_font = QFont('Consolas')
        value_font.setPointSize(11)

        # 每个字段对应一个 QLabel，键为字段名
        self.labels = {}
        fields = [
            ('stamp', '采样时间'),
            ('hostname', '主机名'),
            ('cpu_percent', 'CPU 使用率'),
            ('memory_percent', '内存使用率'),
            ('memory_total', '内存总大小'),
            ('memory_available', '可用内存'),
            ('net_sent', '网络发送'),
            ('net_recv', '网络接收'),
        ]

        for key, title in fields:
            label = QLabel('--')
            label.setFont(value_font)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.labels[key] = label
            form.addRow(f'{title}:', label)

        group.setLayout(form)
        root_layout.addWidget(group)

        self.statusBar = QLabel('等待 /sys_status 消息 ...')
        self.statusBar.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(self.statusBar)

        self.setLayout(root_layout)

    def update_ui(self, msg: SystemStatus):
        """把新消息渲染到界面。"""
        stamp = msg.stamp

        # 手动格式化时间戳，避免依赖额外转换工具
        self.labels['stamp'].setText(
            f'{stamp.sec}.{stamp.nanosec // 1_000_000:03d}'
            f'  ({self._wall_clock_text(stamp)})'
        )
        self.labels['hostname'].setText(msg.hostname)
        self.labels['cpu_percent'].setText(f'{msg.cpu_percent:.1f} %')
        self.labels['memory_percent'].setText(f'{msg.memory_percent:.1f} %')
        self.labels['memory_total'].setText(f'{msg.memory_total:.2f} GB')
        self.labels['memory_available'].setText(
            f'{msg.memory_available:.2f} GB')
        self.labels['net_sent'].setText(f'{msg.net_sent:.3f} MB')
        self.labels['net_recv'].setText(f'{msg.net_recv:.3f} MB')

        self.statusBar.setText('消息持续接收中')

    @staticmethod
    def _wall_clock_text(stamp) -> str:
        """把 ROS 时间戳转换为本地可读时间字符串。"""
        import datetime

        dt = datetime.datetime.fromtimestamp(stamp.sec)
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def main(args=None):
    rclpy.init(args=args)

    subscriber = StatusSubscriber()

    app = QApplication(sys.argv)
    window = StatusWindow(subscriber)
    window.show()

    try:
        # 在 Qt 主循环中交替处理 ROS 回调
        while rclpy.ok() and window.isVisible():
            rclpy.spin_once(subscriber, timeout_sec=0.05)
            app.processEvents()
    except KeyboardInterrupt:
        pass
    finally:
        subscriber.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
