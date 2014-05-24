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

"""
Gerrit SSH Client.

A thin wrapper/extension of Paramiko's SSHClient class, adding logic
to parse the standard configuration file from ~/.ssh.

It also provides lightweight threading protection to allow a single
connection to be used by multiple threads.

"""

from os.path import abspath, expanduser, isfile
import socket
from threading import Event, Lock

from paramiko import SSHClient, SSHConfig
from paramiko.ssh_exception import SSHException


class SSHCommandResult(object):
    """
    Represents the results of a command run over SSH.

    The three attributes are channels representing the
    three standard streams.

    :param stdin:  The channel's input channel
    :param stdout: Standard output channel
    :param stderr: The error output channel

    """

    def __init__(self, command, stdin, stdout, stderr):
        self.command = command

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        return "<SSHCommandResult [%s]>" % self.command


class GerritSSHClient(SSHClient):

    """
    Gerrit SSH Client, extending the paramiko SSH Client.

    :param hostname:     The host to connect to
    :param username:     The optional user name to use on connection
    :param port:         The optional port to use
    :param keyfile_name: The optional key file to use

    """

    def __init__(self, hostname, username=None, port=None, keyfile_name=None):
        """ Initialize and connect to SSH. """
        super(GerritSSHClient, self).__init__()
        self.hostname = hostname
        self.username = username
        self.key_filename = keyfile_name
        self.port = port
        self.__connected = Event()
        self.lock = Lock()

    def _configure(self):
        """
        Configure the ssh parameters from the config file.

        The Port and username are extracted from .ssh/config, unless
        overridden by arguments to the constructor.

        If username and or port are provided to `__init__`, they will
        override the values found in the configuration file.


        :raise:
            SSHException under the following conditions:

            * No configuration file is found
            * It does not contain an entry for the Host.
            * It references a keyfile which does not exist
            * The port number is non-numeric or negative
            * Values for port and username can not be determined

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

        if self.key_filename:
            self.key_filename = abspath(expanduser(self.key_filename))
        elif 'identityfile' in data:
            self.key_filename = abspath(expanduser(data['identityfile'][0]))

        if self.key_filename and not isfile(self.key_filename):
            raise SSHException("Identity file '%s' does not exist" %
                               self.key_filename)

        if self.port is None:
            try:
                self.port = int(data.get('port', '29418'))
            except ValueError:
                raise SSHException("Invalid port: %s" % data['port'])

        config_data = (self.hostname, self.port, self.username)
        if not all(config_data):
            raise SSHException("Missing configuration data in %s" % configfile)

    def _do_connect(self):
        """
        Actually connect to the remote.

        :raise: SSHException if connection fails.

        """
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

        Ensure we're _connected to the remote server, and run `command`.

        :return: the results as an `SSHCommandResult`.

        :raise:
            `ValueError` if `command` is not a string, or `SSHException` if
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
        '''
        Does the client have an open conection?

        :return: True if the client is connected
        '''
        return self.__connected.is_set()

    def disconnect(self):
        '''
        Close any open connection

        :return: self to allow chaining
        '''
        self.lock.acquire()

        try:
            if self.connected():
                self.close()
                self.__connected.clear()
        finally:
            self.lock.release()

        return self
