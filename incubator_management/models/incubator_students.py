from odoo import _, api, fields, models, tools

class IncubatorStudents(models.Model):
    _name = "incubator.students"
    _description = "Etudiants de l'incubateur"

    # Étudiant
    email = fields.Char(string="Adresse Email")
    first_name = fields.Char(string="Prénom")
    last_name = fields.Char(string="Nom")
    birth_date = fields.Date(string="Date de Naissance")
    birth_place = fields.Char(string="Lieu de Naissance")
    residence_address = fields.Char(string="Adresse de Résidence")
    national_id = fields.Char(string="Numéro d'Identification Nationale")
    level = fields.Selection([
        ('l1', 'L1'),
        ('l2', 'L2'),
        ('l3', 'L3'),
        ('m1', 'M1'),
        ('m2', 'M2'),
        ('doctorat', 'Doctorat'),
        ('accompagnateur', 'Accompagnateur'),
        ('diplome', 'Diplomé'),
    ], string="Niveau")
    department = fields.Selection([
        ('math', 'Mathématiques'),
        ('physique', 'Physique'),
        ('chimie', 'Chimie'),
        ('informatique', 'Informatique'),
        ('biologie', 'Biologie'),
        ('geographie', 'Géographie'),
        # Ajouter 25 autres options ici
    ], string="Département")
    faculty = fields.Char(string="Faculté", compute="_compute_faculty", store=True)

    @api.depends('department')
    def _compute_faculty(self):
        for record in self:
            department_to_faculty = {
                'math': 'Faculté des Sciences',
                'physique': 'Faculté des Sciences',
                'chimie': 'Faculté des Sciences',
                'informatique': 'Faculté des Sciences et Techniques',
                'biologie': 'Faculté des Sciences',
                'geographie': 'Faculté des Lettres et Sciences Humaines',
                # Ajouter des correspondances ici pour les 25 autres options
            }
            record.faculty = department_to_faculty.get(record.department, "Autre")
