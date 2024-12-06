import requests

def find_package_info(rpm_package_name):
    url = f"https://repology.org/api/v1/project/{rpm_package_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            aliases = set()
            licenses = set()

            target_distros = [
                "debian", "ubuntu", "raspbian", "alpine", "fedora", "epel", "openwrt", "amazonlinux"
            ]
            
            for repo in data:
                repo_name = repo.get('repo', 'unknown_repo').lower()
                if any(distro in repo_name for distro in target_distros):
                    package_visiblename = repo.get('visiblename', rpm_package_name)
                    aliases.add(package_visiblename)

            return sorted(aliases)
        except ValueError as e:
            print(f"Failed to parse JSON: {e}")
            return [], set()
    elif response.status_code == 403:
        print("Access denied. Make sure your IP is not blocked.")
        return [], set()
    else:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return [], set()

# Example usage
rpm_package = "gcc"
aliases = find_package_info(rpm_package)

if aliases:
    print("Possible Aliases:")
    print(", ".join(sorted(aliases)))
