# News & Social Reader MCP Server

A standalone Model Context Protocol (MCP) server providing structured tools to fetch stories from Hacker News, discussions from Reddit, and articles from any RSS/Atom feed.

## Features
- **Zero External Dependencies**: Pure Python standard library (`urllib.request`, `json`, `xml.etree.ElementTree`).
- **No API Keys Required**: Uses public APIs and RSS/Atom feeds.
- **Stdio JSON-RPC**: Compatible with Hermes Agent, Claude Desktop, Cursor, and any other MCP host.

## Exposed Tools
1. `get_hacker_news(category="top", limit=10)`: Top, best, or new Hacker News stories.
2. `get_reddit_posts(subreddit="archlinux", limit=10)`: Discussions from any subreddit.
3. `read_rss_feed(url="...", limit=5)`: Summary of articles from any RSS/Atom feed.
