# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import json

from decimal import Decimal

from trytond.config import config
from trytond.exceptions import UserError
from trytond.modules.nereid_base.tests.common import (
    create_static_file, create_website)
from trytond.pool import Pool
from trytond.tests.test_tryton import with_transaction
from trytond.transaction import Transaction

from nereid.testing import NereidModuleTestCase

config.set('database', 'path', '/tmp')


class NereidCatalogVariantsTestCase(NereidModuleTestCase):
    'Test Nereid Catalog Variants module'
    module = 'nereid_catalog_variants'

    @with_transaction()
    def test0010_product_variation_attributes(self):
        '''
        Test if product has all the attributes of variation_attributes.
        '''
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        ProductAttribute = pool.get('product.attribute')
        ProductAttributeSet = pool.get('product.attribute.set')
        VariationAttributes = pool.get('product.variation_attributes')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)

        with Transaction().set_context(company=company.id):
            # Create attributes
            attribute1, = ProductAttribute.create([{
                'name': 'size',
                'type_': 'selection',
                'display_name': 'Size',
                'selection': [
                    ('create', [{
                        'name': 'm',
                    }, {
                        'name': 'l',
                    }, {
                        'name': 'xl',
                    }])
                ]
            }])
            attribute2, = ProductAttribute.create([{
                'name': 'color',
                'type_': 'selection',
                'selection': [
                    ('create', [{
                        'name': 'blue',
                    }, {
                        'name': 'black',
                    }])
                ]
            }])
            attribute3, = ProductAttribute.create([{
                'name': 'attrib',
                'type_': 'char',
                'display_name': 'Attrib',
            }])
            attribute4, = ProductAttribute.create([{
                'name': 'ø',
                'type_': 'char',
                'display_name': 'ø',
            }])

            # Create attribute set
            attrib_set, = ProductAttributeSet.create([{
                'name': 'Cloth',
                'attributes': [
                    ('add', [attribute1.id, attribute2.id, attribute4.id])
                ]
            }])

            # Create product template with attribute set
            template1, = Template.create([{
                'name': 'THis is Product',
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'attribute_set': attrib_set.id,
            }])

            # Create variation attributes
            VariationAttributes.create([{
                'template': template1.id,
                'attribute': attribute1.id,
            }, {
                'template': template1.id,
                'attribute': attribute2.id,
            }, {
                'template': template1.id,
                'attribute': attribute4.id,
            }])
            # Provide a context language for gettext messages
            with Transaction().set_context(language='en'):
                # Try to create product with no attributes
                with self.assertRaises(UserError):
                    Product.create([{
                        'template': template1.id,
                        'cost_price': Decimal('5'),
                        'displayed_on_eshop': True,
                        'uri': 'uri1',
                        'code': 'SomeProductCode1',
                    }])

                # Try to create product with only one attribute
                with self.assertRaises(UserError):
                    Product.create([{
                        'template': template1.id,
                        'cost_price': Decimal('5'),
                        'displayed_on_eshop': True,
                        'uri': 'uri2',
                        'code': 'SomeProductCode2',
                        'attributes': [
                            ('create', [{
                                'attribute': attribute2.id,
                                'value_selection': attribute2.selection[0].id,
                            }])
                        ],
                    }])

            # Finally create product with all attributes mentioned in
            # template variation_attributes.
            product1, = Product.create([{
                'template': template1.id,
                'cost_price': Decimal('5'),
                'displayed_on_eshop': True,
                'uri': 'uri3',
                'code': 'SomeProductCode3',
                'attributes': [
                    ('create', [{
                        'attribute': attribute1.id,
                        'value_selection': attribute1.selection[1].id,
                    }, {
                        'attribute': attribute2.id,
                        'value_selection': attribute2.selection[0].id,
                    }, {
                        'attribute': attribute4.id,
                        'value_char': 'Test Char Value',
                    }])
                ],
            }])
            self.assertTrue(product1)

    @with_transaction()
    def test_0020_product_variation_data(self):
        """
        Test get_product_variation_data method.
        """
        pool = Pool()
        Product = pool.get('product.product')
        Template = pool.get('product.template')
        Uom = pool.get('product.uom')
        ProductAttribute = pool.get('product.attribute')
        ProductAttributeSet = pool.get('product.attribute.set')
        VariationAttributes = pool.get('product.variation_attributes')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])
        uom, = Uom.search([], limit=1)
        app = self.get_app()

        with Transaction().set_context(company=company.id), \
            app.test_request_context():
            # Create attributes
            attribute1, = ProductAttribute.create([{
                'name': 'size',
                'type_': 'selection',
                'display_name': 'Size',
                'selection': [
                    ('create', [{
                        'name': 'm',
                    }, {
                        'name': 'l',
                    }, {
                        'name': 'xl',
                    }])
                ]
            }])
            attribute2, = ProductAttribute.create([{
                'name': 'color',
                'type_': 'selection',
                'selection': [
                    ('create', [{
                        'name': 'blue',
                    }, {
                        'name': 'black',
                    }])
                ]
            }])

            # Create attribute set
            attrib_set, = ProductAttributeSet.create([{
                'name': 'Cloth',
                'attributes': [
                    ('add', [attribute1.id, attribute2.id])
                ]
            }])

            # Create product template with attribute set
            template1, = Template.create([{
                'name': 'THis is Product',
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'attribute_set': attrib_set.id,
            }])

            # Create variation attributes
            VariationAttributes.create([{
                'template': template1.id,
                'attribute': attribute1.id,
            }, {
                'template': template1.id,
                'attribute': attribute2.id,
            }])

            product1, = Product.create([{
                'template': template1.id,
                'cost_price': Decimal('5'),
                'displayed_on_eshop': True,
                'uri': 'uri3',
                'code': 'SomeProductCode',
                'attributes': [
                    ('create', [{
                        'attribute': attribute1.id,
                        'value_selection': attribute1.selection[1].id,
                    }, {
                        'attribute': attribute2.id,
                        'value_selection': attribute2.selection[0].id,
                    }])
                ],
            }])

            self.assertGreater(len(template1.get_product_variation_data()), 0)

    @with_transaction()
    def test_0030_product_variation_data_images(self):
        """
        Test get_product_variation_data method for images.
        """
        pool = Pool()
        Product = pool.get('product.product')
        Template = pool.get('product.template')
        Uom = pool.get('product.uom')
        Company = pool.get('company.company')

        create_website()
        company, = Company.search([])

        file_memoryview = memoryview(b'test-content1')
        static_file1 = create_static_file(file_memoryview, name='logo1.png')
        file_memoryview = memoryview(b'test-content2')
        static_file2 = create_static_file(file_memoryview, name='logo2.png')

        with Transaction().set_context(company=company.id):
            uom, = Uom.search([], limit=1)
            product_template, = Template.create([{
                'name': 'test template',
                'type': 'goods',
                'list_price': Decimal('10'),
                'default_uom': uom.id,
                'description': 'Description of template',
                'products': [('create', Template.default_products())],
                'media': [('create', [{
                    'static_file': static_file1.id,
                }])],
            }])

            product, = product_template.products

            Product.write([product], {
                'cost_price': Decimal('5'),
                'displayed_on_eshop': True,
                'uri': 'uri1',
                'media': [('create', [{
                    'static_file': static_file2.id,
                }])],
            })

        app = self.get_app()
        with app.test_request_context('/'):
            res = json.loads(product_template.get_product_variation_data())

            self.assertFalse(
                res['variants'][0]['image_urls'][0]['regular']
                is None)
            self.assertFalse(
                res['variants'][0]['image_urls'][0]['thumbnail']
                is None)
            self.assertFalse(
                res['variants'][0]['image_urls'][0]['large']
                is None)
            self.assertEqual(res['variants'][0]['rec_name'],
                product.rec_name)


del NereidModuleTestCase
