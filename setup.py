#!/usr/bin/env python

"""The setup script."""
# See https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-args

from setuptools import setup, find_packages


# Get metadata without importing the package
with open('chat_analyzer/metadata.py') as metadata_file:
    exec(metadata_file.read())
    metadata = locals()

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [ # TODO: Check if this is correct
    # For the chat_analyzer
    'argparse',
    'numpy',

    # For included chat_downloader
    'requests',
    'isodate',
    # 'argparse',
    'docstring-parser',
    'colorlog',
    'websocket-client'
]

development_requirements = [
    [
        # Building/packaging
        'flake8',
        'twine',
        'wheel',
        'tox',

        # Testing and coverage
        'pytest',
        'coverage',

        # Documentation
        'sphinx',
        'sphinx-rtd-theme',
        'sphinxcontrib-programoutput'
    ]
]

setup(
    name=metadata['__title__'],
    version = metadata['__version__'],
    description=metadata['__summary__'],
    long_description=readme,
    long_description_content_type='text/x-rst',
    url=metadata['__url__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    license=metadata['__license__'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        'Topic :: Communications',
        'Topic :: Communications :: Chat',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3, or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='chat analytics analyze message twitch youtube streamer video VOD editor',
    project_urls={
        'Website': metadata['__website__'],
        'Source': metadata['__url__'],
    },
    packages=find_packages(include=['chat_analyzer', 'chat_analyzer.*']),
    install_requires=requirements,
    python_requires='>=3',
    package_data={
        'chat_analyzer': ['chat_downloader/formatting/*.json']
    },
    entry_points={
        'console_scripts': [
            'chat_analyzer=chat_analyzer.cli:main',
            'chat-analyzer=chat_analyzer.cli:main',
        ],
    },

    extras_require={
        # pip install -e ".[dev]" installs dev dependencies
        'dev': development_requirements,
    },

    # TODO: Reference Xenova's setup for the chat_downloader to see if theres anything worth adding later
)
