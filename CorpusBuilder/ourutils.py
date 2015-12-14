#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Radim Rehurek <radimrehurek@seznam.cz>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

"""
This module contains various general utility functions.
"""

from __future__ import with_statement

import logging
logger = logging.getLogger('gensim.utils')

try:
    from html.entities import name2codepoint as n2cp
except ImportError:
    from htmlentitydefs import name2codepoint as n2cp
try:
    import cPickle as _pickle
except ImportError:
    import pickle as _pickle

import re
import unicodedata
import os

import itertools

from functools import wraps # for `synchronous` function lock
import multiprocessing
import shutil
import sys

from contextlib import contextmanager


if sys.version_info[0] >= 3:
    unicode = str

from six import iteritems, u, string_types, unichr

try:
    from pattern.en import parse
    logger.info("'pattern' package found; utils.lemmatize() is available for English")
    HAS_PATTERN = True
except ImportError:
    HAS_PATTERN = False

PAT_ALPHABETIC = re.compile('([\-"\–(\w]+[),.?:;!"–]*)|([\n]+)', re.UNICODE)

RE_HTML_ENTITY = re.compile(r'&(#?)([xX]?)(\w{1,8});', re.UNICODE)



def synchronous(tlockname):
    """
    A decorator to place an instance-based lock around a method.
    Adapted from http://code.activestate.com/recipes/577105-synchronization-decorator-for-class-methods/
    """
    def _synched(func):
        @wraps(func)
        def _synchronizer(self, *args, **kwargs):
            tlock = getattr(self, tlockname)
            logger.debug("acquiring lock %r for %s" % (tlockname, func.func_name))

            with tlock: # use lock as a context manager to perform safe acquire/release pairs
                logger.debug("acquired lock %r for %s" % (tlockname, func.func_name))
                result = func(self, *args, **kwargs)
                logger.debug("releasing lock %r for %s" % (tlockname, func.func_name))
                return result
        return _synchronizer
    return _synched


class NoCM(object):
    def acquire(self):
        pass
    def release(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        pass
nocm = NoCM()


@contextmanager
def file_or_filename(input):
    """
    Return a file-like object ready to be read from the beginning. `input` is either
    a filename (gz/bz2 also supported) or a file-like object supporting seek.
    """
    if isinstance(input, string_types):
        # input was a filename: open as file
        yield smart_open(input)
    else:
        # input already a file-like object; just reset to the beginning
        input.seek(0)
        yield input


def deaccent(text):
    """
    Remove accentuation from the given string. Input text is either a unicode string or utf8 encoded bytestring.
    Return input string with accents removed, as unicode.
    >>> deaccent("Šéf chomutovských komunistů dostal poštou bílý prášek")
    u'Sef chomutovskych komunistu dostal postou bily prasek'
    """
    if not isinstance(text, unicode):
        # assume utf8 for byte strings, use default (strict) error handling
        text = text.decode('utf8')
    norm = unicodedata.normalize("NFD", text)
    result = u('').join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)


def copytree_hardlink(source, dest):
    """
    Recursively copy a directory ala shutils.copytree, but hardlink files
    instead of copying. Available on UNIX systems only.
    """
    copy2 = shutil.copy2
    try:
        shutil.copy2 = os.link
        shutil.copytree(source, dest)
    finally:
        shutil.copy2 = copy2


def tokenize(text, lowercase=False, deacc=False, errors="strict", to_lower=False, lower=False):
    """
    Iteratively yield tokens as unicode strings, optionally also lowercasing them
    and removing accent marks.
    Input text may be either unicode or utf8-encoded byte string.
    The tokens on output are maximal contiguous sequences of alphabetic
    characters (no digits!).
    >>> list(tokenize('Nic nemůže letět rychlostí vyšší, než 300 tisíc kilometrů za sekundu!', deacc = True))
    [u'Nic', u'nemuze', u'letet', u'rychlosti', u'vyssi', u'nez', u'tisic', u'kilometru', u'za', u'sekundu']
    """
    lowercase = lowercase or to_lower or lower
    text = to_unicode(text, errors=errors)
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    for word in text.split(' '):
        yield word


def simple_preprocess(doc, deacc=False, min_len=1, max_len=150):
    """
    Convert a document into a list of tokens.
    This lowercases, tokenizes, stems, normalizes etc. -- the output are final
    tokens = unicode strings, that won't be processed any further.
    """
    tokens = [token for token in tokenize(doc, lower=False, deacc=deacc, errors='ignore')
            if min_len <= len(token) <= max_len and not token.startswith('_')]
    return tokens


def any2utf8(text, errors='strict', encoding='utf8'):
    """Convert a string (unicode or bytestring in `encoding`), to bytestring in utf8."""
    if isinstance(text, unicode):
        return text.encode('utf8')
    # do bytestring -> unicode -> utf8 full circle, to ensure valid utf8
    return unicode(text, encoding, errors=errors).encode('utf8')
to_utf8 = any2utf8


