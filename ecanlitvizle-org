import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
from html import unescape
from typing import Optional, Dict, List
from urllib.parse import urlparse

headers = {
    "Referer": "https://tv.ecanlitvizle.org/"
}

WEB_URL = "https://tv.ecanlitvizle.org/"
FILE_NAME = "ecanlitvizle-org"
DOMAIN = "ecanlitvizle.org"

GITHUB_USER = os.getenv("GITHUB_USER", "UzunMuhalefet")
GITHUB_REPO = os.getenv("GITHUB_REPO", "streams")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}"

def get_ecanlitv():
    pattern = '"embedUrl": "(.*?)"'
    url = "https://tv.ecanlitvizle.org/"
    r = requests.get(url)
    kanallar = []
    soup = BeautifulSoup(r.content, "html.parser")
    kanal_liste = soup.find("ul", class_="kanallar").find_all("li")
    for kanal in kanal_liste:
        temp_kanal = {
            "name": kanal.find("a")["title"],
            "img": kanal.find("img")["src"],
            "param": ""
        }
        link = kanal.find("a")["href"]
        name = kanal.find("a")["title"]
        img = kanal.find("img")["src"]
        r2 = requests.get(link)
        match = re.search(pattern, r2.text)
        if match:
            embed_url = match.group(1).replace('\\/', '/').split("=")[-1]
            temp_kanal["param"] = embed_url
            print(embed_url)
        kanallar.append(temp_kanal)
    pages = soup.find("div", attrs={"id": "navigation"}).find_all("a")
    for page in pages:
        page_link = page["href"]
        print(page_link)
        r3 = requests.get(page_link)
        soup3 = BeautifulSoup(r3.content, "html.parser")
        kanal_liste3 = soup3.find("ul", class_="kanallar").find_all("li")
        for kanal3 in kanal_liste3:
            temp_kanal3 = {
                "name": kanal3.find("a")["title"],
                "img": kanal3.find("img")["src"],
                "param": ""
            }
            link3 = kanal3.find("a")["href"]
            name3 = kanal3.find("a")["title"]
            img3 = kanal3.find("img")["src"]
            r4 = requests.get(link3)
            match3 = re.search(pattern, r4.text)
            if match3:
                embed_url3 = match3.group(1).replace('\\/', '/').split("=")[-1]
                temp_kanal3["param"] = embed_url3
                print(embed_url3)
            kanallar.append(temp_kanal3)

    return kanallar

def decode_video_url(encrypted_string: str) -> Optional[str]:
    """
    Decode an encrypted video URL.

    Args:
        encrypted_string: The encrypted string in format: "position|delimiter|encrypted_url"

    Returns:
        The decoded URL string, or None if decoding fails
    """
    # Split by delimiter
    delimiter = 'Äx|Xf|x'
    parts = encrypted_string.split(delimiter)

    if len(parts) < 2:
        return None

    # First part is the starting position
    try:
        starting_position = int(parts[0])
    except (ValueError, IndexError):
        return None

    # Second part is the encrypted URL
    encrypted_url = parts[1]

    # Cipher alphabet (special characters used for encoding)
    cipher_alphabet = [
        '€', '$', 'Ă', 'Ä', 'Ë', 'Ģ', 'Ḩ', 'Ķ', 'Ḽ', 'Ņ',
        'Ň', 'Š', 'Ț', 'Ž', 'Ә', 'Є', 'Б', 'Җ', 'Ч', 'Ж',
        'Д', 'Ӡ', 'Ф', 'Ғ', 'Ӷ', 'Ы', 'И', 'К', 'Љ', 'Ө',
        'Ў', 'Њ', 'Һ', 'Г', 'Ş'
    ]

    # URL characters (actual characters in the decoded URL)
    url_chars = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '.', '&', '=', 'w', '?', 'c', 'o', 'm', 'a', 'f',
        'l', 'i', 'h', 't', 's', ':', '/', 'r', 'e', 'd',
        'n', 'k', 'p', '_', '-'
    ]

    # Start decoding
    position = starting_position
    decoded_url = encrypted_url

    # Iterate through each URL character position
    for i in range(len(url_chars)):
        # Wrap around if position exceeds cipher alphabet length
        if position >= len(cipher_alphabet):
            position = 0

        # Replace cipher character with URL character
        cipher_char = cipher_alphabet[position]
        url_char = url_chars[i]
        decoded_url = decoded_url.replace(cipher_char, url_char)

        # Move to next position in cipher alphabet
        position += 1

    return decoded_url


