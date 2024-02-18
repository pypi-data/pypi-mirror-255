import ast
import os.path
import re

from setuptools import find_packages, setup


NAME = 'biopax_explorer'
DESCRIPTION = 'A python library for BIOPAX manipulation'
URL = 'https://forgemia.inra.fr/pegase/biopax-explorer'
EMAIL = 'fjrmoreews@gmail.com'
AUTHOR = 'FJR Moreews'
REQUIRES_PYTHON = '>=3.8.10'
 





# What packages are required for this module to be executed?
REQUIRED = [
  'rdfobj',
  'ipywidgets==8.1.1',
  'ipycytoscape==1.3.3'
]

# What packages are optional?
EXTRAS = {
  'testing': ["pytest"]
}

def findVersion(pkname,srcfile):
 
    vers="0.0.0" 

    reg = re.compile(r'__version__\s*=\s*(.+)')
    with open(os.path.join(pkname, srcfile)) as f:
 
      for line in f:
        print(line) 
        m = reg.match(line)
        if m:
            vers = ast.literal_eval(m.group(1))
 
            break
    return vers


ldescription=open('README.md').read()

setup(
   name=NAME,
   version=findVersion(NAME, '__init__.py'),
   description=DESCRIPTION,
   long_description=ldescription,
   long_description_content_type='text/markdown',
   author=AUTHOR,
   author_email=EMAIL,
   url=URL,
#   packages=[NAME],
   packages=find_packages(exclude=['tests']),
   license='MIT',
   platforms="Posix; MacOS X;",
   classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
   zip_safe=False,
   package_dir={NAME:NAME}, #important 
   package_data={
      NAME: [
             
              'resources/*', NAME+'/resources/*',
              'data/*', NAME+'/data/*'
            ]
   },
   python_requires=REQUIRES_PYTHON,
   install_requires=REQUIRED,
   extras_require=EXTRAS,
)

 


 
