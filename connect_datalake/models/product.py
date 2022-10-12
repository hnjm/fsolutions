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




class ProductTemplate(models.Model):
    _inherit = "product.template"

    data_id = fields.Char()

    def get_data_from_datalake(self,url,token):
        self.ensure_one()
        """
        Communicate with Data Lake to retrieve order information.
        """
        # Include the token in the header.
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+str(token)}
        # Send HTTP GET to retrieve endpoint.
        response = requests.get(url, headers=headers)
        response_as_dict = response.json()  # convert JSON to DICT.
        return response_as_dict


    @api.model
    def _cron_fetch_datalake_product(self):
        companies=self.env['res.company'].search([('datalake_api','!=',False)])
        for company in companies:
            base_api_endpoint = "http://172-105-48-123.ip.linodeusercontent.com:8000/datalake/getAssafProducts"
            product_response=company.get_data_from_datalake(base_api_endpoint,company.datalake_token)
            product_obj = self.env['product.product'].sudo
            for product in product_response:
                product_id = product_obj.search([('name', '=', product['name'])],limit=1)
                if product_id:
                    product_id.write({'data_id':product['data_id']})