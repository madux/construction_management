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

{
    "name": "Odoo Construction Management",
    "version": "1.0",
    "depends": ['base', 'project', 'stock',
                'account', 'hr', 'purchase', 'account_asset','sale','account_budget','project_issue','website_project_issue_sheet',
                ],
    "author": "Browseinfo",
    "summary": "Real Estate Management, Construction Project management, Building Construction",
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps.
    This module use for Real Estate Management, Construction management, Building Construction,
    """,
    "website": "www.browseinfo.in",
    "data": [
        "security/ir.model.access.csv",
        'view/project.xml',
        "view/main_menu.xml",
        'view/bill_of_quantity_view.xml',
        'view/cost_code_view.xml',
        'view/cost_header_view.xml',
        'view/work_package_view.xml',
        'view/work_package_view.xml',
        'view/construction_management.xml',
        'report/construction_report.xml',
        'report/project_project_report.xml',
        'report/project_note_report.xml',
        'report/project_job_orders.xml',
        
    ],
    "images": 'static/main_screenshot.png',
    "price": 55,
    "currency": 'EUR',
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
