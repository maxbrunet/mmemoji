from os import path

from setuptools import find_packages, setup

root_dir = path.abspath(path.dirname(__file__))
src_dir = path.relpath(path.join(root_dir, "src"))

pkg_info = {}
version_module = path.join(root_dir, "src", "mmemoji", "version.py")
with open(version_module) as f:
    exec(f.read(), pkg_info)

readme_file = path.join(root_dir, "README.md")
with open(readme_file) as f:
    readme = f.read()

setup(
    name="mmemoji",
    version=pkg_info["VERSION"],
    description=pkg_info["DESCRIPTION"],
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ],
    keywords="cli emoji mattermost",
    url="https://github.com/maxbrunet/mmemoji",
    license="GPLv3",
    package_dir={"": src_dir},
    packages=find_packages(src_dir),
    python_requires=">=3.5",
    install_requires=[
        "click>=7.0",
        "mattermostdriver>=6.1.2",
        "requests",
        "tablib",
        "tabulate",
    ],
    entry_points={"console_scripts": ["mmemoji = mmemoji.cli:cli"]},
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "pytest-black>=0.3.7",
        "pytest-cov",
        "pytest-flake8",
        "pytest-isort",
        "toml",  # required by isort
    ],
)
