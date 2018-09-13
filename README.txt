pyactr-book
---------------------------

Python package to create and run ACT-R cognitive models.

This includes the (frozen) version of pyactr for the "Formal Linguistics and Cognitive Architecture" book, with all the book code included.

Running the code
---------------------------

All the code for the book "Formal Linguistics and Cognitive Architecture" is in the folder book-code. In order to run it, you need to install pyactr.

Installing pyactr
---------------------------

You have several options. The safest one is to install the pyactr version that is present in this repo (called 'pyactr-frozen'). This is the frozen version that should allow you to run all the code from the book.

To install this, clone this repo, and then go to the folder pyactr-frozen and run:

python3 setup.py install

If you want the latest release of pyactr, you can also use pip:

pip3 install pyactr

Most likely, using the version from pip should work fine for all the code in the book. However, we cannot promise that all future updates of pyactr on pip will be compatible with all the code that appeared in this book. (But if you do encounter a case of incompatibility, let us know.)

Documentation
--------------------------

More documentation about pyactr can be found in the pyactr GitHub repo. Go to:

https://github.com/jakdot/pyactr

Some of the documents are also collected here in the folder docs.

Requirements
--------------------------

pyactr requires Python3 (>=3.3), numpy, simpy and pyparsing; also requires tkinter if you want to see visual output of how ACT-R models interact with environment, but this is not necessary to run any models.
