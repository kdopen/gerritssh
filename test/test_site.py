"""
Tests for `site` module.
"""
import pytest
import gerritssh
from paramiko.ssh_exception import SSHException


@pytest.fixture
def mocked_output(connected_site):

    def helper(f, connected=False):
        class DummySSHClient(object):

            def __init__(self):
                self.connected = connected

            def execute(self, command):
                import io
                import sys
                from gerritssh.borrowed.ssh import SSHCommandResult
                self.connected = True

                cresult = f(command)
                if sys.version_info[0] < 3:
                    cresult = unicode(cresult)

                return SSHCommandResult(command,
                                        io.StringIO(),
                                        io.StringIO(cresult),
                                        io.StringIO())

            def disconnect(self):
                self.connected = False

        connected_site._Site__ssh = DummySSHClient()
        return connected_site
    return helper


class DummyCommand(gerritssh.SiteCommand):
    def __init__(self, v=None, oset=None, ostr=None):
        super(DummyCommand, self).__init__(v, oset, ostr)

    def execute_on(self, site):
        super(DummyCommand, self).execute_on(site)


def test_init():
    s = gerritssh.Site('gerrit.example.com')
    assert s, 'Failed to create a Site object'
    assert s.site == 'gerrit.example.com', \
    'Did not record the site name properly'
    assert repr(s) == ("<gerritssh.gerritsite.Site(args=('gerrit.example.com',"
                       " None, None, None), connected=False)>")

    with pytest.raises(TypeError):
        _ = gerritssh.Site(1)


def test_connect_returns_version(connected_site):
    ''' Mock check_output to return a known version string '''
    s = connected_site
    v = s.version
    c = s.connected
    assert str(v) == '2.9.0'
    assert c, 'Not connected'
    s.connect()  # SHould not raise any problems
    assert s.connected, 'Second call to connect() changed state'


def test_failed_connection1(mocked_output):
    ''' Mock check_output to throw the CalledProcessError'''
    def raiseerror(cmd):
        raise SSHException('cmd = ' + cmd)

    s = mocked_output(raiseerror)
    with pytest.raises(gerritssh.SSHConnectionError): s.connect()


def test_failed_connection2(mocked_output):
    '''Mock check_output to throw TypeError'''
    def raiseerror(cmd): raise TypeError('cmd = ' + cmd)
    s2 = mocked_output(raiseerror)
    with pytest.raises(TypeError): s2.connect()


def test_failed_connection3():
    '''
    Use a clearly invalid site name to ensure the connection
    attempt fails
    '''
    s = gerritssh.Site('...')
    with pytest.raises(gerritssh.SSHConnectionError): s.connect()


def test_disconnect(connected_site):
    s = connected_site
    s.disconnect()
    assert not s.connected, 'Did not disconnect'
    s.disconnect()  # Should not raise an exception
    assert not s.connected, 'Reconnected'


def test_execute_none(connected_site):
    with pytest.raises(gerritssh.InvalidCommandError):
        connected_site.execute(None)
    with pytest.raises(gerritssh.InvalidCommandError):
        connected_site.execute(1)


def test_execute_string(mocked_output):
    def echo(cmd):
        return cmd.strip()
    s = mocked_output(echo, connected=True)
    resp = s.execute('somecommand')
    assert len(resp) == 1
    assert resp[0] == ' '.join(['gerrit', 'somecommand'])


def test_execute_cmd(connected_site):
    lp = gerritssh.ProjectList()
    p = connected_site.execute(lp)
    assert p
    assert len(p) == 1
    assert p[0] == 'gerrit version 2.9.0'


def test_extract_version():
    s = gerritssh.Site('...')
    ev = s._Site__extract_version
    assert ev('gerrit version 1') == '0.0.0'
    assert ev('gerrit version 1.2') == '0.0.0'
    assert ev('gerrit version 1.2.3') == '1.2.3'
    assert ev('gerrit version 1-2ab') == '0.0.0'
    assert ev('gerrit version 1ab') == '0.0.0'
    assert ev('gerrit version abc') == '0.0.0'
    assert ev('g') == '0.0.0'
    assert ev('gerrit  1.2.3') == '0.0.0'
    assert ev('gerrit version 1 2 3') == '0.0.0'
    assert ev('gerrit version 1 abc 2') == '0.0.0'
    assert ev('gerrit version 1.2.3abcd') == '1.2.3'
    assert ev('gerrit version 2.4.4-14-gab7f4c1') == '2.4.4'


def test_version_compare(connected_site):
    with pytest.raises(gerritssh.SSHConnectionError):
        gerritssh.Site('...').version_in('>=2.10')

    s = connected_site
    ev = s.version_in
    v = s.version  # unused but useful if test fails
    assert ev('==2.9.0')
    assert ev('>=2')
    assert ev('==2.9')
    assert not ev('==1.1')
    assert ev('>=1.9,<=3.1')


def test_not_connected(connected_site):
    connected_site.disconnect()
    assert not connected_site.connected, 'Failed to disconnect'
    with pytest.raises(gerritssh.SSHConnectionError):
        connected_site.execute(None)


def test_abstract(connected_site):
    with pytest.raises(TypeError):
        _ = gerritssh.SiteCommand()

    s = connected_site
    c = DummyCommand()
    c.execute_on(s)  # Should not raise anything


def test_t2l():
    c = DummyCommand()
    assert c.text_to_list('string') == ['string']
    assert c.text_to_list('a\nb') == ['a', 'b']
    assert gerritssh.SiteCommand.text_to_list('string') == ['string']
    assert gerritssh.SiteCommand.text_to_list('a\n \nb') == ['a', '', 'b']
    assert (gerritssh.SiteCommand.text_to_list('a\n \nb\n', True)
             == ['a', 'b'])
    assert (gerritssh.SiteCommand.text_to_list(['a\nb', 'c\nd'])
            == ['a', 'b', 'c', 'd'])

    with pytest.raises(TypeError): c.text_to_list(123)
    with pytest.raises(TypeError): c.text_to_list(['abc', 123, 'def'])
    with pytest.raises(TypeError): c.text_to_list(None)


def test_t2j():
    c = DummyCommand()
    js = ['{"a" : false}', '{"b" : 1}\n{"c":2}']
    assert gerritssh.SiteCommand.text_to_json(js[0]) == [{"a":False}]
    assert c.text_to_json(js[0]) == [{"a":False}]
    assert c.text_to_json(js) == [{"a":False}, {"b":1}, {"c":2}]
    js[1] = 1
    with pytest.raises(TypeError):
        c.text_to_json(js)


def test_copying(connected_site):
    import copy
    copies = [connected_site.copy(),
              copy.copy(connected_site),
              copy.deepcopy(connected_site)]
    for s in copies:
        assert not s.connected
        assert s.site == connected_site.site
        assert s._Site__init_args == connected_site._Site__init_args


def test_command_exceptions():
    # Tests the contract-enforcement exceptions. Everything else is
    # tested as part of the concrete command classes.
    with pytest.raises(TypeError):
        DummyCommand(None, ' ')

    with pytest.raises(ValueError):
        DummyCommand(None, None, '--dummy')
