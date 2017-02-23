fixtures = {
    "cc_accounts": {
        "header": ("index", "aws_account", "id", "name"),
        "data": (
            (-1, "aws_id_1", "1,729", "Test Account"),
            (-2, "aws_id_2", "1,728", "No Dynamics"),
        ),
    },
    "lo_accounts": {
        "header": ("index", "id", "name"),
        "data": (
            (-1, 536904, "Logicworks R&D"),
        ),
    },
    "sf_accounts": {
        "header": ("index", "Id", "Name", "Type"),
        "data": (
            (-1, "sf_account_id_1", "Test Account", "Active"),
        )
    },
    "sf_aws": {
        "header": (
            "index",
            "Name",
            "Acct_Number__c",
            "Assoc_Project__c",
            "Cloudcheckr_ID__c",
            "Cloudcheckr_Name__c",
            "Bitdefender_ID__c",
        ),
        "data": (
            (-1, ".meta", "aws_id_1", "sf_project_id_1", "", "", "bd_id_1"),
            (-2, ".no_dynamics", "aws_id_2", "sf_project_id_2", "", "", "bd_id_2"),
        )
    },
    "sf_projects": {
        "header": (
            "index",
            "Id",
            "Name",
            "Account__c",
            "Dynamics_ID__c",
            "JIRAKey__c",
            "LogicOps_ID__c",
            "Main_Project_POC__c",
            "MRR__c",
            "Planned_Spend__c"
        ),
        "data": ((
            -1,
            "sf_project_id_1",
            "Test Account",
            "sf_account_id_1",
            "LOGICWORKSRND",
            "ZEP",
            "536904",
            "",
            0.0,
            100000.0
        ),
        (
            -2,
            "sf_project_id_2",
            "No Dynamics",
            "sf_account_id_1",
            "",
            "",
            "",
            "",
            0.0,
            100000.0
        ))
    }
}
