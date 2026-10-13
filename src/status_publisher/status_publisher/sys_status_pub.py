#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""系统状态发布节点。

周期性采集本机 CPU、内存、网络与主机名信息，封装为自定义消息
status_interfaces/msg/SystemStatus 并发布到 /sys_status 话题。
"""

import platform

import psutil
import rclpy
from rclpy.node import Node

from status_interfaces.msg import SystemStatus


class SysStatusPub(Node):
    """采集并发布系统状态信息的 ROS2 节点。"""

    #: 字节转 GB 的除数
    BYTES_PER_GB = 1024 ** 3
    #: 字节转 MB 的除数
    BYTES_PER_MB = 1024 ** 2

    def __init__(self):
        super().__init__('sys_status_pub')

        # 发布周期，单位：秒
        self.declare_parameter('interval', 1.0)
        interval = self.get_parameter('interval').value

        # 话题名，单位均为 SI 标准
        self.publisher_ = self.create_publisher(SystemStatus, 'sys_status', 10)

        # 用于计算周期性网络增量的上一次采样值
        self._last_net_io = psutil.net_io_counters()

        self.timer = self.create_timer(interval, self.timer_callback)
        self.get_logger().info(
            f'sys_status_pub 已启动，发布周期 {interval}s，话题 /sys_status'
        )

    def get_hostname(self) -> str:
        """获取当前主机名。"""
        return platform.node()

    def get_cpu_percent(self) -> float:
        """获取 CPU 使用率（%）。"""
        return float(psutil.cpu_percent(interval=None))

    def get_memory(self) -> tuple:
        """获取内存信息。

        Returns:
            tuple: (使用率 %, 总大小 GB, 可用大小 GB)
        """
        mem = psutil.virtual_memory()
        return (
            float(mem.percent),
            float(mem.total / self.BYTES_PER_GB),
            float(mem.available / self.BYTES_PER_GB),
        )

    def get_net_io(self) -> tuple:
        """获取自上次调用以来网络收发增量。

        Returns:
            tuple: (发送量 MB, 接收量 MB)
        """
        current = psutil.net_io_counters()
        sent = float((current.bytes_sent - self._last_net_io.bytes_sent)
                     / self.BYTES_PER_MB)
        recv = float((current.bytes_recv - self._last_net_io.bytes_recv)
                     / self.BYTES_PER_MB)
        self._last_net_io = current
        return sent, recv

    def timer_callback(self):
        """定时器回调：采样并发布一条系统状态消息。"""
        msg = SystemStatus()

        # 采样时间戳
        msg.stamp = self.get_clock().now().to_msg()
        msg.hostname = self.get_hostname()

        msg.cpu_percent = self.get_cpu_percent()

        mem_percent, mem_total, mem_available = self.get_memory()
        msg.memory_percent = mem_percent
        msg.memory_total = mem_total
        msg.memory_available = mem_available

        net_sent, net_recv = self.get_net_io()
        msg.net_sent = net_sent
        msg.net_recv = net_recv

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'主机={msg.hostname} | CPU={msg.cpu_percent:.1f}% | '
            f'内存={msg.memory_percent:.1f}% '
            f'({msg.memory_available:.2f}/{msg.memory_total:.2f} GB) | '
            f'网络 发送={msg.net_sent:.3f} MB 接收={msg.net_recv:.3f} MB'
        )


def main(args=None):
    rclpy.init(args=args)
    node = SysStatusPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
