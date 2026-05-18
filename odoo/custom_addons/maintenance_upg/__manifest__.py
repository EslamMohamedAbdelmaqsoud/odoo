{
    'name': 'Smart Maintenance Upgrade',
    'version': '1.0',
    'category': 'Manufacturing/Maintenance',
    'summary': 'Meter-based maintenance with tasks and spare parts',
    'depends': ['base', 'maintenance', 'stock', 'product'],  # يعتمد على المخازن والصيانة
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_views.xml',
        'data/maintenance_cron.xml',
    ],
    'installable': True,
    'application': True,
}
