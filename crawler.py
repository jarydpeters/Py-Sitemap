#!/usr/bin/env python3

"""
Website Crawler & Visualizer

# Example usage:
# Crawl a website and generate a sitemap graph:
#   python crawler.py https://example.com

# Display the graph from a previous run (no crawling):
#   python crawler.py --display

# Dependencies:
# To run this script, you'll need to install the following Python libraries:
# 1. requests: For making HTTP requests.
#    Command: pip install requests
# 2. beautifulsoup4: For parsing HTML content.
#    Command: pip install beautifulsoup4
# 3. lxml: For an alternative and efficient HTML parser.
#    Command: pip install lxml
# 4. networkx: For managing and visualizing the website graph.
#    Command: pip install networkx
# 5. matplotlib: For visualizing the website structure as a graph.
#    Command: pip install matplotlib
# 6. scipy: Required for graph layout calculations in networkx
#    Command: pip install scipy
"""

import argparse
import os
import pickle
import re
from collections import deque, defaultdict
from urllib.parse import urljoin, urlparse

import matplotlib.pyplot as plt
import networkx as nx
import requests
from bs4 import BeautifulSoup

GRAPH_FILENAME = "sitemap_graph.pkl"
ERROR_LOG = "404_errors.txt"


def is_internal_link(link, base_url):
    return urlparse(link).netloc in ("", urlparse(base_url).netloc)


def extract_links(html_content, base_url):
    soup = BeautifulSoup(html_content, "lxml")
    links = set()
    for tag in soup.find_all("a", href=True):
        href = tag['href']
        full_url = urljoin(base_url, href)
        full_url = full_url.split("#")[0].rstrip("/")
        links.add(full_url)
    return links


def crawl(start_url):
    graph = nx.DiGraph()
    visited = set()
    queue = deque([(start_url, [start_url])])
    error_404s = []
    url_depths = {start_url: 0}

    while queue:
        current_url, path = queue.popleft()
        current_depth = len(path) - 1
        print(f"Depth: {current_depth}, Queue: {len(queue)}, Crawling: {current_url}")

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

        for link in links:
            # Skip links between blog posts to avoid crawling "Related Posts" shown on each blog,
            # which leads to redundant traversal of unrelated blogs and depth deflation.
            if "/blog/" in current_url and "/blog/" in link:
                continue

            if is_internal_link(link, start_url) and link not in visited:
                graph.add_edge(current_url, link)
                queue.append((link, path + [link]))
                url_depths[link] = current_depth + 1

    # Save graph
    with open(GRAPH_FILENAME, "wb") as f:
        pickle.dump(graph, f)

    # Save 404 errors
    if error_404s:
        with open(ERROR_LOG, "w", encoding="utf-8") as f:
            for url, path in error_404s:
                f.write(f"404: {url}\nPath: {' -> '.join(path)}\n\n")

    return graph


def visualize_graph(graph):
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(graph, seed=42)
    nx.draw_networkx_nodes(graph, pos, node_size=5000, node_color="skyblue")
    nx.draw_networkx_edges(graph, pos, arrows=True)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_weight='bold', font_color='black')

    plt.title("Website Sitemap")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Website Crawler and Visualizer")
    parser.add_argument("start_url", nargs="?", help="The URL to start crawling from.")
    parser.add_argument("--display", action="store_true", help="Only display the graph without crawling.")
    args = parser.parse_args()

    if args.display:
        if os.path.exists(GRAPH_FILENAME):
            with open(GRAPH_FILENAME, "rb") as f:
                graph = pickle.load(f)
            visualize_graph(graph)
        else:
            print("No graph file found. Run the crawler first.")
    elif args.start_url:
        graph = crawl(args.start_url)
        visualize_graph(graph)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
