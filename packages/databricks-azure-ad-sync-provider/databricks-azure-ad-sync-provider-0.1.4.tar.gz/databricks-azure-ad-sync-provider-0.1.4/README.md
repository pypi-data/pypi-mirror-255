# databricks-azure-ad-sync-provider

`databricks-azure-ad-sync-provider` is a package that allows to sync users, groups and service principals from Microsoft Entra ID to Databricks.

## Requirements

`databricks-azure-ad-sync-provider` is built on top of:

* python 3.9+

#### Authentication

Authenticate to you Microsoft Entra ID and Azure Databricks to use the package.
There are multiple ways available for that, we suggest the following:

**1. With Azure CLI**

+ Authenticate to your Azure account on your machine with `az login`.
+ Specify necessary variables
  1. With environment variables: Setup for `DATABRICKS_HOST` and `DATABRICKS_ACCOUNT_ID`
  2. With a `.databrickscfg` file: Create the `.databrickscfg` file (~ for Linux or macOS, and %USERPROFILE% for Windows) containing the
     following info:

  ```
  [DEFAULT]
  host = https://accounts.azuredatabricks.net/
  account_id = <Databricks account id>
  ```

**2. With Microsoft Entra ID service principal:**

+ Create a service principal in Microsoft Entra ID and add it to Azure Databricks and grant it target permissions (see [reference documentation](https://learn.microsoft.com/en-gb/azure/databricks/dev-tools/service-principals)).
+ Specify necessary variables

  1. With environment variables

     - For Azure: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET (see [Microsoft Entra ID authentication](https://learn.microsoft.com/en-us/azure/communication-services/quickstarts/identity/service-principal?pivots=platform-azcli))
     - For Databricks: DATABRICKS_HOST, DATABRICKS_ACCOUNT_ID, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET (see [Databricks authentication](https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html#language-Environment))
  2. With a `.databrickscfg` file: Create a .databrickscfg file (~ for Linux or macOS, and %USERPROFILE% for Windows) containing the following info:

  ```
  [DEFAULT]
  host = https://accounts.azuredatabricks.net/
  account_id = <Databricks account id>
  azure_tenant_id = <Azure tenant id>
  azure_client_id = <Azure service principal application ID>
  azure_client_secret = <Azure service principal secret>
  ```

## Installation

```
pip install databricks-azure-ad-sync-provider
```

## Usage

**Sync execution**
  ```
<fct_name> -f/--file <path to your yaml file> -d/--delete
  ```
+ -f/--file <path to your yaml file>:  it's required to provide the object ID(s) of Azure groups and (optionally) exclude object ID(s) in a yaml file (ex. see test.yaml).
+ -d/--delete: If provided, this enablew to delete identities in Databricks.
