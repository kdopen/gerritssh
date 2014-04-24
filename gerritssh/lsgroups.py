'''
Implements the ls-groups command

'''
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa


class ListGroups(SiteCommand):
    '''
    Obtain a list of all(visible) groups on a site

    :param option_str: List of options to pass to the command

    '''

    __options = OptionSet(
        Option.valued('project', 'p'),
        Option.valued('user', 'u'),
        Option.flag('visible-to-all'),
        Option.choice('type', choices=['internal', 'system']),
        Option.flag('verbose', 'v', spec='>=2.5'),
        Option.flag('owned', spec='>=2.6'),
        Option.valued('q', 'q', repeatable=True, spec='>=2.6')
        )

    __supported_versions = '>=2.4'

    def __init__(self, option_str=''):
        super(ListGroups, self).__init__()
        self.__parser = CmdOptionParser(ListGroups.__options)
        self.__option_str = option_str
        self.__parsed_options = self.__parser.parse(option_str)

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site to search

        :returns:
            A list of group names, with possibly more information if
            the verbose option is specified.
        '''

        not_supported = (
            'Gerrit version {0} does not support '.format(the_site.version)
            )

        if not the_site.version_in(ListGroups.__supported_versions):
            raise NotImplementedError(not_supported + 'this command')

        if not self.__parsed_options.supported_in(the_site.version):
            raise NotImplementedError(not_supported +
                                      'one or more options provided')

        raw = the_site.execute(' '.join(['ls-groups',
                                        str(self.__parsed_options)]
                                        ).strip())
        self._results = [l for l in raw if l]
        return self._results

__all__ = ['ListGroups']
