import requests
import datetime
import os

def main():
    # Sources configuration
    sources = [
        {
            "name": "IPv6 (FanMingMing)",
            "url": "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
            "type": "ipv6"
        },
        {
            "name": "IPv4 (FrankWu)",
            "url": "https://raw.githubusercontent.com/frankwuzp/iptv-cn/main/tv-ipv4-cn.m3u",
            "type": "ipv4"
        },
        {
            "name": "IPv4 (IPTV-Org)",
            "url": "https://iptv-org.github.io/iptv/countries/cn.m3u",
            "type": "ipv4_backup"
        }
    ]

    target_channels = [
        "CCTV-1", "CCTV-2", "CCTV-3", "CCTV-4", "CCTV-5", "CCTV-5+", 
        "CCTV-6", "CCTV-7", "CCTV-8", "CCTV-9", "CCTV-10", "CCTV-11", 
        "CCTV-12", "CCTV-13", "CCTV-14", "CCTV-15", "CCTV-16", 
        "CCTV-4K", "CCTV-8K"
    ]

    all_channels = []

    for source in sources:
        print(f"Fetching source: {source['name']}...")
        try:
            r = requests.get(source['url'], timeout=30)
            if r.status_code != 200:
                print(f"Failed to fetch {source['name']}: {r.status_code}")
                continue
            
            lines = r.text.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTINF"):
                    # Basic parsing
                    channel_name = line.split(',')[-1].strip()
                    
                    # Check if target
                    is_target = False
                    normalized_name = ""
                    for target in target_channels:
                        if target in channel_name.upper():
                            if channel_name.upper().startswith(target):
                                is_target = True
                                normalized_name = target
                                break
                    
                    if is_target and i + 1 < len(lines):
                        url = lines[i+1].strip()
                        if url and not url.startswith("#"):
                            all_channels.append({
                                "name": normalized_name, # Use standardized name
                                "original_name": channel_name,
                                "url": url,
                                "source_type": source['type'],
                                "line_info": line
                            })
                i += 1
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")

    print(f"Total extracted channels: {len(all_channels)}")

    # Organize channels by name
    channels_map = {}
    for chan in all_channels:
        if chan['name'] not in channels_map:
            channels_map[chan['name']] = []
        channels_map[chan['name']].append(chan)

    # Helper to generate M3U content
    def generate_m3u(channels_data, preferred_type=None):
        content = "#EXTM3U\n"
        for name in target_channels:
            if name in channels_data:
                # Sort streams: preferred_type first
                streams = channels_data[name]
                if preferred_type:
                    streams.sort(key=lambda x: 0 if x['source_type'] == preferred_type else 1)
                
                for stream in streams:
                    # Modify title to indicate type if needed, or keep original
                    # For user clarity, let's append type to title in the #EXTINF
                    title_suffix = f" [{stream['source_type'].upper()}]"
                    new_line_info = stream['line_info'].replace(stream['original_name'], f"{stream['original_name']}{title_suffix}")
                    content += f"{new_line_info}\n{stream['url']}\n"
        return content

    # 1. Generate IPv4 Only M3U (Safe for most users)
    ipv4_content = generate_m3u(channels_map, preferred_type='ipv4')
    with open("cctv_ipv4.m3u", "w", encoding="utf-8") as f:
        f.write(ipv4_content)

    # 2. Generate IPv6 Only M3U
    ipv6_content = generate_m3u(channels_map, preferred_type='ipv6')
    with open("cctv_ipv6.m3u", "w", encoding="utf-8") as f:
        f.write(ipv6_content)

    # 3. Generate Full M3U (IPv4 first as it's more compatible)
    full_content = generate_m3u(channels_map, preferred_type='ipv4')
    
    # Preserve existing custom channels if any (from previous cctv_full.m3u runs)
    # Actually, let's simplify and just overwrite cctv_full.m3u with the high quality CCTV list
    # The user wanted a CCTV app, so merging old garbage might be bad.
    # But if they had custom channels...
    # Let's try to read cctv_full.m3u for non-CCTV channels
    other_channels = ""
    if os.path.exists("cctv_full.m3u"):
        try:
            with open("cctv_full.m3u", "r", encoding="utf-8") as f:
                old_lines = f.readlines()
            
            buffer = []
            skip = False
            for line in old_lines:
                if line.strip().startswith("#EXTM3U"): continue
                if line.startswith("#EXTINF"):
                    # If it's a CCTV channel we generated, skip it
                    if "group-title=\"CCTV" in line or "CCTV-" in line or "[IPV" in line:
                        skip = True
                    else:
                        skip = False
                        buffer.append(line)
                elif not line.startswith("#") and line.strip():
                    if not skip:
                        buffer.append(line)
            other_channels = "".join(buffer)
        except:
            pass

    with open("cctv_full.m3u", "w", encoding="utf-8") as f:
        f.write(full_content + "\n" + other_channels)

    # 4. Generate Markdown
    md_content = "# CCTV Live Sources\n\n> Auto-aggregated from multiple sources. **Recommended: Try IPv4 links if IPv6 fails.**\n\n"
    md_content += f"*Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    md_content += "| Channel | IPv4 Stream | IPv6 Stream |\n|---|---|---|\n"
    
    for name in target_channels:
        if name in channels_map:
            streams = channels_map[name]
            ipv4_url = next((s['url'] for s in streams if 'ipv4' in s['source_type']), "N/A")
            ipv6_url = next((s['url'] for s in streams if 'ipv6' in s['source_type']), "N/A")
            
            v4_link = f"[Link]({ipv4_url})" if ipv4_url != "N/A" else "Unavailable"
            v6_link = f"[Link]({ipv6_url})" if ipv6_url != "N/A" else "Unavailable"
            
            md_content += f"| {name} | {v4_link} | {v6_link} |\n"

    with open("cctv_official.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("Generated cctv_ipv4.m3u, cctv_ipv6.m3u, cctv_full.m3u, cctv_official.md")

if __name__ == "__main__":
    main()
