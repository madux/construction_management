#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Maduka Sopulu Chris kingston
#
# Created:     20/04/2018
# Copyright:   (c) kingston 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
{
    'name': 'Bill of Quantity & Program of Work',
    'version': '10.0.1.0.0',
    'author': 'Maduka Sopulu',
    'description':"""Bill of quantity and Program of work""",
    'category': 'Construction',

    'depends': ['product','construction_management','project'],
    'data': [
        'views/poq_views.xml',
        #'security/security_group.xml',
        #'security/ir.model.access.csv',
    ],
    'price': 14.99,
    'currency': 'USD',


    'installable': True,
    'auto_install': False,
}
