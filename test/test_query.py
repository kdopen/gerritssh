'''
Unit tests for classes and methods in the gerritssh.query module.

'''
import pytest
import gerritssh as gssh
import semantic_version as SV


def test_init():
    '''
    Check that a Query object constructs properly with an empty
    list of results.

    '''
    q = gssh.Query()
    assert q
    assert q.results == []


def test_versioning(dummy_site):
    s = dummy_site(lambda x: x, '2.0.0')
    assert s.version == SV.Version('2.0.0')
    with pytest.raises(SystemExit):
        gssh.Query('--badoption', '')

    # Command is not implemented
    q = gssh.Query('')
    with pytest.raises(NotImplementedError):
        q.execute_on(s)

    s = dummy_site(lambda x: x, '2.4.0')
    q = gssh.Query('--all-reviewers')
    with pytest.raises(NotImplementedError):
        q.execute_on(s)  # Option not implemented in 2.4


def test_execute(open_review_text, open_review):
    responses = [open_review_text, '']

    # Create a duck-typed Site class which returns a set of open
    # code reviews. Each instance will return the value of the
    # responses variable, which should be a list of one or more
    # open-review_text fixtures.

    class DummySite(gssh.Site):
        def __init__(self, site):
            super(DummySite, self).__init__(site)
            self.gen = iter(responses)

        def execute(self, cmd):
            assert type(cmd) == type('abc')
            return next(self.gen)

        @property
        def version(self):
            return SV.Version('2.9.0')

        @property
        def connected(self):
            return True

    # Execute a dummied query and examine the response
    s = DummySite('...')
    q = gssh.Query('', 'status:open', 100)
    r = q.execute_on(s)
    assert type(r) == type([])
    assert len(r) == 1
    assert type(r[0]) == gssh.Review

    # Check that a query for open reviews (suitably dummied) returns
    # an iterable object of the correct length, containing a single
    # Review object.
    opn = gssh.open_reviews()
    r = opn.execute_on(DummySite('...'))
    assert type(r) == type([])
    assert len(r) == 1
    assert type(r[0]) == gssh.Review

    # Ensure we limit the number of responses by creating a list of 20
    # reviews and then limiting the search to only 10 results.
    responses = [open_review_text] * 20 + ['']
    opn = gssh.open_reviews(max_results=10)
    r = opn.execute_on(DummySite('...'))
    assert len(r) == 10

    # Check that iterating over the results returns a sequence
    # of Review results, all with the correct SHA1
    for rv in r:
        assert type(rv) == gssh.Review
        assert rv.SHA1 == open_review.SHA1


def test_statusreviews(monkeypatch, connected_site):
    ''' Test the various searches for specific statii '''

    def dummy_execute_on(self, site):
            assert isinstance(site, gssh.Site)
            return ('Success', self._Query__query)

    monkeypatch.setattr(gssh.Query, 'execute_on', dummy_execute_on)
    methods = [gssh.open_reviews, gssh.abandoned_reviews, gssh.merged_reviews]

    # Test that an unrestricted query does not contain the project or branch
    # search terms
    for f in methods:
        q = f()
        assert isinstance(q, gssh.Query)
        r = q.execute_on(connected_site)
        assert type(r[0]) == type('')
        assert r[0] == 'Success'
        assert 'status:' in r[1]
        assert not 'project:' in r[1]
        assert not 'branch:' in r[1]

    # Test that a query for s epcific branch contains the branch search term.
    for f in methods:
        q = f(project='fred')
        assert isinstance(q, gssh.Query)
        r = q.execute_on(connected_site)
        assert type(r[0]) == type('')
        assert r[0] == 'Success'
        assert 'status:' in r[1]
        assert 'project:fred' in r[1]
        assert not 'branch:' in r[1]

    # Test that a query for sepcific branch and project contains the right
    # search terms
    for f in methods:
        q = f(project='fred', branch='next')
        assert isinstance(q, gssh.Query)
        r = q.execute_on(connected_site)
        assert type(r[0]) == type('')
        assert r[0] == 'Success'
        assert 'status:' in r[1]
        assert 'project:fred' in r[1]
        assert 'branch:next' in r[1]
