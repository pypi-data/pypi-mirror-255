# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
# from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer

import c2.patch.jasplitter


class C2PatchJasplitterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=c2.patch.jasplitter)

    def setUpPloneSite(self, portal):
        pass
        # applyProfile(portal, 'c2.patch.jasplitter:default')


C2_PATCH_JASPLITTER_FIXTURE = C2PatchJasplitterLayer()


C2_PATCH_JASPLITTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(C2_PATCH_JASPLITTER_FIXTURE,),
    name='C2PatchJasplitterLayer:FunctionalTesting'
)
