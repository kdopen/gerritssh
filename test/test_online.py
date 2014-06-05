import pytest
import os

import gerritssh as gssh
import logging

logging.basicConfig(level=logging.CRITICAL)


def online_instance():
    return os.getenv('GSSH_TEST_INSTANCE', '')


pytestmark = pytest.mark.skipif(online_instance() == '',
                                reason=('No live Gerrit instance '
                                          'in environment'))


@pytest.fixture(scope='session')
def live_instance(request):
    s = gssh.Site(online_instance())

    def fin():
        print('Closing connection to ' + online_instance())
        s.disconnect()

    print('Site created: ' + repr(s))
    request.addfinalizer(fin)
    s.connect()
    assert s.connected
    return s


def test_ol_version(live_instance):
    assert str(live_instance.version) != '0.0.0'


def test_ol_lp(live_instance):
    lp = gssh.ProjectList()
    lp.execute_on(live_instance)

    assert len(lp.results) > 0


def test_ol_query(live_instance):
    log = logging.getLogger('test_ol_query')
    log.setLevel(logging.DEBUG)
    log.debug('Launching Query')
    q = gssh.Query(query='status:open', max_results=3)
    qresults = q.execute_on(live_instance)
    log.debug('Query Done {0}'.format(qresults))
    assert qresults != []
    assert len(qresults) <= 3
