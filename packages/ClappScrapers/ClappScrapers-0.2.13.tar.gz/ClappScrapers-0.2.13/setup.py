import setuptools


def readme():
    with open("README.md") as f:
        return f.read()
    

setuptools.setup(
    name="ClappScrapers",
    version="0.2.13",
    description="Clappform Python scraper",
    author = "Clappform B.V.",
    author_email = "info@clappform.com",
    long_description=readme(),
    long_description_content_type="text/markdown",

    license="MIT",
    url = "https://github.com/ClappFormOrg/clappform-scraper",
    classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    ],
    keywords="scraper",
    python_requires = ">=3.10",
    install_requires = ['scrapy','scrapy_user_agents','beautifulsoup4>=4.8','requests>=2','diot>=0.1.5','PyYAML>=5.0','tqdm>=4.42.0','pandas>=1.2','lxml>=4','urllib3==1.26'],
    include_package_data=True,
    exclude_package_data={"":['*.egg-info','build','dist'],'ClappScrapers':['__pycache__'],},

    
)
