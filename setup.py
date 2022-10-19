import os

from setuptools import setup

# Use requirements.txt to build dependencies
# We use this to make developers live easy :)
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as file:
    requirements = file.readlines()

required_modules = []
linked_dependencies = []

# split dependencies from standard modules and git+...
for p in requirements:
    if p.startswith("git+"):
        linked_dependencies.append(p)
    elif p.startswith("--index-url"):
        pass  # linked_dependencies.append(p[12:-1])
    elif p.startswith("--extra-index-url"):
        pass  # linked_dependencies.append(p[12:-1])
    elif p.startswith("#"):
        pass
    else:
        required_modules.append(p)

setup(
    install_requires=required_modules,
    dependency_links=linked_dependencies,
)
