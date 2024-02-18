# ynab-api-import

[![GitHub Release](https://img.shields.io/github/release/dnbasta/ynab-api-import?style=flat)]() 

This library enables importing YNAB transactions via the 
[Gocardless Bank Account Data API (formerly Nordigen)](https://gocardless.com/bank-account-data/). It can be helpful for cases in which your bank is not covered by YNABs native import functionality 

## Preparations
### Gocardless Bank Account API (formerly Nordigen)
1. [Check](https://gocardless.com/bank-account-data/coverage/) if your bank is supported by the API.
2. Create an account with Gocardless for the Bank Account Data API (They have a separate Login for it which you can 
get to by clicking on 'Get API Keys' or clicking the link at the bottom of their standard login page)
3. Go to Developers -> User Secrets and create a new pair of secret_id and secret_key
### YNAB
1. Create a personal access token for YNAB as described [here](https://api.ynab.com/)

## Usage
### 1. Install library from PyPI

```bash
pip install ynab-api-import
```
### 2. Initiate Library
```py
from ynabapiimport import YnabApiImport
ynab_api_import = YnabApiImport(secret_id='<secret_id>', 
                                secret_key='<secret_key>', 
                                token='<token>')
```
Optionally you can initiate an object from a `config.yaml` file. To do that create a YAML file with the following content:
```yaml
secret_id: <secret_id>
secret_key: <secret_key>
token: <ynab_token>
```
Save the file and provide the path to the library when initializing
```py
ynab_api_import = YnabApiImport.from_yaml('path/to/config.yaml')
```
### 2. Find the institution_id of your bank
Countrycode is ISO 3166 two-character country code. 
```py

ynab_api_import.fetch_institutions(countrycode='<countrycode>')
```
You get back a dictionary with all available banks in that country and their institution_ids.
Find and save the institution_id of your bank.
```py
[{'name': '<name>', 'institution_id': '<institution_id>'}]
```

### 3. Create Auth Link and authenticate with your bank
Provide a unique reference (e.g. `'mycheckingaccount'`)  per bank connection to identify the grant later on.
```py
ynab_api_import.create_auth_link(institution_id='<institution_id', reference='<reference>')
```
You get back a link which you need to copy to your browser and go through authentication flow with your bank

### 4. Run import with your reference and YNAB identifiers
You can find the IDs of your budget and the account if you go to https://app.ynab.com/ and open the target account by clicking on the name on the left hand side menu. The URL does now contain both IDs https://app.ynab.com/<budget_id>/accounts/<account_id>
```py
ynab_api_import.import_transactions(reference='<reference>', 
                                    budget_id='<budget_id>', 
                                    account_id='<account_id')
```
## Handling of multiple or no active accounts in your bank connection
The library assumes that you have one active account in your bank connection. It will raise an error if there are
no active accounts in your connection or more than one. In the latter case you need to provide the correct `resource_id`
in your call. You can find the `resource_id` by looking into the available options in the error message.
```py
ynab_api_import.import_transactions(resource_id='<resource_id>',
                                    reference='<reference>', 
                                    budget_id='<budget_id>', 
                                    account_id='<account_id')
```
## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
