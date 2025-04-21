import requests
from bs4 import BeautifulSoup
import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt

# Dependencies:
# - requests: To make HTTP requests to fetch HTML content.
# - beautifulsoup4: To parse and extract links from the HTML content.
# - networkx: To create and visualize the website's crawl as a graph (tree).
# - matplotlib: To visualize the graph as a tree.
# 
# You can install these dependencies using pip:
# pip install requests beautifulsoup4 networkx matplotlib

# Function to fetch HTML content of a URL
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            print(f"Broken link: {url} - 404 Client Error: Not Found")
        else:
            print(f"Error fetching {url}: {e}")
        return None

# Function to extract links from the HTML content
def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # Only add internal links that belong to the base domain
        if link.startswith('http'):
            if base_url in link:  # Check if the link belongs to the base domain
                links.add(link)
        elif link.startswith('/'):
            links.add(base_url + link)  # Handle relative links
    return links

# Function to generate sitemap and capture the shortest depth to each page
def generate_sitemap_with_depth(start_url, base_url, max_depth=10):
    visited = set()
    to_visit = [(start_url, 0)]  # Store URL and its depth
    graph = nx.DiGraph()  # Directed graph to represent the tree structure

    graph.add_node(start_url, depth=0)  # Add the homepage as the root node

    while to_visit:
        url, depth = to_visit.pop(0)
        if url not in visited and depth <= max_depth:
            visited.add(url)
            html = fetch_html(url)
            if html:
                links = extract_links(html, base_url)
                for link in links:
                    if link not in visited:
                        graph.add_node(link, depth=depth + 1)  # Add child node with incremented depth
                        graph.add_edge(url, link)  # Add edge from parent to child (depth relationship)
                        to_visit.append((link, depth + 1))

    return graph

# Function to visualize the graph (tree)
def visualize_graph(graph):
    pos = nx.spring_layout(graph, seed=42)  # Layout for nodes
    depths = nx.get_node_attributes(graph, 'depth')  # Get the depth of each node

    # Set node color based on depth (darker color = deeper node)
    node_colors = [depths[node] for node in graph.nodes()]
    
    plt.figure(figsize=(12, 12))
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color=node_colors, cmap=plt.cm.Blues, font_size=8)
    plt.title("Website Crawl Depth Tree")
    plt.show()

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Crawl a website to generate a sitemap or search for a phrase.")
    parser.add_argument('start_url', help="The URL to start crawling from (e.g., https://www.distek.com).")
    parser.add_argument('--max_depth', type=int, default=10, help="Maximum depth to crawl.")
    parser.add_argument('--output', help="Output file to save the results (optional).", default=None)
    parser.add_argument('--sitemap', action='store_true', help="Flag to generate a sitemap.")
    
    args = parser.parse_args()

    # Check whether to generate a sitemap
    base_url = args.start_url.rstrip('/')
    if args.sitemap:
        print("Generating sitemap with depth visualization...")
        graph = generate_sitemap_with_depth(args.start_url, base_url, args.max_depth)
        
        # Visualize the graph (tree)
        visualize_graph(graph)
        
        if args.output:
            with open(args.output, 'w') as f:
                for node in graph.nodes():
                    f.write(f"{node} (Depth: {graph.nodes[node]['depth']})\n")
        else:
            print("Sitemap generation complete.")

if __name__ == '__main__':
    main()
