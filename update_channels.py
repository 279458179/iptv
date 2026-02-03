import requests
import datetime
import os
import concurrent.futures
import time

def check_stream_url(url, timeout=2):
    """
    Verifies if a stream URL is accessible and responsive.
    Returns (is_valid, response_time)
    """
    try:
        start_time = time.time()
        # Fake a browser user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Use stream=True to avoid downloading the whole file, just headers and start
        # Some servers don't support HEAD properly for m3u8, so GET with stream is safer but slower.
        # Let's try HEAD first, if 405/404 then maybe invalid. 
        # Actually for IPTV, usually HEAD works or GET with stream and close immediately.
        with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
            if r.status_code in [200, 206, 302]:
                return True, time.time() - start_time
            return False, 0
    except:
        return False, 0

def main():
    # Sources configuration - STRICTLY IPv4
    # Prioritizing verified aggregators from search results
    sources = [
        {
            "name": "Guovin IPv4",
            "url": "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
            "type": "ipv4"
        },
        {
            "name": "MyIPTV IPv4 (Suxuang)",
            "url": "https://raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u",
            "type": "ipv4"
        },
        {
            "name": "YueChan Live",
            "url": "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
            "type": "ipv4"
        }
    ]

    target_channels = [
        "CCTV-1", "CCTV-2", "CCTV-3", "CCTV-4", "CCTV-5", "CCTV-5+", 
        "CCTV-6", "CCTV-7", "CCTV-8", "CCTV-9", "CCTV-10", "CCTV-11", 
        "CCTV-12", "CCTV-13", "CCTV-14", "CCTV-15", "CCTV-16", 
        "CCTV-4K", "CCTV-8K"
    ]

    # Temporary storage: { "CCTV-1": [ {url, speed, name}, ... ] }
    candidates = {k: [] for k in target_channels}

    print("Step 1: Fetching and parsing playlists...")
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
                    channel_name_raw = line.split(',')[-1].strip()
                    
                    # Normalize checks
                    is_target = False
                    normalized_name = ""
                    upper_name = channel_name_raw.upper()
                    
                    for target in target_channels:
                        # Exact match start logic
                        if upper_name.startswith(target):
                            suffix = upper_name[len(target):]
                            if suffix and suffix[0].isdigit():
                                continue # Avoid CCTV-10 matching CCTV-1
                            
                            is_target = True
                            normalized_name = target
                            break
                        
                    if is_target and i + 1 < len(lines):
                        url = lines[i+1].strip()
                        if url and not url.startswith("#"):
                            # Filter out IPv6 IPs
                            if "[" in url and "]" in url and ":" in url:
                                i += 1
                                continue
                            
                            candidates[normalized_name].append({
                                "url": url,
                                "original_name": channel_name_raw,
                                "line_info": line,
                                "source_name": source['name']
                            })
                i += 1
        except Exception as e:
            print(f"Error processing {source['name']}: {e}")

    print("Step 2: Validating streams (this may take a minute)...")
    
    final_channels = []
    
    # Process each channel's candidates
    for channel in target_channels:
        links = candidates[channel]
        if not links:
            continue
            
        print(f"Validating {len(links)} links for {channel}...")
        
        # Use ThreadPool to check links in parallel
        valid_links = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_link = {executor.submit(check_stream_url, link['url']): link for link in links}
            for future in concurrent.futures.as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    is_valid, speed = future.result()
                    if is_valid:
                        link['speed'] = speed
                        valid_links.append(link)
                except Exception as exc:
                    pass
        
        # Sort by speed (fastest first) and keep top 10
        valid_links.sort(key=lambda x: x['speed'])
        selected_links = valid_links[:10]
        
        print(f"  -> Found {len(valid_links)} working links. Keeping best {len(selected_links)}.")
        
        for link in selected_links:
            final_channels.append({
                "name": channel,
                "original_name": link['original_name'],
                "url": link['url'],
                "speed": link['speed'],
                "source_name": link['source_name'],
                "line_info": link['line_info']
            })

    # Generate M3U
    header = '#EXTM3U\n'
    
    # CCTV IPv4 List
    content_ipv4 = header
    for ch in final_channels:
        # Update title to include speed info for debugging
        # e.g. CCTV-1 [0.5s]
        speed_ms = int(ch['speed'] * 1000)
        # Use the original EXTINF line but maybe modify the name? 
        # Let's just reconstruct a clean EXTINF line
        # #EXTINF:-1 tvg-id="cctv1" tvg-name="CCTV-1" tvg-logo="https://live.fanmingming.cn/tv/logo/cctv1.png" group-title="CCTV",CCTV-1
        # Since we don't have all metadata, let's try to preserve original line or create a standard one
        
        # Simplified reconstruction for better compatibility
        # We use the normalized name for the group/id to be clean
        clean_name = ch['name']
        logo_name = clean_name.replace("-", "").lower() # cctv1
        logo_url = f"https://live.fanmingming.cn/tv/logo/{logo_name}.png"
        
        line = f'#EXTINF:-1 tvg-id="{logo_name}" tvg-name="{clean_name}" tvg-logo="{logo_url}" group-title="央视频道",{clean_name} [{speed_ms}ms]\n{ch["url"]}\n'
        content_ipv4 += line

    with open("cctv_ipv4.m3u", "w", encoding="utf-8") as f:
        f.write(content_ipv4)
    
    # Also overwrite cctv_full.m3u with this working list
    with open("cctv_full.m3u", "w", encoding="utf-8") as f:
        f.write(content_ipv4)

    # Generate MD
    md_content = "# CCTV 频道列表 (IPv4 Verified)\n\n"
    md_content += f"更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "| 频道 | 响应时间 | 链接 |\n"
    md_content += "| --- | --- | --- |\n"
    
    # Group by channel name for cleaner table
    grouped = {}
    for ch in final_channels:
        if ch['name'] not in grouped:
            grouped[ch['name']] = []
        grouped[ch['name']].append(ch)
        
    for ch_name in target_channels:
        if ch_name in grouped:
            # Take top 3
            for item in grouped[ch_name][:3]:
                 speed_ms = int(item['speed'] * 1000)
                 md_content += f"| {ch_name} | {speed_ms}ms | [点击播放]({item['url']}) |\n"

    with open("cctv_official.md", "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"Generated cctv_ipv4.m3u, cctv_full.m3u, and cctv_official.md with {len(final_channels)} verified channels.")

if __name__ == "__main__":
    main()
