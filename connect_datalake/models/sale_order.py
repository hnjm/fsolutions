# -*- coding: utf-8 -*-

from datetime import datetime
import json
import logging

import requests
from urllib3.exceptions import InsecureRequestWarning
from contextlib import contextmanager
from functools import wraps
import itertools
import logging
import time
import uuid
import warnings

from decorator import decorator
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from odoo.tools import float_compare, float_round

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED, \
    ISOLATION_LEVEL_REPEATABLE_READ
from psycopg2.pool import PoolError
from werkzeug import urls

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

_logger = logging.getLogger(__name__)
from werkzeug import urls

import json
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression
from odoo import api, fields, models, _
from odoo import api, fields, models, _
import requests
from requests import Request
import logging
from pprint import pprint
from odoo.exceptions import ValidationError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from pprint import pformat
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import base64
import json
import re
import subprocess
import os
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError
import sqlite3
import os, fnmatch
import csv
import logging

from datetime import date, datetime, timedelta
from io import StringIO
from io import BytesIO
from pprint import pformat
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import re


class SaleOrder(models.Model):
    _inherit = "sale.order"

    data_id = fields.Char()
    payment_method = fields.Char()


    @api.model
    def _cron_fetch_datalake_order(self):
        companies=self.env['res.company'].search([('datalake_api','!=',False)])
        for company in companies:
            # base_api_endpoint = "http://172-105-48-123.ip.linodeusercontent.com:8000/datalake/getAssafOrders?start_date="+str(fields.Date.today())
            order_response=company.get_order_data_from_datalake()
            order_ids = [str(l['data_id']) for l in order_response]
            # pylint: disable=bad-continuation
            odoo_sale_entries = self.env['sale.order'].sudo().search_read([('data_id', '!=', False)
                                                                           ], ['data_id'])
            odoo_ids = [u['data_id'] for u in odoo_sale_entries]
            new_sale = set(order_ids) - set(odoo_ids)
            product_obj = self.env['product.product'].sudo()
            partner_obj = self.env['res.partner'].sudo()
            sale_obj = self.env['sale.order'].sudo()
            for order in order_response:
                if str(order['data_id']) in new_sale:
                    partner=partner_obj.search([('data_id','=',str(order['data_customer_id']))])
                    if not partner:
                        partner=partner_obj.create({'data_id':str(order['data_customer_id']),
                                                    'name':str(order['data_customer_first_name'])+" "+str(order['data_customer_last_name']),
                                                    'mobile':str(order['data_customer_mobile']),'city':str(order['data_customer_city'])})
                    vals=[]
                    for line in order['data_items']:
                        product_id = product_obj.search(
                            ['|',('name', '=', line['product.name']),('default_code', '=', line['product.sku'])], limit=1)
                        if product_id:
                            vals.append((0,0,{'product_id':product_id.id,
                                              'name':product_id.name,
                                              'product_uom':product_id.uom_id.id,
                                              'product_uom_qty': line['quantity'],
                                              'price_unit': line['amounts.price_without_tax.amount'],
                                              'discount': line['quantity'],
                                              'tax_id':[(4, product_id.taxes_id.id)] if product_id.taxes_id else False}))
                    if vals:
                        sale_order = sale_obj.create({'partner_id': partner.id,
                                                      'data_id':str(order['data_id']),
                                                      'warehouse_id':company.datalake_warehouse_id.id,
                                                      'picking_policy': 'direct',
                                                      'client_order_ref':str(order['data_reference_id']),
                                                      'date_order': order['data_date_date'][:19],
                                                      'pricelist_id': partner.property_product_pricelist.id,
                                                      'company_id':company.id,
                                                      'payment_method':order['data_payment_method'],
                                                      'order_line':vals,
                                                      })
                        sale_order.action_confirm()

