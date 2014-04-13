'''
Miscellaneous SiteCommand classes for simple commands
'''
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa


class ProjectList(SiteCommand):
    '''
    Obtain a list of all(visible) projects on a site

    :param option_str: List of options to pass to the command

    '''

    __options = OptionSet(
        Option.valued('show-branch', 'b', repeatable=True),
        Option.flag('description', 'd', spec='>=2.5'),
        Option.flag('tree', 't'),
        Option.choice('type', choices=['code', 'permissions', 'all']),
        Option.flag('all', spec='>=2.5'),
        Option.valued('limit', spec='>=2.5'),
        Option.valued('has-acl-for', spec='>=2.6'),
        Option.choice('format',
                      choices=['text', 'json', 'json_compact'],
                      spec='>=2.5')
        )

    __supported_versions = '>=2.4'

    def __init__(self, option_str=''):
        super(ProjectList, self).__init__()
        self.__parser = CmdOptionParser(ProjectList.__options)
        self.__option_str = option_str
        self.__parsed_options = self.__parser.parse(option_str)

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site to search
        :param list_all: Indicates whether to list all types of project

        :returns: A list of :class:`Review` objects
        '''

        not_supported = (
            'Gerrit version {0} does not support '.format(the_site.version)
            )

        if not the_site.version_in(ProjectList.__supported_versions):
            raise NotImplementedError(not_supported + 'this command')

        if not self.__parsed_options.supported_in(the_site.version):
            raise NotImplementedError(not_supported +
                                      'one or more options provided')

        raw = the_site.execute(' '.join(['ls-projects',
                                        str(self.__parsed_options)]
                                        ).strip())
        self._results = [l for l in raw if l]
        return self._results

__all__ = ['ProjectList']
