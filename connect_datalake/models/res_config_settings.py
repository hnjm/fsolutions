# -*- coding: utf-8 -*-
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


class ResCompany(models.Model):
    _inherit = 'res.company'


    datalake_api= fields.Boolean()
    datalake_url = fields.Char('URL')
    datalake_order_api = fields.Char('Order')
    datalake_customer_api = fields.Char('Customer')
    datalake_username = fields.Char('UserName')
    datalake_password = fields.Char('Password')
    datalake_token = fields.Text('Token')
    datalake_warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')

    def get_token(self):
        self.ensure_one()

        """
        Authenticate to Data Lake API and get token.
        """
        url = self.datalake_url
        # API uses JSON.
        headers = {'content-type': 'application/json','accept': 'application/json'}
        # Send HTTP POST with username and password.
        response = requests.request("POST",
                                    url,
                                    auth=HTTPBasicAuth(self.datalake_username, self.datalake_password),
                                    headers=headers)

        # Save the token in a variable.
        token = response.json()["Token"]
        self.datalake_token = token
        return token

    def get_order_data_from_datalake(self):
        self.ensure_one()
        """
        Communicate with Data Lake to retrieve order information.
        """
        # Include the token in the header.
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+str(self.datalake_token)}
        # Send HTTP GET to retrieve endpoint.
        url = self.datalake_order_api + str(
            fields.Date.today())
        response = requests.get(url, headers=headers, verify=False)
        response_as_dict = response.json()  # convert JSON to DICT.
        return response_as_dict['rows']

    def get_customer_data_from_datalake(self):
        self.ensure_one()
        """
        Communicate with Data Lake to retrieve order information.
        """
        # Include the token in the header.
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+str(self.datalake_token)}
        # Send HTTP GET to retrieve endpoint.
        url = self.datalake_customer_api
        response = requests.get(url, headers=headers, verify=False)
        response_as_dict = response.json()  # convert JSON to DICT.
        return response_as_dict['rows']



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    datalake_api = fields.Boolean(related='company_id.datalake_api', readonly=False)
    datalake_url = fields.Char(related='company_id.datalake_url', readonly=False)
    datalake_order_api = fields.Char(related='company_id.datalake_order_api', readonly=False)
    datalake_customer_api = fields.Char(related='company_id.datalake_customer_api', readonly=False)
    datalake_username = fields.Char(related='company_id.datalake_username', readonly=False)
    datalake_password = fields.Char(related='company_id.datalake_password', readonly=False)
    datalake_token = fields.Text(related='company_id.datalake_token', readonly=False)
    datalake_warehouse_id = fields.Many2one(related='company_id.datalake_warehouse_id', readonly=False)
