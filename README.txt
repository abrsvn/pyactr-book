pyactr-book
---------------------------

Python package to create and run ACT-R cognitive models.

This includes the (frozen) version of pyactr for the "Computational Cognitive Modeling and Linguistic Theory" book, with all the book code included.

Running the code
---------------------------

All the code for the book "Computational Cognitive Modeling and Linguistic Theory" is in the folder book-code. In order to run it, you need to install and use pyactr.

Installing and using pyactr on your computer -- people familiar with Python
---------------------------------------------------------------------------

You have several options. The safest one is to install the pyactr version that is present in this repo (called 'pyactr-frozen'). This is the frozen version that should allow you to run all the code from the book.

To install this, clone this repo, and then go to the folder pyactr-frozen and run:

python3 setup.py install

If you want the latest release of pyactr, you can also use pip:

pip3 install pyactr

Most likely, using the version from pip should work fine for all the code in the book. However, we cannot promise that all future updates of pyactr on pip will be compatible with all the code that appeared in this book. (But if you do encounter a case of incompatibility, please let us know.)

The usage of pyactr is explained in the book starting from Chapter 2. All the code discussed in the book can be found here as files in the folder book-code.

Installing and using pyactr -- beginners
----------------------------------------------------------

To get started, you should consider a web-based service for Python3 like PythonAnywhere. In this type of services, computation is hosted on separate servers and you don't have to install anything on your computer (of course, you'll need internet access). pyactr is a library for Python3, and you will have to install it on the web-based Python3 service. If you find that you like working with Python3 and pyactr, you can install them on your computer at a later point, together with a good text editor for coding -- Sublime, gedit, Vim, Emacs etc. (not Word) are suitable editor for programming. Alternatively,  you can install an integrated desktop environment (IDE) for Python -- a common choice is anaconda, which comes with a variety of ways of working interactively with Python (IDE with Spyder as the editor, ipython notebooks, nowadays known as jupyter notebooks etc.). But none of this is required to run pyactr and the code in this book.

Using PythonAnywhere:
    a. Go to www.pythonanywhere.com and sign up there.
    b. You'll receive a confirmation e-mail. Confirm your account / e-mail address.
    c. Log into your account on www.pythonanywhere.com.
    d. Click on Bash (below ``Start a new Console'').
    e. In Bash, type:
$ pip3 install --user pyactr

This will install pyactr in your Python account (not on your computer).

    f. Go back to Consoles. Start Python by clicking on any version 3.3 or higher.
    g. A console should open. Type:
import pyactr

If no errors appear, you are set. You might get a warning about the lack of tkinter support and that the simulation GUI is set to false. You can ignore this message.

Throughout the book, we will introduce and discuss various ACT-R models coded in Python. You can either type them in line by line or even better, load them as files in your session on PythonAnywhere. Scripts are uploaded in PythonAnywhere under the tab Files. You should be aware that a free account on PythonAnywhere allows you to run only two consoles, and there is a limit on the amount of CPU you might use per day. The limit should suffice for the tutorials but if you find this is too constraining, you should consider installing Python3 and pyactr on your computer and running scripts directly there.

Most likely, using the version of pyactr that you installed on PythonAnywhere should work fine for all the code in the book. However, what you just installed (pyactr) is an up-to-date package and we cannot promise that all future updates of pyactr will remain compatible with all the code that appeared in this book. If you do encounter a case of incompatibility, please let us know.

The usage of pyactr is explained in the book starting from Chapter 2. All the code discussed in the book can be found here as files in the folder book-code.

If you find you like working with pyactr, we suggest you install it on your computer. You will first have to install Pythoon version 3 on your computer. See here:

https://www.python.org/

After that, you can install pyactr. This is described in the section Installing and using pyactr on your computer, see above.

Documentation
--------------------------

More documentation about the package pyactr can be found in the pyactr GitHub repo. Go to:

https://github.com/jakdot/pyactr

Some of the documents are also collected here in the folder docs.

Requirements
--------------------------

pyactr requires Python3 (>=3.3), numpy, simpy and pyparsing; also requires tkinter if you want to see visual output of how ACT-R models interact with environment, but this is not necessary to run any models.
