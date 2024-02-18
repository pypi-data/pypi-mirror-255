# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase


class NereidWebshopElasticSearchTestCase(ModuleTestCase):
    "Test Nereid Webshop Elastic Search module"
    module = 'nereid_webshop_elastic_search'


del ModuleTestCase
