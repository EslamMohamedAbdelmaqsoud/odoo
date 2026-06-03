{
    'name': 'BioTime Integration',
    'author': 'Eslam Mohamed Abdelmaqsoud',
    'version': '17.0',
    'depends': ['base',
                ],
    'data': [
        "security/ir.model.access.csv",
        'data/biotime_cron.xml',
        "views/base_menu.xml",
        "views/attendance_log_view.xml",

    ],
    'application': True,

}
