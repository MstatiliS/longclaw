#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import subprocess

from setuptools import setup
from setuptools.command.sdist import sdist as base_sdist


class sdist(base_sdist):
    """
    Regular sdist class plus compilation of front end assets
    """

    def compile_assets(self):
        """
        Compile the front end assets
        """
        try:
            # Move into client dir
            curdir = os.path.abspath(os.curdir)
            client_path = os.path.join(os.path.dirname(__file__), 'longclaw', 'client')
            os.chdir(client_path)
            subprocess.check_call(['npm', 'install'])
            subprocess.check_call(['npm', 'run', 'build'])
            os.chdir(curdir)
        except (OSError, subprocess.CalledProcessError) as err:
            print('Error compiling assets:  {}'.format(err))
            raise SystemExit(1)

    def run(self):
        self.compile_assets()
        base_sdist.run(self)


def get_version(*file_paths):
    """Retrieves the version from longclaw/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("longclaw", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist bdist_wheel')
    os.system('python -m twine upload --verbose dist/*')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

try:
    readme = open('README.rst').read()
    history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')
except IOError:
    # Protects against running python from a different dir to setup.py,
    # e.g. on travis
    readme = ''
    history = ''

setup(
    name='longclaw',
    version=version,
    description="""A shop for wagtail cms""",
    long_description=readme + '\n\n' + history,
    author='James Ramm',
    author_email='jamessramm@gmail.com',
    url='https://github.com/JamesRamm/longclaw',
    packages=[
        'longclaw',
    ],
    include_package_data=True,
    install_requires=[
        'django==3.2.7',
        'wagtail==2.13.*',
        'django-countries==7.2.1',
        'django-extensions==3.1.3',
        'djangorestframework==3.12.4',
        'django-ipware==4.0.0',
        'django-polymorphic==3.0.0',
    ],
    license="MIT",
    zip_safe=False,
    keywords='longclaw',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points="""
        [console_scripts]
        longclaw=longclaw.bin.longclaw:main
    """,
    cmdclass={
        'sdist': sdist
    }
)
