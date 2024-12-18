# -*- coding: utf-8 -*-
{
    'name': "p7_invoice_api",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
                    This module is for creating invoice using API and Side Navigation Menu-bar
    """,

    'author': "Pinnacle Seven Technologies Pvt Ltd",
    'website': "https://www.pinnacleseven.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','product'],

    # always loaded
    'data': [
        'views/group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/invoice.xml',
        'views/invoice_line.xml',
        'views/product_view.xml',
        'views/account_move_view.xml',
        'views/partner_view.xml',
        'views/api_keys.xml',
        'views/res_country.xml',
        'views/city_master.xml',
        'views/jinren.xml',
    ],   
    'license': 'LGPL-3',
}

