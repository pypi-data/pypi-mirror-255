# setup.py

from setuptools import setup, find_packages

setup(
    name='tlid',  # This should be a unique name, not already present on PyPI
    version='0.1.11',
    author='GUillaume Isabelle',
    author_email='jgi@jgwill.com',
    description='A utility for creating datetime-based strings for file naming',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tlid/tlid/tree/master/src/python',  # Replace with the actual URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # If your project is licensed under MIT
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
        entry_points={
        'console_scripts': [
            'pytlid=tlid.tlidcli:main',  # Assuming your tlidcli.py has a main() function
        ],
    },
)

