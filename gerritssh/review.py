r'''
Classes to represent a Gerrit code review and its patch sets

Typically, objects of these classes are created by executing
Query operations. There is little obvious use for a bare Review
or Patchset object.

Both classes override __getattr__ to provide acees to the underling
raw JSON. Thus, instead of::

    ref = somepatchset.raw['ref']

one can simply do::

    ref = somepatchset.ref

It also obviates the need to declare many properties that simply
return a field, without needing any manipulation.

However, some properties such as the patchset number, are defined
as explicit properties to allow conversion to a more natural type.

As a note for contributors, it might seem to make sense to move
these classes into the `query` module. But it is not difficult to
envisage other modules which operate solely on collections of
Review or Patchset objects, and do not themselves need to be
coupled to the `gerritsite` or `query` modules.

Safe for: from review import *

'''

import datetime as dt

try:  # pragma: no cover
    import urllib.parse as urlp  # Python 3
except ImportError:  # pragma: no cover
    import urlparse as urlp  # Python 2


class Patchset(object):
    '''
    A single patch set within a GerritReview

    :param review: The enclosing Review object
    :param raw: The raw JSON extracted from the Review details

    :raises:
        TypeError if review is not a Review object, or if raw is not
        a dictionary.

    Other than in initialization, this class is meant to be read-only
    so all instance variables are declared with double leading underscores
    and provided as properties with getters only.

    A library user is not expected to create instances of this class directly.
    They are created as part of a Review object when processing a response from
    Gerrit.

    '''

    def __init__(self, review, raw):
        if not isinstance(review, Review):
            raise TypeError('review must be of type gerritssh.Review')

        if not isinstance(raw, dict):
            raise TypeError('raw value must be a dict')

        self.__parent_review = review
        self.__raw = raw

    def __getattr__(self, name):
        '''
        Allows direct and easy access to elements in the raw JSON
        representation of the patch set.

        :param name: The key to be returned
        :raises: AttributeError if `name` is not a key in the raw JSON.

        '''
        try:
            return self.__dict__[name]
        except KeyError:
            if self.__raw and name in self.__raw:
                return self.__raw[name]
            else:
                raise AttributeError

    @property
    def raw(self):
        '''
        The raw JSON returned from Gerrit

        :returns:  (dict) The keys and values returned from Gerrit.
        '''
        return self.__raw

    @property
    def author(self):
        '''
        Author of the Patchset

        :returns: (str) The uploader's name if available, else their user name.
        '''
        owner = self.raw['uploader']
        return owner['name'] if 'name' in owner else owner['username']

    @property
    def created_on(self):
        '''
        When was the Patchset created

        :returns: (`datetime`) The date and time the patchset was created
        '''
        return dt.datetime.fromtimestamp(self.raw['createdOn'])

    @property
    def number(self):
        ''' The patchset number as an integer rather than a string '''
        return int(self.raw['number'])


class Review(object):
    '''
    A single code review, containing all patchsets

    :param raw: A dict() representing the raw JSON response from Gerrit

    :raises: TypeError if raw is not a dictionary

    Other than in initialization, this class is meant to be read-only
    so all instance variables are declared with double leading underscores
    and provided as properties with getters only

    '''

    def __init__(self, raw):
        if not isinstance(raw, dict):
            raise TypeError('raw must be a dictionary')

        self.__raw = raw
        self.__patchsets = {}
        self.__host = urlp.urlsplit(self.url).netloc

        if 'patchSets' in self.raw:
            for p in self.raw['patchSets']:
                ps = Patchset(self, p)
                self.__patchsets[ps.number] = ps

        # The JSON for the current patch set may contain more information
        # than is returned in the patchSets object
        if 'currentPatchSet' in self.raw:
            cps = Patchset(self, self.raw['currentPatchSet'])
            self.__patchsets[cps.number] = cps

        self.__highestPatchSetNumber = max(self.patchsets.keys())

    def __getattr__(self, name):
        '''
        Allows direct and easy access to elements in the raw JSON
        representation of the patch set.

        :param name: The key to be returned
        :raises: AttributeError if `name` is not a key in the raw JSON.

        '''
        try:
            return self.__dict__[name]
        except KeyError:
            if self.__raw and name in self.__raw:
                return self.__raw[name]
            else:
                raise AttributeError

    @property
    def host(self):
        ''' The Gerrit host name, e.g. review.example.com '''
        return self.__host

    @property
    def patchsets(self):
        ''' List of Patch sets for this Review '''
        return self.__patchsets

    @property
    def highest_patchset_number(self):
        ''' Number of the latest Patch set in the Review '''
        return self.__highestPatchSetNumber

    @property
    def highest_patchset(self):
        ''' The Patchset object for the current patch set '''
        return self.patchsets[self.highest_patchset_number]

    @property
    def author(self):
        ''' Author of the review. '''
        owner = self.__raw['owner']
        return owner['name'] if 'name' in owner else owner['username']

    @property
    def created_on(self):
        ''' When the review was created '''
        return dt.datetime.fromtimestamp(self.__raw['createdOn'])

    @property
    def merged(self):
        ''' Has the change been merged '''
        return self.raw['status'] == 'MERGED'

    @property
    def merged_on(self):
        ''' When was the review merged. :returns: None if not merged '''
        return self.last_updated_on if self.merged else None

    @property
    def last_updated_on(self):
        ''' When was the review last updated '''
        return dt.datetime.fromtimestamp(self.raw['lastUpdated'])

    @property
    def age(self):
        ''' How old is the review as a timedelta '''
        return (self.last_updated_on - self.created_on
                if self.last_updated_on > self.created_on
                else dt.timedelta(0, 0))

    @property
    def raw(self):
        ''' The raw JSON received from Gerrit '''
        return self.__raw

    @property
    def summary(self):
        ''' Summary line of the commit message '''
        return self.raw['subject']

    @property
    def SHA1(self):  # noqa - Inhibit lowercase naming warning
        ''' SHA1 for the latest Patchset '''
        return self.raw['currentPatchSet']['revision']

    @property
    def repo_name(self):
        ''' The name of the repository (including folders) '''
        return self.raw['project']

    @property
    def number(self):
        ''' The review number a an integer '''
        return int(self.raw['number'])

    @property
    def ref(self):
        ''' The REF string for the review (REFS/CHANGES/...) '''
        return self.highest_patchset.ref

__all__ = ['Review', 'Patchset']
