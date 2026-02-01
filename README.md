# 🗺️ Starmap

> Your GitHub Stars Knowledge Base - Track, organize, and query your starred repositories with MCP integration and Supermemory

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔄 **Daily Auto-Sync** - Automatically fetch and update your starred repos
- 📝 **Markdown Generation** - Clean, chronological list of all your stars
- 🧠 **Supermemory Integration** - Semantic search and knowledge graph for your stars
- 🔌 **MCP Server** - Connect Cursor, Claude Desktop, and other AI tools
- 🐳 **Docker Support** - Run locally or in containers
- ⚙️ **Configurable** - Works for any GitHub user

## 🚀 Quick Start

### Option 1: Local Setup

```bash
# Clone the repository
git clone https://github.com/KumarVandit/starmap.git
cd starmap

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run once
python src/sync_stars.py

# Or schedule daily (add to crontab)
0 0 * * * cd /path/to/starmap && python src/sync_stars.py
```

### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: MCP Server (for Cursor/Claude)

Add to your MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` or Cursor config):

```json
{
  "mcpServers": {
    "starmap": {
      "command": "python",
      "args": ["/path/to/starmap/src/mcp_server.py"],
      "env": {
        "GITHUB_USERNAME": "your-github-username",
        "GITHUB_TOKEN": "your-github-token",
        "SUPERMEMORY_API_KEY": "your-supermemory-key"
      }
    }
  }
}
```

## 📦 What Gets Generated

1. **`starred-repos.md`** - Chronological markdown list
   - Repository name, description, language, topics, stars
   - Direct links to repos
   - Last updated timestamp
   - Accessible via raw GitHub URL

2. **Supermemory Integration**
   - Each repo pushed to Supermemory as a memory
   - Semantic search across your stars
   - Knowledge graph connections

## 🔧 Configuration

Create `.env` file:

```env
# Required
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-personal-access-token

# Optional - Supermemory Integration
SUPERMEMORY_API_KEY=your-supermemory-api-key
SUPERMEMORY_API_URL=https://api.supermemory.ai/v1

# Optional - Target Repository
TARGET_REPO_OWNER=your-github-username
TARGET_REPO_NAME=starmap
TARGET_BRANCH=main
```

### GitHub Token Permissions

Create a [Personal Access Token](https://github.com/settings/tokens) with:
- `repo` (if private repos)
- `public_repo` (for public repos only)
- `read:user` (to read starred repos)

### Supermemory API Key

1. Go to [Supermemory Console](https://console.supermemory.ai)
2. Create a new API key
3. Add to `.env` file

## 📖 Usage

### Fetch and Update Stars

```bash
# One-time sync
python src/sync_stars.py

# With custom config
python src/sync_stars.py --config /path/to/config.env
```

### MCP Server

Once configured in your AI tool:

```
# In Cursor or Claude
"Show me all my Python machine learning repos"
"Find repos related to API development"
"What are my most starred repositories?"
```

### Access the Markdown

Raw URL format:
```
https://raw.githubusercontent.com/YOUR_USERNAME/starmap/main/starred-repos.md
```

Use in Cursor:
```
# Add to your project's .cursor/prompts or reference directly
@https://raw.githubusercontent.com/YOUR_USERNAME/starmap/main/starred-repos.md
```

## 🏗️ Architecture

```
starmap/
├── src/
│   ├── sync_stars.py          # Main sync script
│   ├── mcp_server.py           # MCP server implementation
│   ├── supermemory_client.py   # Supermemory API client
│   └── github_client.py        # GitHub API client
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
└── starred-repos.md            # Generated output
```

## 🔄 How It Works

1. **Fetch Stars**: Queries GitHub API for all starred repositories
2. **Extract Metadata**: Name, description, language, topics, stars, last updated
3. **Generate Markdown**: Creates chronological list in `starred-repos.md`
4. **Push to Supermemory**: Sends each repo as a memory for semantic search
5. **Commit & Push**: Updates the repository with latest data
6. **MCP Server**: Exposes tools for AI assistants to query your stars

## 🛠️ Advanced

### Custom Markdown Template

Edit `src/sync_stars.py` and modify the `generate_markdown()` function.

### Different Organization Styles

```python
# In sync_stars.py, change sort_by parameter:
repos.sort(key=lambda x: x['starred_at'], reverse=True)  # Chronological (default)
repos.sort(key=lambda x: x['stargazers_count'], reverse=True)  # By stars
repos.sort(key=lambda x: x['language'])  # By language
```

### Filter Repos

```python
# Only include specific languages
filtered_repos = [r for r in repos if r['language'] in ['Python', 'JavaScript']]
```

## 🤝 Contributing

Contributions welcome! This repo is designed to be open-sourced.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- [Supermemory](https://github.com/supermemoryai/supermemory) - AI memory engine
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- Inspired by the need to organize 1000+ GitHub stars

## 📧 Support

- Issues: [GitHub Issues](https://github.com/KumarVandit/starmap/issues)
- Twitter: [@vaandeetttt](https://twitter.com/vaandeetttt)

---

**Made with ❤️ for developers drowning in GitHub stars**
