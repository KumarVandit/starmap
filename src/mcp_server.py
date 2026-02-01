"""
Starmap MCP Server
Model Context Protocol server for querying GitHub stars
"""

import os
import json
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv
import requests

load_dotenv()

# Initialize server
app = Server("starmap")

# Configuration
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SUPERMEMORY_API_KEY = os.getenv("SUPERMEMORY_API_KEY")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_stars",
            description="Search through your GitHub starred repositories using keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (language, topic, keyword in name/description)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_stars_by_language",
            description="Get starred repositories filtered by programming language",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Programming language (e.g., Python, JavaScript, Go)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["language"]
            }
        ),
        Tool(
            name="get_stars_by_topic",
            description="Get starred repositories filtered by topic/tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic/tag (e.g., machine-learning, api, docker)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_top_stars",
            description="Get most starred repositories from your stars",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top repos to return",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_recent_stars",
            description="Get recently starred repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent repos to return",
                        "default": 10
                    }
                }
            }
        )
    ]


def fetch_starred_repos():
    """Fetch starred repositories from GitHub"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.star+json"
    }

    all_repos = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/starred"
        response = requests.get(url, headers=headers, params={"page": page, "per_page": 100})
        response.raise_for_status()

        repos = response.json()
        if not repos:
            break

        for item in repos:
            repo = item if 'repo' not in item else item['repo']
            starred_at = item.get('starred_at', '') if 'starred_at' in item else ''

            all_repos.append({
                "name": repo.get("full_name", ""),
                "description": repo.get("description", ""),
                "url": repo.get("html_url", ""),
                "language": repo.get("language", "Unknown"),
                "topics": repo.get("topics", []),
                "stars": repo.get("stargazers_count", 0),
                "starred_at": starred_at
            })

        if len(repos) < 100:
            break
        page += 1

    return all_repos


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls"""

    repos = fetch_starred_repos()

    if name == "search_stars":
        query = arguments.get("query", "").lower()
        limit = arguments.get("limit", 10)

        filtered = [
            r for r in repos
            if query in r["name"].lower() or
               query in (r["description"] or "").lower() or
               query in r["language"].lower() or
               any(query in topic.lower() for topic in r["topics"])
        ][:limit]

        result = json.dumps(filtered, indent=2)
        return [TextContent(type="text", text=result)]

    elif name == "get_stars_by_language":
        language = arguments.get("language", "")
        limit = arguments.get("limit", 10)

        filtered = [
            r for r in repos
            if r["language"].lower() == language.lower()
        ][:limit]

        result = json.dumps(filtered, indent=2)
        return [TextContent(type="text", text=result)]

    elif name == "get_stars_by_topic":
        topic = arguments.get("topic", "").lower()
        limit = arguments.get("limit", 10)

        filtered = [
            r for r in repos
            if any(topic in t.lower() for t in r["topics"])
        ][:limit]

        result = json.dumps(filtered, indent=2)
        return [TextContent(type="text", text=result)]

    elif name == "get_top_stars":
        limit = arguments.get("limit", 10)
        sorted_repos = sorted(repos, key=lambda x: x["stars"], reverse=True)[:limit]

        result = json.dumps(sorted_repos, indent=2)
        return [TextContent(type="text", text=result)]

    elif name == "get_recent_stars":
        limit = arguments.get("limit", 10)
        sorted_repos = sorted(repos, key=lambda x: x.get("starred_at", ""), reverse=True)[:limit]

        result = json.dumps(sorted_repos, indent=2)
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text="Unknown tool")]


async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
