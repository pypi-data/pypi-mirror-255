from setuptools import setup, find_packages


with open("README.md",'r') as f:
    long_description = f.read()



setup(
    name='hmpol',  # Replace with your actual package name
    url = 'https://gitlab.com/AnoopANair/the-hmpol-project.git', # Replace with your github project link
    version='0.1.4',
    description="A package to calculate the moments and polarizabilities of molecules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anoop Ajaya Kumar Nair",
    author_email="mailanoopanair@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        # Your project dependencies
    ],
)
