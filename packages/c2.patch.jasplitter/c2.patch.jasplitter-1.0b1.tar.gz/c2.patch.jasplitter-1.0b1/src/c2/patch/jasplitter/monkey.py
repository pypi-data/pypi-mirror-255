# coding: utf-8
import unicodedata
import six
from Products.CMFPlone.UnicodeSplitter.config import (
    rx_U,
    rxGlob_U,
    rx_L,
    rxGlob_L,
    rx_all,
    pattern,
    pattern_g
)


def bigram(u, limit=1):
    """Split into bi-gram.
    limit arg describes ending process.
    If limit = 0 then
        日本人-> [日本,本人, 人]
        金 -> [金]
    If limit = 1 then
        日本人-> [日本,本人]
        金 -> [金]
    """
    if len(u) == 1:
        return [u]
    else:
        if six.PY2:
            return [u[i:i + 2] for i in xrange(len(u) - limit)]
        else:
            return [u[i:i + 2] for i in range(len(u) - limit)]


def process_unicode(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rx_U.findall(normalized):
        swords = [g.group() for g in pattern.finditer(word)]
        for sword in swords:
            if not rx_all.match(sword[0]):
                yield sword
            else:
                for x in bigram(sword, 1):
                    yield x


def process_unicode_glob(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.  Considering globbing.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rxGlob_U.findall(normalized):
        swords = [g.group() for g in pattern_g.finditer(word)
                  if g.group() not in u"*?"]
        for i, sword in enumerate(swords):
            if not rx_all.match(sword[0]):
                yield sword
            else:
                limit = 1
                if len(sword) == 1:
                    bigramed = [sword + u"*"]
                    # bigramed = [sword]  # TODO?
                else:
                    bigramed = bigram(sword, limit)
                for x in bigramed:
                    yield x
