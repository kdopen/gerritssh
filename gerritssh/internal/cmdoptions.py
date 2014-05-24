r'''
A set of cooperating classes which allow command implementations to
specify and parse the various options which Gerrit supports.

In addition, every option can be assigned a semantic-version compatible
specification which identifies the Gerrit versions on which the option
is supported. Thus, a command implementation can not only parse its
option list with ease, but also identify combinations which are not
supported by the site they are being sent to.

Implementing a versioned command has the following requirements (see
the `ProjectList` command for a full implementation).

* Create an OptionSet instance, specify all the supported options. This
  is best done as a class attribute, as the information is constant for
  all instances.

* Pass the OptionSet, and list of options to be parsed, to the constructor
  for the abstract SiteCommand class.

* When the `execute_on` method is invoked, call check_support_for() in the
  base class, which will verify all options (and the command itself) are
  supported in the Gerrit version for the given site.


A complete framework for a command implementation, supported on Gerrit versions
2.7 and above, might look like::

    class SomeCommand(SiteCommand):

        __options = OptionSet(
                        Option.flag(...),
                        Option.choice(...),
                        Option.valued(...),
                        Option.flag('needed'))

        def __init__(self, options_string):
            super(SomeCommand,self).__init__('>=2.7',
                                             SomeCommand.__options,
                                             options_string)

        def execute_on(self, site):
            # We always need to specify --needed for some reason
            self.__parsed.needed = True

            # Check the support *after* overriding options
            self.check_support_for(site)

            return site.execute(' '.join(['some-command',
                                        self.__parsed]).strip())

'''

import collections
import shlex
import argparse
import logging

import semantic_version as SV


_logger = logging.getLogger(__name__)


class OptionRepr(collections.namedtuple('__OptionRepr',
                                        'type key args kwargs spec')):
    pass


class CmdOptionParser(object):
    '''
    A parser configured for a given OptionSet

    :param option_set: An initialized OptionSet instance

    :raises: TypeError if option_set is not an OptionSet

    '''

    def __init__(self, option_set):
        self.__results = None

        if not isinstance(option_set, OptionSet):
            raise TypeError('CmdOptionParser requires an OptionSet instance')

        self._option_set = option_set
        self._parser = argparse.ArgumentParser()

        for opt in option_set:
            kwargs = dict(opt.kwargs, **{'dest': opt.key})
            self._parser.add_argument(*opt.args, **kwargs)

    def parse(self, opt_str):
        '''
        Parse the provided option string.

        :param opt_str:
            A string containing the list of options to be parsed against the
            OptionSet the instiance was initialized with.

        :returns: A ParsedOptions object with the results of parsing the string

        '''
        self.__parser_input = opt_str
        self.__results = ParsedOptions(self._option_set,
                                       self._parser,
                                       opt_str)
        return self.__results

    @property
    def results(self):
        '''
        The ParsedOptions object from the last call to parse

        '''
        return self.__results


class ParsedOptions(object):
    '''
    Results of parsing a list of options

    The value of each option is available as an attribute of the
    instance, allowing setting, getting, and deleting of options.

    This is an internal class, not meant to be instantiated outside
    of this module. Instances are returned by CmdOptionParser.parse().

    :param option_set:
        An OptionSet object containing the options definitions

    :param parser:
        An CmdOptionParser object configured to parse the options
        defined in option_set

    :param opt_str:
        The string of options to be parsed

    :raises" `SystemExit` if any of the options fail to parse

    '''

    def __init__(self, option_set, parser, opt_str):
        self._option_set = option_set
        results = parser.parse_args(shlex.split(opt_str)).__dict__
        _logger.debug('Parsed "%s" to %s' % (opt_str, str(results)))
        self.__dict__.update(results)

    def __str__(self):
        '''
        The parsed options as a string suitable for passing to the
        underlying command.

        if no modifications are made, this should simply return the
        original opt_str. Its value comes after the original parsed
        options are modified by the SiteCommand object.

        :returns: A string containing all options.

        '''
        # no dict comprehensions in 2.6
        results = dict([(k, v)
                        for k, v in list(self.__dict__.items())
                        if not k.startswith('_')])

        strs = []
        for opt in self._option_set:
            value = results.get(opt.key)
            if opt.type == 'flag':
                if value:
                    strs.append(opt.args[0])
            else:
                if value:
                    if not isinstance(value, list):
                        value = [value]

                    for v in value:
                        strs.extend([opt.args[0], v])

        return ' '.join(strs)

    def supported_in(self, version):
        '''
        Determines if all options are supported in the given version.

        :param version: A Version object from the semantic_version package.

        :returns: False if any parsed option is not supported

        '''
        if not isinstance(version, SV.Version):
            raise TypeError('version must be a semantic_version.Version '
                            'instance. Supplied version has type %s' %
                            (type(version)))

        for opt in self._option_set:
            spec = opt.spec
            if not (spec and self.__dict__[opt.key]):
                continue

            if version not in SV.Spec(spec):
                _logger.debug('Option %s not supported in %s. Spec: %s'
                              % (opt.key, str(version), str(spec)))
                return False

        return True


