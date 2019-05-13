#!/usr/bin/env python
# I shamefully ripped most of this off from fbconsole
# http://docs.python.org/distutils/setupscript.html
# http://docs.python.org/2/distutils/examples.html

from setuptools import setup
import re
import os

name = "decorators"
kwargs = {"name": name}

def read(path):
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            return f.read()
    return ""


vpath = os.path.join(name, "__init__.py")
if os.path.isfile(vpath):
    kwargs["packages"] = find_packages(exclude=["tests", "tests.*", "examples"])
else:
    vpath = "{}.py".format(name)
    kwargs["py_modules"] = [name]
kwargs["version"] = re.search(r"^__version__\s*=\s*[\'\"]([^\'\"]+)", read(vpath), flags=re.I | re.M).group(1)


kwargs["long_description"] = read('README.rst')


setup(
    description='Quickly create flexible Python decorators',
    keywords="decorators decorator @ at-syntax"
    author='Jay Marcyes',
    author_email='jay@marcyes.com',
    url='http://github.com/jaymon/{}'.format(name),
    license="MIT",
    classifiers=[ # https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    **kwargs
)
