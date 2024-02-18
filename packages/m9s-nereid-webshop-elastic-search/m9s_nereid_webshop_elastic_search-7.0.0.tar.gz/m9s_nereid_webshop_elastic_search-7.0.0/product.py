# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from pyes import BoolQuery, MatchQuery, NestedQuery
from pyes.filters import ANDFilter, BoolFilter, ORFilter, TermFilter

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval
from trytond.transaction import Transaction

from nereid import request, template_filter


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def create(cls, vlist):
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        products = super().create(vlist)
        IndexBacklog.create_from_records(products)
        return products

    @classmethod
    def write(cls, *args):
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        actions = iter(args)
        all_products = []
        args = []
        for products, values in zip(actions, actions):
            args.extend((products, values))
            all_products.extend(products)
        super().write(*args)
        IndexBacklog.create_from_records(all_products)

    @classmethod
    def delete(cls, products):
        IndexBacklog = Pool().get('elasticsearch.index_backlog')
        IndexBacklog.create_from_records(products)
        super().delete(products)

    def elastic_search_json(self):
        """
        Return a JSON serializable dictionary
        """
        PriceList = Pool().get('product.price_list')
        User = Pool().get('res.user')

        if self.use_template_description:
            description = self.template.description
        else:  # pragma: no cover
            description = self.description

        price_lists = PriceList.search([])
        price_list_data = []

        company = User(Transaction().user).company

        for _list in price_lists:
            price_list_data.append({
                'id': _list.id,
                'price': _list.compute(
                    company.party, self, self.list_price, 1,
                    self.default_uom
                )
            })

        res = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': description,
            'list_price': self.list_price,
            'categories': [{
                'id': category.id,
                'name': category.name,
            } for category in self.categories],
            'tree_nodes': [{
                'id': node.id,
                'name': node.node.name,
                'sequence': node.sequence,
            } for node in self.nodes],
            'type': self.type,
            'price_lists': price_list_data,
            'displayed_on_eshop': (
                "true" if self.displayed_on_eshop else "false"
            ),
            'active': "true" if self.active else "false",
            'attributes': self.elastic_attributes_json(),
        }

        if self.template.account_category:
            res['account_category'] = self.template.account_category.name

        return res

    def elastic_attributes_json(self):
        """
        This method returns the filterable attributes of the product in a
        <name>: <value> format for easy consumption by elasticsearch.
        """
        return dict([
            (attribute.attribute.name, attribute.value) for attribute in
            self.attributes
        ])

    @classmethod
    def get_filterable_attributes(cls):
        """
        This method returns a list of filterable product attributes, which can
        be used in faceting and aggregation. Downstream modules can override
        this method to add any extra filterable fields.
        """
        Attribute = Pool().get('product.attribute')

        return Attribute.search([('filterable', '=', True)])

    @classmethod
    def _update_es_facets(
        cls, search_obj, filterable_attributes=None, facet_filter=None
    ):
        """
        This method takes the input `~pyes.query.Search` object, and then
        adds appropriate terms to the `facet` attribute of this object. By
        default, term facets are generated over filterable attributes.
        """
        # If no filterable attributes in database, return without
        # doing the faceting.
        if not filterable_attributes:
            return

        for attribute in filterable_attributes:
            search_obj.facet.add_term_facet(
                attribute.name,
                facet_filter=facet_filter,
                all_terms=attribute.multiselect,
                size=attribute.display_size,
                order=attribute.display_order
            )

    @classmethod
    def _build_es_query(cls, search_phrase):
        """
        Return an instance of `~pyes.query.Query` for the given phrase.
        If downstream modules wish to alter the behavior of search, for example
        by adding more fields to the query or changing the ranking in a
        different way, this would be the method to change.
        """
        return BoolQuery(
            should=[
                MatchQuery(
                    'code', search_phrase, boost=1.5
                ),
                MatchQuery(
                    'name', search_phrase, boost=2
                ),
                MatchQuery(
                    'name.partial', search_phrase
                ),
                MatchQuery(
                    'name.metaphone', search_phrase
                ),
                MatchQuery(
                    'description', search_phrase, boost=0.5
                ),
                MatchQuery(
                    'account_category', search_phrase
                ),
                NestedQuery(
                    'tree_nodes', BoolQuery(
                        should=[
                            MatchQuery(
                                'tree_nodes.name',
                                search_phrase
                            ),
                        ]
                    )
                ),
            ],
            must=[
                MatchQuery(
                    'active', "true"
                ),
                MatchQuery(
                    'displayed_on_eshop', "true"
                ),
            ]
        )

    @classmethod
    def _build_es_filter(cls, filterable_attributes=None):
        """
        This method generates a `~pyes.filters.Filter` object from the
        request.args dictionary. This is then used to refine the search.

        For example, if the query string is -:
            "/search?q=product&color=black&color=blue&size=xl"
        then the filter will be generated as follows -:
        >>> and_filter = ANDFilter(
                [
                    ORFilter(
                        [
                            TermFilter('color', 'blue'),
                            TermFilter('color', 'black')
                        ]
                    ),
                    ORFilter(
                        [
                            TermFilter('size', 'xl')
                        ]
                    )
                ]
            )
        >>> main_filter = BoolFilter().add_must(and_filter)

        If there are no filters applied in the query string, `None` is returned.
        """
        # If no filterable attributes defined in database, return None.
        if not filterable_attributes:
            return None

        # Search for the attribute name in list of filterable attributes.
        # If present (meaning it is a valid argument), add as TermFilter.
        main_filter = BoolFilter()
        and_filter_list = []

        filterable_attr_names = [x.name for x in filterable_attributes]

        for key in request.args:
            if key in filterable_attr_names:
                or_filter = ORFilter(
                    [
                        TermFilter(key, value) for value
                        in request.args.getlist(key)
                    ]
                )
                and_filter_list.append(or_filter)

        # If no filterable attributes were found in query string
        if not and_filter_list:
            return None

        and_filter = ANDFilter(and_filter_list)
        main_filter.add_must(and_filter)

        return main_filter

    @classmethod
    @template_filter('add_display_counts')
    def add_display_counts(cls, facets):
        """
        This method adds a `display_count` key to each facet depending on
        the corresponding ProductAttribute's `display_count` field.

        :input facets: A nested dictionary containing the facets
        """
        ProductAttribute = Pool().get('product.attribute')

        display_count_attrs = [x.name for x in ProductAttribute.search([
            ('display_count', '=', True)
        ])]

        for key, value in facets.items():
            if key in display_count_attrs:
                value.update({
                    'display_count': True
                })
            else:
                value.update({
                    'display_count': False
                })
        return facets

    @classmethod
    def _quick_search_es(
        cls, search_phrase, autocomplete=False
    ):
        """
        Searches on elasticsearch server for given search phrase.

        TODO:

            * Add support for sorting
            * Migrate to aggregates from facets

        This method passes a query, alongwith term facets, to the search method
        for processing. For example, if one has a `~pyes.query.BoolQuery`
        object, and the product has attributes 'color' and 'size', one may pass
        them as terms as follows -:

        >>> query.facet.add_term_facet('color')
        >>> query.facet.add_term_facet('size')

        The resultset is then obtained and relevant data can be retrieved.

        >>> result_set = conn.search(query, **kwargs)
        >>> print result_set.facets['color']['terms']
        [
            {'count': 1, 'term': 'blue'},
            {'count': 2, 'term': 'black'},
            ...
        ]

        :param search_phrase: Searches for this particular phrase
        :param limit: The number of records to be returned
        :param autocomplete: A boolean which is set to True if the request
        comes from the autocomplete web handler
        :returns: `~pyes.es.ResultSet` object which contains each product's
        attributes
        """
        filterable_attributes = cls.get_filterable_attributes()

        # Create the filter.
        es_filter = cls._build_es_filter(
            filterable_attributes=filterable_attributes
        )
        # Generate the `~pyes.query.Query` object.
        query = cls._build_es_query(search_phrase)

        # Now wrap the query in a `~pyes.query.Search` object for convenience.
        # Apply the filters.
        search_obj = query.search(filter=es_filter)

        # Add faceting. Apply the filters.
        # Faceting isn't applied if autocomplete web handler sends search
        # request.
        if not autocomplete:
            cls._update_es_facets(
                search_obj, facet_filter=es_filter,
                filterable_attributes=filterable_attributes
            )

        return search_obj

    @classmethod
    def _es_autocomplete(cls, phrase):
        """
        Handler for auto-completion via elastic-search.
        The product's URL is generated here as request context is available
        here. This is sent to the front-end for typeaheadJS to compile into
        its suggestions template.
        """
        config = Pool().get('elasticsearch.configuration')(1)

        conn = config.get_es_connection(timeout=5)
        results = []

        search_obj = cls._quick_search_es(phrase, autocomplete=True)

        # Return the top 5 results as a list of dictionaries
        for product in conn.search(
            search_obj,
            doc_types=[config.make_type_name('product.product')],
            size=5
        ):
            display_name = product.name
            if product.code:
                display_name = '%s - %s' % (product.code, display_name)
            results.append(
                {
                    "id": product.id,
                    "type": product.type,
                    "display_name": display_name,
                    "url": cls(product.id).get_absolute_url(
                        _external=True
                    ),
                }
            )

        return results


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        IndexBacklog = pool.get('elasticsearch.index_backlog')
        Product = pool.get('product.product')
        templates = super().create(vlist)
        all_products = []
        all_products.extend(
            [Product(p) for t in templates for p in t.products])
        IndexBacklog.create_from_records(all_products)
        return templates

    @classmethod
    def write(cls, *args):
        pool = Pool()
        IndexBacklog = pool.get('elasticsearch.index_backlog')
        Product = pool.get('product.product')
        actions = iter(args)
        all_products = []
        args = []
        for templates, values in zip(actions, actions):
            args.extend((templates, values))
            all_products.extend(
                [Product(p) for t in templates for p in t.products])
        super().write(*args)
        IndexBacklog.create_from_records(all_products)

    @classmethod
    def delete(cls, templates):
        pool = Pool()
        IndexBacklog = pool.get('elasticsearch.index_backlog')
        Product = pool.get('product.product')
        all_products = []
        all_products.extend(
            [Product(p) for t in templates for p in t.products])
        IndexBacklog.create_from_records(all_products)
        super().delete(templates)


