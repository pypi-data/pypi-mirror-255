import factory
from deci_platform_client.models import APIResponseWorkspaceBase, WorkspaceBase


class WorkspaceBaseFactory(factory.Factory):
    class Meta:
        model = WorkspaceBase

    name = factory.Faker("name")
    id = factory.Faker("uuid4")


class APIResponseWorkspaceBaseFactory(factory.Factory):
    class Meta:
        model = APIResponseWorkspaceBase

    success = True
    data = factory.SubFactory(WorkspaceBaseFactory)
    message = ""
