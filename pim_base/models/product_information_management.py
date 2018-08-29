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

    pim_category_id = fields.Many2many('pim.category', string='Pim Category', ondelete='restrict')
    pim_attributes_with_value = fields.One2many('pim.attribute.with.value', 'product_id',
                                                string='PIM Attribute with value',
                                                ondelete='set null', domain=[('exported', '!=', True)])

    @api.onchange('pim_category_id')
    def _change_category(self):
        attrs_values = []
        for category in self.pim_category_id:
            cat_id = self.env['pim.category'].search([['id', '=', category.id]])
            pim_attributes_with_value = self.pim_attributes_with_value
            if cat_id.pim_attributes_id:
                for attribute in cat_id.pim_attributes_id:
                    existing_attribute = False
                    for attribute_value in pim_attributes_with_value:
                        if cat_id.id != attribute_value.pim_category_id.id:
                            break
                        if attribute_value.pim_attribute_id.id == attribute.id:
                            vals = {
                                'name': attribute.name,
                                'pim_attribute_id': attribute.id,
                                'pim_category_id': cat_id.id,
                                'export_variant': attribute_value.export_variant,
                                'exported': attribute_value.exported,
                            }
                            if attribute_value.pim_attribute_id.pim_attribute_type == 'text':
                                vals.update({'value_text': attribute_value.value_text})
                            elif attribute_value.pim_attribute_id.pim_attribute_type == 'number':
                                vals.update({
                                    'value_numeric': attribute_value.value_numeric,
                                })
                            elif attribute_value.pim_attribute_id.pim_attribute_type == 'radio':
                                vals.update({

                                    'value_radio': attribute_value.value_radio.id,
                                })
                            elif attribute_value.pim_attribute_id.pim_attribute_type == 'select':
                                vals.update({
                                    'value_select': attribute_value.value_select.id,
                                })
                            elif attribute_value.pim_attribute_id.pim_attribute_type == 'checkbox':
                                value_checked = []
                                for checked in attribute_value.value_checkbox:
                                    value_checked.append((4, checked.id))
                                vals.update({'value_checkbox': value_checked})
                            attrs_values.append(self.env['pim.attribute.with.value'].create(vals).id)
                            existing_attribute = True
                            break
                    if not existing_attribute:
                        vals = {
                            'name': attribute.name,
                            'pim_attribute_id': attribute.id,
                            'pim_category_id': cat_id.id,
                        }
                        attrs_values.append(self.env['pim.attribute.with.value'].create(vals).id)
                attrs_values += attrs_values
            else:
                attrs_values += []
        self.pim_attributes_with_value = attrs_values


    @api.multi
    def export_pim_attribute(self):
        for attribute_value in self.pim_attributes_with_value:
            if attribute_value.export_variant == True and attribute_value.exported != True:
                # Se busca el atributo
                new_attribute = False
                attribute = self.env['product.attribute'].search([('name','=', attribute_value.pim_attribute_id.name)])
                if not attribute:
                    # Se crea el atributo
                    attribute = self.create_attribute({'name': attribute_value.pim_attribute_id.name})
                    new_attribute = True
                else:
                    attribute = attribute[0]
                #si es un atributo nuevo
                if new_attribute:
                    if attribute_value.pim_attribute_id.pim_attribute_type == 'text':
                        self.env['product.attribute.line'].create(
                            {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id,
                             'product_tml_id': attribute_value.product_id.id,
                             'value_ids': [(0, 0, {'name': attribute_value.value_text, 'attribute_id': attribute.id,
                                                   'product_ids': [
                                                       (0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})]})
                    elif attribute_value.pim_attribute_id.pim_attribute_type == 'number':
                        self.env['product.attribute.line'].create(
                            {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id,
                             'product_tml_id': attribute_value.product_id.id,
                             'value_ids': [(0, 0, {'name': str(attribute_value.value_numeric), 'attribute_id': attribute.id,
                                                   'product_ids': [
                                                       (0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})]})
                    else:
                        value_ids = []
                        for option in attribute_value.pim_attribute_id.pim_attribute_options_id:
                            value_ids.append((0, 0, {'name': str(option.name), 'attribute_id': attribute.id,
                                                     'product_ids': [
                                                         (0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]}))
                        # Se crea el objeto attribute_line y a traves de la misma los attribute_value por cada opcion tambien se crean todas las relaciones many2many con la estrucura de odoo [(0,0 lis_atriburtos_clase)]
                        self.env['product.attribute.line'].create(
                            {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id,
                             'product_tml_id': attribute_value.product_id.id,
                             'value_ids': value_ids})
                    attribute_value.write({'exported': True})
                # si no es un atributo nuevo
                else:
                    # controlamos si ya existe la linea
                    exists_linea = False
                    for attribute_line in attribute.attribute_line_ids:
                        if attribute_line.product_tmpl_id.id == attribute_value.product_id.id:
                            exists_linea = True
                            break
                    if attribute_value.pim_attribute_id.pim_attribute_type == 'text' :
                        # controlar si ya existe el valor dentro del attributo
                        exists_attribute_value = False
                        for value in attribute.value_ids:
                            if value.name == attribute_value.value_text:
                                exists_attribute_value = True
                                break
                        #si existe la linea de attributo solo hay que modificar los valores para la linea de attributos
                        if exists_linea:
                            # si el valor del atributo ya existe, hay que referenciar la linea de atributo al mismo
                            if exists_attribute_value:
                                attribute_line.value_ids += value
                            # si no existe hay que crear el valor
                            else:
                                attribute_line.value_ids += self.env['product.attribute.value'].create(
                                    {'name': attribute_value.value_text, 'attribute_id': attribute.id,
                                     'product_ids': [(0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})
                        # si no exite la line a attributo hay que crear y agregar a las lineas del attribute
                        else:
                            # si el valor del atributo ya existe, hay que referenciar la linea de atributo al mismo
                            if exists_attribute_value:
                                # se crea la linea de atributo
                                attribute_line = self.env['product.attribute.line'].create({'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id})
                                # crear las variantes de producto
                                value.product_ids += self.env['product.product'].create({'product_tmpl_id': attribute_value.product_id.id, })
                                #instanciamoes el valor a la linea de atributo
                                attribute_line.value_ids += value
                            # si no existe hay que crear el valor
                            else:
                                attribute.attribute_line_ids += self.env['product.attribute.line'].create(
                                    {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id,
                                     'value_ids': [(0, 0, {'name': attribute_value.value_text, 'attribute_id': attribute.id,
                                                   'product_ids': [
                                                       (0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})]})
                    elif attribute_value.pim_attribute_id.pim_attribute_type == 'number':
                        # controlar si ya existe el valor dentro del attributo
                        exists_attribute_value = False
                        for value in attribute.value_ids:
                            if value.name == str(attribute_value.value_numeric):
                                exists_attribute_value = True
                                break
                        #si existe la linea de attributo solo hay que modificar los valores para la linea de attributos
                        if exists_linea:
                            # si el valor del atributo ya existe, hay que referenciar la linea de atributo al mismo
                            if exists_attribute_value:
                                attribute_line.value_ids += value
                            # si no existe hay que crear el valor
                            else:
                                attribute_line.value_ids += self.env['product.attribute.value'].create(
                                    {'name': str(attribute_value.value_numeric), 'attribute_id': attribute.id,
                                     'product_ids': [(0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})
                        # si no exite la line a attributo hay que crear y agregar a las lineas del attribute
                        else:
                            # si el valor del atributo ya existe, hay que referenciar la linea de atributo al mismo
                            if exists_attribute_value:
                                # se crea la linea de atributo
                                attribute_line = self.env['product.attribute.line'].create({'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id})
                                # crear las variantes de producto
                                value.product_ids += self.env['product.product'].create({'product_tmpl_id': attribute_value.product_id.id, })
                                #instanciamoes el valor a la linea de atributo
                                attribute_line.value_ids += value
                            # si no existe hay que crear el valor
                            else:
                                attribute.attribute_line_ids += self.env['product.attribute.line'].create(
                                    {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id,
                                     'value_ids': [(0, 0, {'name': str(attribute_value.value_numeric), 'attribute_id': attribute.id,
                                                   'product_ids': [
                                                       (0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})]})
                    else:
                        #controlar que valores ya existen en el atributo y cuales no
                        exists_values = []
                        new_values = []
                        for option in attribute_value.pim_attribute_id.pim_attribute_options_id:
                            aux_exists = False
                            for value in attribute.value_ids:
                                if value.name == option.name:
                                    exists_values.append(value)
                                    aux_exists = True
                                    break
                            if not aux_exists:
                                new_values.append(option.name)
                        # si existe la linea de attributo solo hay que modificar los valores para la linea de attributos
                        if exists_linea:
                            #por cada valor existente solo hay que agregarlo al attributo
                            for value in exists_values:
                                attribute_line.value_ids += value
                            #por cada valor nuevo hay que crear un valor de atributo y agregarlo al atributo
                            for value in new_values:
                                attribute_line.value_ids += self.env['product.attribute.value'].create(
                                    {'name': str(value), 'attribute_id': attribute.id,
                                     'product_ids': [(0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})

                        # si no exite la line a attributo hay que crear y agregar a las lineas del attribute
                        else:
                            # se crea la linea de atributo
                            attribute_line = self.env['product.attribute.line'].create(
                                {'product_tmpl_id': attribute_value.product_id.id, 'attribute_id': attribute.id})
                            # por cada valor existente solo hay que agregarlo al attributo
                            for value in exists_values:
                                # crear las variantes de producto
                                value.product_ids += self.env['product.product'].create(
                                    {'product_tmpl_id': attribute_value.product_id.id, })
                                attribute_line.value_ids += value
                            # por cada valor nuevo hay que crear un valor de atributo y agregarlo al atributo
                            for value in new_values:
                                attribute_line.value_ids += self.env['product.attribute.value'].create(
                                    {'name': str(value), 'attribute_id': attribute.id,
                                     'product_ids': [(0, 0, {'product_tmpl_id': attribute_value.product_id.id, })]})
                    attribute_value.write({'exported': True})

    def create_attribute(self, vals):
        return self.env['product.attribute'].create(vals)


class PIMCategory(models.Model):
    _name = "pim.category"
    _description = "PIM Category"

    name = fields.Char('Name', index=True, required=True)
    pim_attributes_id = fields.Many2many('pim.attribute', string='PIM Attribute', ondelete='restrict')
    pim_attributes_with_value = fields.One2many('pim.attribute.with.value', 'pim_category_id',
                                                string='PIM Attribute with value')


class PIMAttribute(models.Model):
    _name = "pim.attribute"
    _description = "PIM Attribute"

    name = fields.Char('Name', index=True, required=True)
    pim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='PIM Attribute Type', default='text', required=True)
    pim_attribute_options_id = fields.One2many('pim.options', 'pim_attribute_id', string='PIM Attribute',
                                               ondelete='cascade')

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
    pim_category_id = fields.Many2one('pim.category', 'PIM Category')
    pim_attribute_type = fields.Selection(
        [('text', 'Text'), ('number', 'Number'), ('radio', 'Radio'), ('select', 'Select'),
         ('checkbox', 'Checkbox')], string='PIM Attribute Type', required=True,
        related='pim_attribute_id.pim_attribute_type')
    show_value = fields.Char('Value', compute='_compute_show_value')
    value_select = fields.Many2one('pim.options', string='Value',
                                   domain="[('pim_attribute_id', '=', pim_attribute_id)]")
    value_text = fields.Char('Value')
    value_numeric = fields.Float('Value')
    value_radio = fields.Many2one('pim.options', string='value', domain="[('pim_attribute_id', '=', pim_attribute_id)]")
    value_checkbox = fields.Many2many('pim.options', string='Value')
    export_variant = fields.Boolean(default=False)
    exported = fields.Boolean(default=False)

    @api.depends('pim_attribute_type')
    def _compute_show_value(self):
        for record in self:
            if record.exported is False:
                show = getattr(record, SHOW_VALUE_CASES[record.pim_attribute_type])
                if record.pim_attribute_type in ['select', 'radio']:
                    record.show_value = show.display_name
                elif record.pim_attribute_type in ['checkbox']:
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
            'view_id': self.env.ref('pim_base.pim_attributewith_value_form').id,
            'res_model': 'pim.attribute.with.value',
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
    _name = "pim.options"
    _description = "PIM Attribute Options"

    name = fields.Char('Value', index=True, required=True)
    pim_attribute_id = fields.Many2one('pim.attribute', 'PIM Attribute', ondelete='cascade')
