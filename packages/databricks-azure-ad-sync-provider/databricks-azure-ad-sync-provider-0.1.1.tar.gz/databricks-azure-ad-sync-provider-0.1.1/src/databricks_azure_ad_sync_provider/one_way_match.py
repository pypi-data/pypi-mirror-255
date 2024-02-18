"""
This module does a one-way-sync between azure and databricks users and groups.
Author: nicolas.jankelevitch@dataroots.io
"""


from databricks_azure_ad_sync_provider.sync_classes import SyncGroup, SyncServicePrincipal, SyncStatus, SyncUser


class OneWayMatch:
    def __init__(self, azure_details, databricks_identity):
        self.databricks_identity = databricks_identity
        self.azure_groups = azure_details["members_group"]
        self.azure_users = azure_details["members_user"]
        self.azure_sps = azure_details["members_sp"]
        self.azure_member_structure = azure_details["members_structure"]

    def get_sync_group(
        self, azure_group, databricks_group, status: SyncStatus
    ) -> SyncGroup:
        """
        This method takes info from Azure and Databricks groups and combine them
        Return: A SyncGroup object
        """
        sg = SyncGroup(azure_group, databricks_group, self.databricks_identity)
        sg.status = status

        if azure_group["id"]:
            sg.azure_members = self.azure_member_structure[azure_group["id"]]
        return sg

    def match_groups(self):
        """
        This method checks if there is a match between Azure AD and Databricks groups

        Return: A list of SyncGroup objects to be synced
        """
        sync_groups = []
        databricks_dummy_group = {
            "id": "",
            "display_name": "",
            "external_id": "",
            "members": [],
        }
        azure_dummy_group = {"id": "", "display_name": ""}

        all_databricks_groups = self.databricks_identity.all_databricks_objects[
            "groups"
        ]
        databricks_groups_id = [x for x in all_databricks_groups]
        for azure_group in self.azure_groups:
            # check for match on id
            match = [
                {
                    "id": x,
                    "display_name": all_databricks_groups[x]["display_name"],
                    "external_id": all_databricks_groups[x]["external_id"],
                    "members": all_databricks_groups[x]["members"],
                }
                for x in all_databricks_groups
                if all_databricks_groups[x]["external_id"] == azure_group["id"]
                or (
                    x in self.databricks_identity.relations["groups"]
                    and self.databricks_identity.relations["groups"][x]
                    == azure_group["id"]
                )
                or all_databricks_groups[x]["display_name"]
                == azure_group["display_name"]
            ]

            if len(match) > 1:
                raise Exception(
                    f"Multiple matches found for group with ID {azure_group['id']}."
                )
            if match:
                # As long as we find a match, we store the relation in the json file
                self.databricks_identity.relations["groups"][
                    match[0]["id"]
                ] = azure_group["id"]
                m = self.get_sync_group(azure_group, match[0], SyncStatus.TO_UPDATE)
                databricks_groups_id.remove(match[0]["id"])
                if not m.is_in_sync():
                    sync_groups.append(m)
            else:
                m = self.get_sync_group(
                    azure_group, databricks_dummy_group, SyncStatus.TO_ADD
                )
                sync_groups.append(m)

        for db in databricks_groups_id:
            d = self.get_sync_group(
                azure_dummy_group,
                {
                    "id": db,
                    "display_name": all_databricks_groups[db]["display_name"],
                    "external_id": all_databricks_groups[db]["external_id"],
                    "members": all_databricks_groups[db]["members"],
                },
                SyncStatus.TO_DELETE,
            )
            sync_groups.append(d)

        return sync_groups

    def get_sync_user(self, azure_user, databricks_user, status) -> SyncUser:
        """
        This method takes info from Azure and Databricks users and combine them
        Return: A SyncUser object
        """
        su = SyncUser(azure_user, databricks_user, self.databricks_identity)
        su.status = status
        return su

    def match_users(self) -> list[SyncUser]:
        """
        This method checks if there is a match between Azure AD and Databricks users

        Return: A list of SyncUser objects to be synced
        """
        sync_users = []
        databricks_dummy_user = {
            "id": "",
            "display_name": "",
            "external_id": "",
            "user_name": "",
        }
        azure_dummy_user = {"id": "", "display_name": "", "user_principal_name": ""}
        all_databricks_users = self.databricks_identity.all_databricks_objects["users"]
        databricks_users_id = [x for x in all_databricks_users]
        for azure_user in self.azure_users:
            # check for match on id
            match = [
                {
                    "id": x,
                    "display_name": all_databricks_users[x]["display_name"],
                    "external_id": all_databricks_users[x]["external_id"],
                    "user_name": all_databricks_users[x]["user_name"],
                }
                for x in all_databricks_users
                if all_databricks_users[x]["external_id"] == azure_user["id"]
                # check here for match between AZ ID and databricks ID
                or (
                    x in self.databricks_identity.relations["users"]
                    and self.databricks_identity.relations["users"][x]
                    == azure_user["id"]
                )
                or all_databricks_users[x]["user_name"]
                == azure_user["user_principal_name"]
                or all_databricks_users[x]["display_name"] == azure_user["display_name"]
            ]

            if len(match) > 1:
                raise Exception(
                    f"Multiple matches found for user with ID {azure_user['id']}."
                )
            if match:
                self.databricks_identity.relations["users"][
                    match[0]["id"]
                ] = azure_user["id"]
                m = self.get_sync_user(azure_user, match[0], SyncStatus.TO_UPDATE)
                databricks_users_id.remove(match[0]["id"])
                if not m.is_in_sync():
                    sync_users.append(m)
            else:
                m = self.get_sync_user(
                    azure_user, databricks_dummy_user, SyncStatus.TO_ADD
                )
                sync_users.append(m)
        for du in databricks_users_id:
            sync_users.append(
                self.get_sync_user(
                    azure_dummy_user,
                    {
                        "id": du,
                        "display_name": all_databricks_users[du]["display_name"],
                        "external_id": all_databricks_users[du]["external_id"],
                        "user_name": all_databricks_users[du]["user_name"],
                    },
                    SyncStatus.TO_DELETE,
                )
            )
        return sync_users

    def get_sync_service_principal(
        self, azure_sp, databricks_sp, status
    ) -> SyncServicePrincipal:
        """
        This method takes info from Azure and Databricks sps and combine them
        Return: A SyncServicePrincipal object
        """
        ssp = SyncServicePrincipal(azure_sp, databricks_sp, self.databricks_identity)
        ssp.status = status
        return ssp

    def match_service_principals(self) -> list[SyncServicePrincipal]:
        """
        This method checks if there is a match between Azure AD and Databricks sps

        Return: A list of SyncServicePrincipal objects to be synced
        """
        sync_sps = []

        databricks_dummy_sp = {
            "id": "",
            "display_name": "",
            "external_id": "",
            "application_id": "",
        }
        azure_dummy_sp = {"id": "", "display_name": "", "app_id": ""}
        all_databricks_sps = self.databricks_identity.all_databricks_objects["sps"]
        databricks_sps_id = [x for x in all_databricks_sps]

        for azure_sp in self.azure_sps:
            # check for match on id
            match = [
                {
                    "id": x,
                    "display_name": all_databricks_sps[x]["display_name"],
                    "external_id": all_databricks_sps[x]["external_id"],
                    "application_id": all_databricks_sps[x]["application_id"],
                }
                for x in all_databricks_sps
                if all_databricks_sps[x]["external_id"] == azure_sp["id"]
                or (
                    x in self.databricks_identity.relations["servicePrincipals"]
                    and self.databricks_identity.relations["servicePrincipals"][x]
                    == azure_sp["id"]
                )
                or all_databricks_sps[x]["display_name"] == azure_sp["display_name"]
                or all_databricks_sps[x]["application_id"] == azure_sp["app_id"]
            ]

            if len(match) > 1:
                raise Exception(
                    f"""Multiple matches found for
                    service principal with ID {azure_sp['id']}."""
                )
            if match:
                self.databricks_identity.relations["servicePrincipals"][
                    match[0]["id"]
                ] = azure_sp["id"]
                m = self.get_sync_service_principal(
                    azure_sp, match[0], SyncStatus.TO_UPDATE
                )
                databricks_sps_id.remove(match[0]["id"])
                if not m.is_in_sync():
                    sync_sps.append(m)
            else:
                m = self.get_sync_service_principal(
                    azure_sp, databricks_dummy_sp, SyncStatus.TO_ADD
                )
                sync_sps.append(m)

        for du in databricks_sps_id:
            sync_sps.append(
                self.get_sync_service_principal(
                    azure_dummy_sp,
                    {
                        "id": du,
                        "display_name": all_databricks_sps[du]["display_name"],
                        "external_id": all_databricks_sps[du]["external_id"],
                        "application_id": all_databricks_sps[du]["application_id"],
                    },
                    SyncStatus.TO_DELETE,
                )
            )

        return sync_sps
