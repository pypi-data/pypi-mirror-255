from random import randint
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.client.api_client import ApiClient

from tests.helpers import get_api_response_instance
from tests.mocks import APIResponseWorkspaceBaseFactory

from .base_test_case import BaseTestCase

if TYPE_CHECKING:
    import unittest


def get_create_workspace_mock() -> "unittest.mock._patch[MagicMock]":
    return patch.object(
        PlatformApi,
        "create_workspace",
        return_value=get_api_response_instance(APIResponseWorkspaceBaseFactory.create()),
    )


get_invite_colleague_mock = patch.object(PlatformApi, "invite_colleague_to_join_workspace")
get_frontegg_auth_mock = patch.object(ApiClient, "refresh_frontegg_auth")


class TestCreateWorkspace(BaseTestCase):
    @get_frontegg_auth_mock
    @get_invite_colleague_mock
    @get_create_workspace_mock()
    def test_create_workspace_no_emails(
        self,
        create_workspace_mock: MagicMock,
        invite_colleague_mock: MagicMock,
        frontegg_auth_mock: MagicMock,
    ) -> None:
        name = str(uuid4())
        response = self.client.create_workspace(name)
        self.assertEqual(str(response), create_workspace_mock.return_value.body["data"]["id"])
        create_workspace_mock.assert_called_once_with(body={"name": name})
        invite_colleague_mock.assert_not_called()
        frontegg_auth_mock.assert_called_once_with()

    @get_frontegg_auth_mock
    @get_invite_colleague_mock
    @get_create_workspace_mock()
    def test_create_workspace_with_emails(
        self,
        create_workspace_mock: MagicMock,
        invite_colleague_mock: MagicMock,
        frontegg_auth_mock: MagicMock,
    ) -> None:
        name = str(uuid4())
        emails = [str(uuid4()) for _ in range(randint(1, 5))]
        response = self.client.create_workspace(name, emails)
        self.assertEqual(str(response), create_workspace_mock.return_value.body["data"]["id"])
        create_workspace_mock.assert_called_once_with(body={"name": name})
        forms = [mock_call[2]["body"] for mock_call in invite_colleague_mock.mock_calls]
        self.assertCountEqual([str(response)] * len(emails), map(lambda form: form["workspaceId"], forms))
        self.assertCountEqual(emails, map(lambda form: form["invitedEmail"], forms))
        frontegg_auth_mock.assert_called_once_with()
