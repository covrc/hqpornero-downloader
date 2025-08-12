import sys
import time
import re
import subprocess
import requests
import argparse
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from urllib.parse import urlparse, unquote

def get_cf_cookie(page_url):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    driver.get(page_url)
    time.sleep(7)
    cookies = driver.get_cookies()
    driver.quit()
    for c in cookies:
        if c["name"] == "cf_clearance":
            return c["value"]
    raise RuntimeError("cf_clearance not found!")

def btq(f):
    res = []
    if f & 1: res.append(360)
    if f & 2: res.append(480)
    if f & 4: res.append(720)
    if f & 8: res.append(1080)
    return res

def main():
    parser = argparse.ArgumentParser(description="hqpornero.com video downloader")
    parser.add_argument("url", help="Video URL")
    parser.add_argument("-F", "--list-formats", action="store_true", help="List available formats and exit")
    parser.add_argument("-f", "--format", type=int, choices=[360,480,720,1080], help="Select video quality")
    parser.add_argument("-o", "--output", help="Select output file name (Default: videoname_quality.mp4)")
    parser.add_argument("-r", "--requests", action="store_true", help="Download with requests (Wget not required)")
    args = parser.parse_args()

    start_url = args.url
    session = requests.Session()
    headers_index = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
    }

    print("[*] Downloading website:", start_url)
    r = session.get(start_url, headers=headers_index)
    r.raise_for_status()
    index_html = r.text

    iframe_match = re.search(r'<iframe[^>]+src="([^"]+xiaoshenke\.net/video/[^"]+)"', index_html)
    if not iframe_match:
        raise RuntimeError("iframe not found!")
    iframe_src = iframe_match.group(1)
    if iframe_src.startswith("//"):
        iframe_src = "https:" + iframe_src
    print("[*] iframe has found:", iframe_src)

    headers_iframe = {
        "User-Agent": headers_index["User-Agent"],
        "Referer": start_url
    }
    r = session.get(iframe_src, headers=headers_iframe)
    r.raise_for_status()
    iframe_html = r.text

    id_match = re.search(r'var id = "([^"]+)"\.split', iframe_html)
    quality_match = re.search(r'var quality = parseInt\("(\d+)"\)', iframe_html)

    if not id_match or not quality_match:
        raise RuntimeError("id or quality not found!")

    id_encoded = id_match.group(1)
    quality_int = int(quality_match.group(1))
    video_id = id_encoded[::-1]

    qualities = btq(quality_int)
    print("[*] Available formats:", qualities)

    if args.list_formats:
        return

    chosen_quality = args.format if args.format else max(qualities)
    if chosen_quality not in qualities:
        print(f"[!] Format ({chosen_quality}) is not available.")
        print(f"Available formats: {qualities}")
        sys.exit(1)

    base_host = "xiaoshenke.net"
    video_url = f"https://{base_host}/vid/{video_id}/{chosen_quality}"
    print(f"[*] Chosen format: {chosen_quality}")
    print("[*] Video URL:", video_url)

    cf_clearance = get_cf_cookie(f"https://{base_host}/")

    user_agent = headers_index["User-Agent"]
    referer = f"https://{base_host}/"

    if args.output:
        out_file = args.output
    else:
        path = urlparse(start_url).path
        filename = path.split("/")[-1]
        if filename.endswith(".html"):
            filename = filename[:-5]
        out_file = f"{filename}_{chosen_quality}.mp4"

    print(f"[*] Output filename: {out_file}")

    if args.requests:
        print("[*] [requests] Download is starting...")
        headers_dl = {
            "Referer": referer,
            "User-Agent": user_agent,
            "Cookie": f"cf_clearance={cf_clearance}"
        }
        with session.get(video_url, headers=headers_dl, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            block_size = 1024
            with open(out_file, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=out_file
            ) as bar:
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
    else:
        print("[*] [wget] Download is starting...")
        wget_cmd = [
            "wget",
            "--continue",
            "--header", f"Referer: {referer}",
            "--header", f"User-Agent: {user_agent}",
            "--header", f"Cookie: cf_clearance={cf_clearance}",
            video_url,
            "-O", out_file
        ]
        subprocess.run(wget_cmd)

if __name__ == "__main__":
    main()
