'''
Tests for all classes and functions contained in the gerritssh.review
module.

'''

import pytest

from gerritssh import query
from gerritssh import review


def test_init(open_review):
    '''
    Test the creation of Review and, by extension, Patchset objects.

    Primarily, this focuses on catching all the invalid constructor
    calls. The open_review fixture is used to ensure that patch sets
    are also successfully decoded (thus checking the fixture itself).

    '''
    with pytest.raises(TypeError):
        _ = review.Review('')

    with pytest.raises(TypeError):
        _ = review.Patchset(1, {})

    with pytest.raises(TypeError):
        _ = review.Patchset(open_review, 1)

    with pytest.raises(TypeError):
        _ = review.Patchset(1, 2)

    _ = review.Patchset(open_review, {})


def test_conversions(open_review_text, open_review_json):
    '''
    Test the conversion routines used to convert the responses from
    Gerrit to either a list of text strings or array of JSON objects.

    '''
    q = query.Query()
    j = q.text_to_json(open_review_text)
    assert j == open_review_json
    assert q.text_to_list(open_review_text, True) == \
        [l for l in map(str.strip, open_review_text.split('\n')) if l]


def test_properties(open_review, open_review_json):
    '''
    Test that all the properties are accessible from a properly
    constructed Review object (the open_review fixture).

    Do not check for explicit values, so as to avoid tying the tests
    to the actual review used for the fixtures.

    Just call all the properties to ensure nothing asserts unexpectedly

    '''
    orj = open_review_json[0]
    r = open_review
    _ = r.highest_patchset_number
    assert len(r.patchsets) == r.highest_patchset_number
    assert r.highest_patchset.number == r.highest_patchset_number
    _ = r.author
    _ = r.created_on
    assert not r.merged
    assert not r.merged_on

    _ = r.last_updated_on
    _ = r.age
    assert r.raw == orj
    _ = r.summary
    _ = r.SHA1
#   _ = r.parents  # Not in test data
    _ = r.repo_name
    _ = r.number
    _ = r.url
    assert r.host == 'review.openstack.org'
    _ = r.ref

    with pytest.raises(AttributeError):
        _ = r.doesnotexist

    for p in list(r.patchsets.values()):
        _ = p.raw
        _ = p.author
        _ = p.ref
        _ = p.created_on

    p = r.patchsets[1]

    with pytest.raises(AttributeError):
        _ = p.doesnotexist
