"""
This module is the main logic to sync objects from Azure AD to Databricks
"""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from databricks_azure_ad_sync_provider.azure_identity import AzureIdentity
from databricks.sdk import AccountClient
from databricks_azure_ad_sync_provider.databricks_identity import DatabricksIdentity
from databricks_azure_ad_sync_provider.one_way_match import OneWayMatch
from databricks_azure_ad_sync_provider.sync_classes import SyncStatus
from databricks_azure_ad_sync_provider.yaml_parser import parse_yaml


#json_path = (Path(__file__).parents[2] / "./syncstates.json").resolve()

def sync_az_databricks():

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        required=True,
        help="The path to the yaml file",
    )
    parser.add_argument(
        "--state",
        "-s",
        type=str,
        required=True,
        help="The path to the json file",
    )
    parser.add_argument(
        "--delete",
        "-d",
        help="If specified, you enable databricks identities to be deleted",
        action="store_true",
    )

    args = parser.parse_args()
    yaml_path = args.file
    json_path = args.state
    force_delete = args.delete

    group_objects, exclude_objects = parse_yaml(yaml_path)

    try:
        logging.info("Attempting to authenticate to Azure...")
        azure_credential = DefaultAzureCredential()
        azure_identity = AzureIdentity(azure_credential)
        logging.info("Authenticated to Azure.")

        logging.info("Attempting to authenticate to databricks...")
        db_account_client = AccountClient()
        logging.info("Authenticated to databricks.")

    except ValueError as ve:
        logging.error(ve)
        sys.exit()

    logging.info("Fetching databricks identities...")
    databricks_identity = DatabricksIdentity(db_account_client, json_path)

    logging.info("Calling Azure API...")
    azure_group_details = asyncio.run(
        azure_identity.get_azure_objects_with_exclude(group_objects, exclude_objects)
    )

    ows = OneWayMatch(azure_group_details, databricks_identity)

    logging.info("Compare and get users to be synced...")

    sync_users = ows.match_users()

    print("#" * 80)
    print("USERS TO SYNC")
    print("#" * 80)
    for user in sync_users:
        print(f"{user.azure_display_name}, {user.status}")
        if user.status != SyncStatus.TO_DELETE:
            user.sync_user_to_db(force_delete)

    logging.info("Compare and get service principals to be synced...")

    sync_sps = ows.match_service_principals()

    print("#" * 80)
    print("SERVICE PRINCIPALS TO SYNC")
    print("#" * 80)
    for sp in sync_sps:
        print(f"{sp.azure_display_name}, {sp.status}")
        if sp.status != SyncStatus.TO_DELETE:
            sp.sync_sp_to_db(force_delete)

    logging.info("Compare and get groups to be synced...")

    sync_groups = ows.match_groups()
    print("#" * 80)
    print("GROUPS TO SYNC:")
    print("#" * 80)
    for group in sync_groups:
        print(f"{group.azure_display_name}, {group.status}")

        if group.status == SyncStatus.TO_ADD:
            group.sync_group_add_empty()

    for group in sync_groups:
        if group.status != SyncStatus.TO_DELETE:
            group.sync_group_update(force_delete)

    databricks_identity.write_json()

# sync_az_databricks()
