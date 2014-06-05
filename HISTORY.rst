.. :changelog:

=============
Release Notes
=============

0.1.3 (2014-06-04)
------------------

* Fixes #4 - Unit tests are not sufficient

  Added a baseline set of unit tests which perform end-to-end validation
  against a live Gerrit instance if GSSH_TEST_INSTANCE is set in the 
  environment.

* Corrects a bug found in the ssh client disconnect function by the new
  tests.

* Adds new and extended make targets to better clean and test the package.

* Updated documentation accordingly, including expanded testing information.

* Removed ``pypi`` from the list of environments used on travis-ci.

  The tests all run fine under pypi locally, but something in travis's
  pypi environment seems to be broken since they started supporting
  Python 3.4.

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
