import json

from ..core.ddh import DDH

def iam_users(cache):
    with open(cache, "r") as f:
        response = json.load(f)
    user_details = response[0].get("IamUsersDetails")
    header = [
        "Username",
        "Has MFA",
        "Console Last Used",
        "Access Key 1 Last Used",
        "Access Key 2 Last Used",
    ]
    data = [[
            user["UserName"],
            user["HasMfa"],
            user["LastUsed"],
            user["UserCredential"]["AccessKey1LastUsedDate"],
            user["UserCredential"]["AccessKey2LastUsedDate"],
        ]
            for user in user_details
    ]
    return DDH(header=header, data=data)
