"""
Setup python package.

Setup python package.
"""

import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='irbt',
    version='0.3.1',
    author='D@korp',
    author_email='tidalf@ematome.com',
    description='A Library to interact with irbt appliances',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tidalf/irbt',
    packages=setuptools.find_packages(),
    scripts=['bin/irbt-cli.py'],
    install_requires=[
        'aws-requests-auth',
        'AWSIoTPythonSDK',
        'Pillow>=9.0.0',
    ],
    data_files=[('/usr/local/etc', ['config/aws-root-ca1.cer'])],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    setup_requires=[],
)
