# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class ServiceFeature(models.Model):
    _name = 'tanit_inventory.service.feature'
    _description = 'Service Features'

    service_feature_type_id = fields.Many2one(
        comodel_name='tanit_inventory.service.feature.type',
        string='Feature Type')
    service_id = fields.Many2one('tanit_inventory.service', 'Feature Type')
    service_type_id = fields.Many2one('tanit_inventory.service.type', 'Feature Type')
    value = fields.Char('Value')
    description = fields.Text("Description")

    @api.model
    def create(self, vals):
        res = super().create(vals)

        msg = "Feature <b>" + res.service_feature_type_id.name + "</b> (<code>" + res.service_feature_type_id.key + "</code>) created.</p><ul><li>Value: " + str(res.value) + "</li><li>Description: " + str(res.description) + "</li></ul>"

        if res.service_id:
            res.service_id.message_post(body=msg )
        if res.service_type_id:
            res.service_type_id.message_post(body=msg )
            services_using_type = self.env['tanit_inventory.service'].search([('service_type_id', '=', res.service_type_id.id)])
            for service in services_using_type:
                has_already = self.env['tanit_inventory.service.feature'].search([('service_id', '=', service.id), ('service_feature_type_id', '=', res.service_feature_type_id.id)])
                # if len(has_already.ids) == 0:
                if not has_already:
                    self.env['tanit_inventory.service.feature'].create([{
                        'service_feature_type_id': res.service_feature_type_id.id,
                        'value': res.value,
                        'description': res.description,
                        'service_id': service.id
                    }]) 


        return res

    def write(self, vals):
        for feature in self:
            changes = []

            if 'value' in vals:
                changes.append("<li>Value changed:<ul><li>From: " + str(feature.value) + "</li><li>To: " + str(vals['value']) + "</li></ul></li>")
            if 'description' in vals:
                changes.append("<li>Description changed:<ul><li>From: " + str(feature.description) + "</li><li>To: " + str(vals['description']) + "</li></ul></li>")
            
            if feature.service_id:
                feature.service_id.message_post(body="<p>Feature <b>" + feature.service_feature_type_id.name + "</b> (<code>" + feature.service_feature_type_id.key + "</code>) updated:</p><ul>" + "".join(changes) + "</ul>" )
            if feature.service_type_id:
                feature.service_type_id.message_post(body="<p>Feature <b>" + feature.service_feature_type_id.name + "</b> (<code>" + feature.service_feature_type_id.key + "</code>) updated:</p><ul>" + "".join(changes) + "</ul>" )
        return super().write(vals)