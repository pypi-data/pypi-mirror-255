"""Setup."""
import os
from shutil import copytree

from setuptools import find_packages, setup

# Get setup packages from requirements.txt
with open("requirements_setup.txt", encoding="utf-8") as f:
    requirements_setup = f.read().splitlines()

# Get packages from requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

copytree(
    "out",
    "systembridgefrontend/out",
    dirs_exist_ok=True,
)

package_data = ["out/**/*"]

for root, _, files in os.walk("systembridgefrontend/out"):
    for filename in files:
        package_data.append(
            os.path.join(root, filename)
            .replace("\\", "/", -1)
            .replace("systembridgefrontend/", "")
        )

print(package_data)  # noqa: T201

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="systembridgefrontend",
    author="Aidan Timson (Timmo)",
    author_email="aidan@timmo.dev",
    description="System Bridge Frontend",
    keywords="system-bridge",
    license="Apache-2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/timmo001/system-bridge-frontend",
    install_requires=requirements,
    packages=find_packages(exclude=["tests", "generator"]),
    package_data={"": package_data},
    python_requires=">=3.11",
    setup_requires=requirements_setup,
    use_incremental=True,
)
