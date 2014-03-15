# The MIT License
#
# Copyright 2012 Sony Mobile Communications. All rights reserved.
# Copyright 2014 Keith Derrick
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Gerrit SSH Client. """

from os.path import abspath, expanduser, isfile
import socket
from threading import Event, Lock

from paramiko import SSHClient, SSHConfig
from paramiko.ssh_exception import SSHException


class SSHCommandResult(object):

    """ Represents the results of a command run over SSH. """

    def __init__(self, command, stdin, stdout, stderr):
        self.command = command

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        return "<SSHCommandResult [%s]>" % self.command


class GerritSSHClient(SSHClient):

    """ Gerrit SSH Client, wrapping the paramiko SSH Client. """

    def __init__(self, hostname, username=None, port=None):
        """ Initialise and connect to SSH. """
        super(GerritSSHClient, self).__init__()
        self.hostname = hostname
        self.username = username
        self.key_filename = None
        self.port = port
        self.__connected = Event()
        self.lock = Lock()

    def _configure(self):
        """
        Configure the ssh parameters from the config file.

        The Port and username are extracted from .ssh/config, unless
        overridden by arguments to the constructor.

        """
        configfile = expanduser("~/.ssh/config")

        if not isfile(configfile):
            raise SSHException("ssh config file '%s' does not exist" %
                               configfile)

        config = SSHConfig()
        config.parse(open(configfile))
        data = config.lookup(self.hostname)

        if not data:
            raise SSHException("No ssh config for host %s" % self.hostname)

        self.hostname = data.get('hostname', None)

        if not self.username:
            self.username = data.get('user', None)

        if 'identityfile' in data:
            key_filename = abspath(expanduser(data['identityfile'][0]))

            if not isfile(key_filename):
                raise SSHException("Identity file '%s' does not exist" %
                                   key_filename)
            self.key_filename = key_filename

        if self.port is None:
            try:
                self.port = int(data.get('port', '29418'))
            except ValueError:
                raise SSHException("Invalid port: %s" % data['port'])

        if not (self.hostname and self.port and self.username):
            raise SSHException("Missing configuration data in %s" % configfile)

    def _do_connect(self):
        """ Connect to the remote. """
        self.load_system_host_keys()

        if self.username is None or self.port is None:
            self._configure()

        try:
            self.connect(hostname=self.hostname,
                         port=self.port,
                         username=self.username,
                         key_filename=self.key_filename)
        except socket.error as e:
            raise SSHException("Failed to connect to server: %s" % e)

    def _connect(self):
        """ Connect to the remote if not already _connected. """
        if not self.connected:
            try:
                self.lock.acquire()
                # Another thread may have _connected while we were
                # waiting to acquire the lock
                if not self.connected:
                    self._do_connect()
                    self.__connected.set()
            except SSHException:
                raise
            finally:
                self.lock.release()

    def execute(self, command):
        """ Run the given command.

        Make sure we're _connected to the remote server, and run `command`.

        Return the results as a `SSHCommandResult`.

        Raise `ValueError` if `command` is not a string, or `SSHException` if
        command execution fails.

        """
        if not isinstance(command, str):
            raise ValueError("command must be a string")

        self._connect()

        try:
            stdin, stdout, stderr = self.exec_command(command,
                                                      bufsize=1,
                                                      timeout=None,
                                                      get_pty=False)
        except SSHException as err:
            raise SSHException("Command execution error: %s" % err)

        return SSHCommandResult(command, stdin, stdout, stderr)

    @property
    def connected(self):
        return self.__connected.is_set()

    def disconnect(self):
        self.lock.acquire()

        try:
            if self.connected():
                self.close()
                self.__connected.clear()
        finally:
            self.lock.release()

        return self
