r'''
Representations of a Gerrit site, and the abstract base class for all
executable commands.

All sessions with a Gerrit instance begin by creating a `Site` object and
establishing a connection::

    import gerritssh as gssh
    mysite = gssh.Site('gerrit.exmaple.com').connect()

Commands are executed by creating an instance of a `SiteCommand` concrete
class, and then executing them against the `Site` object. The following
snippet will connect to a site, and then print out a list of all open
reviews by project::

    import gerritssh as gssh
    mysite = gssh.Site('gerrit.example.org').connect()
    lsprojects = gssh.ProjectList()
    lsprojects.execute_on(mysite)

    for p in lsprojects:
        openp = gssh.open_reviews(project=p).execute_on(mysite)
        if not openp:
            continue

        print('\n{0}\n{1}\n'.format(p, '=' * len(p)))
        for r in openp:
            print('{0}\t{1}\n'.format(r.ref, r.summary))


This example also shows both ways of iterating over the results from
executing a command. The line ``for p in lsprojects`` iterates
directly over the `ProjectList` object, while the line ``for r in openp:``
iterates over the list of results returned by calling `execute_on`

.. note::
    This module was original called simply 'site', but that clashed
    with the built in site module which is automatically imported during
    initialization. This lead to strange failures during runs of ``tox`` that
    took a little while to debug.

'''

import logging
import re
import json
import collections
import abc


from gerritssh import GerritsshException
from gerritssh.borrowed import ssh

_logger = logging.getLogger(__name__)


class SSHConnectionError(GerritsshException):
    '''
    Raised when a Site object fails to connect via SSH, or when
    a method is called on an unconnected site which requires a
    connection.

    '''
    pass


class InvalidCommandError(GerritsshException):
    '''
    Raised when an attempt is made to execute a BaseCommand object.
    '''
    pass


class Site(object):
    '''
    An individual Gerrit site.

    An object of this class manages all access, execution of commands, etc.

    :param str sitename:
        The top level URL for the site, e.g. 'gerrit.example.com'

    :raises: TypeError if sitename is not a string

    Usage::

        import gerritssh
        try:
            mysite = gerritssh.Site('gerrit.example.com').connect()
            msg = 'Connected to {}, running Gerrit version {}'
            print(msg.format(mysite.site, mysite.version)
        except gerritssh.SSHConnectionError:
            print('Failed to connect to site '+mysite.site)

    '''

    def __init__(self, sitename, username=None, port=None):
        if not isinstance(sitename, str):
            raise TypeError('sitename must be a string')

        self.__init_args = (sitename, username, port)
        self.__site = sitename
        self.__ssh_prefix = 'gerrit'
        self.__version = (0, 0, 0)
        self.__ssh = ssh.GerritSSHClient(sitename, username, port)

    def __repr__(self):
        return ('<gerritssh.gerritsite.Site(site=%s, connected=%s)>'
                % (self.site, self.connected))

    def copy(self):
        '''
        Construct an unconnected copy of this Site.

        This can be used to create additional Site instances from one
        which has already been initialized. An obvious use would be to
        open multiple connections to the same site, from a point in the
        code which is not aware of the initial values used to identify
        the Gerrit instance.

        for example::

            # In the command line parsing module
            site = gerritssh.Site(sitename, username, port).connect()
            ...

            # In another module:
            def new_connection(asite):
                return asite.copy().connect()

        This method is aliased by __copy__ and __deepcopy__ and allows
        Site objects to be safely used with copy.copy() and copy.deepCopy()

        '''
        return Site(*self.__init_args)

    # Alias the magic methods used by the copy module
    __copy__ = copy

    def __deepcopy__(self, memo):
        '''
        Deep copies are potentially dangerous. In this case we simply return
        a new, shallow copy

        '''
        return self.copy()

    def __extract_version(self, vstr):
        results = re.search(r'gerrit version (\d+)\.(\d+)\.(\d+).*$', vstr)
        vnums = results.groups() if results else (0, 0, 0)
        return tuple(int(s) for s in vnums) if len(vnums) == 3 else (0, 0, 0)

    def __do_command(self, command, args=''):
        '''
        Private method to actually execute a command

        :returns [str]: The output from the command as a list of strings
        :raises: :exc: `SSHException` if the command fails

        '''
        cmdline = '{0} {1} {2}'.format(self.__ssh_prefix, command, args)
        _logger.debug('Executing: %s' % cmdline)
        result = self.__ssh.execute(cmdline)
        _logger.debug('Response:%s' % repr(result))
