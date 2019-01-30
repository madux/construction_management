from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import except_orm, ValidationError

from datetime import datetime, timedelta
import time


from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class Pow_Work(models.Model):
    _name = 'pow.base.with.boq'
    _inherit = ['mail.thread']
    name = fields.Char('Name')
    boq_id = fields.Many2one('bill.quantity', string='BOQ')
    poq_task = fields.One2many('pow.base.with.boq.task', 'pow_task', string='Task Lines',store=True, readonly=False,compute='get_tasks')

    @api.depends('boq_id')
    def get_tasks(self):
        for rec in self:
            sale_comm = []
            for level in rec.boq_id.stage:
                sale_comm.append((0,0,{'stage_id':level.stage_id.id,'stage':level.activity_cus.id,'number_work':0}))
            rec.poq_task = sale_comm



    '''@api.onchange('boq_id')
    def appends_event(self):
        result=[]
        read = self.env['pow.base.with.boq.task'].search([('boq_id','=',self.boq_id.id)])
        for x in read:
            result.append(x.id)
        for record in self:
            record.poq_task=result'''





class Pow_Work_Task(models.Model):

    _name = 'pow.base.with.boq.task'

    sequence = fields.Integer('Sequence')
    pow_task = fields.Many2one('pow.base.with.boq')
    task = fields.Char('Task')
    total_days = fields.Integer('Total Duration(Days)', readonly=False, compute='cal_total')
    number_work = fields.Integer('Number of work', readonly=False, compute='len_event')
    boq_id = fields.Many2one('bill.quantity', string='BOQ')
    pow_lined = fields.One2many('pow.base.with.boq.line','pow_line', string='PoW Line')
    stage_id = fields.Many2one('project.task.type', string = 'Activity',required=True)
    stage = fields.Many2one('activity.customx', 'Stage')
    duration = fields.Integer('Duration(Days)')
    predecessor = fields.Integer('Predecessor')
    single_item = fields.Boolean('Is Single Task')


    @api.depends('pow_lined.duration')
    def cal_total(self):
        for rec in self:
            for rex in rec.pow_lined:
                rec.total_days += rex.duration
    @api.depends('pow_lined.work')
    def len_event(self):
        for rec in self:
            count = len(rec.pow_lined)
            rec.number_work = count

class Pow_Work_Task_Line(models.Model):
    _name = 'pow.base.with.boq.line'
    pow_line = fields.Many2one('pow.base.with.boq.task', string='Pow Line')
    work = fields.Many2one('project.task','Task')
    duration = fields.Integer('Duration(Days)')
    predecessor = fields.Integer('Predecessor')

################## BOQ ########################
class Project_Inherit(models.Model):
    _inherit = 'project.task.type'
    '''total = fields.Float('Total')
    bill_of_quantity_id = fields.Many2one('bill.quantity', 'Bill of Quantity')
    activity = fields.Many2one('bill.of.quantity.stage', 'Task Activity')'''


class Project_Inherit(models.Model):
    _inherit = 'project.task'
    stage = fields.Many2one('activity.customx', 'Stage')

    activity = fields.Many2one('project.task.type', 'Activity')

    @api.onchange('stage')
    def domain_g(self):
        act = []
        domain = {}
        get_act = self.env['project.task.type'].search([('activity_x','=',self.stage.id)])
        for rec in get_act:
            act.append(rec.id)
            domain = {'activity':[('id','=',act)]}
        return {'domain':domain}


class BOQ_Inherit(models.Model):
    _inherit = ['bill.quantity']
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append(
                (record.id,
                 record.boq_name_x +
                 '-'))
        return res
    project_task_stages_ids = fields.Many2many('project.task.type',string='Task Stage')
    #stage_totals = fields.One2many('stage.total', 'stage_bill_idx',string='Stage Total')
    #stage = fields.One2many('bill.of.quantity.stage', 'stage_bill_id',string='Stage Total')
    stage_totals = fields.One2many('stage.total', 'stage_bill_id', string='Stage Total')#, states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    amount_total = fields.Float('Amount Total', compute='compute_overall_total')
    stage = fields.One2many('bill.of.quantity.stage', 'stage_bill_id', store=True,string='Activity',compute='change_all')#, states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    @api.onchange('project_task_stages_ids')
    def changes_stage_total(self):
        get_stage = self.env['stage.total'].search([('stage_id','=', self.project_task_stages_ids.id)])
        result = []
        for rec in get_stage:
            result.append(rec.id)
        for rex in self:
            rex.stage_totals = result


    @api.depends('stage_totals')
    def change_all(self):
        get_qstages = []
        for rec in self:
            for ret in rec.stage_totals:
                get_stage = self.env['bill.of.quantity.stage'].search([('activity_cus','=',ret.stage_id.id)])
                for i in get_stage:
                    get_qstages.append(i.id)
                    rec.stage = [(6,0, get_qstages)]


    @api.depends('stage.total_dummy')
    def compute_overall_total(self):
        total = 0.0
        for rec in self:
            for ret in rec.stage:
                total += ret.total_dummy
            rec.amount_total = total + rec.amount_total


