fixtures = {
    "cc_accounts": [
        {
            "index": -1,
            "aws_account": "aws_id_1",
            "id": "1,729",
            "name": "Test Account"
        },
        {
            "index": -2,
            "aws_account": "aws_id_2",
            "id": "1,728",
            "name": "No Dynamics"
        }
    ],
    "lo_accounts": [{
        "index": -1,
        "id": "536904",
        "name": "Logicworks R&D"
    }],
    "sf_accounts": [{
        "index": -1,
        "Id": "sf_account_id_1",
        "Name": "Test Account",
        "Type": "Active"
    }],
    "sf_aws": [
        {
            "index": -1,
            "Name": ".meta",
            "Acct_Number__c": "aws_id_1",
            "Assoc_Project__c": "sf_project_id_1",
            "Cloudcheckr_ID__c": "",
            "Cloudcheckr_Name__c": "",
            "Bitdefender_ID__c": "bd_id_1"
        },
        {
            "index": -2,
            "Name": ".no_dynamics",
            "Acct_Number__c": "aws_id_2",
            "Assoc_Project__c": "sf_project_id_2",
            "Cloudcheckr_ID__c": "",
            "Cloudcheckr_Name__c": "",
            "Bitdefender_ID__c": "bd_id_2"
        },
    ],
    "sf_projects": [
        {
            "index": -1,
            "Id": "sf_project_id_1",
            "Name": "Test Account",
            "Account__c": "sf_account_id_1",
            "Dynamics_ID__c": "LOGICWORKSRND",
            "JIRAKey__c": "ZEP",
            "LogicOps_ID__c": "536904",
            "Main_Project_POC__c": "",
            "MRR__c": "",
            "Planned_Spend__c": "100000.0"
        },
        {
            "index": -2,
            "Id": "sf_project_id_2",
            "Name": "No Dynamics",
            "Account__c": "sf_account_id_1",
            "Dynamics_ID__c": "",
            "JIRAKey__c": "",
            "LogicOps_ID__c": "",
            "Main_Project_POC__c": "",
            "MRR__c": "",
            "Planned_Spend__c": ""
        }
    ]
}
