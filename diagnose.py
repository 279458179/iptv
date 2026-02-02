import requests

def check_url(url, name):
    print(f"Checking {name}...")
    try:
        r = requests.head(url, timeout=5)
        print(f"[{name}] Status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return False

def check_ipv6_host(host):
    print(f"Checking IPv6 Host {host}...")
    try:
        r = requests.head(host, timeout=3)
        print(f"[IPv6 Host] Status: {r.status_code}")
    except Exception as e:
        print(f"[IPv6 Host] Failed: {e}")

if __name__ == "__main__":
    # 1. Check if IPv4 source list exists
    check_url("https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv4.m3u", "FanMingMing IPv4 List")
    
    # 2. Check if IPv6 source list exists (just to confirm)
    check_url("https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u", "FanMingMing IPv6 List")

    # 3. Check connectivity to a specific IPv6 stream host (from previous logs)
    # Note: IPv6 addresses need brackets in URL
    check_ipv6_host("http://[2409:8087:8:21::18]:6610")
