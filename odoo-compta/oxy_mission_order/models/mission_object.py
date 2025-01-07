# -*- encoding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError

class MissionObject(models.Model):
    _name = 'hr.mission.object'
    _order = "name desc"
    _rec_name = "name"

    name = fields.Char(string="Objet de la mission",required=True)