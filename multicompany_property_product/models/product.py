# -*- coding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_ids = fields.One2many(
        comodel_name='multicompany.property.product',
        compute='_compute_properties',
        inverse='_inverse_properties',
        string='Properties'
    )

    @api.multi
    def _inverse_properties(self):
        ''' Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable, '''
        return

    @api.multi
    def _compute_properties(self):
        for record in self:
            property_obj = self.env['multicompany.property.product']
            companies = self.env['res.company'].search([])
            for company in companies:
                val = property_obj.create({
                    'company_id': company.id,
                    'product_template_id': record.id
                })
                record.property_ids += val


class ProductProduct(models.Model):
    _inherit = 'product.product'

    property_ids = fields.One2many(
        comodel_name='multicompany.property.product',
        compute='_compute_properties',
        inverse='_inverse_properties',
        string='Properties'
    )

    @api.multi
    def _inverse_properties(self):
        ''' Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable, '''
        return

    @api.multi
    def _compute_properties(self):
        for record in self:
            property_obj = self.env['multicompany.property.product']
            companies = self.env['res.company'].search([])
            for company in companies:
                val = property_obj.create({
                    'company_id': company.id,
                    'product_id': record.id,
                    'product_template_id': record.product_tmpl_id.id,
                })
                record.property_ids += val


class MulticompanyPropertyProduct(models.TransientModel):
    _name = 'multicompany.property.product'
    _inherit = 'multicompany.property.abstract'

    _description = "Properties of Products"

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string="Product Template"
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product"
    )
    standard_price = fields.Float(
        'Cost',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for "
             "standard stock valuation in accounting "
             "and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.",
        compute='_compute_property_fields',
        readonly=False)

    @api.one
    def _compute_property_fields(self):

        object = self.product_id or self.product_template_id
        self.get_property_fields(object,
                                 self.env['ir.property'].with_context(
                                     force_company=self.company_id.id))

    @api.one
    def get_property_fields(self, object, properties):
        if object._name == 'product.template':
            if len(object.product_variant_ids) == 1:
                variant = object.product_variant_ids[0]
                self.standard_price = self.get_property_value(
                    'standard_price', variant, properties)
            else:
                self.standard_price = 0.0
        elif object._name == 'product.product':
            self.standard_price = self.get_property_value(
                'standard_price', object, properties)

    @api.multi
    def write(self, vals):
        prop_obj = self.env['ir.property'].with_context(
            force_company=self.company_id.id)
        if 'standard_price' in vals:
            for rec in self:
                obj = rec.product_id or rec.product_template_id
                if obj._name == 'product.template':
                    if len(obj.product_variant_ids) == 1:
                        for pv in obj.product_variant_ids:
                            self.set_property(pv, 'standard_price',
                                              vals['standard_price'], prop_obj)
                            pv._set_standard_price(
                                vals.get('standard_price', 0.0))
                elif obj._name == 'product.product':
                    self.set_property(obj, 'standard_price',
                                      vals['standard_price'], prop_obj)
                    obj._set_standard_price(vals.get('standard_price', 0.0))

        return super(MulticompanyPropertyProduct, self).write(vals)
