============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given. 

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/kdopen/gerritssh/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it. Or look at the `Planned Features`
section of the README file.

Write Documentation
~~~~~~~~~~~~~~~~~~~

`gerritssh` could always use more documentation, whether as part of the 
official `gerritssh` docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/kdopen/gerritssh/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `gerritssh` for
local development.

#. Fork_ the `gerritssh` repo on GitHub.
#. Create a virtual-environment (you *are* using vitualenv, aren't you?)
#. Clone your fork locally and install the basic requirements::

    $ git clone git@github.com:your_name_here/gerritssh.git
    $ cd gerritssh
    $ pip install -r requirements.txt

#. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

#. When you're done making changes, check that your changes pass style and unit
   tests, including testing other Python versions with tox::

    $ tox

   To get ``tox`` and the other test-related tools, just::

    $ pip install -r test-requirements.txt
    
   .. note::
      ``tox`` is configured to apply style checks using ``flake8``, including 
      ``pep8-naming``. Line length limits are set to trigger at 79 characters,
      which will explain some of the seemingly strange layouts of strings and
      expressions.

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

#. Don't expect to get 100% coverage (via ``make coverage``), as there are
   code sections which only activate on specific versions of Python (a cost
   of cross-version support).

#. Submit a pull request through the GitHub website.

.. _Fork: https://github.com/kdopen/gerritssh/fork

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

#. The pull request should include tests.
#. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
#. The pull request should work for Python 2.6, 2.7, 3.3, and 3.4.
   Check https://travis-ci.org/kdopen/gerritssh 
   under pull requests for active pull requests or run the ``tox`` command and
   make sure that the tests pass for all supported Python versions.
   
.. note::
    ``gerritssh`` uses the git-flow branching model. Please request that
    your pull-request be merged to the ``develop`` branch, and ensure your
    changes are based on the ``develop`` branch.

Testing
-------

To run a subset of tests::

	 $ py.test test/test_<module>.py
	 
where ``<module>`` is the name of the actual submodule you wish to test.

To run tests on all Python versions::

    $ make test-all 
      or
    $ tox

To ensure that you have not introduced any errors which would only show up when
actually communicating with a real Gerrit instance, there are a set of tests
which perform no mocking, and actually 'reach out' to a live instance. If you
have an account with review.openstack.org - and have added your public key -
simply run::

    $ make test-all-online
      or
    $ make test-online

If you have an account on a different Gerrit instance, you can test against it
instead::

    $ GSSH_TEST_INSTANCE='gerrit.mysite.com' tox
      or 
    $ GSSH_TEST_INSTANCE-'gerrit.mysite.com' py.test
