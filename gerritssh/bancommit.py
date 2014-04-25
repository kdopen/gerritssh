
'''
Implements the ban-commit command

'''
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa


class BanCommit(SiteCommand):
    '''
    Obtain a list of all(visible) groups on a site

    :param option_str: List of options to pass to the command

    '''

    __options = OptionSet(Option.valued('reason', spec='>=2.5'))
    __supported_versions = '>=2.5'

    def __init__(self, project, commit, option_str=''):
        super(BanCommit, self).__init__()
        self.__parser = CmdOptionParser(BanCommit.__options)
        self.__option_str = option_str
        self.__parsed_options = self.__parser.parse(option_str)
        self.__project = project
        self.__commit = commit

        if not (project and commit):
            raise ValueError('Project and Commit are required by the command')

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site

        :returns:
            An empty list as the command has no return value
        '''

        not_supported = (
            'Gerrit version {0} does not support '.format(the_site.version)
            )

        if not the_site.version_in(BanCommit.__supported_versions):
            raise NotImplementedError(not_supported + 'this command')

        if not self.__parsed_options.supported_in(the_site.version):
            raise NotImplementedError(not_supported +
                                      'one or more options provided')

        the_site.execute(' '.join(['ban-commit',
                                   str(self.__parsed_options),
                                   self.__project,
                                   self.__commit]
                                   ).strip())
        self._results = []
        return self._results

__all__ = ['BanCommit']
