.. :changelog:

=============
Release Notes
=============

0.1.2 (2014-05-??)
------------------

* Fixes #1 - gsshcli.py requires __version__ attribute

  Moved VERSION.py to inside the package so the metadata is avaialable to
  the package and its clients, then modified setup.py and conf.py to use
  execfile to read the data for their own purposes.

0.1.1 (2014-05-23)
------------------

* Minor tweak for pip install

0.1.0 (2014-05-23)
------------------

* First release on PyPI.
