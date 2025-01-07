from odoo import api, fields, models

class Categories(models.Model):
    _name = 'calendar.categories'
    _description = 'Calendar Categories'

    user_id = fields.Many2one('res.users', 'Me', default=lambda self: self.env.user)
    categ_id = fields.Many2one('calendar.event.type', string='category')
    active = fields.Boolean('Active', default=True)