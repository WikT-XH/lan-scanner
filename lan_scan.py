import ipaddress
from concurrent.futures import ThreadPoolExecutor
import socket

def tcp_scan(ip, port=80, timeout=0.8):
    """尝试连接指定端口判断主机是否存活，默认探测80端口"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((str(ip), port))
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def main():
    subnet = input("请输入网段（如 192.168.1.0/24，回车用默认）: ").strip() or "192.168.1.0/24"
    subnet = subnet.replace(" ", "/")
    network = ipaddress.ip_network(subnet, strict=False)

    print(f"正在扫描网段: {network}")
    alive = []
    with ThreadPoolExecutor(max_workers=50) as pool:
        for ip, is_alive in zip(network.hosts(), pool.map(tcp_scan, network.hosts())):
            if is_alive:
                alive.append(str(ip))
                print(f"✅ 在线: {ip}")

    print(f"\n扫描结束，共找到 {len(alive)} 台开放80端口的设备")

if __name__ == "__main__":
    main()
