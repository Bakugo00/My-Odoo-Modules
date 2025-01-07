from odoo import _, api, fields, models, tools

class IncubatorObjective(models.Model):
    _name="incubator.objective"

    name = fields.Char(string="Objective Name", required=True)
    # objectives=fields.Selection([
    #     ('label_startup','Label Startup'),
    #     ('brevet_innovation','Brevet d\'innovation'),
    #     ('recherche_scientifique','Recherche Scientifique'),
    #     ('micro_entreprise','Micro entreprise'),
    #     ('je_ne_sais_pas','Je ne sais pas'),
    #     ]
    # )