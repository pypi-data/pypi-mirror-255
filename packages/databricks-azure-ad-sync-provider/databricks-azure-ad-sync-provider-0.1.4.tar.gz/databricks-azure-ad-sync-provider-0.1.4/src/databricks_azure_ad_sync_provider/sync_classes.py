"""
This module is used for all Sync classes
"""
from enum import Enum


class SyncStatus(Enum):
    INITIAL = 0
    TO_ADD = 1
    TO_DELETE = 2
    TO_UPDATE = 3


class SyncUser:
    def __init__(self, azure_user, databricks_user, databricks_identity):
        self.databricks_display_name = databricks_user["display_name"]
        self.databricks_id = databricks_user["id"]
        self.databricks_external_id = databricks_user["external_id"]
        self.databricks_email = databricks_user["user_name"]

        self.azure_id = azure_user["id"]
        self.azure_display_name = azure_user["display_name"]
        self.azure_email = azure_user["user_principal_name"]
        self.status = SyncStatus.INITIAL
        self.databricks_identity = databricks_identity

    def is_in_sync(self) -> bool:
        """

        Returns:
            bool: True if the Databricks and Azure user are already synced
        """
        display_name = self.databricks_display_name == self.azure_display_name
        email = self.databricks_email == self.azure_email
        id = (
            self.databricks_external_id == self.azure_id
            or self.databricks_identity.relations["users"][self.databricks_id]
            == self.azure_id
        )
        return display_name and email and id

    def sync_user_to_db(self, force_delete=False):
        """Sync a users to Databricks
        Args:
            force_delete : If True, allows to delete users in Databricks
        """
        id = self.databricks_id
        user_name = self.azure_email
        display_name = self.azure_display_name
        external_id = self.azure_id

        if self.status == SyncStatus.TO_UPDATE:
            print(f"Updating user {display_name}")
            self.databricks_identity.update_databricks_user(
                id, display_name, user_name, external_id
            )

        elif self.status == SyncStatus.TO_ADD:
            print(f"Adding user {display_name}")
            self.databricks_identity.add_databricks_user(
                display_name, user_name, external_id
            )

        elif self.status == SyncStatus.TO_DELETE:
            if force_delete:
                self.databricks_identity.delete_databricks_user(id)

        else:
            pass


class SyncGroup:
    def __init__(self, azure_group, databricks_group, databricks_identity):
        self.databricks_id = databricks_group["id"]
        self.databricks_external_id = databricks_group["external_id"]
        self.databricks_display_name = databricks_group["display_name"]
        self.databricks_members = databricks_group["members"]
        self.azure_id = azure_group["id"]
        self.azure_display_name = azure_group["display_name"]
        self.azure_members = []
        self.status = SyncStatus.INITIAL
        self.databricks_identity = databricks_identity

    def is_in_sync(self) -> bool:
        """

        Returns:
            bool: True if the Databricks and Azure groups are already synced
        """
        if len(self.databricks_members) != len(self.azure_members):
            return False

        i = (
            self.databricks_external_id == self.azure_id
            or self.databricks_identity.relations["groups"][self.databricks_id]
            == self.azure_id
        )
        display_name = self.databricks_display_name == self.azure_display_name

        azure_member_ids = [x["id"] for x in self.azure_members]
        databricks_member_ids = []
        for db_member in self.databricks_members:
            db_id = db_member.value
            if db_id in self.databricks_identity.relations["users"]:
                databricks_member_ids.append(
                    self.databricks_identity.relations["users"][db_id]
                )
            elif db_id in self.databricks_identity.relations["groups"]:
                databricks_member_ids.append(
                    self.databricks_identity.relations["groups"][db_id]
                )
            elif db_id in self.databricks_identity.relations["servicePrincipals"]:
                databricks_member_ids.append(
                    self.databricks_identity.relations["servicePrincipals"][db_id]
                )

        members = sorted(azure_member_ids) == sorted(databricks_member_ids)

        return i and display_name and members

    def sync_group_add_empty(self):
        """
        Add a new group without any group members
        """
        print(f"Adding group {self.azure_display_name}")
        # create a new group without any members
        new_group = self.databricks_identity.add_databricks_group(
            self.azure_display_name, self.azure_id
        )
        # We will update the group's members afterwards
        self.status = SyncStatus.TO_UPDATE
        self.databricks_id = new_group.id
        self.databricks_display_name = new_group.display_name
        self.databricks_external_id = new_group.external_id

    def sync_group_update(self, force_delete=False):
        """
        Sync a group to Databricks
        Args:
            force_delete : If True, allows to delete groups in Databricks
        """
        members = [x["id"] for x in self.azure_members]
        members = []
        all_relations = (
            self.databricks_identity.relations["users"]
            | self.databricks_identity.relations["groups"]
            | self.databricks_identity.relations["servicePrincipals"]
        )
        for x in self.azure_members:
            external_id = x["id"]
            for i in all_relations:
                if all_relations[i] == external_id:
                    members.append(i)
        if self.status == SyncStatus.TO_UPDATE:
            print(f"Updating group {self.azure_display_name}")
            self.databricks_identity.update_databricks_group(
                self.databricks_id, self.azure_display_name, members, self.azure_id
            )

        elif self.status == SyncStatus.TO_DELETE:
            if force_delete:
                self.databricks_identity.delete_databricks_user(self.databricks_id)

        else:
            pass


class SyncServicePrincipal:
    def __init__(
        self, azure_service_principal, databricks_service_principal, databricks_identity
    ):
        self.databricks_application_id = databricks_service_principal["application_id"]
        self.databricks_display_name = databricks_service_principal["display_name"]
        self.databricks_external_id = databricks_service_principal["external_id"]
        self.databricks_id = databricks_service_principal["id"]

        self.azure_id = azure_service_principal["id"]
        self.azure_display_name = azure_service_principal["display_name"]
        self.azure_application_id = azure_service_principal["app_id"]

        self.status = SyncStatus.INITIAL
        self.databricks_identity = databricks_identity

    def is_in_sync(self) -> bool:
        """

        Returns:
            bool: True if the Databricks and Azure user are already synced.
            Which means they have the same app_id, display_name and id
        """
        app_id = self.databricks_application_id == self.azure_application_id
        display_name = self.databricks_display_name == self.azure_display_name
        id = (
            self.databricks_external_id == self.azure_id
            or self.databricks_identity.relations["servicePrincipals"][
                self.databricks_id
            ]
            == self.azure_id
        )

        return app_id and display_name and id

    def sync_sp_to_db(self, force_delete=False):
        """Sync a Service Principal to Databricks
        Args:
            force_delete : If True, allows to delete service principals in Databricks
        """
        # do we need the external ID here as we already have an application ID ?
        id = self.databricks_id
        display_name = self.azure_display_name
        application_id = self.azure_application_id
        external_id = self.azure_id

        if self.status == SyncStatus.TO_UPDATE:
            print(f"Updating sp {display_name}")
            self.databricks_identity.update_databricks_sps(
                id, application_id, display_name, external_id
            )

        if self.status == SyncStatus.TO_ADD:
            print(f"Adding sp {display_name}")
            self.databricks_identity.add_databricks_sps(
                application_id, display_name, external_id
            )

        elif self.status == SyncStatus.TO_DELETE:
            if force_delete:
                self.databricks_identity.delete_databricks_user(id)

        else:
            pass
