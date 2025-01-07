from odoo import _, api, fields, models, tools

class IncubatorSupervisor(models.Model):
    _name= "incubator.supervisor"
    _description= "Encadrants de l'incubateur"
    
    supervisor_name = fields.Char(string="Nom de l'encadrant")
    supervisor_email = fields.Char(string="Email de l'encadrant ")