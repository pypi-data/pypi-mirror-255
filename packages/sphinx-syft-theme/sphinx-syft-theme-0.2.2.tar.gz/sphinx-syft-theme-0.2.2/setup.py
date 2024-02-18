from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="sphinx-syft-theme",
    url="https://sphinx-syft-theme.readthedocs.io",
    project_urls={
        "Documentation": "https://openmined.org",
        "Source Code": "https://github.com/callezenwaka/sphinx-syft-theme",
        "Bug Tracker": "https://github.com/callezenwaka/sphinx-syft-theme/issues",
    },
    author="Callis Ezenwaka",
    author_email="callis@openmined.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Sphinx",
        "Framework :: Sphinx :: Theme",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    license="Apache 2.0",
    description="The Sphinx Syft Theme",
    long_description=Path("./README.md").read_text(),
    long_description_content_type="text/markdown",
    keywords="sphinx, theme, jupyter, notebook",
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        "sphinx<=5.0.2",
        "sphinx-book-theme>=1.0.0",
    ],
    packages=find_packages(),
    entry_points={"sphinx.html_themes": ["sphinx_syft_theme = sphinx_syft_theme"]},
    # use_scm_version={"version_scheme": "post-release", "local_scheme": "dirty-tag"},
)
