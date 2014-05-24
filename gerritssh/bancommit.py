
'''
Implements the ban-commit command

'''
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa


class BanCommit(SiteCommand):
    '''
    Obtain a list of all(visible) groups on a site

    :param project: The repository name containingg the commit
    :param commit: The SHA-1 for the commit to be banned
    :param option_str: List of options to pass to the command

    '''

    __options = OptionSet(Option.valued('reason', spec='>=2.5'))
    __supported_versions = '>=2.5'

    def __init__(self, project, commit, option_str=''):
        self.__project = project
        self.__commit = commit

        if not (project and commit):
            raise ValueError('Project and Commit are required by the command')

        super(BanCommit, self).__init__(BanCommit.__supported_versions,
                                        BanCommit.__options,
                                        option_str)

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site

        :returns:
            An empty list as the command has no return value
        '''
        self.check_support_for(the_site)
        the_site.execute(' '.join(['ban-commit',
                                   str(self._parsed_options),
                                   self.__project,
                                   self.__commit]
                                   ).strip())
        self._results = []
        return self._results

__all__ = ['BanCommit']
