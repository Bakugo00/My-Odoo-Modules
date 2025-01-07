{
    "name": "Incubator Management",
    "summary": "Module to manage incubator documents",
    "version": "16.0.1.4.1",
    "license": "AGPL-3",
    "category": "Management",
    "author": "Benottmane Bahaeddine",
    "depends": ['base'],
    "data": [
        "data/incubator_data.xml",
        #security groups
        "security/incubator_security.xml",
        "security/ir.model.access.csv",
        #menus
        "views/menu.xml",
        'views/incubator_students_views.xml',
        'views/incubator_projects_views.xml',
        'views/incubator_objective_views.xml',
    ],
    "application": True,
    "installable": True,
}
