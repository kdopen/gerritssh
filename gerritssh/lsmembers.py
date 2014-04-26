'''
Implements the ls-groups command

'''
from gerritssh import GerritsshException
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa


class InvalidGroupError(GerritsshException):
    pass


class ListMembers(SiteCommand):
    '''
    Obtain a list of all members of a given group

    :param group: The group name
    :param option_str: List of options to pass to the command

    :raises: `SystemExit` if the option string fails to parse.
    :raises: `ValueError` if the group is not provided
    :raises: `AttributeError` if the group is not a string

    '''

    __options = OptionSet(
        Option.flag('recursive', spec='>=2.8'),
        )

    __supported_versions = '>=2.8'

    def __init__(self, group, option_str=''):
        super(ListMembers, self).__init__()

        if not isinstance(group, str):
            raise AttributeError('Group must be a string')

        if not group:
            raise ValueError('Caller must provide a non-null group name')

        self.__group = group
        self.__parser = CmdOptionParser(ListMembers.__options)
        self.__option_str = option_str
        self.__parsed_options = self.__parser.parse(option_str)

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site to search

        :returns:
            A list of dictionaries, one per member, with the keys id, username,
            fullname, and email.

        :raises: NotImplementedError
            If the site does not support the command, or a specified option

        :raises: InvalidGroupError if the command returns an error line

        '''

        not_supported = (
            'Gerrit version {0} does not support '.format(the_site.version)
            )

        if not the_site.version_in(ListMembers.__supported_versions):
            raise NotImplementedError(not_supported + 'this command')

        if not self.__parsed_options.supported_in(the_site.version):
            raise NotImplementedError(not_supported +
                                      'one or more options provided')

        cmd = ' '.join(['ls-members',
                        str(self.__parsed_options),
                        self.__group]
                       ).strip()
        raw = the_site.execute(cmd)

        if not raw:
            raise InvalidGroupError('No Results from Command: ' + cmd)

        if not raw[0].startswith('id\t'):
            raise InvalidGroupError('Error from command: ' + raw[0])

        field_names = ['id', 'username', 'fullname', 'email']
        self._results = [dict(zip(field_names, member.split('\t')))
                         for member in raw[1:]]
        return self._results

__all__ = ['ListMembers', 'InvalidGroupError']
