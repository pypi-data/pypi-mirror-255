from uuid import uuid4

from .base_test_case import BaseTestCase


class TestSwitchToWorkspace(BaseTestCase):
    def test_switch_to_workspace_string(self) -> None:
        self.assertNotIn("x-deci-workspace", self.client.raw_api.api_client.default_headers)
        workspace_id = str(uuid4())
        self.assertIsNone(self.client.switch_to_workspace(workspace_id))
        self.assertEqual(
            self.client.raw_api.api_client.default_headers["x-deci-workspace"],
            workspace_id,
        )
