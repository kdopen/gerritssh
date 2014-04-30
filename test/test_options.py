import pytest
from gerritssh.internal.cmdoptions import *
import semantic_version as SV


@pytest.fixture()
def option_tuple():
    return (
            Option.flag('flag', 'f', spec='>=2.0'),
            Option.valued('valued', 'v', spec='>=1.0,<3.0'),
            Option.choice('pick', 'p', ['a', 'b']),
            Option.choice('repeatable', 'r',
                          choices=['a', 'b', 'c'],
                          repeatable=True)
           )


@pytest.fixture()
def option_set(option_tuple):
    return OptionSet(*option_tuple)


class TestOption(object):

    def test_option_flag(self):
        long_name = 'long-name'
        key = long_name.replace('-', '_')
        short = 'short-name'
        f = Option.flag(long_name, short)
        assert f.key == key
        assert f.type == 'flag'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['action'] == 'store_true'

        f = Option.flag(long_name, short, repeatable=True)
        assert f.kwargs['action'] == 'count'
        assert f.key == key
        assert f.type == 'flag'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)

        f = Option.flag(long_name, short, spec='>1.0')
        assert f.key == key
        assert f.type == 'flag'
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['action'] == 'store_true'
        assert f.spec == '>1.0'

    def test_option_valued(self):
        long_name = 'long_name'
        short = 'short-name'
        key = long_name.replace('-', '_')

        f = Option.valued(long_name, short)
        assert f.key == key
        assert f.type == 'valued'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['action'] == 'store'

        f = Option.valued(long_name, short, repeatable=True)
        assert f.kwargs['action'] == 'append'
        assert f.key == key
        assert f.type == 'valued'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)

        f = Option.valued(long_name, short, repeatable=True, spec='>1.0')
        assert f.kwargs['action'] == 'append'
        assert f.spec == '>1.0'
        assert f.key == key
        assert f.type == 'valued'
        assert f.args == ('--' + long_name, '-' + short)

    def test_option_choices(self):
        long_name = 'long_name'
        short = 'short-name'
        choices = ['a', 'b']
        key = long_name.replace('-', '_')

        f = Option.choice(long_name, short, choices)
        assert f.key == key
        assert f.type == 'choice'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['action'] == 'store'
        assert f.kwargs['choices'] == choices

        f = Option.choice(long_name, short, choices, repeatable=True)
        assert f.kwargs['action'] == 'append'
        assert f.key == key
        assert f.type == 'choice'
        assert not f.spec
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['choices'] == choices

        f = Option.choice(long_name, short, choices, repeatable=True, spec='>1.0')
        assert f.kwargs['action'] == 'append'
        assert f.spec == '>1.0'
        assert f.key == key
        assert f.type == 'choice'
        assert f.args == ('--' + long_name, '-' + short)
        assert f.kwargs['choices'] == choices


class TestOptionSet(object):

    def test_init(self, option_tuple):
        opts = OptionSet(*option_tuple)
        assert opts
        assert all([a == b for a, b in zip(option_tuple, opts)])

    def test_failed_init(self):
        with pytest.raises(TypeError):
            OptionSet((1, 2, 3))

    def test_option_subset(self, option_set):
        subset = option_set.options_supported_in(SV.Version('4.0.0'))
        assert subset
        assert isinstance(subset, OptionSet)
        assert len(list(subset)) < len(list(option_set))
        for opt in subset:
            assert opt.key in ['flag', 'pick', 'repeatable']

    def test_option_subset_2(self, option_set):
        subset = option_set.options_supported_in(SV.Version('2.0.0'))
        assert subset
        assert isinstance(subset, OptionSet)
        assert len(list(subset)) == len(list(option_set))

    def test_option_subset_fail(self, option_set):
        with pytest.raises(TypeError):
            option_set.options_supported_in('2.0')


class TestOptionParser(object):

    def test_init(self, option_set):
        with pytest.raises(TypeError):
            _ = CmdOptionParser('a string')

        parser = CmdOptionParser(option_set)
        assert not parser.results

    def test_parse_empty(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        results = parser.parse('')
        assert results
        assert not results.flag
        assert not results.pick
        assert not results.valued
        assert not results.repeatable
        assert str(results) == ''

    def test_parse_fail(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        with pytest.raises(SystemExit):
            parser.parse('--bad')

    def test_bad_supported_in(self, option_set):
        parser = CmdOptionParser(option_set)
        results = parser.parse('--flag')

        with pytest.raises(TypeError):
            results.supported_in('1.0')

    def test_parse_flag(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        results = parser.parse('--flag')
        assert results
        assert results.flag
        assert not results.pick
        assert not results.valued
        assert str(results) == '--flag'
        assert not results.repeatable

        results = parser.parse('-f')
        assert results
        assert results.flag
        assert not results.pick
        assert not results.valued
        assert str(results) == '--flag'
        assert not results.repeatable

    def test_parse_choice(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        results = parser.parse('--pick a')
        print(results)
        assert results
        assert not results.flag
        assert results.pick == 'a'
        assert not results.valued
        assert str(results) == '--pick a'
        assert not results.repeatable

        results = parser.parse('-p a')
        print(results)
        assert results
        assert not results.flag
        assert results.pick == 'a'
        assert not results.valued
        assert str(results) == '--pick a'
        assert not results.repeatable

    def test_parse_valued(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        results = parser.parse('--valued a')
        assert results
        assert not results.flag
        assert not results.pick
        assert results.valued == 'a'
        assert str(results) == '--valued a'
        assert not results.repeatable

        results = parser.parse('-v a')
        assert results
        assert not results.flag
        assert not results.pick
        assert results.valued == 'a'
        assert str(results) == '--valued a'
        assert not results.repeatable

    def test_parse_repeatable(self, option_set):
        parser = CmdOptionParser(option_set)
        assert not parser.results

        results = parser.parse('--repeatable a -r b')
        assert results
        assert not results.flag
        assert not results.pick
        assert not results.valued
        assert results.repeatable == ['a', 'b']
        assert str(results) == '--repeatable a --repeatable b'
