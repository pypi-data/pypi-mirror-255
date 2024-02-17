from setuptools import setup

requirements = []
with open('/Users/bgallean/Projects/GitHub/astecmanagerelease/requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())


setup(
    name = "AstecManager",
    version = "0.1.45",
    author = "Benjamin GALLEAN",
    author_email = "benjamin.gallean@crbm.cnrs.fr",
    description = "This package creates a management system to run the ASTEC algorithms for developmental biology live "
                  "imaging. ",
    long_description = open('README.md').read(),
    long_description_content_type = "text/markdown",
    url = "https://gite.lirmm.fr/bgallean/astecmanagerelease",
    project_urls = {
        "Bug Tracker": "https://gite.lirmm.fr/bgallean/astecmanagerelease/-/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["AstecManager","AstecManager.libs","AstecManager.atlas","AstecManager.libs.ImageHandling",],
    include_package_data = True,
    install_requires=requirements
)
