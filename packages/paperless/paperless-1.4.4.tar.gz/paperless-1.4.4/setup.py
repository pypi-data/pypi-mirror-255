from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="paperless",
    version="1.4.4",
    description="A papermill implementation to run notebooks inside dataproc serverless",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    py_modules = ['paperless', 'app'],
    python_requires=">=3.10",
    packages=find_packages(exclude=("tests",)),
    
    include_package_data=True,
    install_requires = [requirements],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        paperless=paperless.__main__:cli
    '''
)
