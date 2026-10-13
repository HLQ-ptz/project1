from setuptools import find_packages, setup

package_name = 'status_publisher'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'psutil', 'PyQt5'],
    zip_safe=True,
    maintainer='Putiz',
    maintainer_email='hlq_200801@qq.com',
    description='采集本机系统状态（CPU/内存/网络）并通过 Qt 窗口实时展示',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sys_status_pub = status_publisher.sys_status_pub:main',
            'sys_status_display = status_publisher.sys_status_display:main',
        ],
    },
)
