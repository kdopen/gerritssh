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
        super(ListGroups, self).__init__(ListGroups.__supported_versions,
                                         ListGroups.__options,
                                         option_str)

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site to search

        :returns:
            A list of group names, with possibly more information if
            the verbose option is specified.
        '''

        self.check_support_for(the_site)
        raw = the_site.execute(' '.join(['ls-groups',
                                        str(self._parsed_options)]
                                        ).strip())
        self._results = [l for l in raw if l]
        return self._results

__all__ = ['ListGroups']
