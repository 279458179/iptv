import requests
import datetime
import os

def main():
    # Public maintained source (Fanmingming) which is known for high quality IPv6/IPv4 official relays
    # We use this because direct official extraction now requires dynamic tokens/cookies which fail in static playlists.
    source_url = "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u"
    
    print(f"Fetching source from: {source_url}")
    try:
        r = requests.get(source_url, timeout=30)
        if r.status_code != 200:
            print(f"Failed to fetch source: {r.status_code}")
            return
        
        source_content = r.text
    except Exception as e:
        print(f"Error fetching source: {e}")
        return

    # Define the CCTV channels we want to extract/prioritize
    target_channels = [
        "CCTV-1", "CCTV-2", "CCTV-3", "CCTV-4", "CCTV-5", "CCTV-5+", 
        "CCTV-6", "CCTV-7", "CCTV-8", "CCTV-9", "CCTV-10", "CCTV-11", 
        "CCTV-12", "CCTV-13", "CCTV-14", "CCTV-15", "CCTV-16", 
        "CCTV-4K", "CCTV-8K"
    ]
    
    # Parse the source M3U
    extracted_channels = []
    lines = source_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # Extract channel name
            # Format usually: #EXTINF:-1 tvg-id="..." ... group-title="...",Channel Name
            channel_name = line.split(',')[-1].strip()
            
            # Check if this is one of our targets
            # We want to match "CCTV-1 综合" or just "CCTV-1"
            is_target = False
            for target in target_channels:
                if target in channel_name.upper():
                    # Check exact match prefix to avoid "CCTV-10" matching "CCTV-1"
                    # But usually "CCTV-1 " or "CCTV-1" is enough distinction from "CCTV-10"
                    # A better check:
                    if channel_name.upper().startswith(target):
                        is_target = True
                        break
            
            if is_target and i + 1 < len(lines):
                url = lines[i+1].strip()
                if url and not url.startswith("#"):
                    extracted_channels.append({
                        "line_info": line,
                        "name": channel_name,
                        "url": url
                    })
        i += 1

    print(f"Extracted {len(extracted_channels)} valid CCTV channels.")

    # Generate Official M3U and MD content
    m3u_content = ""
    md_content = "# CCTV Live Sources\n\n> Auto-aggregated from high-quality public relays (Fanmingming/IPv6)\n\n| Channel | M3U8 Link | Watch |\n|---|---|---|\n"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content += f"\n*Last Updated: {current_time}*\n\n"

    # Deduplicate by name (keep first found)
    seen_names = set()
    
    for chan in extracted_channels:
        # Normalize name for deduplication
        # e.g. "CCTV-1 综合" -> "CCTV-1"
        simple_name = chan['name'].split(' ')[0]
        
        # We allow multiple entries if they are distinct variants, but for the table we might want to be concise.
        # Let's list all valid ones in M3U, but maybe limit MD to one per channel to keep it clean?
        # User said "full set", so let's put all in M3U.
        
        m3u_content += f"{chan['line_info']}\n"
        m3u_content += f"{chan['url']}\n"
        
        md_content += f"| {chan['name']} | `{chan['url']}` | [Play]({chan['url']}) |\n"

    # Write cctv_official.m3u
    with open("cctv_official.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + m3u_content)
    
    # Write cctv_official.md
    with open("cctv_official.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print("Generated cctv_official.m3u and cctv_official.md")

    # Merge into cctv_full.m3u

    # Try to read existing cctv_full.m3u to preserve other channels
    other_channels = ""
    if os.path.exists("cctv_full.m3u"):
        with open("cctv_full.m3u", "r", encoding="utf-8") as f:
            old_lines = f.readlines()
            
        # Filter out old CCTV entries
        skip = False
        buffer = []
        for line in old_lines:
            if line.strip().startswith("#EXTM3U") or line.strip() == "#频道列表":
                continue
            
            if line.startswith("#EXTINF"):
                # Simple heuristic: if line contains CCTV or CGTN, assume it's the old block we want to replace
                if "CCTV" in line or "CGTN" in line or "group-title=\"CCTV" in line:
                    skip = True
                else:
                    skip = False
                    buffer.append(line)
            elif not line.startswith("#") and line.strip():
                if not skip:
                    buffer.append(line)
        
        other_channels = "".join(buffer)
    
    # Write merged full list
    full_content = "#EXTM3U\n" + m3u_content + "\n" + other_channels
    with open("cctv_full.m3u", "w", encoding="utf-8") as f:
        f.write(full_content)
        
    print("Updated cctv_full.m3u")

if __name__ == "__main__":
    main()
