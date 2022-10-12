# -*- coding: utf-8 -*-

from datetime import datetime
import json
import logging
import logging
import os
import requests
from urllib3.exceptions import InsecureRequestWarning

from werkzeug import urls

from odoo import api, fields, models, _
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

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    data_id = fields.Char()



    @api.model
    def _cron_fetch_datalake_partner(self):
        companies=self.env['res.company'].search([('datalake_api','!=',False)])
        for company in companies:
            # base_api_endpoint = "http://172-105-48-123.ip.linodeusercontent.com:8000/datalake/getAssafCustomers"
            partner_response=company.get_customer_data_from_datalake()
            partner_ids = [l['customer_id'] for l in partner_response]
            # pylint: disable=bad-continuation
            odoo_partner_entries = self.env['res.partner'].sudo().search_read([('data_id', '!=', False)
                                                                           ], ['data_id'])
            odoo_ids = [u['data_id'] for u in odoo_partner_entries]
            new_partner = set(partner_ids) - set(odoo_ids)
            partner_obj = self.env['res.partner'].sudo()
            for partner in partner_response:
                if str(partner['customer_id']) in new_partner:
                    partner_obj.create({'data_id': str(partner['customer_id']),
                                                  'name': str(partner['first_name']) + " " + str(
                                                      partner['last_name']),})