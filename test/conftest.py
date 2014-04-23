'''
Pytest test fixtures used in the various unit tess contained in other modules.

'''

import pytest
import gerritssh
import semantic_version as SV

from gerritssh.borrowed.ssh import SSHCommandResult


@pytest.fixture()
def connected_site(monkeypatch):
    '''
    This fixture provides a Site object, monkeypatched so that any attempt to
    execute a command acts as if a 'gerrit version' command had been executed.

    In essence it provides a properly constructed Site object which will report
    a version of 2.9.0 and a site of 'gerrit.example.com.

    '''
#     monkeypatch.setattr(gerritssh.Site, '_Site__do_command',
#                         lambda self, cmd: self._Site__ssh.execute(cmd))

    class DummySSHClient(object):

        def __init__(self, *args, **kwargs):
            self.connected = False

        def execute(self, command):
            import io
            self.connected = True
            result = SSHCommandResult(command,
                                      io.StringIO(),
                                      io.StringIO(u'gerrit version '
                                                  '2.9.0\n'),
                                      io.StringIO())

            return result

        def disconnect(self):
            self.connected = False

    s = gerritssh.Site('gerrit.example.com')
    s._Site__ssh = DummySSHClient()
    assert not s.connected, 'Thinks its connected after construction'
    s.connect()
    assert s.connected
    assert s.version == SV.Version('2.9.0')
    return s


@pytest.fixture
def dummy_site():
    def f(exec_func, version):
        class DummySite(gerritssh.Site):

            def __init__(self):
                super(DummySite, self).__init__('gerrit.example.com')

            def execute(self, cmd):
                return exec_func(cmd)

            @property
            def version(self):
                return SV.Version(version)

            @property
            def connected(self):
                return True

        return DummySite()
    return f


'''
The file 'testreview.json' contains the result of a query for a (randomly
chosen) open code review at review.openstack.org. It is used within numerous
tests which expect a properly formatted response from a working Gerrit
instance.

'''
with open('test/testreview.json', 'r') as f:
    __random_text = f.read()


@pytest.fixture()
def open_review_text():
    '''
    This fixure returns the plain text response of a query to fetch a single
    open review.

    '''
    return __random_text


@pytest.fixture()
def open_review_json(open_review_text):
    '''
    This fixture provides the canned open review, converted to a JSON
    dictionary.

    '''
    import json
    return [json.loads(l.strip()) for l in open_review_text.split('\n') if l]


@pytest.fixture()
def open_review(open_review_json):
    '''
    This fixture provides a Review object initialized with a single open
    review.

    '''
    from gerritssh import Review
    r = Review(open_review_json[0])
    assert r.raw == open_review_json[0]
    return r
