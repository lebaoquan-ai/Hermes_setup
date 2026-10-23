#!/home/lebaoquan/.local/share/pipx/venvs/hermes-agent/bin/python
"""
Social & News Reader MCP Server
Provides structured tools for Hacker News, Reddit, and RSS feeds via stdio JSON-RPC.
Zero dependencies — uses only Python standard library.
"""

import sys
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 HermesAgent/1.0"

def fetch_json(url: str, timeout: int = 10) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="ignore"))

def get_hacker_news(category: str = "top", limit: int = 10) -> str:
    limit = min(max(1, limit), 25)
    endpoint = {
        "top": "topstories",
        "best": "beststories",
        "new": "newstories"
    }.get(category, "topstories")

    ids_url = f"https://hacker-news.firebaseio.com/v0/{endpoint}.json"
    ids = fetch_json(ids_url)[:limit]

    stories: List[Dict[str, Any]] = []
    for item_id in ids:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        try:
            item = fetch_json(item_url, timeout=5)
            if item:
                stories.append({
                    "title": item.get("title", "No title"),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                    "score": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "by": item.get("by", "unknown"),
                    "id": item_id
                })
        except Exception:
            continue

    return json.dumps({"source": "Hacker News", "category": category, "count": len(stories), "stories": stories}, indent=2)

def get_reddit_posts(subreddit: str, category: str = "hot", limit: int = 10) -> str:
    sub = subreddit.strip().replace("r/", "")
    limit = min(max(1, limit), 25)
    
    rss_url = f"https://www.reddit.com/r/{sub}/.rss?limit={limit}"
    req = urllib.request.Request(rss_url, headers={"User-Agent": "curl/8.10.1"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()

        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        posts = []
        for entry in root.findall("atom:entry", ns)[:limit]:
            title = entry.findtext("atom:title", "", ns)
            link_el = entry.find("atom:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            author = entry.findtext("atom:author/atom:name", "", ns)
            updated = entry.findtext("atom:updated", "", ns)
            
            posts.append({
                "title": title.strip() if title else "",
                "author": author.strip() if author else "",
                "url": link.strip() if link else "",
                "updated": updated.strip() if updated else ""
            })

        return json.dumps({"source": f"Reddit (r/{sub})", "count": len(posts), "posts": posts}, indent=2)
    except Exception as e:
        return json.dumps({"source": f"Reddit (r/{sub})", "error": f"Failed to retrieve feed: {str(e)}", "posts": []}, indent=2)

def read_rss_feed(url: str, limit: int = 5) -> str:
    limit = min(max(1, limit), 20)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    items = []

    # Handle standard RSS 2.0
    for item in root.findall(".//item")[:limit]:
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        description = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")
        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "published": pub_date.strip(),
            "summary": description.strip()[:300] if description else ""
        })

    # Handle Atom feeds if no RSS items found
    if not items:
        # Atom namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns)[:limit]:
            title = entry.findtext("atom:title", "", ns)
            link_el = entry.find("atom:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            summary = entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns)
            updated = entry.findtext("atom:updated", "", ns)
            items.append({
                "title": title.strip(),
                "link": link.strip(),
                "published": updated.strip(),
                "summary": summary.strip()[:300] if summary else ""
            })

    return json.dumps({"source": "RSS/Atom", "feed_url": url, "count": len(items), "items": items}, indent=2)

TOOLS = [
    {
        "name": "get_hacker_news",
        "description": "Fetch top, best, or new tech discussions and stories from Hacker News.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["top", "best", "new"],
                    "description": "The category of stories to retrieve.",
                    "default": "top"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of stories (1 to 25).",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_reddit_posts",
        "description": "Fetch trending, hot, or new discussions from any subreddit (e.g. r/archlinux, r/localllama, r/technology).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subreddit": {
                    "type": "string",
                    "description": "Subreddit name without 'r/' (e.g. 'archlinux' or 'technology')."
                },
                "category": {
                    "type": "string",
                    "enum": ["hot", "new", "top", "rising"],
                    "description": "Feed sorting category.",
                    "default": "hot"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of posts to fetch (1 to 25).",
                    "default": 10
                }
            },
            "required": ["subreddit"]
        }
    },
    {
        "name": "read_rss_feed",
        "description": "Fetch and extract recent article summaries from any RSS or Atom feed URL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full RSS/Atom feed URL."
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of articles to return (1 to 20).",
                    "default": 5
                }
            },
            "required": ["url"]
        }
    }
]

def handle_rpc(line: str) -> None:
    try:
        msg = json.loads(line)
    except Exception:
        return

    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "news-reader",
                    "version": "1.0.0"
                }
            }
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
        return

    if method == "notifications/initialized":
        return

    if method == "tools/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS
            }
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
        return

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "get_hacker_news":
                result = get_hacker_news(args.get("category", "top"), args.get("limit", 10))
            elif tool_name == "get_reddit_posts":
                result = get_reddit_posts(args.get("subreddit", "technology"), args.get("category", "hot"), args.get("limit", 10))
            elif tool_name == "read_rss_feed":
                result = read_rss_feed(args.get("url", ""), args.get("limit", 5))
            else:
                result = f"Error: Unknown tool '{tool_name}'"
        except Exception as e:
            result = f"Error executing {tool_name}: {str(e)}"

        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
        return

    # Default fallback for unrecognized methods
    if msg_id is not None:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found"
            }
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
