'''
Tests for the lsgroups command.

'''
from gerritssh.lsgroups import ListGroups
import pytest


def test_lg_all(dummy_site):
    '''
    Test the List Projects command

    Use a duck-typed Site class which simply returns the command
    passed in. This lets us ensure that the commands are formatted
    properly. The actual query object is tested separately.

    '''
    s = dummy_site(lambda x: [x], '2.7.0')
    cmd = ListGroups('--visible-to-all').execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-groups --visible-to-all'
    cmd = ListGroups().execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-groups'


def test_lg_iter(dummy_site):
    '''
    Test that the resulting object from a List Projects command can be
    iterated over successfully.

    A duck-typed Site object is used to return a fixed result.

    '''
    s = dummy_site(lambda _: ['p1', 'p2'], '2.7.0')
    lp = ListGroups()
    r = lp.execute_on(s)
    assert r == ['p1', 'p2']
    for i, p in enumerate(lp):
        assert p == ['p1', 'p2'][i]


def test_lg_not_supported(dummy_site):
    s = dummy_site(lambda x: [x], '2.0.0')
    lp = ListGroups()

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)


def test_lg_not_supported_option(dummy_site):

    s = dummy_site(lambda x: [x], '2.4.7')
    lp = ListGroups('--owned')

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)
