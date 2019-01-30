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


class cost_header(models.Model):
    _name = 'cost.header'
    _description = 'Cost Header'

    @api.one
    @api.depends('cost_code_ids.price_unit', 'cost_code_ids.qty')
    def _compute_amount(self):
        cost = 0.0
        for cost_code_line in self.cost_code_ids:
            cost += cost_code_line.price_unit * cost_code_line.qty
        self.cost_of_header = cost

    number = fields.Integer("Cost Header Number", required=True, )
    name = fields.Char("Cost Header Name", required=True, size=64, )
    cost_of_header = fields.Float(
        'Cost Of Header', compute='_compute_amount',
        readonly=True, store=True,
        digits=dp.get_precision('Account'), )
    cost_code_ids = fields.One2many(
        'cost.code', 'cost_code_id', string="Cost Code")

