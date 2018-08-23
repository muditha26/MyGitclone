# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Information Management',
    'version' : '1.0',
    'category': 'Sales',
    'website': '',
    'summary': 'Product Information Management Odoo module',
    'description': """
Add a PIM (Product Information Management) interface for products, with a category, attributes and attribute values, 
the attributes are made up of a value and type (text, number, radio, select, checkbox)
""",
    'depends': ['product', 'stock'],
    'data': [
        'views/pim.xml',
        'views/product_template_pim_views.xml',
        #'security/pim_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
