# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import logging

from trytond.pool import Pool, PoolMeta

from nereid import render_template, request, route

from .pagination import ElasticPagination

logger = logging.getLogger(__name__)


class Website(metaclass=PoolMeta):
    __name__ = 'nereid.website'

    @classmethod
    def auto_complete(cls, phrase):
        """
        This is a downstream implementation which uses elasticsearch to return
        results for a query.
        """
        pool = Pool()
        Product = pool.get('product.product')
        Config = pool.get('elasticsearch.configuration')(1)

        if not Config.get_es_connection(timeout=5):
            # NO ES fallback to default search
            return super().auto_complete(phrase)

        return Product._es_autocomplete(phrase)

    @classmethod
    @route('/search')
    def quick_search(cls):
        """
        This version of quick_search uses elasticsearch to build
        search results for searches from the website.
        """
        pool = Pool()
        Product = pool.get('product.product')
        Config = pool.get('elasticsearch.configuration')(1)

        if not Config.get_es_connection(timeout=5):
            # NO ES fallback to default search
            return super().quick_search()

        page = request.args.get('page', 1, type=int)
        phrase = request.args.get('q', '')

        search_obj = Product._quick_search_es(phrase)

        products = ElasticPagination(
            Product.__name__, search_obj, page, Product.per_page
        )

        if products:
            logger.info(
                "Search for %s yielded in %d results." %
                (phrase, products.count)
            )
        else:
            logger.info(
                "Search for %s yielded no results from elasticsearch." % phrase
            )

        return render_template(
            'search-results.jinja',
            products=products,
            facets=products.result_set.facets
        )
