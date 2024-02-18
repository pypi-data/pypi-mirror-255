from setuptools import setup, find_packages
with open(f'pxapp/README.md', 'r') as f:
    description = f.read()

setup(
    name='RFPX',
    version='1.1.5',
    description="A helping tool",
    package_dir={"": "pxapp"},
    packages=find_packages(where="pxapp"),
    long_description=description,
    long_description_content_type="text/markdown",
    author="rf123",
    license="RFPX Software Subscription Agreement",
    install_requires=["bson >= 0.5.10",
                      "twine>=4.0.2",
                      "PyAutoGUI~=0.9.54",
                      "pytesseract~=0.3.10",
                      "pillow~=10.2.0",
                      "selenium~=4.16.0",
                      ],
    python_requires=">=3.9"
)
