# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).
from odoo import models


class PerformanceObligationAcceptance(models.Model):
    _name = "performance_obligation_acceptance"
    _inherit = [
        "performance_obligation_acceptance",
        "mixin.work_object",
    ]

    _work_log_create_page = True
