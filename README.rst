=========
gerritssh
=========

.. image:: https://badge.fury.io/py/gerritssh.png
    :target: http://badge.fury.io/py/gerritssh
    
.. image:: https://travis-ci.org/kdopen/gerritssh.png?branch=master
        :target: https://travis-ci.org/kdopen/gerritssh

.. image:: https://pypip.in/d/gerritssh/badge.png
        :target: https://crate.io/packages/gerritssh?version=latest


Python package wrapping the Gerrit command line API.

This is very much a work in progress, and intended to be the basis
for building more sophisticated scripts and applications, for example
automating complex work flows in large projects.

Rationale
---------

This project was started as a test-bed for me to explore the wider
world of Python, such as:

* Unit testing
* Continuous Integration
* Sphinx rst documentation
* tox, flake8, etc.
* Supporting multiple versions of Python.
* Pythonic style

Basically, everything that goes into making an industrial-strength Python
library or application. So you are going to see novice mistakes and code
which is not idiomatic. 

All contributions and suggestions are welcome, and indeed that's the logic
behind making this open source. I want to learn from the experience of those
who've been there before me.


Features
--------

* Handles the low-level details of the gerrit SSH command line syntax.

* Makes the results of those commands available to the programmer in a
  format which is more natural for Python programmers to manipulate.

* Is aware of which combinations of commands and versions are supported
  for versions of Gerrit from 2.4 through 2.8.
  
* Supports Python 2.6, 2.7, 3.3, and 3.4


Planned Features
----------------

* Support options-versioning on the query command

* Support a broad range of commands including the latest commands for Gerrit
  v2.8 (such as ls-members)

* Add a module to operate on sets of Review objects to perform more
  complex searches, such as building dependency graphs of open reviews.
  
* Add support for the administrators ``gsql`` command

  * Implement queries such as examining the audit trail on group membership
  
  * Wrapping generation of properly quoted SQL statements
  
  * Extract the SCHEMA information with a ``\d`` command and dynamically
    clone the database into a memory-resident sqlite database.
    
* Implement support for the stream-events command, serving up events
  using an observer-pattern approach to allow many threads to consume
  events.

Feedback
--------

If you have any suggestions or questions about **gerritssh** feel free to email me
at kderrick_public@att.net.

If you encounter any errors or problems with **gerritssh**, please let me know!
Open an Issue at the GitHub http://github.com/kdopen/gerritssh main repository.
