from setuptools import setup

VERSION = '0.2.3-1'

setup(name='pyactr-book',
      version=VERSION,
      description='ACT-R in Python3, package frozen for the _Formal Linguistics and Cognitive Architecture_ book by Adrian Brasoveanu and Jakub Dotlacil; includes all code referred to in the book',
      url='https://github.com/jakdot/pyactr,https://github.com/abrsvn/pyactr-book',
      author='jakdot,abrsvn',
      author_email='j.dotlacil@gmail.com,abrsvn@gmail.com',
      packages=['pyactr-book'],
      install_requires=['numpy', 'simpy', 'pyparsing'],
      classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'Development Status :: 3 - Alpha', 'Topic :: Scientific/Engineering'],
      zip_safe=False)
