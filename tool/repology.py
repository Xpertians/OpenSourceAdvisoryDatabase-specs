import requests

def normalize_to_spdx(entry):
    # Map non-SPDX license names to SPDX equivalents
    SPDX_LICENSE_MAP = {
        "ASL 1.1": "Apache-1.1",
        "ASL 2.0": "Apache-2.0",
        "BSD": "BSD-2-Clause",
        "BSD with advertising": "BSD-4-Clause",
        "GPL+": "GPL-1.0-or-later",
        "GPLv2": "GPL-2.0-only",
        "GPLv2 with exceptions": "LicenseRef-GPLv2-with-exceptions",
        "GPL-2.0 with Classpath": "GPL-2.0-with-classpath-exception",
        "GPL-2.0-with-classpath-exception": "GPL-2.0-with-classpath-exception",
        "GPLv2+": "GPL-2.0-or-later",
        "GPLv3+": "GPL-3.0-or-later",
        "GPL-3.0-or-later": "GPL-3.0-or-later",
        "GPL": "GPL-1.0-or-later",
        "IJG": "IJG",
        "LGPLv2+": "LGPL-2.1-or-later",
        "LGPL+": "LGPL-2.0-or-later",
        "LGPLv2": "LGPL-2.0",
        "LGPL-2.1-or-later": "LGPL-2.1-or-later",
        "LGPL-2.1-or-later GPL-2.0-or-later": "LGPL-2.1-or-later",
        "MIT": "MIT",
        "MPLv1.0": "MPL-1.0",
        "MPLv1.1": "MPL-1.1",
        "MPLv2.0": "MPL-2.0",
        "Public Domain": "Public-Domain",
        "W3C": "W3C",
        "zlib": "Zlib",
        "ISC": "ISC",
        "FTL": "FTL",
        "RSA": "LicenseRef-RSA",
        "LicenseRef-Callaway-BSD": "LicenseRef-Callaway-BSD",
        "LicenseRef-Callaway-BSD-with-advertising": "LicenseRef-Callaway-BSD-with-advertising",
        "LicenseRef-Callaway-GPLv2-with-exceptions": "LicenseRef-GPLv2-with-exceptions",
        "LicenseRef-Callaway-LGPLv2+": "LicenseRef-LGPLv2+",
        "LicenseRef-Callaway-MIT": "LicenseRef-MIT",
        "LicenseRef-Callaway-Public-Domain": "Public-Domain",
        "NOASSERTION": "NOASSERTION",
        "custom": "Custom",
    }

    all_licenses = set()
    licenses = [lic.strip() for lic in entry.split(",")]
    for lic in licenses:
        normalized = SPDX_LICENSE_MAP.get(lic, lic)
        all_licenses.add(normalized)
    
    return sorted(all_licenses)

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
                    package_licenses = repo.get('licenses', ['unknown_license'])

                    # Add aliases and licenses
                    aliases.add(package_visiblename)
                    licenses.update(package_licenses)

            return sorted(aliases), sorted(licenses)
        except ValueError as e:
            print(f"Failed to parse JSON: {e}")
            return [], []
    elif response.status_code == 403:
        print("Access denied. Make sure your IP is not blocked.")
        return [], []
    else:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return [], []

# Example usage
rpm_package = "ffmpeg"
aliases, licenses = find_package_info(rpm_package)

if aliases:
    print("Possible Aliases:")
    for alias in aliases:
        print(f"  - {alias}")

if licenses:
    print("\nUnique Licenses Found:")
    for license in licenses:
        txt = license.replace(' and ', ', ').replace(' AND ', ', ')
        txt = normalize_to_spdx(txt)
        print(f"  - {txt}")