#         return result if isinstance(result, str) else result.decode('utf-8')
        return [l for s in result.stdout.readlines() for l in s.splitlines()]

    def connect(self):
        '''
        Establish an SSH connection to the site

        :returns: self to allow chaining

        :raises: `SSHConnectionError`
            if it is not possible to connect to the site

        '''
        if self.connected:
            return

        _logger.debug('Attempting to connect to site: {0}'.format(self.site))

        try:
            resp = self.__do_command('version')
        except ssh.SSHException:
            raise SSHConnectionError('Failed to connect to ' + self.site)

        _logger.debug('Connected OK: resp: {0}'.format(resp[0].strip()))
        self.__version = self.__extract_version(resp[0])
        return self

    def disconnect(self):
        '''
        Terminate the connection to the site

        :returns: self to allow chaining

        '''
        self.__ssh.disconnect()
        return self

    def execute(self, cmd):
        '''
        Execute a command and return the results

        :param cmd: The command to execute as either a `SiteComand` object,
            or a string. If a SiteCommand object is passed in, double-dispatch
            is used to evaluate the command. Otherwise, the string is treated
            as a valid command string and executed directly.

        :returns [str]:
            A list of stripped strings containing the output of the command.

        :raises:
            `InvalidCommandError` if the cmd object does not report a valid
            command

        :raises:
            `SSHConnectionError` if there is no current connection to the site

        :raises:
            `CalledProcessError` if the command returns an error

        '''
        if not self.connected:
            raise SSHConnectionError('No connection')

        if isinstance(cmd, SiteCommand):
            return cmd.execute_on(self)
        elif cmd and not isinstance(cmd, str):
            raise InvalidCommandError(('Expected an instance of SiteCommand,'
                                       ' or a string. Got ')
                                      + str(type(cmd)))

        if not cmd:
            raise InvalidCommandError('No command found')

        return self.__do_command(cmd)

    @property
    def site(self):
        '''
        The original site name provided to the constructor

        This needs to be an immutable attribute of the instance once
        it is created,hence the definition of a 'read-only' property.

        '''
        return self.__site

    @property
    def version(self):
        '''
        After connection, provides the version of Gerrit running on the site.

        :returns:
            A tuple containing the (major,minor,patch) values extracted from
            the response to a 'gerrit version' command.

            Before connecting, or if a valid version number can not be found
            in the response from Gerrit, it has the value (0,0,0).

        This needs to be an immutable attribute of the instance once
        it is created,hence the definition of a 'read-only' property.

        '''
        return self.__version

    def version_at_least(self, major, minor=0, patch=0):
        '''
        Compare the version of the connected site and return true if it
        is greater than or equal to the provided tuple.

        Useful in supporting specific versions of Gerrit.

        :param (major,minor,patch): The version to use in the comparison.

        :returns: A Boolean result of the comparison.
        :raises: SSHConnectionError if there is no connection

        '''
        if not self.connected:
            raise SSHConnectionError('Site is not connected')

        return self.version >= (major, minor, patch)

    @property
    def connected(self):
        ''' Indicates if there is a connection active. '''
        return self.__ssh.connected


# The unusual class definition is a version-agnostic means
# of setting the metaclass attribute for the class. It creates, at runtime,
# a temporary class 'newbase' with a meta-class of ABCMeta and base class of
# object which is then used as a the base class for SiteCommand, allowing it
# to inherit the metaclass. See the documentation of type() for details.

