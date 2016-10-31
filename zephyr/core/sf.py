import sqlite3

import pandas as pd

from simple_salesforce import Salesforce

def cache(db, config=None):
    username, password, token = config
    salesforce = get_session(username, password, token)
    database = sqlite3.connect(db)
    get_accounts(salesforce, database)
    get_aws_accounts(salesforce, database)
    get_projects(salesforce, database)
    return database

def get_accounts(salesforce, database):
    query_acct = """
        SELECT Id, Name, Type
        FROM Account
        WHERE Type='Active' OR Type='Active Legacy'
    """
    return soql_to_sql(
        query_acct,
        "accounts",
        salesforce,
        database,
    )

def get_aws_accounts(salesforce, database):
    query_aws = """
        SELECT Name,
            Acct_Number__c,
            Assoc_Project__c,
            Cloudcheckr_ID__c,
            Cloudcheckr_Name__c,
            Bitdefender_ID__c
        FROM AWS_Account__c
    """
    return soql_to_sql(
        query_aws,
        "aws",
        salesforce,
        database,
    )

def get_projects(salesforce, database):
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
    return soql_to_sql(
        query_project,
        "projects",
        salesforce,
        database,
    )

def get_session(username, password, token):
    return Salesforce(
        username=username,
        password=password,
        security_token=token,
    )

def soql_to_sql(query, table, salesforce, database):
    res = salesforce.query_all(query)
    header = list(zip(*res["records"][0].items()))[0][1:]
    data = [list(zip(*record.items()))[1][1:] for record in res["records"]]
    df = pd.DataFrame(data, columns=header)
    df.to_sql(table, database, if_exists="replace")
    return df

