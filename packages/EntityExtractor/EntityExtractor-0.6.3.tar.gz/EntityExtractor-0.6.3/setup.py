from setuptools import setup, find_packages

setup(
    name='EntityExtractor',
    author='Ankit Mor',
    version='0.6.3',
    packages=find_packages(),
    description='Extract specific entities from a text. Give Base64 and get a JSON formatted output data.',
    long_description="""Run following before using : \n spacy.cli.download('web_en_core_trf')""",
    long_description_content_type="text/markdown",
    install_requires=[
        'nltk>=3.8.1',
        'requests',
        'BeautifulSoup4',
        'spacy>=3.7.2',
        'spacy-transformers'
    ],
)
