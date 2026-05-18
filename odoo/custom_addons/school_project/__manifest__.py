{
    'name': 'Simple Sales & Customer Management System',
    'version': '17.1',
    'author': 'Eslam Mohamed Abdelmaqsoud',
    'depends': ['base', 'mail', ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/school_customer_view.xml',
        'views/school_product_view.xml',
        'views/school_order_view.xml',
        'reports/school_order_report.xml',
    ],
    'installable': True,
    'application': True,
}
