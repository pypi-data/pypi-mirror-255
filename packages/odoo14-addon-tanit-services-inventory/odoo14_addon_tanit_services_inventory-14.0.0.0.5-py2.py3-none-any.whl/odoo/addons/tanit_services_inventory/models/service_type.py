# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ServiceType(models.Model):
    _name = 'tanit_inventory.service.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Types'

    name = fields.Char('Name', tracking=True)
    
    description = fields.Html("Description", tracking=True)

    service_type_feature_ids = fields.One2many("tanit_inventory.service.feature", "service_type_id", string="Features")


