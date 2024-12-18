# -*- coding: utf-8 -*-
###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#
#   Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Aslam A K( odoo@cybrosys.com )
#
#   You can modify it under the terms of the GNU AFFERO
#   GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   (AGPL v3) along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': "Cheque Print",

    'summary': """Print bank cheques format in odoo""",
    'description': """ This module was developed to print cheques formats in
     odoo community edition""",
     'author': "P7",
    'website': "https://www.pinnacleseven.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','account_check_printing','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/cheque_format_views.xml',
        'views/account_payment_views.xml',
        'report/cheque_format_templates.xml',
        'report/cheque_format_reports.xml',
        'wizard/cheque_type_views.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
}
