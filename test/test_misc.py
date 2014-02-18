'''
Tests for the miscellaneous commands contained in the misc module.

'''

from gerritssh import misc
import pytest


def test_lp_all():
    '''
    Test the List Projects command

    Use a duck-typed Site class which simply returns the command
    passed in. This lets us ensure that the commands are formatted
    properly. The actual query object is tested separately.

    '''
    class DummySite(object):
        def execute(self, cmd):
            return cmd

    s = DummySite()
    cmd = misc.ProjectList(True).execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-projects --all'
    cmd = misc.ProjectList().execute_on(s)
    assert len(cmd) == 1
    assert cmd[0] == 'ls-projects'


def test_lp_iter():
    '''
    Test that the resulting object from a List Projects command can be
    iterated over successfully.

    A duck-typed Site object is used to return a fixed result.

    '''
    class DummySite:
        def execute(self, _): return 'p1\np2\n'

    s = DummySite()
    lp = misc.ProjectList()
    r = lp.execute_on(s)
    assert r == ['p1', 'p2']
    for i, p in enumerate(lp):
        assert p == ['p1', 'p2'][i]
