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


class cost_code(models.Model):
    _name = 'cost.code'
    _description = 'Cost Code'

    number = fields.Integer("Cost Header Number", required=True, )
    name = fields.Char("Cost Header Name", required=True, size=64, )
    description = fields.Char("Description", required=True, size=64, )
    price_unit = fields.Float(
        "Unit Price", digits_compute=dp.get_precision('Account'), )
    qty = fields.Float("Qty", default=1)
    cost_code_id = fields.Many2one(
        'cost.header', "Cost Code")

