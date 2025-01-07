{
    "name": "Importation des données",
    "category": "Sale",
    "license": "",
        "author": "Emploi Partner",
    "version": "14.0",
    "summary": "Module pour importer des données à partir des fichiers csv dans les tables d'odoo directement",
    "depends": ["base", "account"],
    "data": [
        # security
        "security/ir.model.access.csv",
        # views
        "wizard/data_import.xml",
    ],
    "demo": [],
    "installable": True,
}
