from odoo import _, api, fields, models, tools

class IncubatorProjects(models.Model):
    _name= "incubator.projects"
    _description= "Projets de l'incubateur"
    
    # Étudiant
    email = fields.Char(string="Adresse Email",required=True)
    first_name = fields.Char(string="Prénom",required=True)
    last_name = fields.Char(string="Nom",required=True)
    birth_date = fields.Date(string="Date de Naissance",required=True)
    birth_place = fields.Char(string="Lieu de Naissance",required=True)
    residence_address = fields.Char(string="Adresse de Résidence",required=True)
    national_id = fields.Char(string="Numéro d'Identification Nationale",required=True)
    level = fields.Selection([
        ('l1', 'L1'),
        ('l2', 'L2'),
        ('l3', 'L3'),
        ('m1', 'M1'),
        ('m2', 'M2'),
        ('doctorat', 'Doctorat'),
        ('accompagnateur', 'Accompagnateur'),
        ('diplome', 'Diplomé'),
    ], string="Niveau",required=True)
    department = fields.Selection([
        ('math', 'Mathématiques'),
        ('physique', 'Physique'),
        ('chimie', 'Chimie'),
        ('informatique', 'Informatique'),
        ('biologie', 'Biologie'),
        ('geographie', 'Géographie'),
        # Ajouter 25 autres options ici
    ], string="Département",required=True)
    faculty = fields.Char(string="Faculté", compute="_compute_faculty", store=True)

    # Projet
    project_title = fields.Char(string="Intitulé du Projet",required=True)
    project_idea_origin = fields.Selection([
        ('personnel', 'Personnel'),
        ('collectif', 'Collectif'),
        ('externe', 'Externe'),
    ], string="Origine de l'idée du Projet",required=True)
    project_team_members = fields.Text(string="Membres de l'Équipe du Projet (s'ils existent)",required=True)
    project_description = fields.Text(string="Description du Projet",required=True)
    project_needs = fields.Text(string="Besoins Éventuels du Projet",required=True)
    project_objectives = fields.Many2many(
        'incubator.objective',
        string="Objectifs du Projet",required=True
    )
    other_objective = fields.Char(string="Autre Objectif")

    # Encadrement
    main_supervisor_name = fields.Char(string="Encadrant Principal (Nom)",required=True)
    main_supervisor_email = fields.Char(string="Encadrant Principal (Email)")
    co_supervisor_name = fields.Char(string="Co-Encadrant (Nom)")
    co_supervisor_email = fields.Char(string="Co-Encadrant (Email)")
    no_supervisor = fields.Boolean(
        string="Sans Encadrant",
        help="Cochez si le projet n'a pas d'encadrants"
    )

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
            
    @api.model
    def create(self, vals):
        email= vals.get('email')
        first_name= vals.get('first_name')
        last_name= vals.get('last_name')
        birth_date= vals.get('birth_date')
        birth_place= vals.get('birth_place')
        residence_address= vals.get('residence_address')
        national_id= vals.get('national_id')
        level= vals.get('level')
        department= vals.get('department')
        faculty= vals.get('faculty')
        main_supervisor_name= vals.get('main_supervisor_name')
        main_supervisor_email= vals.get('main_supervisor_email')
        co_supervisor_name = vals.get('co_supervisor_email')
        co_supervisor_email = vals.get('co_supervisor_email')

        student_vals= {
            'email':email,
            'first_name':first_name,
            'last_name':last_name,
            'birth_date':birth_date,
            'residence_address':residence_address,
            'national_id':national_id,
            'level':level,
            'department':department,
            'faculty':faculty
        }
        student= self.env['incubator.students'].create(student_vals)
        # if main_supervisor_name and main_supervisor_email:
        #     main_supervisor= {
        #         'supervisor_name':main_supervisor_name,
        #         'supervisor_email':main_supervisor_email,
        #     }
        #     main_supervisor= self.env['incubator.supervisor'].create(main_supervisor)
        # if main_supervisor_name and main_supervisor_email:
        #     co_supervisor= {
        #         'supervisor_name':co_supervisor_name,
        #         'supervisor_email':co_supervisor_email,
        #     }
        #     co_supervisor= self.env['incubator.supervisor'].create(co_supervisor)
        res = super(IncubatorProjects, self).create(vals)
        return res
