"""
Tests for `site` module.
"""
import pytest
import gerritssh
import subprocess


@pytest.fixture
def mocked_output(monkeypatch):
    def helper(f):
        monkeypatch.setattr(gerritssh.gerritsite, '_check_output', f)
    return helper


class DummyCommand(gerritssh.SiteCommand):
    def __init__(self):
        super(DummyCommand, self).__init__()

    def execute_on(self, site):
        super(DummyCommand, self).execute_on(site)


class TestGerritssh(object):

    def test_init(self):
        s = gerritssh.Site('gerrit.example.com')
        assert s, 'Failed to create a Site object'
        assert s.site == 'gerrit.example.com', \
        'Did not record the site name properly'

        with pytest.raises(TypeError):
            _ = gerritssh.Site(1)

    def test_connect_returns_version(self, connected_site):
        ''' Mock check_output to return a known version string '''
        s = connected_site
        v = s.version
        c = s.connected
        assert v == (1, 0, 0), 'Failed to retrieve version string'
        assert c, 'Not connected'
        s.connect()  # SHould not raise any problems
        assert s.connected, 'Second call to connect() changed state'

    def test_failed_connection1(self, mocked_output):
        ''' Mock check_output to throw the CalledProcessError'''
        s = gerritssh.Site('...')

        def raiseerror(a, b=''):
            raise subprocess.CalledProcessError(255, 'cmd')
        mocked_output(raiseerror)
        with pytest.raises(gerritssh.ConnectionError): s.connect()

    def test_failed_connection2(self, mocked_output):
        '''Mock check_output to throw TypeError'''
        s2 = gerritssh.Site('...')

        def raiseerror(a, b=''): raise TypeError()
        mocked_output(raiseerror)
        with pytest.raises(TypeError): s2.connect()

    def test_failed_connection3(self):
        '''
        Use a clearly invalid site name to ensure the connection
        attempt fails
        '''
        s = gerritssh.Site('...')
        with pytest.raises(gerritssh.ConnectionError): s.connect()

    def test_disconnect(self, connected_site):
        s = connected_site
        s.disconnect()
        assert not s.connected, 'Did not disconnect'
        s.disconnect()  # Should not raise an exception
        assert not s.connected, 'Reconnected'

    def test_execute_none(self, connected_site):
        with pytest.raises(gerritssh.InvalidCommandError):
            connected_site.execute(None)
        with pytest.raises(gerritssh.InvalidCommandError):
            connected_site.execute(1)

    def test_execute_string(self, connected_site, mocked_output):
        s = connected_site

        def echo(a, _=''):
            return a
        mocked_output(echo)
        assert s.execute('somecommand') == \
            ['ssh', s.site, 'gerrit', 'somecommand']

    def test_execute_cmd(self, connected_site):
        lp = gerritssh.ProjectList()
        p = connected_site.execute(lp)
        assert p
        assert len(p) == 1
        assert p[0] == 'gerrit version 1.0.0'

    def test_extract_version(self):
        s = gerritssh.Site('...')
        ev = s._Site__extract_version
        assert ev('gerrit version 1') == (0, 0, 0)
        assert ev('gerrit version 1.2') == (0, 0, 0)
        assert ev('gerrit version 1.2.3') == (1, 2, 3)
        assert ev('gerrit version 1-2ab') == (0, 0, 0)
        assert ev('gerrit version 1ab') == (0, 0, 0)
        assert ev('gerrit version abc') == (0, 0, 0)
        assert ev('g') == (0, 0, 0)
        assert ev('gerrit  1.2.3') == (0, 0, 0)
        assert ev('gerrit version 1 2 3') == (0, 0, 0)
        assert ev('gerrit version 1 abc 2') == (0, 0, 0)
        assert ev('gerrit version 1.2.3abcd') == (1, 2, 3)
        assert ev('gerrit version 2.4.4-14-gab7f4c1') == (2, 4, 4)

    def test_version_compare(self, connected_site):
        with pytest.raises(gerritssh.ConnectionError):
            gerritssh.Site('...').version_at_least(1)

        s = connected_site
        ev = s.version_at_least
        assert ev(1, 0, 0)
        assert ev(1)
        assert ev(1, 0)
        assert not ev(1, 1)
        assert ev(0, 9, 1)

    def test_not_connected(self, connected_site):
        connected_site.disconnect()
        assert not connected_site.connected, 'Failed to disconnect'
        with pytest.raises(gerritssh.ConnectionError):
            connected_site.execute(None)

    def test_abstract(self, connected_site):
        with pytest.raises(TypeError):
            _ = gerritssh.SiteCommand()

        s = connected_site
        c = DummyCommand()
        c.execute_on(s)  # Should not raise anything

    def test_t2l(self):
        c = DummyCommand()
        assert c.text_to_list('string') == ['string']
        assert c.text_to_list('a\nb') == ['a', 'b']
        assert gerritssh.SiteCommand.text_to_list('string') == ['string']

        with pytest.raises(TypeError): c.text_to_list(c)
        with pytest.raises(TypeError): c.text_to_list(None)

    def test_t2j(self):
        c = DummyCommand()
        js = ['{"a" : false}', '{"b" : 1}\n{"c":2}']
        assert gerritssh.SiteCommand.text_to_json(js[0]) == [{"a":False}]
        assert c.text_to_json(js[0]) == [{"a":False}]
        assert c.text_to_json(js) == [{"a":False}, {"b":1}, {"c":2}]
        js[1] = 1
        with pytest.raises(TypeError):
            c.text_to_json(js)