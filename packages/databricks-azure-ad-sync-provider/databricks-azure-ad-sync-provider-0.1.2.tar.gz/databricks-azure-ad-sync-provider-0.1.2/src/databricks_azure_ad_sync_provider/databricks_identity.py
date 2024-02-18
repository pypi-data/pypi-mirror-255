"""
This module is for Databricks Identities objects
"""

import contextlib
import json
from datetime import datetime

from databricks.sdk import AccountClient
from databricks.sdk.service.iam import (
    Group,
    Patch,
    PatchOp,
    PatchSchema,
    ServicePrincipal,
    User,
)


class DatabricksIdentity:
    def __init__(self, account_client: AccountClient, json_path: str):
        """
        Args:
            account_client (databricks.sdk.AccountClient):
                Object containing information needed for authentication in databricks
            relations: A JSON object storing relations between a databricks object
                       and an Azure AD object
            all_databricks_objects: A JSON object storing all databricks objects
            json_path: The json file path (in the root directory)
        """
        self.account_client = account_client
        self.json_path = json_path
        self.relations = self.read_json()
        self.all_databricks_objects = self.get_all_databricks_objects()

    def read_json(self) -> dict:
        """
        This method read syncstates.json file which stores the relations between
        Databricks objects and Azure AD objects. The file is stored in root directory

        Returns:
            dict: a dict of sync states
        """
        with open(self.json_path) as f:
            return json.load(f)

    def write_json(self):
        """
        This method writes the updated relations between
        Databricks objects and Azure AD objects to syncstates.json file
        The file is stored in root directory
        """
        self.relations["lastSyncTime"] = str(datetime.now())
        with open(self.json_path, "w") as outfile:
            outfile.write(json.dumps(self.relations, indent=4))

    # Users
    def fetch_databricks_users(self) -> list[User]:
        """
        This method returns a list of databricks users

        Returns:
            list: a list of all users in databricks
        """
        return list(self.account_client.users.list())

    # def fetch_databricks_user(self, id: str) -> User:
    #     """
    #     Return single user with id

    #     Args:
    #         id (str): databricks id of user
    #     Returns:
    #         databricks.sdk.service.iam.User: user with id
    #     """
    #     return self.account_client.users.get(id)

    def add_databricks_user(
        self, display_name: str, user_name: str, external_id: str
    ) -> User:
        """
        This method adds a user to databricks and returns that user.

        Args:
            display_name (str): Name used to represent the user in databricks
            user_name (str): email of the user
            external_id (str): Azure entra Id of user

        Returns:
            databricks.sdk.service.iam.User:
                databricks user item representing the created user
        """
        new_user = self.account_client.users.create(
            display_name=display_name, user_name=user_name, external_id=external_id
        )
        # external_id won't be updated as it's not supported now
        self.relations["users"][new_user.id] = external_id
        self.all_databricks_objects["users"][new_user.id] = {
            "display_name": new_user.display_name,
            "external_id": external_id,
            "user_name": new_user.user_name,
        }

        return new_user

    def update_databricks_user(
        self,
        id: str,
        display_name: str = None,
        user_name: str = None,
        external_id: str = None,
    ):
        """
        Update a user in databricks.
        Currently only the display_name and user_name are supported for update.
        If the user_name is updated, the databricks user will be deleted and recreated.
        This is done because the databricks API doesn't provide an option to update the
         user_name or email.
        All attributes that don't relate to the user_name are copied over to the new
        user.

        Args:
            id (str): databricks id of the user
            display_name (str): Name used to represent the user in databricks
            user_name (str): email of the user
            external_id (str): azure id synced from Azure
        """
        if user_name:
            old_user = self.account_client.users.get(id)
            old_user.user_name = user_name
            self.account_client.users.delete(id)
            self.account_client.users.create(
                active=old_user.active,
                display_name=old_user.display_name,
                entitlements=old_user.entitlements,
                groups=old_user.groups,
                roles=old_user.roles,
                schemas=old_user.schemas,
                user_name=old_user.user_name,
            )
        else:
            operations = []
            if display_name:
                # Note that the corresponding family_name and given_name
                # will be updated accordingly
                operations.append(Patch(PatchOp.REPLACE, "displayName", display_name))
                self.all_databricks_objects["users"][id]["display_name"] = display_name
            if external_id:
                # the following won't work as it's not supported by Databricks API now
                operations.append(Patch(PatchOp.REPLACE, "externalId", external_id))
                self.all_databricks_objects["users"][id]["external_id"] = external_id

            # We don't update self.relations["users"] here because we want to
            # store relations regardless of whether we perform an update action

            self.account_client.users.patch(
                id,
                operations=operations,
                schemas=[PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP],
            )

    def delete_databricks_user(self, id: str):
        """
        Delete a user in databricks based on it's Id.

        Args:
            id (str): databricks id of the user to be deleted
        """
        self.account_client.users.delete(id=id)
        with contextlib.suppress(KeyError):
            del self.relations["users"][id]
            del self.all_databricks_objects["users"][id]

    # Groups
    def fetch_databricks_groups(self) -> list[Group]:
        """
        This method returns a list of databricks groups

        Returns:
            List: list of groups that exist in databricks
        """
        return list(self.account_client.groups.list())

    # def fetch_databricks_group(self, id: str) -> Group:
    #     """
    #     Return single group with id

    #     Args:
    #         id (str): databricks id of group
    #     Returns:
    #         databricks.sdk.service.iam.Group: group with id
    #     """
    #     return self.account_client.groups.get(id)

    def add_databricks_group(self, display_name: str, external_id: str) -> Group:
        """
        Add a new group without any members in databricks.

        Args:
            display_name (str): Name used to represent the group
            external_id (str): Azure Entra Id of group

        Returns:
            databricks.sdk.service.iam.Group:
                databricks group item representing the created group
        """
        new_group = self.account_client.groups.create(
            display_name=display_name, external_id=external_id
        )

        self.relations["groups"][new_group.id] = external_id
        self.all_databricks_objects["groups"][new_group.id] = {
            "display_name": new_group.display_name,
            "external_id": external_id,
            "members": None,
        }

        return new_group

    # def replace_databricks_group(
    #     self,
    #     id: str,
    #     display_name: str = None,
    #     member_ids: list[str] = None,
    #     external_id: str = None,
    # ):
    #     """
    #     Replace a databricks group.
    #     Currently only the display name and members are supported.

    #     Args:
    #         id (str): databricks id of the group to be updated
    #         display_name (str): Name used to represent the group
    #         member_ids (List[str]):
    #             List of databricks ids of the users that belong to the group
    #     """
    #     if member_ids is not None:
    #         complex_members = self.get_list_of_complex_values(member_ids)
    #     else:
    #         complex_members = self.get_current_members_of_group(id)
    #     self.account_client.groups.update(
    #         id, display_name=display_name, members=complex_members
    #     )

    def update_databricks_group(
        self,
        id: str,
        display_name: str = None,
        member_ids: list[str] = None,
        external_id: str = None,
    ):
        """
        Partially update a databricks group.
        Args:
            id (str): databricks id of the group to be updated
            display_name (str): Name used to represent the group
            member_ids (List[str]):
                List of databricks ids of the users that belong to the group
            external_id: external id of the group
        """
        operations = []
        if member_ids:
            json_members = self.get_list_of_group_members(member_ids)
            operations.append(Patch(PatchOp.REPLACE, "members", json_members))
            self.all_databricks_objects["groups"][id]["members"] = json_members

        if display_name:
            operations.append(Patch(PatchOp.REPLACE, "displayName", display_name))
            self.all_databricks_objects["groups"][id]["display_name"] = display_name

        if external_id:
            operations.append(Patch(PatchOp.REPLACE, "externalId", external_id))
            self.all_databricks_objects["groups"][id]["external_id"] = external_id

        # We don't update self.relations["groups"] here because we want to
        # store relations regardless of whether we perform an update action

        self.account_client.groups.patch(
            id,
            operations=operations,
            schemas=[PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP],
        )

    def delete_databricks_group(self, id: str):
        """
        Delete a group in databricks based on its Id.

        Args:
            id (str): databricks id of the group to be deleted
        """
        self.account_client.groups.delete(id=id)
        with contextlib.suppress(KeyError):
            del self.relations["groups"][id]
            del self.all_databricks_objects["groups"][id]

    # def get_current_members_of_group(self, id: str) -> list[ComplexValue]:
    #     """
    #     Return the members of a group.

    #     Args:
    #         id (str): databricks id of the group that you want to get the members of

    #     Returns:
    #         List (databricks.sdk.service.iam.ComplexValue):
    #             list of complexValues representing the users
    #     """
    #     return self.account_client.groups.get(id=id).members

    # Service Principals
    def fetch_databricks_sps(self) -> list[ServicePrincipal]:
        """
        This method returns a list of databricks service principals
        """
        all_sps = self.account_client.service_principals.list()
        return list(all_sps)

    # def fetch_single_databricks_sps(self, id: str) -> ServicePrincipal:
    #     """
    #     Return single service principal with id

    #     Args:
    #         id (str): databricks id of service principal
    #     Returns:
    #         databricks.sdk.service.iam.ServicePrincipal: service principal with id
    #     """
    #     return self.account_client.service_principals.get(id)

    def add_databricks_sps(
        self, application_id: str, display_name: str, azure_id: str
    ) -> ServicePrincipal:
        """
        Create a new service principal in databricks
        Return: A ServicePrincipal object
        """
        new_sps = self.account_client.service_principals.create(
            active=True,
            display_name=display_name,
            application_id=application_id,
            external_id=azure_id,
        )

        self.relations["servicePrincipals"][new_sps.id] = azure_id
        self.all_databricks_objects["sps"][new_sps.id] = {
            "display_name": new_sps.display_name,
            "application_id": new_sps.application_id,
            "external_id": new_sps.azure_id,
        }

        return new_sps

    def update_databricks_sps(
        self,
        id: str,
        display_name: str = None,
        external_id: str = None,
    ) -> ServicePrincipal:
        """
        Update a service principal in databricks
        """
        operations = []

        if display_name:
            operations.append(Patch(PatchOp.REPLACE, "displayName", display_name))
            self.all_databricks_objects["sps"][id]["display_name"] = display_name

        if external_id:
            operations.append(Patch(PatchOp.REPLACE, "externalId", external_id))
            self.all_databricks_objects["sps"][id]["external_id"] = external_id

        self.account_client.service_principals.patch(
            id,
            operations=operations,
            schemas=[PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP],
        )

    def delete_databricks_sps(self, id: str):
        """
        Delete a Service Principal in databricks based on it's Id.

        Args:
            id (str): databricks id of the user to be deleted
        """
        self.account_client.service_principals.delete(id=id)
        with contextlib.suppress(KeyError):
            del self.relations["servicePrincipals"][id]
            del self.all_databricks_objects["sps"][id]

    # General
    def get_list_of_group_members(self, members: list[str]) -> list[dict]:
        """
        Convert a list of id's to a list of json objects.
        """
        li = []
        if len(members) == 0:
            return li
        for member_id in members:
            li.append(
                {
                    "value": member_id,
                }
            )
        return li

    def get_all_databricks_objects(self) -> dict:
        """
        This method fetches all databricks identities.
        Return: a dict containing all users, groups, service principals
        """
        databricks_json_objects = {
            "users": {},
            "groups": {},
            "sps": {},
        }
        db_groups = self.fetch_databricks_groups()
        for g in db_groups:
            databricks_json_objects["groups"][g.id] = {
                "display_name": g.display_name,
                "external_id": g.external_id,
                "members": g.members,
            }

        db_users = self.fetch_databricks_users()
        for u in db_users:
            databricks_json_objects["users"][u.id] = {
                "display_name": u.display_name,
                "external_id": u.external_id,
                "user_name": u.user_name,
            }

        db_sps = self.fetch_databricks_sps()
        for s in db_sps:
            databricks_json_objects["sps"][s.id] = {
                "display_name": s.display_name,
                "external_id": s.external_id,
                "application_id": s.application_id,
            }

        return databricks_json_objects
