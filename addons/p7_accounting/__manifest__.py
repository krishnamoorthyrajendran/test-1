# -*- coding: utf-8 -*-
{
    'name': "p7_accounting",

    'summary': "Accounting changes",

    'description': """
                    Accounting module updates
    """,

    'author': "Pinnacle Seven Technologies Pvt Ltd",
    'website': "https://www.pinnacleseven.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
   
    'license': 'LGPL-3',
}

