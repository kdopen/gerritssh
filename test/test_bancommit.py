'''
Tests for the lsgroups command.

'''
from gerritssh.bancommit import BanCommit
from gerritssh.internal.cmdoptions import *

import pytest


def test_bc_all(dummy_site):
    '''
    Test the ban commit command

    Use a duck-typed Site class which simply returns the command
    passed in. This lets us ensure that the commands are formatted
    properly. The actual query object is tested separately.

    '''
    s = dummy_site(lambda x: [x], '2.7.0')
    cmd = BanCommit('theproject', 'thecommit', '--reason Why').execute_on(s)
    assert len(cmd) == 0

    with pytest.raises(ValueError):
        BanCommit('', 'OK')

    with pytest.raises(ValueError):
        BanCommit('OK', '')

    with pytest.raises(ValueError):
        BanCommit('', '')


def test_bc_not_supported(dummy_site):
    s = dummy_site(lambda x: [x], '2.4.0')
    lp = BanCommit('p', 'c')

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)


def test_bc_not_supported_option(monkeypatch, dummy_site):
    with pytest.raises(SystemExit):
        BanCommit('p', 'c', '--badoption')

    opts = OptionSet(Option.flag('new', spec='>=2.6'))
    s = dummy_site(lambda x: x, '2.5.0')

    monkeypatch.setattr(BanCommit, '_BanCommit__options', opts)
    bc = BanCommit('p', 'c', '--new')

    with pytest.raises(NotImplementedError):
        bc.execute_on(s)
