# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class Service(models.Model):
    _name = 'tanit_inventory.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Services'

    partner = fields.Many2one(comodel_name='res.partner', string='Client', tracking=True)
    contact_partner = fields.Many2one(comodel_name='res.partner', string='Contact partner', tracking=True)
    contact_partner_mail = fields.Char('Mail', related='contact_partner.email', readonly=True)
    partner = fields.Many2one(comodel_name='res.partner', string='Client', tracking=True)
    employee = fields.Many2one(comodel_name='hr.employee', string='Employee', tracking=True)
    employee_mail = fields.Char('Mail', related='employee.work_email', readonly=True)
    name = fields.Char(string="Service Name", tracking=True)
    description = fields.Html(string="Description", sanitize_style=True)
    is_active = fields.Boolean(string="Is Active", tracking=True)
    priority = fields.Selection([("0", 'Very Low'),("1", 'Low'),("2", 'Medium'),("3", 'High')])

    service_start_date = fields.Date(string="Service start date", tracking=True)

    service_type_id = fields.Many2one("tanit_inventory.service.type", string="Service Type", tracking=True)

    comments = fields.Html(string="Comments", sanitize_style=True, tracking=True)

    service_contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        tracking=True
    )

    contract_end_date = fields.Date(compute="_compute_contract_end_date")

    service_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        tracking=True
    )

    service_feature_ids = fields.One2many(
        comodel_name="tanit_inventory.service.feature",
        inverse_name="service_id",
        auto_join=True,
        string="Features"
    )
    

    related_service_ids = fields.Many2many("tanit_inventory.service", "tanit_inventory_services_related", "service_1_id", "service_2_id", string="Related services",tracking=True)
    related_service_reverse_ids = fields.Many2many("tanit_inventory.service", "tanit_inventory_services_related", "service_2_id", "service_1_id", string="Related services inverse")
    related_services_computed = fields.Many2many("tanit_inventory.service", "tanit_inventory_services_related", compute="_compute_related_services", inverse="_inverse_related_services", string="Related services")
    
    # https://www.odoo.com/es_ES/forum/ayuda-1/field-referring-to-the-same-model-119371
    def _compute_related_services(self):
        service_ids = self.related_service_ids + self.related_service_reverse_ids
        for service in self:
            service.related_services_computed = service_ids

    def _inverse_related_services(self):
        for service in self:
            service.related_service_ids = [(6,0,service.related_services_computed.ids)]


    @api.depends("service_contract_id")
    def _compute_contract_end_date(self):
        for record in self:
            record.contract_end_date = record.service_contract_id.date_end

    @api.model
    def create(self, vals):
        res = super().create(vals)
        
        res.copy_template_features() # call your method

        return res

    
    def copy_template_features(self):
        # self.service_type_id.service_type_feature_ids

        for feature in self.service_type_id.service_type_feature_ids:
            ff = self.env['tanit_inventory.service.feature'].browse(feature.id);

            self.env['tanit_inventory.service.feature'].create([{
                'service_feature_type_id': ff.service_feature_type_id.id,
                'value': ff.value,
                'description': ff.description,
                'service_id': self.id
            }])            


        return True


    @api.model
    def advanced_search(self, args):
        # https://www.cybrosys.com/blog/how-to-execute-sql-queries-odoo-14

        params = []
        where_clauses = []
        query = "SELECT \"tanit_inventory_service\".id FROM \"tanit_inventory_service\""

        if args['search']:
            where_clauses.append("(\"tanit_inventory_service\".\"name\" like %s)")
            params.append("%" + args['search'] + "%")

        if args['service_type_ids'] and len(args['service_type_ids']):
            where_clauses.append("(\"tanit_inventory_service\".\"service_type_id\" in %s)")
            params.append(tuple(args['service_type_ids']))

        if args['filters'] and len(args['filters']):
            for filt in args['filters']:
                if filt['compare'] in ['=', '!=', 'like', 'not like', 'ilike', 'not ilike', 'in', 'not in']:
                    parts = []
                    parts.append("SELECT \"tanit_inventory_service_feature\".\"id\"")
                    parts.append("FROM \"tanit_inventory_service_feature\"")
                    parts.append("WHERE \"tanit_inventory_service_feature\".\"service_id\" = \"tanit_inventory_service\".id")
                    parts.append("AND \"tanit_inventory_service_feature\".\"service_feature_type_id\" = %s")
                    parts.append("AND \"tanit_inventory_service_feature\".\"value\" " + filt['compare'] + " %s")

                    c = "EXISTS (" + " ".join(parts) + ")"

                    where_clauses.append(c)
                    params.append(filt['service_feature_type_id'])
                    params.append(filt['value'])

        query += " WHERE " + " and ".join(where_clauses)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()

        return result
