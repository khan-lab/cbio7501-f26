"""Check the answers before any file is created."""

import re
import sys

slug = "{{ cookiecutter.project_slug }}"
orcid = "{{ cookiecutter.author_orcid }}"

if not re.fullmatch(r"[a-z][a-z0-9-]*[a-z0-9]", slug):
    sys.exit(f"ERROR: '{slug}' is not a good folder name. Use lowercase letters, digits and dashes, e.g. ltee-variant-calling.")

if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", orcid):
    sys.exit(f"ERROR: '{orcid}' does not look like an ORCID iD (0000-0000-0000-0000). Keep the zeros if you do not have one yet.")
