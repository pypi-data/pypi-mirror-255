.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
c2.patch.jasplitter
==============================================================================


This product is bugfix splitter of Plone for Japanese.

Monkey patching below functions.

- Products.CMFPlone.UnicodeSplitter.splitter.bigram
- Products.CMFPlone.UnicodeSplitter.splitter.process_unicode
- Products.CMFPlone.UnicodeSplitter.splitter.process_unicode_glob

Details
--------

bigram
========

.. code-block:: python

    return [u[i : i + 2] for i in range(len(u) - limit)]


to

.. code-block:: python

    if len(u) == 1:
        return [u]
    else:
        return [u[i:i + 2] for i in range(len(u) - limit)]


process_unicode
================

.. code-block:: python

    swords = [g.group() for g in pattern.finditer(word)]
    for sword in swords:
        if not rx_all.match(sword[0]):
            yield sword
        else:
            yield from bigram(sword, 0)

to

.. code-block:: python

    swords = [g.group() for g in pattern.finditer(word)]
    for sword in swords:
        if not rx_all.match(sword[0]):
            yield sword
        else:
            for x in bigram(sword, 1):  # modified
                yield x

process_unicode_glob
=====================

.. code-block:: python

    if i == len(swords) - 1:
        limit = 1
    else:
        limit = 0

to

.. code-block:: python

    limit = 1


Installation
------------

Install c2.patch.jasplitter by adding it to your buildout::

    [buildout]

    ...

    eggs =
        c2.patch.jasplitter


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://bitbucket.org/cmscom/c2.patch.jasplitter/admin/issues
- Source Code: https://bitbucket.org/cmscom/c2.patch.jasplitter


Support
-------

If you are having issues, please let us know on the issue tracker.


License
-------

The project is licensed under the GPLv2.
