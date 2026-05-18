{
    'name': 'Gym Management System ',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Manage Gym Memberships, Trainers, and Attendance',
    'depends': ['base', 'mail', 'account'],  # نعتمد على الحسابات لإصدار الفواتير
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/member_views.xml',
        'views/membership_views.xml',
        'views/gym_membership_contract_views.xml',
        'reports/membership_card_report.xml',
    ],
    'installable': True,
    'application': True,
}
