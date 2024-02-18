# -*- coding: utf-8 -*-
{
    'name': "Tanit Services Inventory",

    'summary': """
        tanit_services_inventory""",

    'description': """
        tanit_services_inventory
    """,

    'author': "Talaios",
    'website': "https://talaios.coop",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard.xml',
        'views/service.xml',
        'views/service_type.xml',
        'views/service_feature.xml',
        'views/service_feature_type.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,    
}