class Stage_Total(models.Model):
    _name = 'stage.total'
    stage_bill_id = fields.Many2one('bill.quantity', string='Bill of Quantity', index=True, ondelete='cascade')

    #stage_bill_id = fields.Many2one('bill.quantity', 'Bill of Quantity')
    stage_id =fields.Many2one('activity.customx', 'Stage', required=True)
    total = fields.Float('Total', compute='get_stage_id')


    @api.depends('stage_id')
    def get_stage_id(self):
        get_ids = []

        for ret in self:
            totals = 0.0
            stage_get = self.env['bill.of.quantity.stage'].search([('activity_cus','=',ret.stage_id.id)])
            for rec in stage_get:
                #totals = rec.material_total + rec.labour_total
                #g = get_ids.append(rec.id)
                totals += rec.total_dummy
                ret.total = totals



class Bill_of_Stage(models.Model):
    _name = 'bill.of.quantity.stage'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bill.of.quantity.stage')# or '/'
        return super(Bill_of_Stage, self).create(vals)

    name = fields.Char('Sequence', default='New')
    stage_bill_id = fields.Many2one('bill.quantity', string='Boq', index=True, ondelete='cascade')

    material_total = fields.Float('Material Total', compute='material_cost')
    labour_total = fields.Float('Labour Total',compute='labour_cost')
    #material_total_before_variance = fields.Float('Material Total Before variance')
    #labour_total_before_variance = fields.Float('Labour Total before variance')

    stage_id = fields.Many2one('project.task.type', string = 'Activity',required=True)
    activity_cus = fields.Many2one('activity.customx', string = 'Stage',required=True)

    stage_datas_material = fields.One2many('bill.of.quantity.stage.data','stage_id',string='Stage Material Line')
    stage_datas_labour = fields.One2many('bill.of.quantity.stage.data.labor','stage_id',string='Stage Labour Line')

    total_dummy = fields.Float('Total overal', store=True, compute='total_mat_lab')





    def get_activity_id(self):
        return self.stage_id.activity_x.id

    @api.depends('material_total','labour_total')
    def total_mat_lab(self):
        for rec in self:
            rec.total_dummy = rec.material_total + rec.labour_total

    #@api.one
    @api.depends('stage_datas_material')
    def material_cost(self):
        total_all = 0.0

        for rex in self:
            for rec in rex.stage_datas_material:
                total_all += rec.total
            rex.material_total =total_all

    #@api.one
    @api.depends('stage_datas_labour')
    def labour_cost(self):
        total_all = 0.0
        for rex in self:
            for rec in rex.stage_datas_labour:
                total_all += rec.amount_total
                rex.labour_total =total_all



class Bill_stage_Data(models.Model):
    _name = 'bill.of.quantity.stage.data'

    stage_id = fields.Many2one('bill.of.quantity.stage')
    product_id = fields.Many2one('product.product', string = 'Product')
    ###stage_mat_id = fields.Many2one('activity.task.line', string='Material Id')
    #variance_qty = fields.Float('Variance quantity',default=1.0)
    qty = fields.Float('Quantity',default=1.0)
    #total_qty = fields.Float('Total Quantity',compute='total_quantity')
    #used_qty = fields.Float('Used Quantity',default=1.0)
    #remain_qty = fields.Float('Remaining Quantity',compute='_remaining_qty')
    label = fields.Many2one('product.uom','Label')
    rate = fields.Float('Rate',related='product_id.list_price')
    #total_before_variance = fields.Float('Total before Variance',compute='get_total')
    total = fields.Float('Total',compute='get_total')


    '''@api.depends('variance_qty','qty')
    def total_quantity(self):
        for rec in self:
            totals = rec.variance_qty + rec.qty
            rec.total_qty = totals

    @api.depends('total_qty','qty')
    def _remaining_qty(self):
        for rec in self:
            totals = (rec.variance_qty + rec.qty)- rec.used_qty
            rec.remain_qty = totals'''


    @api.depends('qty','rate')
    def get_total(self):
        for rec in self:
            totals = rec.qty * rec.rate

            rec.total = totals


class Bill_stage_Labour(models.Model):
    _name = 'bill.of.quantity.stage.data.labor'

    stage_id = fields.Many2one('bill.of.quantity.stage')
    activity_id = fields.Many2one('project.task.type', string = 'Activity')
    qty = fields.Float('Quantity',default=0.0)
    label = fields.Many2one('product.uom','Label')
    rate = fields.Float('Rate',default=0.00)
    ###stage_lab_id = fields.Many2one('activity.task.line', string='Labour Id')

    #variance_amount = fields.Float('Variance amount',default=0.0)
    #total_amount_before_variance = fields.Float('Total before before Variance', compute='get_total')

    amount_total = fields.Float('Amount',compute='get_total')
    state = fields.Selection([('paid','Paid'),('not_paid','Not Paid')],string='Payment Status')


    @api.depends('qty','rate')
    def get_total(self):
        for rec in self:
            totals = rec.qty * rec.rate
            #rec.total_amount_before_variance = totals
            rec.amount_total = totals







