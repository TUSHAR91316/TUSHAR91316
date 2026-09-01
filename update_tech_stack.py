import os
import re
import sys
import requests
from typing import Dict, List, Set, Optional
from collections import defaultdict

# ==========================================
# Configuration & Constants
# ==========================================
GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "TUSHAR91316")
GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
README_PATH: str = "README.md"
API_URL: str = "https://api.github.com/users/{}/repos"

# Pre-compile regex for performance
MARKER_PATTERN = re.compile(
    r"(<!-- TECH-STACK:START -->)(.*?)(<!-- TECH-STACK:END -->)",
    re.DOTALL
)

CATEGORIES: Dict[str, Set[str]] = {
    "Languages": {
        "python", "c++", "c", "c#", "javascript", "typescript", "dart", "java", "kotlin", "swift", "go", "golang", "rust"
    },
    "Frontend": {
        "flutter", "react", "tailwindcss", "html", "css", "vue", "angular", "next.js", "nextjs", "bootstrap", "material-ui"
    },
    "Backend & Cloud": {
        "firebase", "docker", "docker-container", "nginx", "redis", "django", "flask", "fastapi", "node", "express", "aws", "gcp", "azure", "mongodb", "postgresql", "mysql", "vercel"
    },
    "AI & Machine Learning": {
        "tensorflow", "pytorch", "scikit-learn", "llm", "ai-agent", "pydantic-ai"
    },
    "Security & OS": {
        "linux", "git", "kali", "wireshark", "metasploit", "bash", "shell", "powershell", "nmap", "burp suite", "vpn", "onion-routing"
    }
}

BADGE_MAP: Dict[str, str] = {
    "python": "Python-3776AB?style=for-the-badge&logo=python&logoColor=white",
    "c++": "C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white",
    "c#": "C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white",
    "javascript": "JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black",
    "typescript": "TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white",
    "dart": "Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white",
    "java": "Java-ED8B00?style=for-the-badge&logo=java&logoColor=white",
    "kotlin": "Kotlin-0095D5?style=for-the-badge&logo=kotlin&logoColor=white",
    "go": "Go-00ADD8?style=for-the-badge&logo=go&logoColor=white",
    "golang": "Go-00ADD8?style=for-the-badge&logo=go&logoColor=white",
    "flutter": "Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white",
    "react": "React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB",
    "tailwindcss": "Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white",
    "html": "HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white",
    "nextjs": "Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white",
    "firebase": "Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black",
    "docker": "Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white",
    "docker-container": "Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white",
    "fastapi": "FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white",
    "vercel": "Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white",
    "nginx": "Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white",
    "redis": "Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white",
    "linux": "Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black",
    "git": "Git-F05032?style=for-the-badge&logo=git&logoColor=white",
    "kali": "Kali_Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white",
    "vpn": "VPN-4CAF50?style=for-the-badge&logo=openvpn&logoColor=white"
}

class TechStackUpdater:
    def __init__(self, username: str, token: Optional[str] = None):
        self.username = username
        self.token = token
        # O(1) Optimization: Pre-compute reverse mapping for instant lookups
        self.keyword_to_category: Dict[str, str] = {
            keyword: category
            for category, keywords in CATEGORIES.items()
            for keyword in keywords
        }

    def fetch_repos(self) -> List[Dict]:
        """Fetch all public repositories for the user with robust error handling."""
        headers: Dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        repos: List[Dict] = []
        page: int = 1
        
        print(f"Fetching repositories for {self.username}...")
        
        with requests.Session() as session:
            session.headers.update(headers)
            while True:
                url = f"{API_URL.format(self.username)}?per_page=100&page={page}"
                try:
                    response = session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    if not data:
                        break  # No more pages
                        
                    repos.extend(data)
                    page += 1
                except requests.exceptions.HTTPError as e:
                    print(f"HTTP Error fetching repos: {e.response.status_code} - {e.response.text}", file=sys.stderr)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Network error while fetching repos: {e}", file=sys.stderr)
                    break
                    
        print(f"Found {len(repos)} repositories.")
        return repos

    def extract_technologies(self, repos: List[Dict]) -> Set[str]:
        """Scan repositories for languages and topics."""
        detected_tech: Set[str] = set()
        
        for repo in repos:
            language = repo.get("language")
            if language:
                detected_tech.add(language.lower())
            
            topics = repo.get("topics", [])
            for topic in topics:
                detected_tech.add(topic.lower())
                
        print(f"Detected {len(detected_tech)} unique technologies/topics.")
        return detected_tech

    def categorize_tech(self, detected_tech: Set[str]) -> Dict[str, List[str]]:
        """Sort detected technologies into categories using O(1) lookup."""
        categorized: Dict[str, List[str]] = defaultdict(list)
        
        for tech in detected_tech:
            # O(1) instant lookup
            category = self.keyword_to_category.get(tech)
            if category:
                categorized[category].append(tech)
                
        # Sort internal lists and return standard dict
        return {cat: sorted(items) for cat, items in categorized.items()}

    def generate_markdown(self, categorized_tech: Dict[str, List[str]]) -> str:
        """Generate the markdown table payload."""
        lines: List[str] = [
            '<div align="center">',
            '',
            '| **Domain** | **Technologies** |',
            '| :--- | :--- |'
        ]
        
        # Ensure categories always appear in the defined canonical order
        for category in CATEGORIES.keys():
            items = categorized_tech.get(category)
            if not items:
                continue
                
            badges: List[str] = []
            for item in items:
                # Use mapped style or generate dynamic default
                style = BADGE_MAP.get(item, f"{item.replace('-', '--')}-gray?style=for-the-badge&logo={item}&logoColor=white")
                badge_md = f"![{item.title()}](https://img.shields.io/badge/{style})"
                badges.append(badge_md)
                
            lines.append(f"| **{category}** | {' '.join(badges)} |")
            
        lines.append('')
        lines.append('</div>')
        
        return '\n'.join(lines)

    def update_readme(self, new_content: str, filepath: str = README_PATH) -> None:
        """Update the README file between the specific HTML comment markers."""
        if not os.path.exists(filepath):
            print(f"Error: '{filepath}' not found!", file=sys.stderr)
            return
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not MARKER_PATTERN.search(content):
            print("Error: Markers not found in README.md. Please add <!-- TECH-STACK:START --> and <!-- TECH-STACK:END -->.", file=sys.stderr)
            return
            
        replacement = f"\\1\n{new_content}\n\\3"
        new_readme = MARKER_PATTERN.sub(replacement, content)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_readme)
            
        print("README.md updated successfully!")

    def run(self) -> None:
        """Main execution pipeline."""
        repos = self.fetch_repos()
        if not repos:
            print("No repositories found or failed to fetch. Aborting update.")
            return
            
        detected = self.extract_technologies(repos)
        categorized = self.categorize_tech(detected)
        markdown_table = self.generate_markdown(categorized)
        
        self.update_readme(markdown_table)


if __name__ == "__main__":
    updater = TechStackUpdater(GITHUB_USERNAME, GITHUB_TOKEN)
    updater.run()
