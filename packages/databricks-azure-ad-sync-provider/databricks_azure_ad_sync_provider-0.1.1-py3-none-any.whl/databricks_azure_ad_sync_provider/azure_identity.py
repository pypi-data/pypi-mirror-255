"""
This module is for Microsoft Entra ID (formely Azure Active Directory) objects
Author: xuyao@dataroots.io
"""
from msgraph import GraphServiceClient


class AzureIdentity:
    def __init__(self, azure_credential):
        """Authenticate AD service principle

        Args: client_id, client_secret, tenant_id
        """
        self.credential = azure_credential
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.client = GraphServiceClient(
            credentials=self.credential, scopes=self.scopes
        )

    async def get_group_direct_members(
        self, group_object_id: str, exclude_objects: list[str]
    ) -> (list[dict], list[dict], list[dict]):
        """
        This method fetches all direct AD identities in a group

        Args: group_object_id
        return: a list of direct AD users
                a list of direct AD groups
                a list of direct AD service principals
        """

        url = "https://graph.microsoft.com/beta/groups/" + group_object_id + "/members"
        users_list = []
        groups_list = []
        sps_list = []

        while url:
            """
            This loop solves the paging problem
            """
            try:
                members = (
                    await self.client.groups.with_url(url)
                    .by_group_id(group_object_id)
                    .members.get()
                )
                for user in members.value:
                    if user.id not in exclude_objects:
                        if user.odata_type == "#microsoft.graph.user":
                            users_list.append(
                                {
                                    "id": user.id,
                                    "display_name": user.display_name,
                                    "user_principal_name": user.user_principal_name,
                                }
                            )
                        elif user.odata_type == "#microsoft.graph.group":
                            groups_list.append(
                                {
                                    "id": user.id,
                                    "display_name": user.display_name,
                                }
                            )
                        elif user.odata_type == "#microsoft.graph.servicePrincipal":
                            sps_list.append(
                                {
                                    "id": user.id,
                                    "display_name": user.display_name,
                                    "app_id": user.app_id,
                                }
                            )
                url = members.odata_next_link
            except ValueError:
                break

        return (users_list, groups_list, sps_list)

    async def get_group_members_recursively(
        self, group_object_id: str, exclude_objects: list[str]
    ) -> dict:
        """
        This method fetches all AD identities in a group recursively

        Args: group_object_id
              exclude_objects: a list of Azure object id to be excluded
        return: a dictionary containing the group info and its 3 types of members
        """
        root_group = await self.client.groups.by_group_id(group_object_id).get()
        groups_list = [group_object_id]
        group_members_users = []
        group_members_groups = [
            {
                "id": group_object_id,
                "display_name": root_group.display_name,
            }
        ]
        group_member_sps = []
        members_structure = {}

        while len(groups_list):
            group_id = groups_list.pop(0)
            (
                direct_users,
                direct_groups,
                direct_sps,
            ) = await self.get_group_direct_members(group_id, exclude_objects)

            members_structure[group_id] = direct_users + direct_groups + direct_sps

            group_members_users += direct_users
            group_members_groups += direct_groups
            group_member_sps += direct_sps

            for g in direct_groups:
                groups_list.append(g["id"])

        return {
            "members_user": group_members_users,
            "members_group": group_members_groups,
            "members_sp": group_member_sps,
            "members_structure": members_structure,
        }

    async def get_azure_objects_with_exclude(
        self, group_objects: list[str], exclude_objects: list[str]
    ) -> dict:
        """
        Args:
          group_objects: A list of Azure group object id
          exclude_objects: A list of Azure object ids which should be
                           excluded from the sync

        Return: A dict containing all users, groups, service principals to be synced
        """
        members_user = []
        members_group = []
        members_sp = []
        members_structure = {}

        for group_id in group_objects:
            members = await self.get_group_members_recursively(
                group_id, exclude_objects
            )
            members_user += members["members_user"]
            members_group += members["members_group"]
            members_sp += members["members_sp"]
            for g in members["members_structure"]:
                if g not in members_structure:
                    members_structure[g] = members["members_structure"][g]

        # drop duplicates
        members_user = {frozenset(item.items()): item for item in members_user}.values()
        members_group = {
            frozenset(item.items()): item for item in members_group
        }.values()
        members_sp = {frozenset(item.items()): item for item in members_sp}.values()

        return {
            "members_user": members_user,
            "members_group": members_group,
            "members_sp": members_sp,
            "members_structure": members_structure,
        }
