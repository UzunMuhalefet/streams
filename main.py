import re
import requests
import sys
import json
import os
from urllib.parse import urljoin
from slugify import slugify
from tqdm import tqdm

def get_stream_url(url, pattern, method="GET", headers={}, body={}):
    if method == "GET":
        r = requests.get(url, headers=headers)
    elif method == "POST":
        r = requests.post(url, json=body, headers=headers)
    else:
        print(method, "is not supported or wrong.")
        return None
    results = re.findall(pattern, r.text)
    if len(results) > 0:
        return results[0]
    else:
        print("No result found in the response. \nCheck your regex pattern {} for {}".format(method, url))
        return None

def playlist_text(url):
    text = ""
    r = requests.get(url)
    if r.status_code == 200:
        for line in r.iter_lines():
            line = line.decode()
            if not line:
                continue
            if line[0] != "#":
                text = text + urljoin(url, str(line))
            else:
                text = str(text) + str(line)
            text += "\n"

        return text
    return ""



def main():
    config_file = open(sys.argv[1], "r", encoding="utf-8")
    config = json.load(config_file)
    for site in config:
        site_path = os.path.join(os.getcwd(), site["slug"])
        os.makedirs(site_path, exist_ok=True)
        for channel in tqdm(site["channels"]):
            channel_file_path = os.path.join(site_path, slugify(channel["name"].lower()) + ".m3u8")
            channel_url = site["url"]
            for variable in channel["variables"]:
                channel_url = channel_url.replace(variable["name"], variable["value"])
            stream_url = get_stream_url(channel_url, site["pattern"])
            if not stream_url:
                if os.path.isfile(channel_file_path):
                    os.remove(channel_file_path)
                continue
            if site["output_filter"] not in stream_url:
                if os.path.isfile(channel_file_path):
                    os.remove(channel_file_path)
                continue
            if site["mode"] == "variant":
                text = playlist_text(stream_url)
            elif site["mode"] == "master":
                text = "#EXTM3U\n##EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH={}\n{}".format(site["bandwidth"], stream_url)
            else:
                print("Wrong or missing playlist mode argument")
                text = ""
            if text:
                channel_file = open(channel_file_path, "w+")
                channel_file.write(text)
            else:
                if os.path.isfile(channel_file_path):
                    os.remove(channel_file_path)
                

if __name__=="__main__": 
    main() 
