"""
Setup python package.

Setup python package.
"""

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='irbt',
    version_config={
        "version_format": "{tag}.dev{sha}",
        "starting_version": "0.3.0"
    },
    author='Cyril Leclerc',
    author_email='cyril.leclerc@gmail.com',
    description='A Library to interact with irbt appliances',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tidalf/irbt',
    packages=setuptools.find_packages(),
    scripts=['bin/irbt-cli.py'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    setup_requires=['better-setuptools-git-version'],
)
