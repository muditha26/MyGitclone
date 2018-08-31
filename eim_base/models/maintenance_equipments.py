from traceback import print_tb
from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _name = "maintenance.equipment"
    _inherit = "maintenance.equipment"

    name_att = fields.Many2many('eim.attribute', string='Eim')


class EIMAttribute(models.Model):
    _name = "eim.attribute"
    _description = "EIM Attribute"

    name = fields.Char('Name', index=True, required=True)
    eim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='PIM Attribute Type', default='text', required=True)
    eim_attribute_options_id = fields.One2many('eim.options', 'eim_attribute_id', string='EIM Attribute',
                                               ondelete='cascade')
    eim_eqiument_id = fields.Many2one('maintenance.equipment', 'EIM Category')
    eim_attribute_id = fields.Many2many('eim.options')

    @api.model
    def create(self, vals):
        try:
            if vals['eim_attribute_options_id']:
                if vals['eim_attribute_type'] == 'text' or vals['eim_attribute_type'] == 'number':
                    vals['eim_attribute_options_id'] = None
        except Exception as e:
            print(e)
            print_tb(e.__traceback__)
            pass
        return super(EIMAttribute, self).create(vals)

    @api.multi
    def copy(self, default=None):
        eimattribute = super(EIMAttribute, self).copy(default=default)
        eimattribute.name += ' (Copy)'
        for option in self.eim_attribute_options_id:
            eimattribute.eim_attribute_options_id += self.env['eim.options'].create({
                'name': option.name, 'eim_attribute_id': eimattribute.ids[0]})
        return eimattribute

    @api.multi
    def write(self, vals):
        try:
            if vals['eim_attribute_type'] == 'text' or vals['eim_attribute_type'] == 'number':
                for option in self.eim_attribute_options_id:
                    option.unlink()
        except Exception as e:
            print(e)
            print_tb(e.__traceback__)
            pass
        return super(EIMAttribute, self).write(vals)

    @api.multi
    def call_edit_view1(self):
        res = {
            'name': 'Attribute Value',
            'view_type': 'tree,form',
            'view_mode': 'form',
            'view_id': self.env.ref('maintance_extends').id,
            'res_model': 'eim.options',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'flags': {'action_buttons': True,
                      'tag': 'reload'}
        }
        return res

class PIMAttributeWithValue(models.Model):
    _name = "eim.attribute.with.value"
    _description = "EIM Attribute with value"

    name = fields.Char('Name', index=True, required=True)
    product_id = fields.Many2one('product.template', 'Product', ondelete='cascade')
    eim_attribute_id = fields.Many2one('eim.attribute', 'EIM Attribute')
    # eim_category_id = fields.Many2one('eim.category', 'EIM Category')
    eim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='EIM Attribute Type', required=True,
        related='eim_attribute_id.eim_attribute_type')
    show_value = fields.Char('Value', compute='_compute_show_value')
    value_select = fields.Many2one('eim.options', string='Value',
                                   domain="[('eim_attribute_id', '=', eim_attribute_id)]")
    value_text = fields.Char('Value')
    value_numeric = fields.Float('Value')
    value_radio = fields.Many2one('eim.options', string='value', domain="[('eim_attribute_id', '=', eim_attribute_id)]")
    value_checkbox = fields.Many2many('eim.options', string='Value')
    export_variant = fields.Boolean(default=False)
    exported = fields.Boolean(default=False)

    @api.depends('eim_attribute_type')
    def _compute_show_value(self):
        for record in self:
            if record.exported is False:
                show = getattr(record, SHOW_VALUE_CASES[record.eim_attribute_type])
                if record.eim_attribute_type in ['select', 'radio']:
                    record.show_value = show.display_name
                elif record.eim_attribute_type in ['checkbox']:
                    record.show_value = ""
                    for option in show:
                        record.show_value += ' | ' + option.display_name
                    if record.show_value != "": record.show_value += ' |'
                else:
                    record.show_value = show

    @api.multi
    def call_edit_view(self):
        res = {
            'name': 'Attribute Value',
            'view_type': 'tree,form',
            'view_mode': 'form',
            'view_id': self.env.ref('maintance_extends').id,
            'res_model': 'eim.attribute.with.value',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'flags': {'action_buttons': True,
                      'tag': 'reload'}
        }
        return res

    @api.multi
    def post_write(self, vals):
        self.write(vals)
        return {}



class Options(models.Model):
    _name = "eim.options"
    _description = "EIM Attribute Options"

    name = fields.Char('Value', index=True, required=True)
    eim_attribute_id = fields.Many2one('eim.attribute', ondelete='cascade')









