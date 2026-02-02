# CCTV IPTV Subscription Generator

This project automatically generates reliable IPTV subscription lists for CCTV channels (1-16+), aggregating sources to support both **IPv4** and **IPv6** network environments.

## Subscription Links (Recommend)

If you are experiencing playback issues, try the **IPv4** list first.

| Type | Filename | Description |
|------|----------|-------------|
| **IPv4 Only** | `cctv_ipv4.m3u` | **Best for most users.** Uses pure IPv4 sources (Mobile/Unicom/Telecom). Compatible with all networks. |
| **IPv6 Only** | `cctv_ipv6.m3u` | High-speed, low-latency streams. Requires your network to support IPv6. |
| **Full (Combo)** | `cctv_full.m3u` | Contains both IPv4 and IPv6 sources. IPv4 is prioritized. |

### How to Use
Copy the Raw link of the file you need and add it to your IPTV player (APTV, TiviMate, etc.).

**Example URL Structure:**
`https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO>/main/cctv_ipv4.m3u`

*(Replace `<YOUR_USERNAME>` and `<YOUR_REPO>` with your actual GitHub repository details)*

## Features
- **Multi-Source Aggregation**: Fetches from verified community sources (FrankWu, FanMingMing, IPTV-Org).
- **Network Compatibility**: Provides separate lists for IPv4 and IPv6 to solve "cannot play" issues.
- **Auto-Update**: Script `update_channels.py` fetches the latest valid streams.

## Manual Update
Run the update script to refresh the lists:
```bash
python update_channels.py
```
