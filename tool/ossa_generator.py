import os
import json
import subprocess
import hashlib
import datetime
import ssdeep
import glob
import shutil
from pathlib import Path

def cleanup_source_packages(folder_path="./source_packages"):
    rpm_files = glob.glob(f"{folder_path}/*.rpm")
    for file_path in rpm_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def get_all_available_packages():
    """Fetch all available packages from enabled repositories."""
    command = ["dnf", "repoquery", "--available", "--source"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to fetch available packages: {result.stderr}")
        return []
    
    packages = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                parts = line.rsplit("-", 2)
                name = parts[0]
                version_release = parts[1]
                arch = "src"
                packages.append((name, version_release, arch))
            except IndexError:
                print(f"Failed to parse line: {line}")
    return packages


def cleanup_extracted_files(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Deleted: {folder_path}")
    except Exception as e:
        print(f"Failed to clean up {folder_path}: {e}")

def compute_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha1.update(chunk)
    return sha1.hexdigest()

def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def compute_fuzzy_hash(file_path):
    return ssdeep.hash_from_file(file_path)

def compute_swhid(file_path):
    sha1_hash = compute_sha1(file_path)
    swhid = f"swh:1:cnt:{sha1_hash}"
    return swhid

def compute_folder_swhid(folder_path):
    """Calculate the SWHID for a folder using `sw identify .`."""
    try:
        command = ["sw", "identify", folder_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.startswith("swh:1:dir:"):
                    return line.strip()
        else:
            print(f"Failed to compute folder SWHID: {result.stderr}")
    except FileNotFoundError:
        print(f"The `sw` command is not installed or not found in PATH.")
    return None

def extract_tarballs(srpm_path, dest_dir="./extracted_sources"):
    os.makedirs(dest_dir, exist_ok=True)
    try:
        command = f"rpm2cpio {srpm_path} | cpio -idmv -D {dest_dir}"
        subprocess.run(command, shell=True, check=True)
        tarballs = [os.path.join(dest_dir, f) for f in os.listdir(dest_dir) if f.endswith((".tar.gz", ".tar.bz2", ".tar.xz", ".tgz"))]
        return tarballs
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract tarballs from {srpm_path}: {e}")
    return []

def process_tarball(tarball_path):
    """Extract tarball, calculate SWHID for folder, and clean up."""
    temp_dir = "./temp_tarball_extraction"
    os.makedirs(temp_dir, exist_ok=True)
    try:
        # Extract the tarball
        command = f"tar -xf {tarball_path} -C {temp_dir}"
        subprocess.run(command, shell=True, check=True)
        
        # Calculate SWHID for the extracted folder
        folder_swhid = compute_folder_swhid(temp_dir)
        return folder_swhid
    except subprocess.CalledProcessError as e:
        print(f"Failed to process tarball {tarball_path}: {e}")
    finally:
        cleanup_extracted_files(temp_dir)
    return None

def generate_ossa_file(package, version, arch, output_dir):
    package_name = f"{package}-{version}-{arch}"
    ossa_id = f"OSSA-{datetime.datetime.now().strftime('%Y%m%d')}-{hash(package_name) % 10000}-{package}"
    output_path = Path(output_dir) / f"{ossa_id.lower()}.json"

    source_path = get_source_package(package)
    if not source_path:
        print(f"Source package for {package} not found in {package}.")
        return

    tarballs = extract_tarballs(source_path)
    swhids = [compute_swhid(source_path)]
    fuzzy_hashes = [
        {
            "algorithm": "ssdeep",
            "hash": compute_fuzzy_hash(source_path)
        }
    ]
    artifacts = [
        {
            "url": f"file://{os.path.basename(source_path)}",
            "hashes": {
                "sha256": compute_sha256(source_path)
            },
            "swhid": compute_swhid(source_path),
            "fuzzy_hash": compute_fuzzy_hash(source_path)
        }
    ]

    for tarball in tarballs:
        swhid = compute_swhid(tarball)
        folder_swhid = process_tarball(tarball)
        fuzzy_hash = compute_fuzzy_hash(tarball)
        swhids.append(swhid)
        if folder_swhid:
            swhids.append(folder_swhid)
        fuzzy_hashes.append({
            "algorithm": "ssdeep",
            "hash": fuzzy_hash
        })
        artifacts.append({
            "url": f"file://{os.path.basename(tarball)}",
            "hashes": {
                "sha256": compute_sha256(tarball)
            },
            "swhid": swhid,
            "folder_swhid": folder_swhid,
            "fuzzy_hash": fuzzy_hash
        })

    cleanup_extracted_files("./extracted_sources")

    ossa_data = {
        "id": ossa_id,
        "version": version,
        "severity": "Informational",
        "title": f"Advisory for {package}",
        "package_name": package,
        "publisher": "Generated by OSSA Collector",
        "last_updated": datetime.datetime.now().isoformat(),
        "approvals": [
            {
                "consumption": True,
                "externalization": True
            }
        ],
        "description": f"Automatically generated OSSA for {package}.",
        "purls": [f"pkg:rpm/{package}@{version}?arch={arch}"],
        "regex": [f"^pkg:rpm/{package}.*"],
        "affected_versions": ["*.*", version],
        "artifacts": artifacts,
        "licenses": [],
        "aliases": [],
        "references": []
    }

    with open(output_path, "w") as f:
        json.dump(ossa_data, f, indent=4)
    print(f"Generated OSSA file: {output_path}")
    cleanup_source_packages()

def main(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    packages = get_all_available_packages()
    for package, version, arch in packages:
        generate_ossa_file(package, version, arch, output_dir)

if __name__ == "__main__":
    output_directory = "./ossa_reports"
    main(output_directory)
