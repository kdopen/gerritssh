'''
Tests for the ls-members command.

'''
from gerritssh.lsmembers import ListMembers, InvalidGroupError
from gerritssh.internal.cmdoptions import Option, OptionSet
import pytest


def test_lm_init():
    with pytest.raises(ValueError):
        ListMembers('')

    with pytest.raises(AttributeError):
        ListMembers(dict())


def test_lm_execute(dummy_site):
    s = dummy_site(lambda x: ['id\t', x + '\tn\tf\te'], '2.8.0')
    cmd = ListMembers('somegroup', '--recursive').execute_on(s)
    assert len(cmd) == 1
    assert cmd[0]['id'] == 'ls-members --recursive somegroup'
    cmd = ListMembers('somegroup')
    lm = cmd.execute_on(s)
    assert len(lm) == 1
    assert lm[0]['id'] == 'ls-members  somegroup'
    s = dummy_site(lambda x: ['id\t' + x], '2.8.0')
    r = cmd.execute_on(s)
    assert r == []


def test_lm_errors(dummy_site):
    s = dummy_site(lambda x: ['cmd=' + x], '2.8.0')
    lm = ListMembers('group')

    with pytest.raises(InvalidGroupError):
        lm.execute_on(s)

    s = dummy_site(lambda x: [], '2.8.0')
    with pytest.raises(InvalidGroupError):
        lm.execute_on(s)


def test_lm_iter(dummy_site):
    result = ['id\tusername\tfull name\temail',
              '100000\tjim\tJim Bob\tsomebody@example.com',
              '100001\tjohnny\tJohn Smith\tn/a']
    s = dummy_site(lambda _: result, '2.8.0')
    lm = ListMembers('somegroup')
    r = lm.execute_on(s)
    assert len(r) == len(result) - 1
    assert all([isinstance(d, dict) for d in r])
    assert r[0] == {'id': '100000',
                    'username': 'jim',
                    'fullname': 'Jim Bob',
                    'email': 'somebody@example.com'}
    assert r[1]['id'] == '100001'


def test_lm_not_supported(dummy_site):
    s = dummy_site(lambda x: [x], '2.0.0')
    lp = ListMembers('group')

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)


def test_lm_not_supported_option(dummy_site, monkeypatch):

    s = dummy_site(lambda x: [x], '2.4.7')
    lp = ListMembers('group')

    with pytest.raises(NotImplementedError):
        lp.execute_on(s)

    opts = OptionSet(Option.flag('new', spec='>=2.9'))
    s = dummy_site(lambda x: x, '2.8.0')

    monkeypatch.setattr(ListMembers, '_ListMembers__options', opts)
    lm = ListMembers('p', '--new')

    with pytest.raises(NotImplementedError):
        lm.execute_on(s)