def any2unicode(text, encoding='utf8', errors='strict'):
    """Convert a string (bytestring in `encoding` or unicode), to unicode."""
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding, errors=errors)
to_unicode = any2unicode


def chunkize_serial(iterable, chunksize, as_numpy=False):
    """
    Return elements from the iterable in `chunksize`-ed lists. The last returned
    element may be smaller (if length of collection is not divisible by `chunksize`).
    >>> print(list(grouper(range(10), 3)))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    import numpy
    it = iter(iterable)
    while True:
        if as_numpy:
            # convert each document to a 2d numpy array (~6x faster when transmitting
            # chunk data over the wire, in Pyro)
            wrapped_chunk = [[numpy.array(doc) for doc in itertools.islice(it, int(chunksize))]]
        else:
            wrapped_chunk = [list(itertools.islice(it, int(chunksize)))]
        if not wrapped_chunk[0]:
            break
        # memory opt: wrap the chunk and then pop(), to avoid leaving behind a dangling reference
        yield wrapped_chunk.pop()

grouper = chunkize_serial



class InputQueue(multiprocessing.Process):
    def __init__(self, q, corpus, chunksize, maxsize, as_numpy):
        super(InputQueue, self).__init__()
        self.q = q
        self.maxsize = maxsize
        self.corpus = corpus
        self.chunksize = chunksize
        self.as_numpy = as_numpy

    def run(self):
        if self.as_numpy:
            import numpy # don't clutter the global namespace with a dependency on numpy
        it = iter(self.corpus)
        while True:
            chunk = itertools.islice(it, self.chunksize)
            if self.as_numpy:
                # HACK XXX convert documents to numpy arrays, to save memory.
                # This also gives a scipy warning at runtime:
                # "UserWarning: indices array has non-integer dtype (float64)"
                wrapped_chunk = [[numpy.asarray(doc) for doc in chunk]]
            else:
                wrapped_chunk = [list(chunk)]

            if not wrapped_chunk[0]:
                self.q.put(None, block=True)
                break

            try:
                qsize = self.q.qsize()
            except NotImplementedError:
                qsize = '?'
            logger.debug("prepared another chunk of %i documents (qsize=%s)" %
                        (len(wrapped_chunk[0]), qsize))
            self.q.put(wrapped_chunk.pop(), block=True)
#endclass InputQueue


if os.name == 'nt':
    logger.info("detected Windows; aliasing chunkize to chunkize_serial")

    def chunkize(corpus, chunksize, maxsize=0, as_numpy=False):
        for chunk in chunkize_serial(corpus, chunksize, as_numpy=as_numpy):
            yield chunk
else:
    def chunkize(corpus, chunksize, maxsize=0, as_numpy=False):
        """
        Split a stream of values into smaller chunks.
        Each chunk is of length `chunksize`, except the last one which may be smaller.
        A once-only input stream (`corpus` from a generator) is ok, chunking is done
        efficiently via itertools.
        If `maxsize > 1`, don't wait idly in between successive chunk `yields`, but
        rather keep filling a short queue (of size at most `maxsize`) with forthcoming
        chunks in advance. This is realized by starting a separate process, and is
        meant to reduce I/O delays, which can be significant when `corpus` comes
        from a slow medium (like harddisk).
        If `maxsize==0`, don't fool around with parallelism and simply yield the chunksize
        via `chunkize_serial()` (no I/O optimizations).
        >>> for chunk in chunkize(range(10), 4): print(chunk)
        [0, 1, 2, 3]
        [4, 5, 6, 7]
        [8, 9]
        """
        assert chunksize > 0

        if maxsize > 0:
            q = multiprocessing.Queue(maxsize=maxsize)
            worker = InputQueue(q, corpus, chunksize, maxsize=maxsize, as_numpy=as_numpy)
            worker.daemon = True
            worker.start()
            while True:
                chunk = [q.get(block=True)]
                if chunk[0] is None:
                    break
                yield chunk.pop()
        else:
            for chunk in chunkize_serial(corpus, chunksize, as_numpy=as_numpy):
                yield chunk


def make_closing(base, **attrs):
    """
    Add support for `with Base(attrs) as fout:` to the base class if it's missing.
    The base class' `close()` method will be called on context exit, to always close the file properly.
    This is needed for gzip.GzipFile, bz2.BZ2File etc in older Pythons (<=2.6), which otherwise
    raise "AttributeError: GzipFile instance has no attribute '__exit__'".
    """
    if not hasattr(base, '__enter__'):
        attrs['__enter__'] = lambda self: self
    if not hasattr(base, '__exit__'):
        attrs['__exit__'] = lambda self, type, value, traceback: self.close()
    return type('Closing' + base.__name__, (base, object), attrs)


def smart_open(fname, mode='rb'):
    _, ext = os.path.splitext(fname)
    if ext == '.bz2':
        from bz2 import BZ2File
        return make_closing(BZ2File)(fname, mode)
    if ext == '.gz':
        from gzip import GzipFile
        return make_closing(GzipFile)(fname, mode)
    return open(fname, mode)






