from setuptools import setup, find_packages

setup(
    name='standardize_country',
    version='0.0.2',
    packages=find_packages(),
    description='  package to standardize country names.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Harshil Chidura',
    author_email='harshil0217@gmail.com',
    url='https://github.com/harshil0217/standardize_country',
    license='LICENSE',
    install_requires=[
        'pycountry'
    ],
)
