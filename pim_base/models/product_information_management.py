# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from traceback import print_tb

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    pim_category_id = fields.Many2one('pim.category', 'Pim Category', ondelete='restrict')

class PIMCategory(models.Model):
    _name = "pim.category"
    _description = "PIM Category"

    name = fields.Char('Name', index=True, required=True)
    pim_attributes_id = fields.Many2many('pim.attribute', string='PIM Attribute', ondelete='restrict')


class PIMAttribute(models.Model):
    _name = "pim.attribute"
    _description = "PIM Attribute"

    name = fields.Char('Name', index=True, required=True)
    pim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='PIM Attribute Type', default='text', required=True)
    pim_attribute_options_id = fields.One2many('pim.options', 'pim_attribute_id',string='PIM Attribute', ondelete='cascade')

    @api.model
    def create(self, vals):
        try:
            if vals['pim_attribute_options_id']:
                if vals['pim_attribute_type'] == 'text' or vals['pim_attribute_type'] == 'number':
                    vals['pim_attribute_options_id'] = None
        except Exception as e:
            print(e)
            print_tb(e.__traceback__)
            pass
        return super(PIMAttribute, self).create(vals)


    @api.multi
    def copy(self, default=None):
        pimattribute = super(PIMAttribute, self).copy(default=default)
        pimattribute.name += ' (Copy)'
        for option in self.pim_attribute_options_id:
            pimattribute.pim_attribute_options_id += self.env['pim.options'].create({
                'value': option.value, 'pim_attribute_id': pimattribute.ids[0]})
        return pimattribute


    @api.multi
    def write(self, vals):
        try:
            if vals['pim_attribute_type'] == 'text' or vals['pim_attribute_type'] == 'number':
                for option in self.pim_attribute_options_id:
                    option.unlink()
        except Exception as e:
            print(e)
            print_tb(e.__traceback__)
            pass
        return super(PIMAttribute, self).write(vals)


class Options(models.Model):
    _name = "pim.options"
    _description = "PIM Attribute Options"

    value = fields.Char('Value', index=True, required=True)
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute', ondelete='cascade')


class PIMAttributeValue(models.Model):
    _name = "pim.attributevalue"
    _description = "PIM Attribute Value for product_template"

    value = fields.Char('Value', index=True, required=True)
    active = fields.Boolean("Active", default=True)
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute', ondelete='restrict')
    product_template_id = fields.Many2one('product.template', 'Product Template', ondelete='cascade')
    options_id = fields.Many2many('pim.options', string='Value Options', ondelete='cascade')