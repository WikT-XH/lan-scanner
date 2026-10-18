import argparse
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


def port_open(ip, port, timeout):
    """探测单个 IP 的单个端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((str(ip), port))
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def hostname_of(ip):
    """解析主机名，失败返回空串"""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except socket.herror:
        return ""


def main():
    parser = argparse.ArgumentParser(description="局域网存活主机与端口扫描工具")
    parser.add_argument("-n", "--network", default="192.168.1.0/24", help="网段，如 192.168.1.0/24")
    parser.add_argument("-p", "--ports", default="80", help="端口列表，逗号分隔，如 80,443,22")
    parser.add_argument("-t", "--timeout", type=float, default=0.8, help="连接超时（秒）")
    parser.add_argument("-w", "--workers", type=int, default=50, help="并发线程数")
    parser.add_argument("-o", "--output", help="结果导出文件路径，不填则不导出")
    args = parser.parse_args()

    try:
        network = ipaddress.ip_network(args.network, strict=False)
    except ValueError:
        print(f"网段格式无效: {args.network}")
        return
    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    hosts = list(network.hosts())
    if not hosts:
        print(f"网段 {network} 内没有可用主机")
        return

    total = len(hosts) * len(ports)
    print(f"网段 {network} 共 {len(hosts)} 台主机，扫描端口 {ports}")

    open_results = {}  # ip -> [(port, hostname)]
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(port_open, ip, port, args.timeout): (ip, port)
                   for ip in hosts for port in ports}
        for future in as_completed(futures):
            ip, port = futures[future]
            done += 1
            if future.result():
                open_results.setdefault(str(ip), []).append(port)
            if done % 20 == 0 or done == total:
                print(f"\r进度 {done}/{total}", end="", flush=True)
    print()

    if not open_results:
        print("未发现开放端口的主机")
        return

    print(f"\n扫描完成，发现 {len(open_results)} 台主机开放端口:")
    lines = []
    for ip, ports_open in sorted(open_results.items()):
        name = hostname_of(ip)
        suffix = f" ({name})" if name else ""
        line = f"{ip}{suffix}: " + ", ".join(str(p) for p in sorted(ports_open))
        print(f"✅ {line}")
        lines.append(line)

    if args.output:
        with open(args.output, "w", encoding="utf-8-sig") as f:
            f.write(f"网段: {network}\n")
            f.write("\n".join(lines) + "\n")
        print(f"\n结果已导出到 {args.output}")


if __name__ == "__main__":
    main()
