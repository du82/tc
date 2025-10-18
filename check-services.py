import csv
import requests
import socket
from datetime import datetime
from typing import List, Dict

# Configure requests to use Tor SOCKS proxy
session = requests.Session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def check_onion_service(url: str, timeout: int = 30) -> bool:
    """
    Check if a Tor hidden service is reachable.

    Args:
        url: The .onion URL to check
        timeout: Timeout in seconds

    Returns:
        True if service is online, False otherwise
    """
    try:
        # Ensure URL has proper scheme
        if not url.startswith('http'):
            url = f'http://{url}'

        response = session.get(url, timeout=timeout)
        return response.status_code < 500  # Consider 4xx as "online"
    except Exception as e:
        print(f"  ❌ {url}: {type(e).__name__}")
        return False

def read_services_csv(filename: str = 'services.csv') -> List[Dict[str, str]]:
    """
    Read the CSV file containing Tor hidden services.
    Expected columns: name, url, description (optional)
    """
    services = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            services.append(row)
    return services

def update_readme(online_services: List[Dict[str, str]],
                  offline_services: List[Dict[str, str]],
                  readme_file: str = 'README.md'):
    """
    Update README.md with the status of Tor services.
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Create the status section
    status_content = f"""## 🧅 Tor Hidden Services Status

*Last checked: {timestamp}*

### ✅ Online Services ({len(online_services)})

"""

    if online_services:
        for service in online_services:
            name = service.get('name', 'Unknown')
            url = service.get('url', '')
            desc = service.get('description', '')

            status_content += f"- **{name}**\n"
            status_content += f"  - URL: `{url}`\n"
            if desc:
                status_content += f"  - {desc}\n"
            status_content += "\n"
    else:
        status_content += "*No services are currently online.*\n\n"

    status_content += f"### ❌ Offline Services ({len(offline_services)})\n\n"

    if offline_services:
        for service in offline_services:
            name = service.get('name', 'Unknown')
            url = service.get('url', '')
            status_content += f"- **{name}** - `{url}`\n"
    else:
        status_content += "*All services are online!*\n"

    status_content += "\n---\n"

    # Read existing README
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            readme = f.read()
    except FileNotFoundError:
        readme = "# Tor Hidden Services Monitor\n\n"

    # Replace or append status section
    start_marker = "## 🧅 Tor Hidden Services Status"
    end_marker = "\n---\n"

    if start_marker in readme:
        # Find and replace existing status section
        start_idx = readme.find(start_marker)
        # Find the end marker after the start
        end_idx = readme.find(end_marker, start_idx)
        if end_idx != -1:
            end_idx += len(end_marker)
            readme = readme[:start_idx] + status_content + readme[end_idx:]
        else:
            readme = readme[:start_idx] + status_content
    else:
        # Append to end of README
        readme += "\n" + status_content

    # Write updated README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme)

def main():
    print("🧅 Starting Tor hidden service check...")

    # Read services from CSV
    try:
        services = read_services_csv()
        print(f"📋 Found {len(services)} services to check\n")
    except FileNotFoundError:
        print("❌ services.csv not found!")
        return

    online_services = []
    offline_services = []

    # Check each service
    for service in services:
        name = service.get('name', 'Unknown')
        url = service.get('url', '')

        print(f"Checking {name}...")
        if check_onion_service(url):
            print(f"  ✅ Online")
            online_services.append(service)
        else:
            print(f"  ❌ Offline")
            offline_services.append(service)

    # Update README
    print(f"\n📝 Updating README...")
    update_readme(online_services, offline_services)
    print(f"✅ Done! {len(online_services)} online, {len(offline_services)} offline")

if __name__ == '__main__':
    main()
