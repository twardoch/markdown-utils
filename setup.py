import os.path
from codecs import open

from setuptools import setup

try:
    from sh import pandoc

    isPandoc = True
except ImportError:
    isPandoc = False

# Get the long description from the README file
readmepath = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'README.md')
long_description = ''
if os.path.exists(readmepath):
    if isPandoc:
        long_description = pandoc(readmepath, read='markdown', write='rst')
    else:
        long_description = open(readmepath, encoding='utf-8').read()

setup(
    name='mdutils',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.4.5',

    description='Python package for working with Markdown. Includes `docxtomd`, a Word .docx to Markdown converted '
                'using `pandoc` and `wmf2svg`, and `wmftosvgpng`, an intelligent WMF to SVG or PNG converter using '
                '`wmf2svg`.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/twardoch/markdown-utils',
    download_url='https://github.com/twardoch/markdown-utils/archive/master.zip',

    # Author details
    author='Adam Twardoch',
    author_email='adam+github@twardoch.com',

    # Choose your license
    license='LICENSE',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: MacOS X',
        "Environment :: Console",
        'Operating System :: MacOS :: MacOS X',
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords=['Markdown', 'typesetting', 'pandoc', 'word', 'docx', 'wmf', 'svg'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['mdutils'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'sh>=1.11', 'scour>=0.35', 'pandocfilters>=1.4.1',
        'Markdown>=2.6.8', 'pymdown-extensions>=3.1.0', 'markdown-include>=0.5.1',
        'mdx_sections>=0.1', 'mdx_steroids>=0.4.0', 'Pillow>=4.2.1', 
    ],
    dependency_links=[
        'git+https://github.com/twardoch/markdown-steroids.git/@master#egg=mdx_steroids-0.4.0',
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'docxtomd=mdutils.docxtomd:main',
            'wmftosvgpng=mdutils.wmftosvgpng:main',
            'mkdocs2print=mdutils.mkdocs2print:main',
        ],
    },
)
