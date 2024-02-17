# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from c2.patch.jasplitter.testing import C2_PATCH_JASPLITTER_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import setRoles

import unittest


class TestPatches(unittest.TestCase):
    """Test that c2.patch.jasplitter functions"""

    layer = C2_PATCH_JASPLITTER_FUNCTIONAL_TESTING
    SEARCH_TERMS = (
        (u"検索", 1),
        (u"検索結果・検索インデックス", 1),
        (u"果検", 0),
        (u"結果", 1),
        (u"インデック", 1),
        (u"索イン", 1),
        (u"結果・検索", 1),
        (u"果", 0), #TODO: shuld 1
        (u"果・検索", 0), #TODO: shuld 1
        (u"果・検", 0), #TODO: shuld 1
        (u"る", 1),
        (u"ス", 0),
        (u"「る」の世界", 1),
        (u"脱・原発", 1),
        (u"脱・原", 0), #TODO: shuld 1
        (u"某・図", 1),
        (u"大統領Update", 1)
    )

    SEARCH_ORG_TERMS = (
        (u"検索", 1),
        (u"検索結果・検索インデックス", 0),
        (u"果検", 0),
        (u"結果", 1),
        (u"インデック", 1),
        (u"索イン", 1),
        (u"結果・検索", 0),
        (u"果", 1), #TODO: shuld 0
        (u"果・検索", 1), #TODO: shuld 0
        (u"果・検", 0),
        (u"る", 1),
        (u"ス", 1), #TODO:
        (u"「る」の世界", 1),
        (u"脱・原発", 1),
        (u"脱・原", 0), #TODO: shuld 1
        (u"某・図", 1),
        (u"大統領Update", 0), #TODO: shuld 1
    )

    def setUp(self):
        """Custom shared utility setup for tests."""
        portal = api.portal.get()
        setRoles(portal, TEST_USER_ID, ['Manager'])
        obj = api.content.create(container=portal, type="Document",
                                 title=u"検索結果・検索インデックス")
        obj.description = "「る」の世界\n脱・原発\n某・図\n大統領Update"
        obj.reindexObject()
        setRoles(portal, TEST_USER_ID, ['Member'])
        import transaction
        transaction.commit()

    def test_ja_search(self):
        """Test Japanese search"""
        portal = api.portal.get()
        catalog = portal.portal_catalog
        for term, number in self.SEARCH_TERMS:
            items = catalog(SearchableText=term)
            # print term, number
            self.assertEqual(len(items), number)

    # def test_org_ja_search(self):
    #     """Test Japanese search"""
    #     portal = api.portal.get()
    #     catalog = portal.portal_catalog
    #     for term, number in self.SEARCH_ORG_TERMS:
    #         items = catalog(SearchableText=term)
    #         print term, number
    #         self.assertEqual(len(items), number)


