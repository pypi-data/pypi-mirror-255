# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from functools import partial

from babel import numbers
from flask import json

from trytond.exceptions import UserError
from trytond.i18n import gettext
from trytond.model import ModelSQL, ModelView, Unique, fields, sequence_ordered
from trytond.pool import PoolMeta
from trytond.pyson import Eval

from nereid import current_website, url_for


class Template(metaclass=PoolMeta):
    "Product Template"
    __name__ = 'product.template'

    variation_attributes = fields.One2Many('product.variation_attributes',
        'template', 'Variation Attributes')

    def validate_variation_attributes(self):
        for product in self.products_displayed_on_eshop:
            # Ugly hack to disable validation on copy, when validate is called
            # in the copy chain before the actual attributes are copied
            # (#2587).
            if '-copy-' not in product.uri:
                product.validate_attributes()

    @classmethod
    def validate(cls, templates):
        super().validate(templates)
        for template in templates:
            template.validate_variation_attributes()

    def _get_product_variation_data(self):
        """
        This method returns the variation data in a serializable format
        for the main API. Extend this module to add data that your
        customization may need. In most cases, just extending the serialize
        api method in product and variation should be sufficient.
        """
        variation_attributes = [
            variation.serialize() for variation in self.variation_attributes]

        variants = []
        for product in self.products_displayed_on_eshop:
            variant_data = product.serialize(purpose='variant_selection')
            variant_data['attributes'] = {}
            for variation in self.variation_attributes:
                if variation.attribute.type_ == 'selection':
                    # Selection option objects are obviously not serializable
                    # So get the name
                    variant_data['attributes'][variation.attribute.id] = str(
                        product.get_attribute_value(variation.attribute).id)
                else:
                    variant_data['attributes'][variation.attribute.name] = \
                        product.get_attribute_value(variation.attribute)
            variants.append(variant_data)

        rv = {
            'variants': variants,
            'variation_attributes': variation_attributes,
            }
        return rv

    def get_product_variation_data(self):
        """
        Returns json data for product for variants. The data returned
        by this method should be sufficient to render a product selection
        interface based on variation data.

        The structure of the data returned is::

        {
            'variants': [
                # A list of active records of the variants if not
                # requested as JSON. If JSON, the record is serialized
                # with type JSON.
                {
                    # see documentation of the serialize method
                    # on product.product to see values sent.
                }
            ],
            'variation_attributes': [
                {
                    # see documentation of the serialize method
                    # on product.varying_attribute to see values sent.
                }
                ...
            ]
        }

        .. tip::

            If your downstream module needs more information in the
            JSON, subclass and implement _get_product_variation_data
            which returns a dictionary. Otherwise, it would require you
            to deserialize, add value and then serialize again.
        """
        return json.dumps(self._get_product_variation_data())


class Product(metaclass=PoolMeta):
    "Product"
    __name__ = 'product.product'

    def validate_attributes(self):
        """Check if product defines all the attributes specified in
        template variation attributes.
        """
        if not self.displayed_on_eshop:
            return
        required_attrs = set(
            [v.attribute for v in self.template.variation_attributes])
        missing = required_attrs - \
            set([attr.attribute for attr in self.attributes])
        if missing:
            missing = '; '.join([attr.name for attr in missing])
            raise UserError(
                gettext('nereid_catalog_variants.missing_attributes',
                    name=self.rec_name, missing=missing))

    @classmethod
    def validate(cls, products):
        super().validate(products)
        for product in products:
            product.validate_attributes()

    def get_attribute_value(self, attribute, silent=True):
        """
        :param attribute: Active record of attribute
        """
        for product_attr in self.attributes:
            if product_attr.attribute == attribute:
                return getattr(product_attr,
                    'value_%s' % attribute.type_)
        else:
            if silent:
                return True
            raise AttributeError(attribute.name)

    def serialize(self, purpose=None):
        """
        Return serializable dictionary suitable for use with variant
        selection.
        """
        if purpose != 'variant_selection':
            return super().serialize(purpose)

        currency_format = partial(
            numbers.format_currency,
            currency=current_website.company.currency.code,
            locale=current_website.default_locale.language.code
            )

        return {
            'id': self.id,
            'rec_name': self.rec_name,
            'name': self.name,
            'code': self.code,
            'price': currency_format(self.sale_price(1)),
            'url': url_for('product.product.render', uri=self.uri),
            'image_urls': [
                {
                    'large': (
                        image.transform_command().thumbnail(500, 500, 'a')
                        .url()
                    ),
                    'thumbnail': (
                        image.transform_command().thumbnail(120, 120, 'a')
                        .url()
                    ),
                    'regular': image.url,
                }
                for image in self.get_images()
                ],
            }


class ProductVariationAttributes(sequence_ordered(), ModelSQL, ModelView):
    "Variation attributes for product template"
    __name__ = 'product.variation_attributes'

    template = fields.Many2One('product.template', 'Template', required=True,
        ondelete='CASCADE')
    attribute = fields.Many2One('product.attribute', 'Attribute',
        required=True,
        domain=[('sets', '=',
                Eval('_parent_template', {}).get('attribute_set', -1))])
    widget = fields.Selection([
            ('dropdown', 'Dropdown'),
            ('swatches', 'Swatches'),
            ], 'Widget', required=True)

    @staticmethod
    def default_widget():
        return 'dropdown'

    def serialize(self, purpose=None):
        """
        Returns serialized version of the attribute::

            {
                'sequence': 1, # Integer id to determine order
                'name': 'shirt color', # Internal name of the attribute
                'display_name': 'Color', # (opt) display name of attr
                'rec_name': 'Color', # The name that should be shown
                'widget': 'swatch', # clue on how to render widget
                'options': [
                    # id, value of the options available to choose from
                    (12, 'Blue'),
                    (13, 'Yellow'),
                    ...
                ]
            }
        """
        if self.attribute.type_ == 'selection':
            # The attribute type needs options to choose from.
            # Send only the options that the products displayed on webshop
            # can have, instead of the exhaustive list of attribute options
            # the attribute may have.
            #
            # For example, the color attribute values could be
            # ['red', 'yellow', 'orange', 'green', 'black', 'blue']
            # but the shirt itself might only be available in
            # ['red', 'yellow']
            #
            # This can be avoided by returning options based on the product
            # rather than on the attributes list of values
            options = set()
            for product in self.template.products_displayed_on_eshop:
                value = product.get_attribute_value(self.attribute)
                options.add((value.id, value.name))
        else:
            options = []

        return {
            'sequence': self.sequence,
            'name': self.attribute.name,
            'display_name': self.attribute.display_name,
            'widget': self.widget,
            'options': list(options),
            'attribute_id': self.attribute.id,
            }


class ProductAttribute(metaclass=PoolMeta):
    __name__ = 'product.attribute'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('unique_name', Unique(table, table.name),
                'Attribute name must be unique!'),
            ]
