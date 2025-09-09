#!/usr/bin/env python3
import os
import time
import sys
import math
import concurrent.futures
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import urlopen, Request, URLError, HTTPError
from html.parser import HTMLParser

BASE_URL = "https://archive.org/download/sesame-street_202308/"
OUT_DIR = "download"
MAX_WORKERS = 4
RETRIES = 5
BACKOFF_SECS = 2.0
TIMEOUT = 60  # seconds
USER_AGENT = "Mozilla/5.0 (compatible; bulk-downloader/1.0; +https://archive.org)"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

def fetch(url, method="GET", headers=None):
    headers = headers or {}
    req = Request(url, method=method, headers={"User-Agent": USER_AGENT, **headers})
    return urlopen(req, timeout=TIMEOUT)

def list_ia_mp4_links(index_url):
    resp = fetch(index_url, "GET")
    html = resp.read().decode("utf-8", errors="ignore")
    parser = LinkParser()
    parser.feed(html)
    # Convert to absolute & filter *.ia.mp4
    out = []
    for href in parser.links:
        abs_url = urljoin(index_url, href)
        if abs_url.lower().endswith(".ia.mp4"):
            out.append(abs_url)
    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for u in out:
        if u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq

def get_remote_size(url):
    # HEAD to get Content-Length
    try:
        with fetch(url, "HEAD") as r:
            size = r.headers.get("Content-Length")
            return int(size) if size is not None else None
    except Exception:
        return None

def download_one(url):
    os.makedirs(OUT_DIR, exist_ok=True)
    # Choose filename from path and decode URL encoding
    fname = unquote(os.path.basename(urlparse(url).path))
    dest = os.path.join(OUT_DIR, fname)

    remote_size = get_remote_size(url)
    # Check if complete already
    if os.path.exists(dest) and remote_size is not None and os.path.getsize(dest) == remote_size:
        print(f"[SKIP] {fname} (already complete)")
        return dest

    attempt = 0
    while attempt < RETRIES:
        attempt += 1
        try:
            # Support resume
            headers = {}
            mode = "ab" if os.path.exists(dest) else "wb"
            local_size = os.path.getsize(dest) if os.path.exists(dest) else 0
            if local_size > 0:
                headers["Range"] = f"bytes={local_size}-"

            with fetch(url, "GET", headers=headers) as r:
                status = getattr(r, "status", r.getcode())
                if status in (206, 200):
                    # If server ignored Range and returned 200, and we had partial bytes, start over.
                    if status == 200 and local_size > 0:
                        print(f"[INFO] Server did not honor Range for {fname}. Restarting download.")
                        local_size = 0
                        mode = "wb"

                    with open(dest, mode) as f:
                        downloaded = local_size
                        chunk = 1024 * 256
                        while True:
                            data = r.read(chunk)
                            if not data:
                                break
                            f.write(data)
                            downloaded += len(data)
                            # Simple progress line
                            if remote_size:
                                pct = (downloaded / remote_size) * 100
                                sys.stdout.write(f"\r[DOWN] {fname} {downloaded}/{remote_size} bytes ({pct:5.1f}%)")
                            else:
                                sys.stdout.write(f"\r[DOWN] {fname} {downloaded} bytes")
                            sys.stdout.flush()
                    sys.stdout.write("\n")
                else:
                    raise HTTPError(url, status, f"HTTP {status}", hdrs=None, fp=None)

            # Verify size if known
            if remote_size is not None and os.path.getsize(dest) != remote_size:
                raise IOError(f"Incomplete download for {fname}: got {os.path.getsize(dest)} of {remote_size} bytes")

            print(f"[OK]   {fname}")
            return dest

        except (HTTPError, URLError, IOError) as e:
            wait = BACKOFF_SECS * (2 ** (attempt - 1))
            print(f"[WARN] {fname} attempt {attempt}/{RETRIES} failed: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    print(f"[FAIL] {fname} after {RETRIES} attempts")
    return None

def main():
    print(f"[INFO] Scanning index: {BASE_URL}")
    links = list_ia_mp4_links(BASE_URL)
    if not links:
        print("[INFO] No .ia.mp4 files found.")
        return

    print(f"[INFO] Found {len(links)} files:")
    for u in links:
        print("  -", os.path.basename(urlparse(u).path))

    print(f"[INFO] Downloading to: {os.path.abspath(OUT_DIR)}")
    # polite small stagger to avoid hammering
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(download_one, u) for u in links]
        for fut in concurrent.futures.as_completed(futures):
            _ = fut.result()

    print("[DONE] All tasks completed.")

if __name__ == "__main__":
    main()
