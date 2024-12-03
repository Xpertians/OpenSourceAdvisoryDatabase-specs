# OSS Advisory Specification
The OSS Advisory Specification repository defines a standardized schema for Open Source Software (OSS) advisory files. This schema ensures consistent formatting and structure for reporting issues such as license violations, deprecated packages, or compliance concerns. The repository also includes examples demonstrating correct usage of the schema.

## Repository Contents
* specs/schema.json: The JSON schema defining the structure of OSS advisory files.
* examples/OSSA-2024-0001.json: A sample advisory file adhering to the schema for reference.
* tools/validator.py: A simple script used to validate an advisory file against the schema.


## Purpose
This repository serves as a reference specification for organizations and developers creating OSS advisory files. By adhering to this schema, stakeholders can ensure uniformity and reliability in their advisories, enabling easier integration with tools and systems.

### Features of the Schema
* Standardized Structure: Defines consistent fields for creating OSS advisory files.
* Support for Approvals: Includes fields to track consumption and externalization statuses.
* Rich Metadata: Supports versioning, severity levels, and detailed descriptions of advisories.
* Flexibility: Handles multiple affected versions, package URLs (PURLs), and regex patterns.

### Schema Overview
The schema includes the following key fields:

* ID: A unique identifier for the advisory.
* Version: The affected package version.
* Severity: The severity level of the issue (Low, Medium, High, or Informational).
* Package Name: Name of the affected package.
* Approvals: Array tracking consumption and externalization statuses.
* Description: Detailed explanation of the issue.
* PURLs: A list of Package URLs associated with the advisory.
* Affected Versions: Versions or version ranges impacted by the issue.
* References: External resources or documentation links.

For a complete definition, refer to schema.json or <documentation>.

# Contributing
Contributions to the schema or examples are welcome! To contribute:

* Fork the repository.
* Make your changes.
* Submit a pull request for review.

# License
This project is licensed under the MIT License. See the LICENSE file for details.