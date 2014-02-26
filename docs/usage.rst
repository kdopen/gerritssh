========
Usage
========

To use gerritssh in a project::

	import gerritssh
	
The script, gsshcli, will be installed as part of the ``pip install`` command.
It is not really meant to be used for real work, but does provide an example
of how to use the library.

For help::

    $ gsshcli.py --help
    usage: gsshcli.py [-h] [-v] [-V] site {projects,query,version} ...
    
    Simple CLI script to use gerritssh to talk to a site
    
    positional arguments:
      site                  The Gerrit instance to connect to, e.g
                            review.openstack,org
      {projects,query,version}
        projects            List the projects
        query               Search for reviews
        version             Show the Gerrit version
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         set verbosity level [default: None]
      -V, --version         show program's version number and exit    
    $
    
