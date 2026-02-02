# CCTV IPTV Subscription Generator

This project automatically generates a reliable IPTV subscription list for CCTV channels (1-16+), using stable IPv6 relay sources.

## Features
- **Auto-Update**: Fetches the latest working streams from reliable relays.
- **IPv6 Support**: Uses high-speed IPv6 direct links (requires IPv6 network support).
- **Playlist Generation**: Creates `cctv_official.m3u` (pure CCTV) and `cctv_full.m3u` (merged with custom channels).

## Usage

### Subscription URL
You can use the following URL in your IPTV player (e.g., APTV, TiviMate):
`https://raw.githubusercontent.com/<YOUR_USERNAME>/<YOUR_REPO>/main/cctv_full.m3u`

*(Note: Replace `<YOUR_USERNAME>` and `<YOUR_REPO>` with your actual GitHub details)*

### Manual Update
Run the update script:
```bash
python update_channels.py
```

## Disclaimer
This project aggregates publicly available signals. Use for personal study only.
