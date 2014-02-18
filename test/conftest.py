'''
Pytest test fixtures used in the various unit tess contained in other modules.

'''

import pytest
import gerritssh


@pytest.fixture()
def connected_site(monkeypatch):
    '''
    This fixture provides a Site object, monkeypatched so that any attempt to
    execute a command acts as if a 'gerrit version' command had been executed.

    In essence it provides a properly constructed Site object which will report
    a version of 1.0.0 and a site of 'gerrit.example.com.

    '''
    monkeypatch.setattr(gerritssh.gerritsite, '_check_output',
                        lambda *args, **kwargs: 'gerrit version 1.0.0\n')
    s = gerritssh.Site('gerrit.example.com')
    assert not s.connected, 'Thinks its connected after construction'
    s.connect()
    return s

'''
The file 'testreview.json' contains the result of a query for a (randomly
chosen) open code review at review.openstack.org. It is used within numerous
tests which expect a properly formatted response from a working Gerrit
instance.

'''
with open('test/testreview.json', 'r') as f:
    __random_text = f.read()


@pytest.fixture()
def open_review_text():
    '''
    This fixure returns the plain text response of a query to fetch a single
    open review.

    '''
    return __random_text


@pytest.fixture()
def open_review_json(open_review_text):
    '''
    This fixture provides the canned open review, converted to a JSON
    dictionary.

    '''
    import json
    return [json.loads(l.strip()) for l in open_review_text.split('\n') if l]


@pytest.fixture()
def open_review(open_review_json):
    '''
    This fixture provides a Review object initialized with a single open
    review.

    '''
    from gerritssh import Review
    r = Review(open_review_json[0])
    assert r.raw == open_review_json[0]
    return r
