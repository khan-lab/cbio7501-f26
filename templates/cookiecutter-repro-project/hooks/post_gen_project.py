"""Finish the new project: pick the license file and remove unwanted stubs."""

import shutil
from pathlib import Path

license_choice = "{{ cookiecutter.license }}"
files = {
    "MIT": "mit.txt",
    "BSD-3-Clause": "bsd-3-clause.txt",
    "Apache-2.0": "apache-2.0.txt",
    "CC-BY-4.0": "cc-by-4.0.txt",
}
licenses = Path(".licenses")
if license_choice in files:
    shutil.copyfile(licenses / files[license_choice], "LICENSE")
shutil.rmtree(licenses)

if "{{ cookiecutter.include_workflow_stubs }}" == "no":
    shutil.rmtree("workflow")
    shutil.rmtree("config")
if "{{ cookiecutter.include_container_stubs }}" == "no":
    shutil.rmtree("containers")
    Path(".dockerignore").unlink()

print(
    """
Created {{ cookiecutter.project_slug }}/

Next steps:
  cd {{ cookiecutter.project_slug }}
  pixi install            # create the environment and pixi.lock
  pixi run check          # check that the tools work

Read README.md and the README.md in each folder: they explain what goes where.
"""
)
if license_choice not in files:
    print("No LICENSE file was added. Choose a license before you share the project (lesson 11).")
