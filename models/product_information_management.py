# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from traceback import print_tb

from odoo import api, fields, models

SHOW_VALUE_CASES = {
    'text': 'value_text',
    'number': 'value_numeric',
    'radio': 'value_radio',
    'select': 'value_select',
    'checkbox': 'value_checkbox'
}


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = "product.template"

    pim_category_id = fields.Many2one('pim.category', 'Pim Category', ondelete='restrict')
    pim_attributes_with_value = fields.One2many('pim.attribute.with.value', 'product_id', string='PIM Attribute with value',
                                               ondelete='set null')

    @api.onchange('pim_category_id')
    def _change_category(self):
        attrs_values = []
        cat_id = self.env['pim.category'].search([['id', '=', self.pim_category_id.id]])
        if cat_id.pim_attributes_id:
            # if self.pim_attributes_with_value.product_id.pim_category_id == cat_id:
            #     for attribute in cat_id.pim_attributes_id:
            #         for attribute_value in self.pim_attributes_with_value:
            #             if attribute == attribute_value:
            #                 attrs_values.append(attribute_value.id)
            #             else:
            #                 vals = {
            #                     'name': attribute.name,
            #                     'pim_attribute_id': attribute.id,
            #                 }
            #                 attrs_values.append(self.env['pim.attribute.with.value'].create(vals).id)
            #     self.pim_attributes_with_value = attrs_values
            # else:
                for attribute in cat_id.pim_attributes_id:
                    vals = {
                        'name': attribute.name,
                        'pim_attribute_id': attribute.id,
                        }
                    attrs_values.append(self.env['pim.attribute.with.value'].create(vals).id)
                self.pim_attributes_with_value = attrs_values
        else:
            self.pim_attributes_with_value = []



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
                'name': option.name, 'pim_attribute_id': pimattribute.ids[0]})
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


class PIMAttributeWithValue(models.Model):
    _name = "pim.attribute.with.value"
    _description = "PIM Attribute with value"

    name = fields.Char('Name', index=True, required=True)
    product_id = fields.Many2one('product.template', 'Product', ondelete='cascade')
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute')
    pim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='PIM Attribute Type', required=True, related='pim_attribute_id.pim_attribute_type')
    show_value = fields.Char('Value', compute='_compute_show_value')
    value_select = fields.Many2one('pim.options', string='Value', domain="[('pim_attribute_id', '=', pim_attribute_id)]")
    value_text = fields.Char('Value')
    value_numeric = fields.Float('Value')
    value_radio = fields.Many2one('pim.options', string='value', domain="[('pim_attribute_id', '=', pim_attribute_id)]")
    value_checkbox = fields.Many2many('pim.options', string='Value')

    @api.depends('pim_attribute_type')
    def _compute_show_value(self):
        for record in self:
            show = getattr(record, SHOW_VALUE_CASES[record.pim_attribute_type])
            if record.pim_attribute_type in ['select', 'radio']:
                record.show_value = show.display_name
            elif record.pim_attribute_type in ['checkbox']:
                record.show_value = ""
                for option in show:
                    record.show_value += ' | '+option.display_name
                if record.show_value!="": record.show_value += ' |'
            else:
                record.show_value = show


class Options(models.Model):
    _name = "pim.options"
    _description = "PIM Attribute Options"

    name = fields.Char('Value', index=True, required=True)
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute', ondelete='cascade')


class PIMAttributeValue(models.Model):
    _name = "pim.attributevalue"
    _description = "PIM Attribute Value for product_template"

    value = fields.Char('Value', index=True, required=True)
    active = fields.Boolean("Active", default=True)
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute', ondelete='restrict')
    product_template_id = fields.Many2one('product.template', 'Product Template', ondelete='cascade')
    options_id = fields.Many2many('pim.options', string='Value Options', ondelete='cascade')