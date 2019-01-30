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


class work_package(models.Model):
    _name = 'work.package'
    _description = 'Work Packages'

    @api.one
    @api.depends('cost_header_ids.cost_of_header')
    def _compute_amount(self):
        for cost_header in self.cost_header_ids:
            self.work_package_cost += cost_header.cost_of_header

    name = fields.Char("Work Package Name", size=64, required=True, )
    work_package_cost = fields.Float(
        'Work Package Cost', compute='_compute_amount',
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
    cost_header_ids = fields.Many2many(
        'cost.header', 'work_package_cost_header_rel', 'work_package_id',
        'cost_header_id', 'Cost Header')
    product_uom = fields.Many2one('product.uom','Unit Of Measure')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
