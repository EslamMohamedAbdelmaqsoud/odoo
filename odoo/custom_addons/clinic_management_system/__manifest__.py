{
    'name': 'Clinic Management System',
    'depends': ['base', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/base_menu.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
        "wizard/cancel_appointment_wizard_view.xml",
        "reports/prescription_report.xml",
    ],

    'application': True,

}
