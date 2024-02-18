from setuptools import setup, find_packages

setup(
    name='keraslayers',
    version='0.3',
    packages=find_packages(),
    author='',
    author_email='',
    description='Keras models and utilities',
    license='MIT', 
    install_requires=[
        'numpy',
        'tensorflow',
        'keras',
        'pandas', 
        'cloudscraper',
        'requests',
        'beautifulsoup4',
        'keras',
    ]
)
