#!/usr/bin/env python3
import os
import re
import sys
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp")

visited = set()
total = 0

def download_image(img_url, path, count):
    global total

    try:
        response = requests.get(img_url, stream=True, timeout=10)
        response.raise_for_status()

        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            return
        
        filepath = os.path.join(path, filename)

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        total += 1
        return (1)
    except Exception as e:
        print(f"[!] Failed to download {img_url}: {e}")
        return (0)

def crawl(url, path, depth, max_depth, recursive):

    if url in visited:
        return
    visited.add(url)

    print(f"\n{'  ' * depth}[*] Crawling (depth {depth}): {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"{'  ' * depth}[!] Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    count = 0
    for img_tag in soup.find_all("img", src=True):
        img_url = urljoin(url, img_tag["src"])
        if img_url.lower().endswith(IMAGE_EXTENSIONS):
           count = count + download_image(img_url, path, count)

        if count:
            print(f"{'  ' * depth}[+] Downloaded {count} image(s) from {url}")

    print(f"\n-> Total image downloaded {count}")

    if recursive and depth < max_depth:
        for link_tag in soup.find_all("a", href=True):
            link_url = urljoin(url, link_tag["href"])
            if link_url.startswith(urlparse(url).scheme + "://"):
               crawl(link_url, path, depth + 1, max_depth, recursive)
    return (count)

def main():
    parser = argparse.ArgumentParser(description="Image Spider: Download images from a website")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("-r", action="store_true", help="Recursively download images")
    parser.add_argument("-l", type=int, default=5, help="Maximum depth level for recursion (default=5)")
    parser.add_argument("-p", default="./data/", help="Path to save downloaded files (default=./data/)")

    args = parser.parse_args()

    os.makedirs(args.p, exist_ok=True)
    crawl(args.url, args.p, 0, args.l, args.r)
    print(f"\n[✔] Finished. Total images downloaded: {total}")

if __name__ == "__main__":
    main()

