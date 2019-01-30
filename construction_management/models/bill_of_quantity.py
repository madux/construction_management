# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class Activity_Customx(models.Model):
    _name = 'activity.customx'
    name = fields.Char('Stage Name')
    activity_typex = fields.Selection([('main','Main Activity'),('sub','Sub Activity')],string='Select Stage Type')


class House_Type_Customx(models.Model):
    _name = 'house.type'
    name = fields.Char('House Type')


class House_Type_Line(models.Model):
    _name = 'house.type.line'

    @api.one
    @api.depends('boq_rate', 'quantity_x')
    def _compute_price(self):
        self.price_subtotalx = self.quantity_x * self.boq_rate

    @api.depends('house_type_x')
    def search_rate(self):
        bol = self.env['bill.quantity'].search([('house_type_x','=',self.house_type_x.id)])
        for rec in bol:
            self.boq_rate = bol.material_cost * self.quantity_x
    project_id = fields.Many2one(
        'project.project', 'Project', track_visibility='always')
    house_type_id = fields.Many2one('bill.quantity', 'boq ID')
    name = fields.Char('House Type Name', required=False, default='/')
    house_type_x = fields.Many2one('house.type', 'House Type')
    quantity_x = fields.Float('Quantity',default=0.0)
    boq_rate = fields.Float('Rate', compute='search_rate')
    price_subtotalx = fields.Float(
        "Total", compute='_compute_price',
        readonly=True, store=True,
        digits_compute=dp.get_precision('Account'), )
#




class Boq_Categx(models.Model):
    _name = 'boq.categx'
    name = fields.Char('BoQ Name')

class bill_quantity(models.Model):
    _name = 'bill.quantity'
    _inherit = ['mail.thread']
    _rec_name = 'project_id'

    @api.one
    @api.depends('quantity_line')
    def _compute_amount(self):
        material_price_subtotal = 0.0
        labor_price_subtotal = 0.0
        subcontract_price_subtotal = 0.0
        equipment_price_subtotal = 0.0
        work_package_price_subtotal = 0.0
        for record in self.quantity_line:
            if record.key == 'material':
                material_price_subtotal = record.price_subtotal + material_price_subtotal
                self.material_cost = material_price_subtotal
            if record.key == 'labor':
                labor_price_subtotal = record.price_subtotal + labor_price_subtotal
                self.labor_cost = labor_price_subtotal
            if record.key == 'subcontract':
                subcontract_price_subtotal = record.price_subtotal + subcontract_price_subtotal
                self.subcontract_cost = subcontract_price_subtotal
            if record.key == 'equipment':
                equipment_price_subtotal = record.price_subtotal + equipment_price_subtotal
                self.equipment_cost = equipment_price_subtotal
            if record.key == 'work_package':
                work_package_price_subtotal = record.price_subtotal + work_package_price_subtotal
                self.work_package_cost = work_package_price_subtotal
