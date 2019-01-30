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
from datetime import datetime, timedelta

class project_note_note(models.Model):
    _name = 'project.note.note'
    _inherit = ['mail.thread']
    
    tag_id = fields.Many2one('project.tags', 'Tags')
    construction_proj_id = fields.Many2one('project.project','Construction Project',required='True')
    responsible_user = fields.Many2one('res.users','Responsible Person')
    description = fields.Html('Description')
    
class product_product(models.Model):
    _inherit = 'product.product'
    
    boq_type = fields.Selection([('machine_qui','Machinery / Equipment'),('worker','Worker / Resource'),('work_package','Work Cost Package'),('subcontract','Subcontract')],'BOQ Type')
    project_task_id = fields.Many2one('project.task',string='Project Task')
    
class project_issue(models.Model):
    _inherit = 'project.issue'
    
    progress = fields.Float(store=True, string='Progress Bar', group_operator="avg")

class project_task(models.Model):
    _inherit = 'project.task'
    
    prod_material_ids = fields.One2many('product.product','project_task_id')
    material_req_stock_ids = fields.One2many('stock.picking','project_task_stock_id')
    stock_move_ids = fields.One2many('stock.move','project_stock_move_id')

class stock_move(models.Model):
    _inherit = 'stock.move'
    
    project_stock_move_id = fields.Many2one('project.task',string='Stock Move')

class product_template(models.Model):
    _inherit = 'product.template'
    
    pur_order_wiz_id = fields.Many2one('purchase.order.wizard',string='Ordersss')    

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    res_partner_id = fields.Many2one('purchase.order.wizard',string='partner')    
    
class product_quantity(models.Model):
    _name = 'product.quantity'
    
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_id = fields.Many2one('product.product',string="Products")
    product_on_hand = fields.Integer(string="On Hand Qty")
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    tmpl_id = fields.Many2one('purchase.order.wizard',string='Product') 
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        print "=====product_id=====self============",self
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        print "======domain=========",domain
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=datetime.now(),
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        return {'domain': domain}
        
'''class product_template(models.Model):
    _inherit = 'product.product'
    
    quantity = fields.Integer(string="Quantity")
    tmpl_id = fields.Many2one('purchase.order.wizard',string='Product') '''
            
class purchase_order_wizard(models.Model):
    _name= 'purchase.order.wizard'

    #partner_ids = fields.One2many('res.partner','res_partner_id',string="Purchase Order")
    partner_ids = fields.Many2many('res.partner','wizard_partner_rel','purchase_partner_id','purchase_line_id',string='Partner')
    product_ids = fields.One2many('product.quantity','tmpl_id', string='Products')
    
    
    @api.multi
    def create_purchase_order(self):
        print "===========partner_ids================",self.partner_ids
        print "===========product_ids=======product_ids=========",self.product_ids
        stock_picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
        vals ={}
        list_of_order = []
        for par_id in self.partner_ids:
            vals['partner_id'] = par_id.id
            vals['date_order'] = datetime.now()
            #vals['origin'] = stock_picking_id.origin
            purchase_order = self.env['purchase.order'].create(vals)
            vals = {}
            list_of_order.append(purchase_order)
            print "=======list_of_order============",list_of_order
            
        for prod_line in list_of_order:
            print "=======prod_line===========",prod_line
            for products in self.product_ids:
                print "=========products==========",products.product_id
                vals['product_id'] = products.product_id.id
                vals['product_qty'] = products.product_uom_qty
                vals['name'] = products.product_id.name
                vals['price_unit'] = products.product_id.list_price
                vals['date_planned'] = datetime.now()
                vals['order_id'] = prod_line.id
                vals['product_uom'] = products.product_uom.id
                purchase_order_line = self.env['purchase.order.line'].create(vals)
                print "========purchase_order_line=============",vals
            vals = {}
        return True
            
class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    job_orders_id = fields.Many2one('project.task','Task / Job Orders')
    job_orders_user_id = fields.Many2one('res.users','Task / Job Orders User')
    construnction_pro_id = fields.Many2one('project.project','Construction Project')
    analylic_acc_id = fields.Many2one('account.analytic.account','Analylic Account')
    bill_of_qty_id = fields.Many2one('bill.quantity','Bill Of Quantity')
    cost_equipment = fields.Float(related='bill_of_qty_id.equipment_cost',string="Equipment Cost",store=True)
    worker_cost = fields.Float(related='bill_of_qty_id.labor_cost',string="Worker / Resource Cost",store=True)
    work_cost_package = fields.Float(related='bill_of_qty_id.work_package_cost',string="Work Cost Package",store=True)
    sub_contract_cost = fields.Float(related='bill_of_qty_id.subcontract_cost',string="SubContract Cost",store=True)
    project_task_stock_id = fields.Many2one('project.task',string='Project Task')
    
    @api.onchange('job_orders_id')
    def _onchange_job_orders_id(self):
        self.job_orders_user_id = self.job_orders_id.user_id
        self.construnction_pro_id = self.job_orders_id.project_id
        
    '''@api.model
    def create(self,vals):
        print "===================vals===",vals
        
        if self.construnction_pro_id:
            val = {}
           
        return super(stock_picking, self).create(vals)'''
    
