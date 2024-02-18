from setuptools import setup, find_packages

setup(
    name='zeus_py',
    version='0.1.0b2',
    packages=find_packages(),
    install_requires=[
        'httpx'
    ],
    author='C&S',
    description='A simple wrapper written in Python for the Zeus API.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/EPI-Companion/zeus.py',
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)

