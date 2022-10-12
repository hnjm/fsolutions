# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AssetDepreciationConfirmationWizard(models.TransientModel):
    _name = "asset.depreciation.confirmation.wizard"
    _description = "asset.depreciation.confirmation.wizard"


    def asset_compute(self):
        self.ensure_one()
        context = self._context
        assets = self.env['account.asset'].search([])
        for asset in assets:
            asset.compute_depreciation_board()

        return {'type': 'ir.actions.act_window_close'}
