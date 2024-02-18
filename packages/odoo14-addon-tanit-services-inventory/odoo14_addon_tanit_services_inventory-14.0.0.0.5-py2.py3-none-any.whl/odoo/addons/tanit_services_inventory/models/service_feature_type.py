# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ServiceFeatureType(models.Model):
    _name = 'tanit_inventory.service.feature.type'
    _description = 'Service Features Types'

    name = fields.Char('Name')
    key = fields.Char('Key')
    description = fields.Text("Description")
    


