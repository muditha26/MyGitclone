# -*- coding: utf-8 -*-
{
    'name': "Maintenance Equipments Muditha Aravinda",

    'summary': """
        EIM Module""",

    'description': """
        Equipment Information Management
    """,

    'author': "Nisus Solution Pvt ltd",
    'website': "http://www.nisus.lk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance', 'product', 'stock'],


    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        'views/new_file.xml',
        # 'views/views.xml',
        'views/templates.xml',

    ],
    'installable': True,

}
