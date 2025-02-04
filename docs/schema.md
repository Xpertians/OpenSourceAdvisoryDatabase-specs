# Open Source Software Advisory (OSSA) Schema

## Overview
The **OSSA Schema** provides a structured format for defining and assessing open-source package advisories. It ensures consistency and compliance in tracking package issues such as deprecations, security risks, and licensing concerns.

## Schema Specification
The schema defines structured fields for advisory documents.

### **Key Fields**
| **Field**         | **Type**             | **Description** |
|-------------------|---------------------|----------------|
| `id`             | string               | Unique identifier (format: OSSA-YYYYMMDD-NNNN) |
| `version`        | string               | Version of the affected package |
| `severity`       | string (enum)        | Severity level: Low, Medium, High, Informational |
| `title`          | string               | Summary of the advisory |
| `package_name`   | string               | Name of the affected package |
| `purls`          | array                | List of Package URLs (PURLs) |
| `references`     | string or array      | External references (URLs) |
| `licenses`       | string or array      | SPDX license identifier(s) |
| `approvals`      | array                | Approval status (consumption, externalization, etc.) |
| `artifacts`      | array                | Files related to the advisory with hashes |

For the full schema, refer to [`schema-1.5.json`](specs/schema-1.5.json).

---

## Severity Levels
OSSA defines severity levels to assess the **business continuity risks** of a package.

### **High Severity**
- Immediate threat to **functionality, legality, or continuity**.
- Package is **officially deprecated or unmaintained** with no migration path.
- Risks **business-critical operations** (e.g., compliance, supply chain breakdown).

### **Medium Severity**
- Package shows signs of **becoming unsupported** (e.g., low update frequency).
- Partial alternatives exist, but migration would require significant effort.
- **Potential future risks** to business continuity.

### **Low Severity**
- Package is **old but stable**, with minimal impact on business operations.
- Migration is possible but **not yet required**.
- Risks are minimal and mitigatable.

### **Informational Severity**
- Package flagged for **awareness** (e.g., approaching end-of-life but still functional).

For detailed risk assessment, see [`severity.md`](severity.md).


## Usage

### **Validating an OSSA File**
Use the Python validation tool to check if an advisory file follows the schema:

```sh
python3 tool/validator.py specs/schema-1.5.json examples/OSSA-20241205-0001-ffmpeg.json
```

If the advisory is valid, a success message will be displayed. Otherwise, the script will report validation errors.

### **Creating a New Advisory**
* Copy an example from the examples/ folder.
* Fill in the required fields (id, severity, purls, etc.).
* Validate using the validator.py tool.

## License
This specification is released under the MIT license.
