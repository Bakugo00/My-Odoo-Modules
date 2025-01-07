# -*- encoding: utf-8 -*-
import time
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from odoo import models,api,fields
#from . import outils
from odoo.tools.safe_eval import safe_eval

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    type = fields.Selection([('gain','Gains'),('retenu','Retenus')],"Type de la Rubrique")