========
Usage
========

To use gerritssh in a project::

	import gerritssh
	
The script, ``gsshcli``, will be installed as part of the ``pip install`` command.
It is not really meant to be used for real work, but does provide an example
of how to use the library.

For help, use the ``--help`` option, specifying the sub-command for more detailed help::

    $ gsshcli.py --help
    usage: gsshcli.py [-h] [-v] [-V] {projects,query,version} ...
    
    Simple CLI script to use gerritssh to talk to a site
    
    positional arguments:
      {projects,query,version}
        projects            List the projects
        query               Search for reviews
        version             Show the Gerrit version
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         set verbosity level [default: None]
      -V, --version         show program's version number and exit
                
    $ gsshcli.py query -h
    usage: gsshcli.py query [-h] [-s {open,merged,abandoned}] [-b BRANCH]
                            [-l MAXRESULTS] [-p PROJECT]
                            site ...
    
    positional arguments:
      site                  The Gerrit instance to connect to, e.g
                            review.openstack,org
      QUERY
    
    optional arguments:
      -h, --help            show this help message and exit
      -s {open,merged,abandoned}, --status {open,merged,abandoned}
                            Find all reviews with he given status
      -b BRANCH, --branch BRANCH
                            Restrict search to a given branch
      -l MAXRESULTS, --limit MAXRESULTS
                            Limit the number of results
      -p PROJECT, --project PROJECT
                            Project for which reviews are required
                            
    $ gsshcli.py projects --help
    usage: gsshcli.py projects [-h] [-a] site
    
    positional arguments:
      site        The Gerrit instance to connect to, e.g review.openstack,org
    
    optional arguments:
      -h, --help  show this help message and exit
      -a, --all   List all project types
      
    $ gsshcli.py version --help
    usage: gsshcli.py version [-h] site
    
    positional arguments:
      site        The Gerrit instance to connect to, e.g review.openstack,org
    
    optional arguments:
      -h, --help  show this help message and exit
 
Sample commands::

    $ gsshcli.py version review.openstack.org
    review.openstack.org is running version 2.4.4 of Gerrit
    $ gsshcli.py projects review.openstack.org
    ...
    $ gsshicli.py query review.openstack.org --project openstack-infra/gerritlib --status open
    ...
 

