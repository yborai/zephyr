import sqlite3

import pandas as pd

from . import client as sf

class SalesForceAccounts(sf.SalesForce):

    def request(self):
        query_acct = """
            SELECT Id, Name, Type
            FROM Account
            WHERE Type='Active' OR Type='Active Legacy'
        """
        return self.soql_to_sql(query_acct, "sf_accounts")

class SalesForceAWSAccounts(sf.SalesForce):

    def request(self):
        query_aws = """
            SELECT Name,
                Acct_Number__c,
                Assoc_Project__c,
                Cloudcheckr_ID__c,
                Cloudcheckr_Name__c,
                Bitdefender_ID__c
            FROM AWS_Account__c
        """
        return self.soql_to_sql(query_aws, "sf_aws")

class SalesForceProjects(sf.SalesForce):

    def request(self):
        query_project = """
            SELECT
                Id,
                Name,
                Account__c,
                Dynamics_ID__c,
                JIRAKey__c,
                LogicOps_ID__c,
                Main_Project_POC__c,
                MRR__c,
                Planned_Spend__c
            FROM Projects__c
        """
        return self.soql_to_sql(query_project, "sf_projects")