class ProductAttribute(metaclass=PoolMeta):
    __name__ = 'product.attribute'

    filterable = fields.Boolean(
        'Filterable',
        help="Makes the attribute filterable in faceted navigation"
    )

    # All the below are required only if the attribute is filterable
    display_count = fields.Boolean(
        'Display Counts',
        help="Display the number of matching products with the filter",
        states={
            'invisible': ~Bool(Eval('filterable'))
        },
    )
    multiselect = fields.Boolean(
        'Multi Select',
        help="Allow selecting multiple values to filter the attribute",
        states={
            'invisible': ~Bool(Eval('filterable'))
        },
    )
    display_size = fields.Integer(
        'Display Size',
        help="Number of top N matching values to be displayed.",
        states={
            'invisible': ~Bool(Eval('filterable'))
        },
    )
    display_order = fields.Selection(
        [
            ('count', 'No. of matching products (DESC)'),
            ('reverse_count', 'No. of matching products (ASC)'),
            ('term', 'Value of attribute (ASC)'),
            ('reverse_term', 'Value of attribute (DESC)'),
        ], 'Display Order',
        states={
            'invisible': ~Bool(Eval('filterable'))
        },
    )

    @classmethod
    def view_attributes(cls):
        return super().view_attributes() + [
            ('//separator[@id="settings"]', "states", {
                "invisible": ~Bool(Eval("filterable"))
                })]

    @staticmethod
    def default_filterable():
        return True

    @staticmethod
    def default_display_count():
        return False

    @staticmethod
    def default_multiselect():
        return True

    @staticmethod
    def default_display_size():
        return 10

    @staticmethod
    def default_display_order():
        return 'term'
