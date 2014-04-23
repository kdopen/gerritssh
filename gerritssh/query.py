'''
Commands for querying code review objects on a Gerrit Site

Specifically, the Query command encapsulates the 'query' command line
utility.

Some common queries are provided in the form of functions which return
a prepared Query object. For example, `open_reviews` reviews a Query
prepared to return a complete list of all open code reviews, optionally
restricted to a single project::

    import gerritssh
    s = gerritssh.Site('gerrit.example.com').connect()
    r = gerritssh.open_reviews('myproject').execute_on(s)

Following the PEP8 naming conventions, methods which return prepared
Query objects will have names in all lowercase. Classes which represent
more complex queries will have CamelCase names.

The 'more complex' distinction may be necessary if, for example, variants
of a command are supported only in specific versions of Gerrit.

'''

import logging

from . import review
from .gerritsite import SiteCommand
from .internal.cmdoptions import *  # noqa

_logger = logging.getLogger(__name__)


class Query(SiteCommand):
    '''
    Command to execute queries on reviews

    :param option_str:
        One or more supported options to be passed to the command

        :note: In order to ensure that the necessary information is returned
               to allow creation of the `Review` objects, many of the options
               will be overridden by `execute_on`. The following will always
               be sent:

               * --current-patch-set
               * --patch-sets
               * --all-approvals
               * --dependencies
               * --commit-message
               * --format JSON

    :param query:
        arguments to the query commands, e.g. 'status:abandoned owner:self'

    :param max_results:
        limit the result set to the first 'n'. If not given, all results
        are returned. This may require multiple commands being sent to the
        Gerrit site, as Gerrit instances often have a built-in limit to the
        number of results it returns (often around 500).

    '''

    __options = OptionSet(
        Option.choice('format', choices=['json', 'text']),
        Option.flag('current-patchset'),
        Option.flag('patch-sets'),
        Option.flag('all-approvals'),
        Option.flag('files'),
        Option.flag('comments'),
        Option.flag('dependencies'),
        Option.flag('submit-records', spec='>=2.5'),
        Option.flag('commit-message', spec='>=2.5'),
        Option.flag('all-reviewers', spec='>=2.9')
        )

    __supported_versions = '>=2.4'

    def __init__(self, option_str='', query='', max_results=0):
        super(Query, self).__init__()
        self.__query = query
        self.__max_results = max_results
        self.__parser = CmdOptionParser(Query.__options)
        self.__option_str = option_str
        self.__parsed_options = self.__parser.parse(option_str)

    def execute_on(self, the_site):
        '''
        Perform a Gerrit query command.

        :param the_site: A `Site` object on which to execute the command

        :returns: A list of GerritReview objects converted from returned JSON

        '''

        not_supported = (
            'Gerrit version {0} does not support '.format(the_site.version)
            )

        if not the_site.version_in(Query.__supported_versions):
            raise NotImplementedError(not_supported + 'this command')

        if not self.__parsed_options.supported_in(the_site.version):
            raise NotImplementedError(not_supported +
                                      'one or more options provided')

        # Set the options we require in order to parse the results.
        opts = self.__parsed_options
        opts.current_patch_set = True
        opts.patch_sets = True
        opts.all_approvals = True
        opts.dependencies = True
        opts.commit_message = True
        opts.format = 'JSON'
        result, resume_key, remaining = [], '', self.__max_results

        def partial_query():
            '''Helper to perform a single sub-query'''
            resume = ('resume_sortkey:{0}'.format(resume_key)
                      if resume_key else '')
            standard_flags = ' '.join([str(opts), resume])
            limit = 'limit:{0}'.format(remaining) if self.__max_results else ''
            raw = the_site.execute(' '.join(['query', limit,
                                             self.__query,
                                             standard_flags]))
            lines = self.text_to_json(raw)
            return ([review.Review(l) for l in lines[:-1]]
                    if len(lines) > 1 else [])

        while self.__max_results == 0 or len(result) < self.__max_results:
            partial = partial_query()
            if not partial: break
            result.extend(partial)
            resume_key = partial[-1].raw['sortKey']
            remaining -= len(partial)

        self._results = (result[:self.__max_results]
                         if (self.__max_results and
                             len(result) > self.__max_results)
                         else result)
        return self._results


def _reviews_by_status(project, branch, max_results, status):
    r'''
    Private method to create a Query for reviews with a specific status.

    :param project: Project for which reviews are required
    :param branch:  Specific branch to restrict the search
    :param max_results: Optionally restrict the number of results returned.
    :param status: Status qualifier to restrict the results list.

    Any parameter provided with a logicall False value (zero, None, '') will
    be omittted from the generated query.

    '''
    def format_option(name, value):
        ''' Helper to format a possible False option '''
        return '{0}:{1}'.format(name, value) if value else ''

    flags = [format_option('project', project),
             format_option('branch', branch),
             format_option('status', status)]
    return Query('', ' '.join(flags), max_results)


def open_reviews(project=None, branch=None, max_results=0):
    '''
    Query for all open reviews on a site, optionally restricted to a single
    project and/or branch.

    :param project: If specified, limits the search to a specific project
    :param branch: If specified, limits the search to a specific branch
    :param max_results:
        Limit the result set to the first 'n'. A value of zero (the default)
        results in all possible results being returned,

    :returns: A list of `Review` objects

    '''
    return _reviews_by_status(project, branch, max_results, 'open')


def merged_reviews(project=None, branch=None, max_results=0):
    '''
    Query for all merged reviews on a site, optionally restricted to a single
    project and/or branch.

    :param project: If specified, limits the search to a specific project
    :param branch: If specified, limits the search to a specific branch
    :param max_results:
        Limit the result set to the first 'n'. A value of zero (the default)
        results in all possible results being returned,

    :returns: A list of `Review` objects

    '''
    return _reviews_by_status(project, branch, max_results, 'merged')


def abandoned_reviews(project=None, branch=None, max_results=0):
    '''
    Query for all abandoned reviews on a site, optionally restricted to a
    single project and/or branch.

    :param project: If specified, limits the search to a specific project
    :param branch: If specified, limits the search to a specific branch
    :param max_results:
        Limit the result set to the first 'n'. A value of zero (the default)
        results in all possible results being returned,

    :returns: A list of `Review` objects

    '''
    return _reviews_by_status(project, branch, max_results, 'abandoned')

__all__ = ['Query', 'open_reviews', 'merged_reviews', 'abandoned_reviews']
