'''
Tests for the miscellaneous commands contained in the lsprojects module.

'''
from gerritssh.lsprojects import ProjectList
import pytest


def test_lp_all(dummy_site):
    '''
    Test the List Projects command

    Use a duck-typed Site class which simply returns the command
    passed in. This lets us ensure that the commands are formatted
    properly. The actual query object is tested separately.

    '''
    s = dummy_site(lambda x: [x], '2.7.0')
    cmd = ProjectList('--all').execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-projects --all'
    cmd = ProjectList().execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-projects'


def test_lp_iter(dummy_site):
    '''
    Test that the resulting object from a List Projects command can be
    iterated over successfully.

    A duck-typed Site object is used to return a fixed result.

    '''
    s = dummy_site(lambda _: ['p1', 'p2'], '2.7.0')
    lp = ProjectList()
    r = lp.execute_on(s)
    assert r == ['p1', 'p2']
    for i, p in enumerate(lp):
        assert p == ['p1', 'p2'][i]


def test_lp_not_supported(dummy_site):
    s = dummy_site(lambda x: [x], '2.0.0')
    lp = ProjectList()

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)


def test_lp_not_supported_option(dummy_site):

    s = dummy_site(lambda x: [x], '2.4.7')
    lp = ProjectList('-d')

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)
