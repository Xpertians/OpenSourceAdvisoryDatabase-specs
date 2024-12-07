import os
import json
import subprocess
import hashlib
import datetime
import ssdeep
import glob
import shutil
from pathlib import Path
from swh.model.swhids import CoreSWHID

def cleanup_source_packages(folder_path="./source_packages"):
    rpm_files = glob.glob(f"{folder_path}/*.rpm")
    for file_path in rpm_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

def compute_hash_as_hex(file_path, hash_type="sha1"):
    hash_function = hashlib.new(hash_type)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_function.update(chunk)
    return hash_function.hexdigest()

def compute_folder_swhid(folder_path):
    """Calculate the SWHID for a folder using `sw identify .`."""
    try:
        command = ["swh", "identify", folder_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                # Split the output to extract the SWHID
                if line.startswith("swh:1:dir:"):
                    swhid = line.split("\t")[0]  # Extract the SWHID part
                    return swhid
        else:
            print(f"Failed to compute folder SWHID: {result.stderr}")
    except FileNotFoundError:
        print(f"The `swh` command is not installed or not found in PATH.")
    return None

def cleanup_extracted_files(folder_path):
    """Recursively clean up files and directories in the specified folder."""
    try:
        for file_path in glob.glob(f"{folder_path}/*"):
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Recursively delete directories
                print(f"Deleted directory: {file_path}")
            else:
                os.remove(file_path)  # Delete files
                print(f"Deleted file: {file_path}")
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

def get_all_available_packages():
    command = ["dnf", "repoquery", "--source"]
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

def get_source_package(package_name, dest_dir="./source_packages"):
    os.makedirs(dest_dir, exist_ok=True)
    command = ["yumdownloader", "--source", "--destdir", dest_dir, package_name]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        for file in os.listdir(dest_dir):
            if file.endswith(".src.rpm"):
                return os.path.join(dest_dir, file)
    return None

def extract_spec_file(srpm_path, dest_dir="./extracted_specs"):
    os.makedirs(dest_dir, exist_ok=True)
    try:
        command = f"rpm2cpio {srpm_path} | cpio -idmv -D {dest_dir}"
        subprocess.run(command, shell=True, check=True)
        spec_files = [os.path.join(dest_dir, f) for f in os.listdir(dest_dir) if f.endswith(".spec")]
        if spec_files:
            return spec_files[0]
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract spec file from {srpm_path}: {e}")
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

def extract_urls_from_spec(spec_file_path):
    project_url = None
    source_url = None
    try:
        with open(spec_file_path, "r") as spec_file:
            for line in spec_file:
                if line.startswith("URL:"):
                    project_url = line.split(":", 1)[1].strip()
                elif line.startswith("Source0:"):
                    source_url = line.split(":", 1)[1].strip()
    except FileNotFoundError:
        print(f"Spec file not found: {spec_file_path}")
    return project_url, source_url

def process_tarball(tarball_path):
    """Extract tarball, calculate SWHID for folder, and clean up."""
    temp_dir = "./temp_tarball_extraction"
    os.makedirs(temp_dir, exist_ok=True)
    try:
        # Extract the tarball
        command = f"tar -xf {tarball_path} -C {temp_dir}"
        subprocess.run(command, shell=True, check=True)
        
        # Calculate SWHID for the extracted folder
        folder_swhid = compute_folder_swhid(temp_dir).trim()
        print("folder_swhid:", folder_swhid)
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

    spec_dir = "./extracted_specs"
    spec_file = extract_spec_file(source_path, spec_dir)
    project_url, source_url = (None, None)
    licenses = []
    license_categories = {
        "copyleft": ["GPL", "AGPL"],
        "weak_copyleft": ["LGPL", "MPL", "EPL", "CDDL"],
        "permissive": ["MIT", "BSD", "Apache"]
    }

    if spec_file:
        project_url, source_url = extract_urls_from_spec(spec_file)
        try:
            with open(spec_file, "r") as spec:
                for line in spec:
                    if line.startswith("License:"):
                        licenses.append(line.split(":", 1)[1].strip())
        except FileNotFoundError:
            print(f"Spec file not found: {spec_file}")
        cleanup_extracted_files(spec_dir)

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
        swhids.append(swhid)
        fuzzy_hash = compute_fuzzy_hash(tarball)
        folder_swhid = process_tarball(tarball)
        if folder_swhid:
            swhids.append(folder_swhid)
            swhid = folder_swhid
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
            "fuzzy_hash": fuzzy_hash
        })

    cleanup_extracted_files("./extracted_sources")

    aliases = []
    package_cleaned = ''.join([char if not char.isdigit() else ' ' for char in package])
    words = [word for word in package_cleaned.replace('-', ' ').split() if len(word) >= 3]
    aliases.extend(words)

    license_category = "Informational"
    reason = "Automatically generated OSSA for the package."
    for license in licenses:
        if any(license.startswith(c) for c in license_categories["copyleft"]):
            license_category = "High"
            reason = "This package contains copyleft licenses, which impose strong obligations."
        elif any(license.startswith(c) for c in license_categories["weak_copyleft"]):
            license_category = "Medium"
            reason = "This package contains weak copyleft licenses, which impose moderate obligations."

    ossa_data = {
        "id": ossa_id,
        "version": version,
        "severity": license_category,
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
        "description": reason,
        "purls": [f"pkg:rpm/{package}@{version}?arch={arch}"],
        "regex": [f"^pkg:rpm/{package}.*"],
        "affected_versions": ["*.*", version],
        "artifacts": artifacts,
        "licenses": licenses,
        "aliases": aliases,
        "references": [project_url] if project_url else []
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
