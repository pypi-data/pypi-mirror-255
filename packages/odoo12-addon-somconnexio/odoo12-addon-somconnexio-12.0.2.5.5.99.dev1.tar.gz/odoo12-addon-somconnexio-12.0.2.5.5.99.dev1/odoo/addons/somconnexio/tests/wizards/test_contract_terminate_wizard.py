from datetime import date
from ..sc_test_case import SCTestCase


class TestContractTerminateWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.terminate_reason = self.env['contract.terminate.reason'].create({
            'name': 'terminate_reason'
        })
        self.terminate_user_reason = self.env['contract.terminate.reason'].create({
            'name': 'terminate_user_reason'
        })

    def test_wizard_terminate_contract_user_reason(self):
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        terminate_date = date.today()
        wizard = (
            self.env["contract.terminate.wizard"]
            .with_context(active_id=contract.id)
            .create(
                {
                    "terminate_date": terminate_date,
                    "terminate_reason_id": self.terminate_reason.id,
                    "terminate_user_reason_id": self.terminate_user_reason.id,
                }
            )
        )

        wizard.terminate_contract()
        self.assertTrue(contract.is_terminated)
        self.assertEqual(contract.terminate_date, terminate_date)
        self.assertEqual(
            contract.terminate_user_reason_id.id, self.terminate_user_reason.id
        )
        contract.action_cancel_contract_termination()
        self.assertFalse(contract.is_terminated)
        self.assertFalse(contract.terminate_reason_id)
        self.assertFalse(contract.terminate_user_reason_id)
        self.assertFalse(wizard.is_fiber_contract_in_pack)

    def test_wizard_terminate_is_fiber_contract_in_pack(self):
        fiber_pack_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        wizard = (
            self.env["contract.terminate.wizard"]
            .with_context(active_id=fiber_pack_contract)
            .create({})
        )

        self.assertTrue(wizard.is_fiber_contract_in_pack)
