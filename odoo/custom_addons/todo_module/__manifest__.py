{
    'name': 'To-Do Module ',
    'author': 'Eslam Mohamed Abdelmaqsoud',
    'version': '17.0',
    'category': 'tools',
    'summary': 'To-Do Module',
    'depends': ['base', 'mail', 'contacts',
                ],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/base_menu.xml",
        "views/todo_task_view.xml",
        'wizard/bulk_task_assignment_wizard.xml',
        'reports/todo_task_report.xml',

    ],

    'application': True,
}
