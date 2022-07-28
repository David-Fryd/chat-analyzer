#!/usr/bin/env python

"""The setup script."""
# See https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-args

from setuptools import setup, find_packages

# Get metadata without importing the package
with open('chat_analyzer/metadata.py') as metadata_file:
    exec(metadata_file.read())
    metadata = locals()

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [ # TODO: Check if this is correct
    # For the chat_analyzer
    'argparse',
    'numpy',
    # 'logging',


    # For included chat_downloader
    'requests',
    'isodate',
    # 'argparse',
    'docstring-parser',
    'colorlog',
    'websocket-client'
]

setup(
    name=metadata['__title__'],
    version = metadata['__version__'],
    description=metadata['__summary__'],
    long_description=readme,
    long_description_content_type='text/markdown', # TODO: Update README into x-rst cuz it looks nicer?
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
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='chat analytics analyze message twitch youtube streamer video VOD editor',
    project_urls={
        'Website': metadata['__website__'],
        'Source': metadata['__url__'],
        # TODO Add Documentation, Funding/Say thanks
    },
    packages=find_packages(include=['chat_analyzer', 'chat_analyzer.*']),
    install_requires=requirements,
    python_requires='>=3',
    # TODO wtf is this? do we need to include the stuff from the chat_downloader as well?
    # package_data={
    #     'chat_downloader': ['formatting/*.json']
    # },
    entry_points={
        'console_scripts': [
            'chat_analyzer=chat_analyzer.cli:main',
        ],
    },

    # author=metadata['__author__'],
    # author_email=metadata['__email__'],
    # url=metadata['__url__'],
    # version=metadata['__version__'],
    # python_requires='>=3.6',
    # classifiers=[
    #     'Development Status :: 4 - Beta',
    #     'Intended Audience :: Developers',
    #     'License :: OSI Approved :: MIT License',
    #     'Natural Language :: English',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.6',
    #     'Programming Language :: Python :: 3.7',
    #     'Programming Language :: Python :: 3.8',
    #     'Programming Language :: Python :: 3.9',
    #     'Programming Language :: Python :: 3.10',
    #     'Operating System :: OS Independent',
    # ],
    # description=metadata['__summary__'],
    # entry_points={
    #     'console_scripts': [
    #         'chat_analyzer=chat_analyzer.cli:main',
    #     ],
    # },
    # install_requires=requirements,
    # extras_require={
    #     'dev': [
    #         'flake8',
    #         'twine',
    #         'wheel',
    #         'tox',

    #         # Testing and coverage
    #         'pytest',
    #         'coverage',

    #         # Documentation
    #         'sphinx',
    #         'sphinx-rtd-theme',
    #         'sphinxcontrib-programoutput'
    #     ]
    # },
    # license='MIT license',
    # long_description=readme,  # + '\n\n' + history,
    # long_description_content_type='text/x-rst',
    # include_package_data=True,
    # keywords='python chat downloader youtube twitch',
    # name='chat-downloader',
    # packages=find_packages(include=['chat_downloader', 'chat_downloader.*']),
    # package_data={
    #     'chat_downloader': ['formatting/*.json']
    # },
    # test_suite='tests',
    # zip_safe=False,
)
