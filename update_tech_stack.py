import requests
import os
import re

# Configuration
GITHUB_USERNAME = "TUSHAR91316"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
README_PATH = "README.md"

# Mappings: Define which keywords belong to which category
# All keywords should be lowercase for matching
CATEGORIES = {
    "Languages": {
        "python", "c++", "c", "javascript", "typescript", "dart", "java", "kotlin", "swift", "go", "rust"
    },
    "Frontend": {
        "flutter", "react", "tailwindcss", "html", "css", "vue", "angular", "next.js", "bootstrap", "material-ui"
    },
    "Backend & Cloud": {
        "firebase", "docker", "nginx", "redis", "django", "flask", "fastapi", "node", "express", "aws", "gcp", "azure", "mongodb", "postgresql", "mysql"
    },
    "Security & OS": {
        "linux", "git", "kali", "wireshark", "metasploit", "bash", "shell", "powershell", "nmap", "burp suite"
    }
}

# Icon mapping for shields.io (Optional: Add specific colors/logos if needed)
# Format: "keyword": "Badge String"
# If not found, a default badge will be generated
BADGE_MAP = {
    "python": "Python-3776AB?style=flat&logo=python&logoColor=white",
    "c++": "C++-00599C?style=flat&logo=c%2B%2B&logoColor=white",
    "javascript": "JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black",
    "flutter": "Flutter-02569B?style=flat&logo=flutter&logoColor=white",
    "react": "React-20232A?style=flat&logo=react&logoColor=61DAFB",
    "tailwindcss": "Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white",
    "firebase": "Firebase-FFCA28?style=flat&logo=firebase&logoColor=black",
    "docker": "Docker-2496ED?style=flat&logo=docker&logoColor=white",
    "nginx": "Nginx-009639?style=flat&logo=nginx&logoColor=white",
    "redis": "Redis-DC382D?style=flat&logo=redis&logoColor=white",
    "linux": "Linux-FCC624?style=flat&logo=linux&logoColor=black",
    "git": "Git-F05032?style=flat&logo=git&logoColor=white",
    "kali": "Kali_Linux-557C94?style=flat&logo=kali-linux&logoColor=white"
}

def fetch_repos():
    """Fetch all public repositories for the user."""
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repos: {response.text}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def extract_technologies(repos):
    """Scan repos for languages and topics."""
    detected_tech = set()
    
    # 1. Add top languages from all repos
    for repo in repos:
        if repo.get("language"):
            detected_tech.add(repo["language"].lower())
        
        # 2. Add topics (repo tags)
        for topic in repo.get("topics", []):
            detected_tech.add(topic.lower())
            
    return detected_tech

def categorize_tech(detected_tech):
    """Sort detected technologies into categories."""
    categorized = {cat: [] for cat in CATEGORIES}
    
    for tech in detected_tech:
        found = False
        for cat, keywords in CATEGORIES.items():
            if tech in keywords:
                categorized[cat].append(tech)
                found = True
                break
        # Optional: Log unclassified tech if needed
        # if not found: print(f"Unclassified: {tech}")
    
    # Sort for consistency
    for cat in categorized:
        categorized[cat].sort()
        
    return categorized

def generate_markdown(categorized_tech):
    """Generate the markdown table."""
    markdown = '<div align="center">\n\n| **Domain** | **Technologies** |\n| :--- | :--- |\n'
    
    for cat, items in categorized_tech.items():
        if not items: continue # Skip empty categories
        
        badges = []
        for item in items:
            # Generate badge URL
            # Use mapped style or default style
            style = BADGE_MAP.get(item, f"{item.replace('-', '--')}-gray?style=flat&logo={item}&logoColor=white")
            badge_md = f"![{item.title()}](https://img.shields.io/badge/{style})"
            badges.append(badge_md)
            
        row = f"| **{cat}** | {' '.join(badges)} |\n"
        markdown += row
        
    markdown += '\n</div>'
    return markdown

def update_readme(new_content):
    """Update the README file between markers."""
    if not os.path.exists(README_PATH):
        print("README.md not found!")
        return
        
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"(<!-- TECH-STACK:START -->)(.*?)(<!-- TECH-STACK:END -->)"
    replacement = f"\\1\n{new_content}\n\\3"
    
    if re.search(pattern, content, re.DOTALL):
        new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README.md updated successfully.")
    else:
        print("Markers not found in README.md. Please add <!-- TECH-STACK:START --> and <!-- TECH-STACK:END -->.")

def main():
    print(f"Fetching repos for {GITHUB_USERNAME}...")
    repos = fetch_repos()
    print(f"Found {len(repos)} repositories.")
    
    detected = extract_technologies(repos)
    print(f"Detected technologies: {detected}")
    
    categorized = categorize_tech(detected)
    markdown_table = generate_markdown(categorized)
    
    print("Generated Markdown:")
    print(markdown_table)
    
    update_readme(markdown_table)

if __name__ == "__main__":
    main()
