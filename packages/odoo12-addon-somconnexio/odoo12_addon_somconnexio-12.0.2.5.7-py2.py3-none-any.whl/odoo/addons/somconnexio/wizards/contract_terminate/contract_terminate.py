from odoo import api, fields, models


class ContractContractTerminate(models.TransientModel):

    _inherit = 'contract.contract.terminate'

    terminate_user_reason_id = fields.Many2one(
        comodel_name="contract.terminate.user.reason",
        string="Termination User Reason",
        required=True,
        ondelete="cascade",
    )
    is_fiber_contract_in_pack = fields.Boolean(
        compute="_compute_is_fiber_contract_in_pack"
    )

    @api.multi
    def terminate_contract(self):
        for wizard in self:
            wizard.contract_id.terminate_contract(
                wizard.terminate_reason_id,
                wizard.terminate_comment,
                wizard.terminate_date,
                wizard.terminate_user_reason_id,
            )
        return True

    @api.depends("contract_id")
    def _compute_is_fiber_contract_in_pack(self):
        for wizard in self:
            wizard.is_fiber_contract_in_pack = bool(
                wizard.contract_id.is_fiber
                and wizard.contract_id.children_pack_contract_ids
            )
