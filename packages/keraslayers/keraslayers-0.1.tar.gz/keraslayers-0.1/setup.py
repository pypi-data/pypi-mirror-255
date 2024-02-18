from setuptools import setup, find_packages

setup(
    name='keraslayers',
    version='0.1',
    packages=find_packages(),
    author='',
    author_email='',
    description='Keras models',
    license='MIT', 
    install_requires=[
        'numpy',
        'tensorflow',
        'keras',
    ]
)
