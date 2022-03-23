import requests
import json


#Define the Login Call Function
def loginCall(userName, passWord):
    url = "https://dm-us.informaticacloud.com/saas/public/core/v3/login"
    payload = {
        "username" : userName,
        "password" : passWord
    }
    payload_json = json.dumps(payload)
    headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }
    response = requests.request("POST", url, headers=headers, data = payload_json)
    response_json = response.json() if response and response.status_code == 200 else None
    infa_session_id = response_json['userInfo']['sessionId']
    return infa_session_id

#Define the Objects call with Tag
def ObjectsCall(iicsTag,infa_session_id):
    url = """https://na1.dm-us.informaticacloud.com/saas/public/core/v3/objects?q=tag=='""" + iicsTag + "'"""
    payload = {}
    headers = {
        'Accept': 'application/json',
        'INFA-SESSION-ID': infa_session_id
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json() if response and response.status_code == 200 else None
    assetPath = response_json ['objects'][0]['path']
    assetType = response_json['objects'][0]['type']
    assetId = response_json['objects'][0]['id']
    return (assetPath, assetType, assetId)

#Get commitHistory for Asset
def commitHistoryCall(assetPath, assetType, infa_session_id):
    url = """https://na1.dm-us.informaticacloud.com/saas/public/core/v3/commitHistory/?q=path=='""" + assetPath + "' and type=='""" + assetType + "'"""
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': infa_session_id
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json() if response and response.status_code == 200 else None
    commitHash = response_json['commits'][0]['hash']
    return commitHash

#Function to Pull an Asset
def gitPull(assetId, commitHash, infa_session_id):
    print(assetId)
    print(commitHash)
    print(infa_session_id)
    url = "https://na1.dm-us.informaticacloud.com/saas/public/core/v3/pull"
    payload = json.dumps({
        "commitHash": commitHash,
        "objects": [
            {
                "id": assetId
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': infa_session_id
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json() if response and response.status_code == 200 else None
    print(response_json)
    pullActionId = response_json['pullActionId']
    return pullActionId


#Check the status of the Pull action
def checkGitActionId(gitActionId, infa_session_id):
    url = """https://na1.dm-us.informaticacloud.com/saas/public/core/v3/sourceControlAction/""" + gitActionId
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': infa_session_id
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json() if response and response.status_code == 200 else None
    pullActionStatus = response_json['status']['state']
    print(pullActionStatus)
    return pullActionStatus

# Logout of the session

def sessLogout(infa_session_id):
    url = "https://dm-us.informaticacloud.com/saas/public/core/v3/logout"
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'INFA-SESSION-ID': infa_session_id
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


####Application Starts here

print ("Welcome to CI_CD Application")

#Get the Tag Info that has to be used
iicsTag = input("Enter the IICS Asset Tag : ")

#Make a Login Call

srcInfaSessionID = loginCall("username","password")
print("1. Source Org Login is done")


#Make Objects call

srcAssetPath, srcAssetType, srcAssetId = ObjectsCall(iicsTag, srcInfaSessionID)

print("2. Got the Asset details using Object API + Tags")

#Make commitHistory call

commitHash = commitHistoryCall(srcAssetPath, srcAssetType, srcInfaSessionID)

print("3. Got the commit Hash")

#Target Org Login Call
tgtInfaSessionID = loginCall("username","password")

print("4. Target Org Login is done")

#Initiate Pull Operation on Target

print("5. Pull operation on Target Org")

srcActionId = gitPull(srcAssetId,commitHash,tgtInfaSessionID)



#Check the status
pullActionStatus = checkGitActionId(srcActionId, tgtInfaSessionID)

while pullActionStatus != "SUCCESSFUL":
    print("Pull operation status checking...")
    pullActionStatus = checkGitActionId(srcActionId, tgtInfaSessionID)

print("6. Pull operation is completed")

#Log out of the session

sessLogout(srcInfaSessionID)

sessLogout(tgtInfaSessionID)