# Created by 1e0n in 2013
import re
import sys
import hashlib
import logging
import numbers
import collections
from itertools import groupby

from .hashtype import hashtype

if sys.version_info[0] >= 3:
    basestring = str
    unicode = str
    long = int
else:
    range = xrange


def _hashfunc(x):
    return int(hashlib.md5(x).hexdigest(), 16)


class Simhash(object):

    def __init__(
        self, value, f=96, reg=r'[\w\u4e00-\u9fcc]+', hashfunc=None, log=None
    ):
        """
        `f` is the dimensions of fingerprints
        `reg` is meaningful only when `value` is basestring and describes
        what is considered to be a letter inside parsed string. Regexp
        object can also be specified (some attempt to handle any letters
        is to specify reg=re.compile(r'\w', re.UNICODE))
        `hashfunc` accepts a utf-8 encoded string and returns a unsigned
        integer in at least `f` bits.
        """

        self.f = f
        self.reg = reg
        self.value = None

        if hashfunc is None:
            self.hashfunc = _hashfunc
        else:
            self.hashfunc = hashfunc

        if log is None:
            self.log = logging.getLogger("simhash")
        else:
            self.log = log

        if isinstance(value, Simhash):
            self.value = value.value
        elif isinstance(value, basestring):
            self.build_by_text(unicode(value))
        elif isinstance(value, collections.Iterable):
            self.build_by_features(value)
        elif isinstance(value, numbers.Integral):
            self.value = value
        else:
            raise Exception('Bad parameter with type {}'.format(type(value)))

    def __eq__(self, other):
        """
        Compare two simhashes by their value.
        :param Simhash other: The Simhash object to compare to
        """
        return self.value == other.value

    def _slide(self, content, width=4):
        return [content[i:i + width] for i in range(max(len(content) - width + 1, 1))]

    def _tokenize(self, content):
        content = content.lower()
        content = ''.join(re.findall(self.reg, content))
        ans = self._slide(content)
        return ans

    def build_by_text(self, content):
        features = self._tokenize(content)
        features = {k:sum(1 for _ in g) for k, g in groupby(sorted(features))}
        return self.build_by_features(features)

    def build_by_features(self, features):
        """
        `features` might be a list of unweighted tokens (a weight of 1
                   will be assumed), a list of (token, weight) tuples or
                   a token -> weight dict.
        """
        v = [0] * self.f
        masks = [1 << i for i in range(self.f)]
        if isinstance(features, dict):
            features = features.items()
        for f in features:
            if isinstance(f, basestring):
                h = self.hashfunc(f.encode('utf-8'))
                w = 1
            else:
                assert isinstance(f, collections.Iterable)
                h = self.hashfunc(f[0].encode('utf-8'))
                w = f[1]
            for i in range(self.f):
                v[i] += w if h & masks[i] else -w
        ans = 0
        for i in range(self.f):
            if v[i] > 0:
                ans |= masks[i]
        self.value = ans

    def distance(self, another):
        assert self.f == another.f
        x = (self.value ^ another.value) & ((1 << self.f) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans



class SimhashTwo(hashtype):
    def create_hash(self, tokens):
        """Calculates a Charikar simhash with appropriate bitlength.
        Input can be any iterable, but for strings it will automatically
        break it into words first, assuming you don't want to iterate
        over the individual characters. Returns fingerprint so it can be used
        for temporary use without initializing a new object.
        Reference used: http://dsrg.mff.cuni.cz/~holub/sw/shash
        """
        if type(tokens) == str:
            tokens = tokens.split()
        v = [0]*self.hashbits
        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0
            for i in range(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1

        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        self.hash = fingerprint
        return fingerprint

    def _string_hash(self, v):
        "A variable-length version of Python's builtin hash. Neat!"
        if v == "":
            return 0
        else:
            x = ord(v[0]) << 7
            m = 1000003
            mask = 2 ** self.hashbits-1
            for c in v:
                x = ((x*m) ^ ord(c)) & mask
            x ^= len(v)
            if x == -1:
                x = -2
            return x

    def similarity(self, other_hash):
        """Calculate how similar this hash is from another SimhashTwo.
        Returns a float from 0.0 to 1.0 (linear distribution, inclusive)
        """
        if type(other_hash) != SimhashTwo:
            raise Exception('Hashes must be of same type to find similarity')
        b = self.hashbits
        if b != other_hash.hashbits:
            raise Exception('Hashes must be of equal size to find similarity')
        return float(b - self.hamming_distance(other_hash)) / b