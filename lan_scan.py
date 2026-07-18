import subprocess
import socket
from datetime import datetime


def scan_lan(subnet="192.168.1"):
    """
    扫描指定C类网段的存活主机
    :param subnet: 网段前缀，例如 192.168.1
    """
    print(f"开始扫描网段: {subnet}.1 ~ {subnet}.254")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    alive_hosts = []
    # 遍历1-254号地址
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        # 调用Windows系统ping命令，发送1个包，超时时间1000毫秒
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True,
            text=True
        )
        # 返回码为0表示ping通，主机存活
        if result.returncode == 0:
            # 尝试反向解析主机名，失败则显示未知
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                hostname = "未知主机名"

            alive_hosts.append((ip, hostname))
            print(f"[存活] {ip:15}  主机名: {hostname}")

    print("-" * 50)
    print(f"扫描完成，共发现 {len(alive_hosts)} 台存活设备")

    # 将扫描结果导出到文本文件
    with open("scan_result.txt", "w", encoding="utf-8") as f:
        f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"扫描网段: {subnet}.0/24\n")
        f.write("=" * 40 + "\n")
        f.write("IP地址\t\t主机名\n")
        for ip, name in alive_hosts:
            f.write(f"{ip}\t{name}\n")
    print("扫描结果已保存到 scan_result.txt")


if __name__ == "__main__":
    # 此处修改为你自己的网段，常见为 192.168.1 或 192.168.0
    scan_lan("192.168.1")