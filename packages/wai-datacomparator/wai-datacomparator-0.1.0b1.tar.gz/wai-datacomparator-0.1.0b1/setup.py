from setuptools import setup, find_packages

setup(
    name="wai-datacomparator",
    version="0.1.0-beta.1",
    packages=find_packages(),

    author="RAJ PATEL",
    author_email="rajp@aliteprojects.in",
    maintainer="RAJ PATEL",
    maintainer_email="rajp@aliteprojects.in",
    description='Data Comparator: A Python package for comparing data from two files. The service reads a '
                'configuration file that specifies the details of the comparison operation, such as the logger '
                'configurations, old file and new file for the comparison along with the file type, Primary key '
                'information. Easy to use and highly flexible, Data Comparator simplifies the process of merging data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://bitbucket.org/wilsonai/wai_misc/src/wai-pkg-001",

    install_requires=[
        "pandas",
        "tabulate"
    ],

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],

    python_requires="==3.10.*",  # Created with Python 3.10.6
)