class SiteCommand(abc.ABCMeta('newbase', (object,), {})):
    '''
    Base class for a command to be executed against a :class:`Site`

    This is not meant to be used directly by clients. Instead is allows for
    duck-typing of sub-classes representing the various Command Line tools
    supported by Gerrit. Clients can use this to support commands which are
    missing from the release version of gerritssh or to create macro commands.

    The key method to override is :meth:`execute_on` which uses the provided
    Site object to actually implement the command. The method returns its
    results, usually as an iterable. The parameters for the command are
    meant to be provided to the constructor.

    On completion, the `execute_on` method should store its results in
    self._results as an iterable object, to allow iteration over the object.

    For example, a class to represent the ls-projects command, with the
    response in JSON format (on a site which supports it) might declare the
    method as follows::

        class JSONProjects(SiteCommand):
            def __init__(self):
                super(JSONProjects,self).__init__()

            def execute_on(self, site):
                self._results = site.execute('ls-projects --format JSON')
                return self._results

    and be used thus::

        site=Site('gerrit.example.com').connect()
        cmd=JSONProjects()
        projects = cmd.execute_on(site)

    or, the command object can be passed to the site (useful in building
    macro operations)::

        site=Site('gerrit.example.com').connect()
        cmd=JSONProjects()
        projects = site.execute(cmd)

    Either way, providing the SiteCommand class sets _results properly,
    the caller can then iterate over the results in two ways. By directly
    iterating over the returned value::

        projects = site.execute(cmd)
        for p in projects:
            pass

    or, by iterating over the command object itself::

        site.execute(cmd) # or cmd.execute_on(site)
        for p in cmd:
            pass

    '''

    def __init__(self):
        self._results = []

    def __iter__(self):
        '''
        Allows iteration through the results of the last command execution

        '''
        return iter(self._results)

    @property
    def results(self):
        ''' Results from the most recent execution '''
        return self._results

    @abc.abstractmethod
    def execute_on(self, the_site):
        '''
        Execute the command on the given site

        This method must be overridden in concrete classes, and thus the
        base class implementation guaranteed to raise an exception.

        :raises: TypeError
        '''

    @staticmethod
    def text_to_list(text, nonempty=False):
        r'''
        Split a single string containing embedded newlines into a list
        of trimmed strings

        Useful for cleaning up multi-line output from commands.

        :param str text: String with embedded newlines
        :param bool nonempty:
            If true, all empty lines will be removed from the output.

        :returns [str]: List of stripped strings, one string per embedded line.
        :raises: :exc:`TypeError` if `text` is not a string

        Usage::
            >>> SiteCommand.text_to_list('a\n \nb')
            ['a', '', 'b']
            >>> SiteCommand.text_to_list('a\n \nb\n', True)
            ['a', 'b']

        '''
        if not isinstance(text, str):
            raise TypeError('Argument must be a string')
        stripempty = lambda x: x if nonempty else True
        stripped_list = [l.strip() for l in text.splitlines()]
        return [l for l in stripped_list if stripempty(l)]

    @staticmethod
    def text_to_json(text_or_list):
        '''
        Convert one or more JSON strings to a list of dictionaries.

        Every string is split and stripped (via :meth:`text_to_list`)
        before decoding. All empty strings (or substrings) are ignored.

        :param text_or_list:
            Either a single string, or a list of strings to be interpreted as
            JSON.
        :returns [dict]:
            A list of dictionaries, one per string, produced by interpreting
            each string JSON.
        :raises:
            :exc:`TypeError` if text_or_list` is not one or more strings or if
            one of the strings can't be decode as valid JSON.

        '''
        if isinstance(text_or_list, str):
            text_or_list = SiteCommand.text_to_list(text_or_list,
                                                    nonempty=True)

        if not (isinstance(text_or_list, collections.Iterable) and
                all([isinstance(x, str) for x in text_or_list])):
            raise TypeError('Argument must be one or more strings')

        jstrings = [s for l in text_or_list
                    for s in SiteCommand.text_to_list(l, nonempty=True)]
        return [json.loads(s) for s in [_f for _f in jstrings if _f]]

__all__ = ['Site', 'SSHConnectionError', 'InvalidCommandError', 'SiteCommand']
