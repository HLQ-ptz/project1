# 系统实时状态消息
# 记录一次系统状态采样，包含时间戳、主机名、CPU、内存与网络信息

# 采样时刻的时间戳
builtin_interfaces/Time stamp

# 主机名
string hostname

# CPU 使用率，单位：%
float32 cpu_percent

# 内存使用率，单位：%
float32 memory_percent

# 内存总大小，单位：GB
float32 memory_total

# 可用内存，单位：GB
float32 memory_available

# 本次采样周期内发送的数据量，单位：MB
float32 net_sent

# 本次采样周期内接收的数据量，单位：MB
float32 net_recv
