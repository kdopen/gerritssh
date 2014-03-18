=======
Credits
=======

Development Lead
----------------

* Keith Derrick <kderrick_public@att.net>

Indirect Contributors
---------------------

* Eduardo Felipe for his backport of subprocess.check_output to python 2.6. 
  Available at https://gist.github.com/edufelipe/1027906. This was used in
  the initial version, before switching to paramiko.

* David Pursehouse and the people at Sony Xperia Developer World for their 
  excellent pygerrit repository at https://github.com/sonyxperiadev/pygerrit
  from which I have taken the core of the ssh.py module to avoid reinventing
  the wheel in gerritsite.py.

* Scott K Maxwell for providing a cross-version branch of Paramiko. This is
  available at https://github.com/scottkmaxwell/paramiko/tree/py3-support-without-py25.
  This has now been merged to master in the main paramiko repository and should
  be included in v1.14 of paramiko.

Direct Contributors
-------------------

None yet. Why not be the first?