def extract_file_from_html(html: str) -> Optional[str]:
    """
    Extract the file parameter from HTML content.

    Args:
        html: The HTML content containing the file parameter

    Returns:
        The extracted file parameter value, or None if not found
    """
    # Decode HTML entities first
    html = unescape(html)

    # Try multiple patterns to find the file parameter
    patterns = [
        r"file\s*:\s*['\"]([^'\"]+)['\"]",           # file: 'value'
        r"file\s*:\s*&#039;([^&#039;]+)&#039;",      # file: &#039;value&#039;
        r"file\s*=\s*['\"]([^'\"]+)['\"]",           # file= 'value'
        r"'file'\s*:\s*['\"]([^'\"]+)['\"]",         # 'file': 'value'
        r'"file"\s*:\s*["\']([^"\']+)["\']',         # "file": "value"
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_quality_options(html: str) -> Dict[str, str]:
    """
    Extract quality options from HTML content.

    Args:
        html: The HTML content containing quality options

    Returns:
        Dictionary mapping resolution (e.g., "720", "480") to encoded URL
    """
    # Decode HTML entities first
    html = unescape(html)

    qualities = {}

    # Pattern to find quality options like kalite720, kalite480, kalite360
    # Looking for: changeVideo('encoded_string')
    pattern = r'["\']#kalite(\d+)["\'].*?changeVideo\(["\']([^"\']+)["\']\)'

    matches = re.findall(pattern, html, re.DOTALL)

    for match in matches:
        resolution = match[0]  # e.g., "720", "480", "360"
        encoded_url = match[1].strip()
        qualities[resolution] = encoded_url

    return qualities


def decode_all_qualities(qualities: Dict[str, str]) -> Dict[str, str]:
    """
    Decode all quality options.

    Args:
        qualities: Dictionary mapping resolution to encoded URL

    Returns:
        Dictionary mapping resolution to decoded URL
    """
    decoded_qualities = {}

    for resolution, encoded_url in qualities.items():
        if 'Äx|Xf|x' in encoded_url:
            decoded_url = decode_video_url(encoded_url)
            if decoded_url:
                decoded_qualities[resolution] = decoded_url
        else:
            decoded_qualities[resolution] = encoded_url

    return decoded_qualities


def select_best_quality(decoded_qualities: Dict[str, str],
                       preferred_quality: Optional[str] = None) -> tuple[str, str]:
    """
    Select the best quality from available options.

    Args:
        decoded_qualities: Dictionary mapping resolution to decoded URL
        preferred_quality: Optional preferred quality (e.g., "720")

    Returns:
        Tuple of (selected_quality, url)
    """
    if not decoded_qualities:
        return None, None

    # If preferred quality is specified and available, use it
    if preferred_quality and preferred_quality in decoded_qualities:
        return preferred_quality, decoded_qualities[preferred_quality]

    # Priority: 1080 > 720 > 480 > 360 > any other
    quality_priority = ['1080', '720', '480', '360']

    for quality in quality_priority:
        if quality in decoded_qualities:
            return quality, decoded_qualities[quality]

    # If none of the priority qualities exist, use the highest available
    sorted_qualities = sorted(decoded_qualities.keys(), key=lambda x: int(x), reverse=True)
    best_quality = sorted_qualities[0]
    return best_quality, decoded_qualities[best_quality]

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

def save_file(path, streams):
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
            bw_list = ["800000", "1200000", "1800000", "2500000", "3000000"]
            for i, url in enumerate(streams):
                f.write(f"#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH={bw_list[i]}\n")
                f.write(f"{url}\n")
        f.close()
        return "success"
    except Exception as e:
        print(f"Error creating file {path}: {e}")
        return ""


def get_stream_urls(param, yayin=1):
    if yayin > 3:
        return None
    url = f"https://tv.ecanlitvizle.org/embed.php?kanal={param}&yayin={yayin}"
    r = requests.get(url, headers=headers)
    html_content = r.text
    decoded_streams = []
    try:
        streams = extract_quality_options(html_content)
        decoded_streams = list(decode_all_qualities(streams).values())
        if not streams:
            stream = extract_file_from_html(html_content)
            decoded_stream = decode_video_url(stream) if stream and 'Äx|Xf|x' in stream else stream
            decoded_streams.append(decoded_stream)
        if DOMAIN in decoded_streams[0]:
            print(decoded_streams)
            return decoded_streams
        else:
            decoded_streams = get_stream_urls(param, yayin + 1)
            return decoded_streams
    except Exception as e:
        print(f"Error extracting streams: {e}")
        return None

if __name__ == "__main__":
    kanallar = get_ecanlitv()
    shutil.rmtree(FILE_NAME, ignore_errors=True)
    os.makedirs(FILE_NAME, exist_ok=True)
    os.makedirs("playlists", exist_ok=True)
    playlist_file_path = os.path.join("playlists", FILE_NAME + ".m3u")
    playlist_file = open(playlist_file_path, "w", encoding="utf-8")
    playlist_file.write("#EXTM3U\n")
    
    for kanal in kanallar:
        print(f"Channel: {kanal['name']}")
        stream_urls = get_stream_urls(kanal['param'])
        if stream_urls:
            channel_slug = urlparse(stream_urls[0]).path.split('/')[-1].split('.')[0].replace("-master", "")
            file_name = f"{channel_slug}.m3u8"
            file_path = os.path.join(FILE_NAME, file_name)
            result = save_file(file_path, stream_urls)
            if result == "success":
                github_url = f"{BASE_URL}/{FILE_NAME}/{file_name}"
                playlist_file.write(f'#EXTINF:-1 tvg-id="" tvg-name="{kanal["name"]}" tvg-logo="{kanal["img"]}",{kanal["name"]}\n')
                playlist_file.write(f"#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36\n")
                playlist_file.write(f"{github_url}\n")

    playlist_file.close()
    print("Playlist generation completed!")
