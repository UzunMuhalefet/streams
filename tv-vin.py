import requests
from bs4 import BeautifulSoup
import re
import os
import shutil

# Get cookies from environment variables
LS_ACCOUNT_KEY = os.getenv("LS_ACCOUNT_KEY", "")
LS_ACCOUNT_NUM_KEY = os.getenv("LS_ACCOUNT_NUM_KEY", "")
LS_TOKEN_KEY = os.getenv("LS_TOKEN_KEY", "")

# GitHub repository configuration
GITHUB_USER = os.getenv("GITHUB_USER", "UzunMuhalefet")
GITHUB_REPO = os.getenv("GITHUB_REPO", "streams")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}"

headers = {
    "Cookie": f"LS_ACCOUNT_KEY={LS_ACCOUNT_KEY}; LS_ACCOUNT_NUM_KEY={LS_ACCOUNT_NUM_KEY}; LS_TOKEN_KEY={LS_TOKEN_KEY}",
    "Referer": "https://tv.vin/"
}

pattern = r'file:\s*[\'"]([^\'"]*\.m3u8[^\'"]*)[\'"]'
pattern2 = r'changeVideo\([\'"]([^\'"]*\.m3u8[^\'"]*)[\'"\)]'

def get_all_channels():
    url = "https://tv.vin/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    channels = []
    for item in soup.find_all("div", class_="channel-card"):
        temp_channel = {
            "channel_name": item.find("a").get("title"),
            "channel_url": item.find("a").get("href"),
            "channel_icon": item.find("img").get("src")
        }
        channels.append(temp_channel)
    return channels

def get_iframe_url(channel_url):
    response = requests.get(channel_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    iframe_tag = soup.find("iframe")
    if iframe_tag:
        return iframe_tag.get("src")
    return None

def extract_streaming_url(iframe_url, number=1):
    if number > 4:
        return None
    if number != 1:
        url_parts = iframe_url.split("/")
        iframe_url = "/".join(url_parts[:-1] + [str(number)])
    response = requests.get(iframe_url, headers=headers)
    matches = re.search(pattern, response.text)
    matches2 = re.findall(pattern2, response.text)
    streams = []
    if matches and matches2:
        for url in matches2:
            streams.append(url)
    elif matches:
        stream = matches.group(1)
        if "tv.vin" not in stream:
            stream = extract_streaming_url(iframe_url, number + 1)
        streams.append(stream)
    else:
        print("No stream found")
        return None
    return streams

def create_file(path, streams):
    try:
        if len(streams) == 1:
            url = streams[0]
            r = requests.get(url)
            if r.status_code != 200:
                print(f"Failed to fetch stream URL: {url}")
                return ""
            if "EXT-X-STREAM-INF" in r.text:
                lines = r.text.splitlines()
                f = open(path, "w", encoding="utf-8")
                for line in lines:
                    if line.startswith("#"):
                        f.write(f"{line}\n")
                    else:
                        if "http" not in line:
                            base_url = url.rsplit("/", 1)[0]
                            line = f"{base_url}/{line}"
                        f.write(f"{line}\n")
            else:
                f = open(path, "w", encoding="utf-8")
                f.write("#EXTM3U\n")
                f.write("#EXT-X-VERSION:3\n")
                f.write(f"#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000\n")
                f.write(f"{url}\n")
        elif len(streams) > 1:
            f = open(path, "w", encoding="utf-8")
            f.write("#EXTM3U\n")
            for url in streams:
                f.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=800000\n")
                f.write(f"{url}\n")
        f.close()
        return "success"

    except Exception as e:
        print(f"Error creating file {path}: {e}")
        return ""

if __name__ == "__main__":
    channels = get_all_channels()
    shutil.rmtree("tv-vin", ignore_errors=True)
    os.makedirs("tv-vin", exist_ok=True)
    os.makedirs("playlists", exist_ok=True)
    playlist_file_path = os.path.join("playlists", "tv-vin.m3u")
    playlist_file = open(playlist_file_path, "w", encoding="utf-8")
    playlist_file.write("#EXTM3U\n")
    
    for channel in channels:
        print(f"Channel: {channel['channel_name']}")
        iframe_url = get_iframe_url(channel['channel_url'])
        if iframe_url:
            streams = extract_streaming_url(iframe_url)
            if streams:
                channel_path = iframe_url.split("/")[-2]
                file_path = os.path.join("tv-vin", f"{channel_path}.m3u8")
                check = create_file(file_path, streams)
                if check != "":
                    # Use GitHub raw URL instead of direct stream URL
                    github_url = f"{BASE_URL}/tv-vin/{channel_path}.m3u8"
                    playlist_file.write(f"#EXTINF:-1 tvg-logo=\"{channel['channel_icon']}\",{channel['channel_name']}\n")
                    playlist_file.write(f"#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36\n")
                    playlist_file.write(f"{github_url}\n")
    
    playlist_file.close()
    print("Playlist generation completed!")
