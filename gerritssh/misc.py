'''
Miscellaneous SiteCommand classes for simple commands
'''
from .gerritsite import SiteCommand


class ProjectList(SiteCommand):
    '''
    Obtain a list of all(visible) projects on a site

    :param list_all: If true, adds the ``--all`` option, to return
    '''

    def __init__(self, list_all=False):
        super(ProjectList, self).__init__()
        self.__listall = list_all

    def execute_on(self, the_site):
        '''
        :param the_site: A :class:`Site` representing the site to search
        :param list_all: Indicates whether to list all types of project

        :returns: A list of :class:`Review` objects
        '''
        raw = the_site.execute(''.join(['ls-projects',
                                        ' --all' if self.__listall else '']))
        self._results = [l for l in raw if l]
        return self._results

__all__ = ['ProjectList']
