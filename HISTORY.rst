.. :changelog:

=============
Release Notes
=============

0.1.2 (2014-06-03)
------------------

* Fixes #1 - gsshcli.py requires __version__ attribute

  Moved VERSION.py to inside the package so the metadata is avaialable to
  the package and its clients, then modified setup.py and conf.py to use
  execfile to read the data for their own purposes.

* Fixes #2 - gsshcli.py query command fails when --limit option used 

  The demo script now reconstitues all option arguments as strings.
  
* Fixes #3 - Query command throws TypeError under Python2.7

  The JSON responses from the query command are correctly converted to
  strings in Python 2.x.
  
* Initiates unit-test coverage reporting via coveralls.io

0.1.1 (2014-05-23)
------------------

* Minor tweak for pip install

0.1.0 (2014-05-23)
------------------

* First release on PyPI.
