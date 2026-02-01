"""
Starmap - GitHub Stars Sync Script
Fetches starred repositories and generates markdown + Supermemory integration
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
import argparse
from dotenv import load_dotenv


class GitHubClient:
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3.star+json"
        }

    def fetch_starred_repos(self) -> List[Dict]:
        """Fetch all starred repositories with pagination"""
        all_repos = []
        page = 1
        per_page = 100

        print(f"[{datetime.utcnow().isoformat()}] Fetching starred repos for @{self.username}...")

        while True:
            url = f"{self.base_url}/users/{self.username}/starred"
            params = {"page": page, "per_page": per_page}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = response.json()
            if not repos:
                break

            # Extract relevant metadata
            for item in repos:
                repo = item if not isinstance(item, dict) or 'repo' not in item else item['repo']
                starred_at = item.get('starred_at', '') if isinstance(item, dict) and 'starred_at' in item else ''

                all_repos.append({
                    "name": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "url": repo.get("html_url", ""),
                    "language": repo.get("language", "Unknown"),
                    "topics": repo.get("topics", []),
                    "stars": repo.get("stargazers_count", 0),
                    "last_updated": repo.get("updated_at", ""),
                    "starred_at": starred_at,
                    "homepage": repo.get("homepage", "")
                })

            print(f"  Fetched page {page} ({len(repos)} repos)...")
            page += 1

            # Break if less than per_page (last page)
            if len(repos) < per_page:
                break

        print(f"✅ Total starred repos: {len(all_repos)}")
        return all_repos


class SupermemoryClient:
    def __init__(self, api_key: str, api_url: str = "https://api.supermemory.ai/v1"):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def add_memory(self, content: str, metadata: Dict) -> bool:
        """Add a memory to Supermemory"""
        try:
            payload = {
                "content": content,
                "metadata": metadata
            }
            response = requests.post(
                f"{self.api_url}/memories",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"  ⚠️ Supermemory error: {e}")
            return False

    def sync_repos(self, repos: List[Dict]) -> int:
        """Sync all repos to Supermemory"""
        if not self.api_key:
            print("⚠️ Supermemory API key not provided, skipping sync")
            return 0

        print(f"[{datetime.utcnow().isoformat()}] Syncing {len(repos)} repos to Supermemory...")
        success_count = 0

        for repo in repos:
            content = f"""Repository: {repo['name']}
Description: {repo['description'] or 'No description'}
Language: {repo['language']}
Topics: {', '.join(repo['topics']) if repo['topics'] else 'None'}
Stars: {repo['stars']}
URL: {repo['url']}
"""
            metadata = {
                "type": "github_star",
                "repo_name": repo['name'],
                "language": repo['language'],
                "stars": repo['stars'],
                "url": repo['url']
            }

            if self.add_memory(content, metadata):
                success_count += 1

        print(f"✅ Synced {success_count}/{len(repos)} repos to Supermemory")
        return success_count


def generate_markdown(repos: List[Dict]) -> str:
    """Generate markdown file content"""
    # Sort chronologically (most recently starred first)
    repos.sort(key=lambda x: x.get('starred_at', ''), reverse=True)

    md_content = f"""# 🗺️ My GitHub Stars

> Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
> Total repositories: {len(repos)}

---

"""

    for repo in repos:
        # Format topics
        topics_str = ""
        if repo['topics']:
            topics_str = " · ".join([f"`{t}`" for t in repo['topics'][:5]])

        # Format language badge
        lang_badge = f"![{repo['language']}](https://img.shields.io/badge/-{repo['language'].replace(' ', '%20')}-grey)" if repo['language'] != "Unknown" else ""

        # Add repo entry
        md_content += f"""## [{repo['name']}]({repo['url']})

{repo['description'] or '_No description provided_'}

{lang_badge} ⭐ {repo['stars']} stars

{topics_str}

---

"""

    return md_content


def commit_to_github(owner: str, repo: str, branch: str, token: str, markdown_content: str):
    """Commit markdown file to GitHub repository"""
    print(f"[{datetime.utcnow().isoformat()}] Committing to GitHub...")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get current file SHA (if exists)
    file_path = "starred-repos.md"
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    try:
        response = requests.get(url, headers=headers, params={"ref": branch})
        if response.status_code == 200:
            sha = response.json().get("sha")
        else:
            sha = None
    except:
        sha = None

    # Create/update file
    payload = {
        "message": f"Update starred repos - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "content": requests.utils.quote(markdown_content.encode('utf-8')).replace('%', ''),
        "branch": branch
    }

    if sha:
        payload["sha"] = sha

    # Base64 encode content
    import base64
    payload["content"] = base64.b64encode(markdown_content.encode('utf-8')).decode('utf-8')

    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()

    print(f"✅ Committed to {owner}/{repo}/{branch}/{file_path}")


def main():
    parser = argparse.ArgumentParser(description="Sync GitHub stars to markdown and Supermemory")
    parser.add_argument("--config", default=".env", help="Path to .env config file")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv(args.config)

    # Required config
    github_username = os.getenv("GITHUB_USERNAME")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_username or not github_token:
        raise ValueError("GITHUB_USERNAME and GITHUB_TOKEN are required in .env")

    # Optional config
    supermemory_api_key = os.getenv("SUPERMEMORY_API_KEY")
    supermemory_api_url = os.getenv("SUPERMEMORY_API_URL", "https://api.supermemory.ai/v1")

    target_repo_owner = os.getenv("TARGET_REPO_OWNER", github_username)
    target_repo_name = os.getenv("TARGET_REPO_NAME", "starmap")
    target_branch = os.getenv("TARGET_BRANCH", "main")

    # Initialize clients
    github_client = GitHubClient(github_username, github_token)

    # Fetch starred repos
    repos = github_client.fetch_starred_repos()

    if not repos:
        print("⚠️ No starred repositories found")
        return

    # Generate markdown
    markdown_content = generate_markdown(repos)

    # Save locally
    with open("starred-repos.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"✅ Saved to starred-repos.md")

    # Sync to Supermemory (if configured)
    if supermemory_api_key:
        supermemory_client = SupermemoryClient(supermemory_api_key, supermemory_api_url)
        supermemory_client.sync_repos(repos)

    # Commit to GitHub
    try:
        commit_to_github(target_repo_owner, target_repo_name, target_branch, github_token, markdown_content)
    except Exception as e:
        print(f"⚠️ Failed to commit to GitHub: {e}")

    print(f"\n🎉 Sync complete!")
    print(f"Raw URL: https://raw.githubusercontent.com/{target_repo_owner}/{target_repo_name}/{target_branch}/starred-repos.md")


if __name__ == "__main__":
    main()
