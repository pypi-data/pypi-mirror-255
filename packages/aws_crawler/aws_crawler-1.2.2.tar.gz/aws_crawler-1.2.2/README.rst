===============
**aws_crawler**
===============

Overview
--------

Crawl through AWS accounts in an organization using master assumed role. You can specify a comma-separated string of account IDs for specific accounts, an Organizational Unit ID to crawl through all accounts therein, or a comma-separated string of account statuses to crawl through matching accounts in the organization.  

Crawling Precedence:

1. Specific accounts
2. Organizational Unit
3. All matching accounts in the organization

Usage
-----

Installation:

.. code-block:: BASH

    pip3 install aws_crawler
    python3 -m pip install aws_crawler

Example:

- Get STS caller identities
- Also featuring (installed with aws_crawler):
   - `Automated authentication <https://pypi.org/project/aws-authenticator/>`_
   - `Multithreading <https://pypi.org/project/multithreader/>`_

.. code-block:: PYTHON

   import aws_crawler
   import boto3
   from multithreader import threads
   from aws_authenticator import AWSAuthenticator as awsauth
   from pprint import pprint as pp


   def get_caller_identity(
      account_id: str,
      items: dict
   ) -> dict:
      """Get AWS STS caller identities from accounts."""
      print(f'Working on {account_id}...')

      try:
         # Get auth credential for each account.
         credentials = aws_crawler.get_credentials(
               items['session'],
               f'arn:aws:iam::{account_id}:role/{items["assumed_role_name"]}',
               items['external_id']
         )

         # Get STS caller identity.
         client = boto3.client(
               'sts',
               aws_access_key_id=credentials['aws_access_key_id'],
               aws_secret_access_key=credentials['aws_secret_access_key'],
               aws_session_token=credentials['aws_session_token'],
               region_name=items['region']
         )
         response = client.get_caller_identity()['UserId']

      except Exception as e:
         response = str(e)

      # Return result.
      return {
         'account_id': account_id,
         'details': response
      }


   if __name__ == '__main__':
      # Login to AWS through SSO.
      auth = awsauth(
         sso_url='https://myorg.awsapps.com/start/#',
         sso_role_name='AWSViewOnlyAccess',
         sso_account_id='123456789012'
      )
      session = auth.sso()

      # # Create account list from comma-separated string of IDs.
      # account_ids = aws_crawler.create_account_list(
      #    session,
      #    '123456789012, 234567890123, 345678901234'
      # )
      # Get account list for an Organizational Unit.
      account_ids = aws_crawler.list_ou_accounts(
         session,
         'ou-abc123-asgh39'
      )
      # # Get matching account list for the entire organization.
      # account_ids = aws_crawler.list_accounts(
      #    session,
      #    'ACTIVE,SUSPENDED'
      # )

      # Execute task with multithreading.
      items = {
         'session': session,
         'assumed_role_name': 'MyOrgCrossAccountAccess',
         'external_id': 'lkasf987923ljkf2;lkjf298fj2',
         'region': 'us-east-1'
      }
      results = threads(
         get_caller_identity,
         account_ids,
         items,
         thread_num=5
      )

      # Print results.
      pp(results)
