# Open Source Software Advisory (OSSA) - Specification
The [Open Source Software Advisory](https://github.com/Xpertians/OpenSourceSoftwareAdvisory) (OSSA) Specification repository defines a standardized schema for [OSSA](https://github.com/Xpertians/OpenSourceSoftwareAdvisory) files, ensuring consistent formatting and structure for reporting issues like license violations, deprecated packages, or compliance concerns. The repository also includes examples that demonstrate correct usage of the schema.

While the current implementation is limited, it meets our requirements for the initial cases we plan to support in our first release

## Repository Contents
* specs/: The JSON schema defining the structure of OSS advisory files.
* examples/: A sample advisory file adhering to the schema for reference.
* tools/validator.py: A simple script used to validate an advisory file against the schema.


## Purpose
This repository serves as a reference specification for organizations and developers creating OSS advisory files. By adhering to this schema, stakeholders can ensure uniformity and reliability in their advisories, enabling easier integration with tools and systems.

### Features of the Schema
* Standardized Structure: Defines consistent fields for creating OSS advisory files.
* Support for Approvals: Includes fields for tracking consumption and externalization approvals, along with the ability to extend the schema for additional use cases.
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

For a complete definition, refer to [schema file](https://github.com/Xpertians/OpenSourceSoftwareAdvisory-spec/blob/main/specs/schema-1.0.json) or the [documentation](https://github.com/Xpertians/OpenSourceSoftwareAdvisory-spec/tree/main/docs).

# License
This project is licensed under the MIT License. See the LICENSE file for details.