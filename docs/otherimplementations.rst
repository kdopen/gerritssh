=====================
Other Implementations
=====================

Any quick perusal of pypi will show a large collection of existing Python
libraries and packages which provide similar features and capabilities. This
raises the obvious question, "Why yet another library?". The answer to that
question is many-fold.

* First, see the `Rationale` above. I needed *something* to act as a vehicle
  for this learning exercise. I could hardly take over someone else's project
  and experiment with all the things I wanted to try. Gerrit, and its SSH API
  is something I currently deal with on a daily basis, so this has the small
  chance of being useful to me.
  
* The nature of the Open Source community is somewhat darwinian. In almost
  any area, there are multiple choices and implementations. Eventually, the
  best ones become widely adopted and over time de-facto standards evolve. I
  don't seriously expect this library to reach that level of acceptance, but
  you never know.
  
* None of the others worked quite the way I wanted, and I'm not sure my own
  vision would match that of their owners. And producing my own clone, or
  wrapping their version would be almost as much work as writing one from
  scratch.
  
That's not to say there are not features and/or ideas in those projects which
are not inspiring. I have borrowed shamelessly when it makes sense. See the
Indirect Contributors section under Contributing for the appropriate credits.

The following subsections indicate the issues I was concerned with in each
implementation.

Openstack's gerritlib
---------------------

ssh://review.openstack.org/openstack-infra/gerritlib

The underlying implementation has the following shortcomings from my point of view:

* The query and bulk_query operations are broken if a query generates more than
  500 results. The actual number is a configuration option for the Gerrit instance
  but this is typical. If the limit is reached, Gerrit returns a subset of results
  and provides a sortkey which can be used to fetch the next set. Gerritlib ignores
  this.
  
* Every SSH command creates a new session, with the full overhead of logging in. This
  seems to defeat the value of creating a connection once and then using it for a
  sequence of commands. My hope was to avoid this overhead once I switched to Paramiko.
  
* The list of commands is embedded in the main class, making it difficult for library
  clients to add support for new commands.
  
It does, however, provide a useful reference in understanding how to use some of
Paramiko's features.

gerrit-cli
----------

git@github.com:FlaPer87/gerrit-cli.git

This is basically a command line interface to for python-gerrit.

gerritrestclient
----------------

git@github.com:lann/gerritrestclient.git

The name says it all. I'm interested in the command line API, not the REST one. Though
I may eventually use REST to implement more advanced features.

pygerrit
--------

git@github.com:sonyxperiadev/pygerrit.git

This one has many interesting ideas and is pretty close to what I had in mind. Had I
been pressed for time, I may well have forked this and bent it to my will. But, as
previously mentioned, I really wanted to develop something from scratch.

It still fails with really large result sets, but does reuse the same SSH connection
for sequences of commands. 

I have borrowed large parts of the ssh module from this library.

python-gerrit
-------------

git@github.com:FlaPer87/python-gerrit.git

This is a partial implementation, with numerous performance issues. It is also focused
on the ``gerrit review`` command, which is not particularly of interest to me.

However, the 'filters' module (and its representation of AND and OR terms) is simple
and elegant. I intend to leverage that in a future version.

