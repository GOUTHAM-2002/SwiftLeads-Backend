import os, json
from Supabase.utils import (
    createCampaignObj,
    addCampaignContactInfo,
    getCampaignsOfUser,
    getFullCampaignContactInfo,
    getCampaignContactContents,
    update_campaign_contact,
    create_campaign_metrics_obj,
    fetch_campaign_metrics_obj,
    update_campaign_metrics_obj,
)


def createCampaign(campaign_data, campaign_info):
    response, status = createCampaignObj(campaign_data)
    campaign_id = response["data"][0]["id"]
    user_id = campaign_data["user_id"]
    campaign_cost = create_new_campaign_cost(campaign_id)
    create_campaign_metrics_obj(campaign_cost)
    if status == 200:
        updatedCampaignInfo = []
        for info_obj in campaign_info:
            info_obj = dict(info_obj)
            info_obj["campaign_id"] = campaign_id
            info_obj["user_id"] = user_id
            verifiedObj = verifyCampaignInfo(info_obj)
            print(verifiedObj)
            print("\n")
            if verifiedObj is not None:
                updatedCampaignInfo.append(verifiedObj)
        return addCampaignContactInfo(updatedCampaignInfo)
    return response, status


def editCampaign(campaignId, newCampaignInfo):
    existingCampaign = getCampaignContactContents(campaignId)[0]["data"][0]
    updatedData = updateLatestCampaign(existingCampaign, newCampaignInfo)
    verifiedObj = verifyCampaignInfo(updatedData)
    if verifiedObj is not None:
        return update_campaign_contact(campaignId, verifiedObj)


def getUsersCampaigns(user_id):
    return getCampaignsOfUser(user_id)


def getCampaignDetails(campaign_id):
    return getFullCampaignContactInfo(campaign_id)


def get_campaign_cost(campaign_id):
    return fetch_campaign_metrics_obj(campaign_id)


def updateLatestCampaign(existingCampaign, newCampaignInfo, user_id):
    existingCampaign = dict(existingCampaign)
    newCampaignInfo = dict(newCampaignInfo)
    updatedCampaign = existingCampaign.copy()
    for key, new_value in newCampaignInfo.items():
        if new_value is not None and new_value != "":
            if isinstance(new_value, list):
                if new_value:
                    updatedCampaign[key] = new_value
            else:
                updatedCampaign[key] = new_value
    return updatedCampaign


def create_new_campaign_cost(campaign_id):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    with open(config_path, "r") as file:
        data = json.load(file)

    campaign_cost_default = data["campaign_cost"]

    new_campaign_cost = {
        "campaign_id": campaign_id,
        **campaign_cost_default,
    }

    return new_campaign_cost


def update_campaign_cost(campaign_id, new_campaign_cost_obj):
    return update_campaign_metrics_obj(campaign_id, new_campaign_cost_obj)


def verifyCampaignInfo(campaignInfoObj):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    with open(config_path, "r") as file:
        data = json.load(file)["campaignInfoDefault"]

    required_fields = ["user_id", "campaign_id", "phone", "name"]

    for field in required_fields:
        if field not in campaignInfoObj or not campaignInfoObj[field]:
            return None

    verified_info = {}

    for field in required_fields:
        verified_info[field] = campaignInfoObj[field]

    for key, default_value in data.items():
        if key in campaignInfoObj:
            input_value = campaignInfoObj[key]

            if input_value not in [None, "", [], 0, False]:
                verified_info[key] = input_value
            else:
                verified_info[key] = default_value
        else:
            verified_info[key] = default_value

    return verified_info