class OptionSet(object):
    '''
    A set of options supported by a command.

    Basically this is currently a wrapper around a tuple that allows
    for a natural form of creation. It also allows the representation
    to be changed later without producing widespread changes.

    All arguments to the constructor need to be created by calls to
    the static methods of the Option class::

        options = OptionSet(Option.flag(...),
                            Option.choice(...),
                            Option.valud(...),
                            ...)

    :raises: TypeError if other types of arguments are created.

    '''

    def __init__(self, *args):
        self.options = args
        arg_types = [isinstance(arg, OptionRepr) for arg in args]
        if not all(arg_types):
            raise TypeError('OptionSet expects all values to be '
                            'created by the Option class')

    def options_supported_in(self, version):
        '''
        Return a subset of the OptionSet containing only those
        options supported by the provided version.

        :param version: A Version object from the semantic_version package.
        :returns: A filtered OptionSet

        :raises: TypeError if version is not a semantic_version.Version object

        '''

        if not isinstance(version, SV.Version):
            raise TypeError

        new_set = []
        for opt in self.options:
            if (not opt.spec) or version in SV.Spec(opt.spec):
                new_set.append(opt)

        return OptionSet(*new_set)

    def __iter__(self):
        return iter(self.options)


class Option(object):
    '''
    This class provides a namespace for static methods that create Option
    objects for inclusion in an Optionset.

    Typically, these are used in initializing an OptionSet as follows::

        OptionSet(Option.flag(...),
                  Option.choices(...),
                  Option.values(...))

    flags, choices, and valued option definitions each take the following
    parameters:

    :param long_name:
        A string providing the long name for the option (without the leading
        '--')
    :param short:
        A string providing the short name for the option (withoutthe leading
        '-').
        This defaults to None.
    :param repeatable:
        A boolean keyword argument, defaulting to False. If True, the option
        can be specified more than once (for example, '-vv' to increase the
        level of verbosity twice)
    :param spec:
        A semantic_version compatible specification, defining which versions
        support this option. Defaults to 'all versions'

    The specific behavior of each is documented in the option creation methods.

    '''

    @staticmethod
    def __check_args(opt_type,
                     long_name,
                     short,
                     kwargs,
                     repeat_action,
                     default_action,
                     extra_kwords=dict()):
        rdict = extra_kwords.copy()
        if kwargs.get('repeatable'):
            rdict['action'] = repeat_action
        else:
            rdict['action'] = default_action

        p_args = (('--' + long_name, '-' + short) if short else ('--' + long_name,))
        option = OptionRepr(type=opt_type,
                            key=long_name.replace('-', '_'),
                            args=p_args,
                            kwargs=rdict,
                            spec=kwargs.get('spec'))
        return option

    @staticmethod
    def flag(long_name, short='', **kwargs):
        '''
        Create a simple flag option.

        Flag options are either boolean, or repeatable.

        If repeatable is True, the flags value will represent a count of how
        often it was found.

        Examples::

            # An option, '--long' or '-l', which is only supported in version
            # 2.0.0 or better.
            Option.flag('long', 'l', spec='>=2.0.0')

            # An option '--verbose'or '-v' which can specified many times
            Option.flag('--verbose','-v', repeatable=True)

        '''
        return Option.__check_args('flag',
                                   long_name,
                                   short,
                                   kwargs,
                                   'count',
                                   'store_true')

    @staticmethod
    def choice(long_name, short='', choices=[], **kwargs):
        r'''
        Define an option which requires a seleciton from a list of values.

        :param choices:
            A keyword argument providing the list of acceptable values.

        The selected value is stored as an array if repeatable is True.

        Example::

            Option.choice('format', 'f', choices=['json', 'text', 'html'])

        '''
        return Option.__check_args('choice', long_name, short, kwargs, 'append',
                                   'store', extra_kwords={'choices': choices})

    @staticmethod
    def valued(long_name, short='', **kwargs):
        '''
        Define an option which takes a value.

        The value is stored as an array if repeatable is True.

        Example::

            Option.valued('project', 'p', repeatable=True, spec='>=1.2.3')

        '''
        return Option.__check_args('valued', long_name, short, kwargs, 'append',
                                   'store')

__all__ = ['OptionSet', 'Option', 'CmdOptionParser']
