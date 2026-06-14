{
    'name': 'School',
    'author': 'Eslam Mohamed Abdelmaqsoud',
    'version': '17.0',
    'summary': 'this module for school management system',
    'category': 'School Management System',
    'depends': ['base', 'sale_management', 'account','hr', 'mail'
                ],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/base_menu.xml",
        "views/student_view.xml",
        "views/course_view.xml",
        "views/year_view.xml",
        "views/classs_view.xml",
        "views/subject_view.xml",
        "wizard/ex_wizard_view.xml",
        "wizard/employee_report_wizard_view.xml",
        "reports/student_report.xml",
        "reports/invoice_report_inherit.xml",
        "reports/employee_report_view.xml",
    ],
    'application': True,

}