#        self.revision = 0
    ####################################
    boq_name_x = fields.Char('BOQ Name', required=True, default='/')
    activity_x = fields.Many2one('activity.customx', 'Main Activity')
    activity_typex = fields.Selection([('main','Main Activity'),('sub','Sub Activity')],string='Select Activity Type')
    boq_typex = fields.Selection([('cont','Conntract'),('com','Company')],string='BOQ Type')
    boq_categoryx = fields.Many2one('boq.categx', 'Category')
    house_type_x = fields.Many2one('house.type', 'House Type', required=True)
    house_type = fields.One2many('house.type.line', 'house_type_id',string='House Type Line')
    #activity_type = fields.Selection([('Main Activity')])

    #####################################

    project_id = fields.Many2one(
        'project.project', 'Project', track_visibility='always')
    subcontract_cost = fields.Float(
        'Subcontract Cost',compute='_compute_amount', track_visibility='always')
    equipment_cost = fields.Float(
        'Equipment Cost', compute='_compute_amount',
        readonly=True, store=False,
        digits=dp.get_precision('Account'), )
    estimated_cost = fields.Float('Estimated Cost', )
    revision = fields.Integer(
        'Revision', readonly=True,
        )
    material_cost = fields.Float(
        'Material Cost', compute='_compute_amount',
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
    labor_cost = fields.Float(
        'Labor Cost', compute='_compute_amount',
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
    work_package_cost = fields.Float(
        'Work Package Cost', compute='_compute_amount',
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
    markup_cost = fields.Float('Markup Cost (in %)', track_visibility='always')
    quantity_line = fields.One2many(
        'bill.quantity.line', 'bill_quantity_id',
        string='Bill Of Quantity Lines', readonly=False, copy=True)

    @api.multi
    def create_new_revision(self):
        bill_line = []
        for line in self.quantity_line:
            bill_line.append(
                (0, False, {'product_id': line.product_id.id,
                            'type': line.type,
                            'uom_id': line.uom_id.id,
                            'description': line.description,
                            'qty': line.qty,
                            'bill_quantity_id': self.id,
                            'key':line.key,
                            'employee_id':line.employee_id.id,
                            'product_id':line.product_id.id,
                            'partner_id':line.partner_id.id,
                            'work_package_id':line.work_package_id.id,
                            'price_unit': line.price_unit,
                            'price_subtotal': line.price_subtotal,
                           }))
        vals = {'project_id': self.project_id.id,
                     'quantity_line': bill_line
                    }
        res = self.create(vals)
        res.revision = self.revision + 1

class Project_Inherit(models.Model):
    _inherit = 'project.task.type'
    activity_x = fields.Many2one('activity.customx', 'Stage')



class bill_quantity_line(models.Model):
    _name = 'bill.quantity.line'
    _description = 'Bill Of Quantity Line'

    @api.one
    @api.depends('price_unit', 'qty', 'product_id')
    def _compute_price(self):
        self.price_subtotal = self.qty * self.price_unit

    @api.depends('project_stage')
    def change_activity(self):
        for rec in self:
            rec_act = rec.project_stage.activity_x
            rec.activity_typex = rec_act.activity_typex
#
    house_type_x = fields.Many2one('house.type', 'House Type')#, required=True)

    project_stage = fields.Many2one('project.task.type', 'Project stage', required=True)
    activity_x = fields.Many2one('activity.customx', 'Main Activity', related='project_stage.activity_x')
    activity_typex = fields.Selection([('main','Main Activity'),('sub','Sub Activity')],string='Select Activity Type', compute='change_activity')

    bill_quantity_id = fields.Many2one(
        'bill.quantity', string='Bill of Quantity Reference',
        ondelete='cascade', index=True)
    key = fields.Selection(
        [('equipment', 'Equipment'),
         ('labor', 'Labor'),
         ('material', 'Material'),
         ('subcontract', 'Subcontract'),
         ('work_package', 'Work Package'),
         ], 'Key', default='labor')
    product_id = fields.Many2one(
        'product.product', string='Product',
        ondelete='restrict', index=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee',)
    assest_id = fields.Many2one(
        'account.asset.asset',string='Assets',)
    partner_id = fields.Many2one(
        'res.partner',string='Partners',)
    work_package_id = fields.Many2one(
        'work.package',string='Work Package',)
    type = fields.Char('Type', size=64,)
    description = fields.Char(
        'Description', size=64, )
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure', )
    qty = fields.Float("Qty", default=1)
    price_unit = fields.Float(
        "Rate", digits_compute=dp.get_precision('Account'), )
    price_subtotal = fields.Float(
        "Total", compute='_compute_price',
        readonly=True, store=True,
        digits_compute=dp.get_precision('Account'), )
#

    @api.onchange('key')
    def onchange_key(self):
        self.price_unit = 0.0


    @api.onchange('work_package_id')
    def onchange_work_package_id(self):
        if self.work_package_id:
            self.price_unit = self.work_package_id.work_package_cost
            self.uom_id = self.work_package_id.product_uom.id

    @api.onchange('assest_id')
    def onchange_assest_id(self):
        if self.assest_id:
            self.price_unit = self.assest_id.value_residual

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
