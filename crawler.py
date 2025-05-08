#!/usr/bin/env python3

"""
Website Crawler Tool

Usage Examples:
1. Crawl a site and store the results:
   python crawler.py --crawl https://example.com

2. Visualize from a stored graph:
   python crawler.py --map

3. Export to Excel from a stored graph:
   python crawler.py --excel

4. Do everything:
   python crawler.py --crawl https://example.com --map --excel

Dependencies:
1. requests: For HTTP requests.      pip install requests
2. beautifulsoup4: For HTML parsing. pip install beautifulsoup4
3. lxml: For efficient HTML parsing. pip install lxml
4. networkx: For graph handling.     pip install networkx
5. matplotlib: For plotting graphs.  pip install matplotlib
6. pandas: For Excel export.         pip install pandas
7. openpyxl: Excel file writer.      pip install openpyxl
"""

import argparse
import os
import pickle
import random
import sys
import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

GRAPH_FILENAME = "sitemap_graph.pkl"
ERROR_LOG = "404_errors.txt"
EXCEL_FILE = "sitemap_export.xlsx"

IGNORED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')

def is_internal_link(link, base_url):
    return urlparse(link).netloc in ("", urlparse(base_url).netloc)

def normalize_url(url):
    return url.rstrip("/")

def extract_links(html_content, base_url):
    soup = BeautifulSoup(html_content, "lxml")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        full_url = urljoin(base_url, href).split("#")[0].rstrip("/")

        # Check for pagination (older posts) links, as seen in your HTML example
        if 'Older posts' in tag.get_text():
            links.add(full_url)

        # Exclude ignored file types (e.g., images, etc.)
        if full_url.lower().endswith(IGNORED_EXTENSIONS):
            continue

        links.add(full_url)

    return links

def crawl(start_url):
    graph = nx.DiGraph()
    visited = set()
    queue = deque([(normalize_url(start_url), [normalize_url(start_url)])])
    error_404s = []

    while queue:
        current_url, path = queue.popleft()
        print(f"Current Queue: {len(queue):04d} | Crawling: {current_url}")
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=5)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                error_404s.append((current_url, path))
            continue
        except requests.exceptions.RequestException:
            continue

        page_content = response.text
        links = extract_links(page_content, start_url)

        is_on_blog_post = (
            "/blog/" in current_url and
            "/blog/page/" not in current_url and
            not current_url.endswith("/blog")
        )

        for link in links:
            normalized_link = normalize_url(link)

            # Skip blog-to-blog post links inside a blog post (prevent loop)
            if is_on_blog_post and "/blog/" in normalized_link and "/blog/page/" not in normalized_link:
                continue

            if is_internal_link(normalized_link, start_url) and normalized_link not in visited:
                graph.add_edge(current_url, normalized_link)
                queue.append((normalized_link, path + [normalized_link]))

def visualize_graph(graph):
    labels = {node: urlparse(node).path or '/' for node in graph.nodes}
    edge_colors = [random.choice(['#1f78b4', '#33a02c', '#e31a1c', '#ff7f00']) for _ in graph.edges]

    plt.figure(figsize=(100, 75))
    pos = nx.spring_layout(graph, seed=42, k=10.0, iterations=3000)
    nx.draw_networkx(graph, pos, labels=labels, with_labels=True,
                     node_size=150, font_size=8, width=1.0,
                     edge_color=edge_colors)
    plt.axis('off')
    plt.title("Website Structure Graph")
    plt.show()

def write_to_excel(graph):
    edges = list(graph.edges())
    data = [{"Source": src, "Target": tgt} for src, tgt in edges]
    df = pd.DataFrame(data)
    df.to_excel(EXCEL_FILE, index=False)
    print(f"Excel file written to {EXCEL_FILE}")

def load_graph():
    if os.path.exists(GRAPH_FILENAME):
        with open(GRAPH_FILENAME, "rb") as f:
            return pickle.load(f)
    print("No existing graph found. Run --crawl first.")
    return None

def main():
    parser = argparse.ArgumentParser(description="Website Crawler with Map and Excel Export")
    parser.add_argument("--crawl", metavar="URL", help="Crawl the given website URL.")
    parser.add_argument("--map", action="store_true", help="Visualize the graph.")
    parser.add_argument("--excel", action="store_true", help="Export graph to Excel.")
    args = parser.parse_args()

    graph = None

    if args.crawl:
        graph = crawl(args.crawl)
    elif args.map or args.excel:
        graph = load_graph()

    if graph:
        if args.map:
            visualize_graph(graph)
        if args.excel:
            write_to_excel(graph)

    print("")             # blank line
    sys.stdout.flush()    # flush all output
    input("Press Enter to exit...")  # wait for user to hit Enter

if __name__ == "__main__":
    main()