# Library imports
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import asyncio, os


# Function imports
from Auth.jwt import verifyJsonWebToken
from Login.register import registerProcess
from Settings.settings import getUserSettings, editUserSettings
from Login.login import loginProcess
from Settings.phoneNumbers import (
    addPhoneNumber,
    delPhoneNumber,
    getUsersNumbers,
    editPhoneNumStatus,
)
from CRM.campaigns import (
    createCampaign,
    getFullCampaignContactInfo,
    getCampaignsOfUser,
    get_campaign_cost,
)
from CRM.contacts import addContacts, getUserContacts
from Caller.caller import CampaignCaller
from Supabase.utils import (
    deleteContactFromDB,
    updateCampaign,
    deleteCampaign,
    updateContactInDB,
    getProperties,
    get_active_phone_number,
    getCampaignContactContents,
)
from Analytics.analytics import createAnalyticsData, get_hot_leads
from extensions import mail

# from pyRedis import init_redis

# from Caller.callerTemp import onStartCampaign
# from pyCelery import init_celery

# from pyCelery import taskQueue

load_dotenv()

app = Flask(__name__)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail.init_app(app)

# redis = init_redis(app)

# celery_app = init_celery(app)

# Update CORS configuration
# ... existing imports ...

# Update CORS configuration
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["https://swift-leads-frontend.vercel.app"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "allow_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    }
)


# ... rest of the code ...

# @app.before_request
# def before_request():
#     if request.path.startswith("/api"):
#         auth_token = request.headers.get("Authorization")
#         print(auth_token)
#         if not auth_token:
#             return jsonify({"error": "Authorization token is missing"}), 401
#         response_data, status_code = verifyJsonWebToken(auth_token)
#         if status_code != 200:
#             return jsonify(response_data), status_code
#         pass


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@app.route("/register", methods=["POST"])
def registerFunction():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    response, status_code = registerProcess(email, password)
    return jsonify(response), status_code


@app.route("/api/getSettings", methods=["GET"])
def getSettings():
    user_id = request.args.get("user_id")
    response, status_code = getUserSettings(user_id)
    return jsonify(response), status_code


@app.route("/api/editSettings", methods=["POST"])
def editSettings():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    user_id = request.args.get("user_id")
    data = request.json
    response, status_code = editUserSettings(user_id, data)
    return jsonify(response), status_code


@app.route("/api/addPhoneNumberSettings", methods=["POST"])
def addPhoneSettings():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        response, status_code = addPhoneNumber(data)
        return jsonify(response), status_code

    except Exception as e:
        print(f"Error in addPhoneSettings: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/delPhoneNumberSettings", methods=["GET"])
def delPhoneSettings():
    idToDelete = request.args.get("id")
    response, status_code = delPhoneNumber(idToDelete)
    return jsonify(response), status_code


@app.route("/api/getUsersPhoneNums", methods=["GET"])
def getUsersPhoneNums():
    user_id = request.args.get("user_id")
    response, status_code = getUsersNumbers(user_id)
    return jsonify(response), status_code


@app.route("/api/changePhoneStatus", methods=["POST"])
def changePhoneStatus():
    data = request.json
    id = data.get("id")
    status = data.get("status")
    response, status_code = editPhoneNumStatus(id, status)
    return jsonify(response), status_code


@app.route("/api/createCampaign", methods=["POST"])
def makeCampaign():
    data = request.json
    campaignData = data.get("campaignData")
    campaignInfoData = data.get("campaignInfoData")
    response, status_code = createCampaign(campaignData, campaignInfoData)
    return jsonify(response), status_code


@app.route("/api/getCampaignList")
def getCampaignList():
    user_id = request.args.get("user_id")
    response, status = getCampaignsOfUser(user_id)
    return jsonify(response), status


@app.route("/api/getCampaignDeets")
def getCampaignContent():
    campaign_id = request.args.get("campaign_id")
    response, status = getFullCampaignContactInfo(campaign_id)
    return jsonify(response), status


@app.route("/api/addContacts", methods={"POST"})
def addUserContacts():
    data = request.json
    user_id = data.get("user_id")
    contacts = data.get("contacts")
    response, status = addContacts(user_id, contacts)
    return jsonify(response), status


@app.route("/api/getContacts")
def getContacts():
    user_id = request.args.get("user_id")
    response, status = getUserContacts(user_id)
    return jsonify(response), status


@app.route("/api/deleteContact", methods=["DELETE"])
def deleteContact():
    contact_id = request.args.get("contact_id")
    response, status_code = deleteContactFromDB(contact_id)
    return jsonify(response), status_code


@app.route("/login", methods=["POST", "OPTIONS"])
def loginFunction():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.json
    email = data.get("email")
    password = data.get("password")
    response, status_code = loginProcess(email, password)
    return jsonify(response), status_code


@app.route("/verifyjwt")
def verify():
    token = request.args.get("token")
    response, status_code = verifyJsonWebToken(token)
    return jsonify(response), status_code


@app.route("/api/startCampaignCalls", methods=["POST"])
def start_campaign_calls():
    try:
        print("here")
        data = request.json
        campaign_id = data.get("campaign_id")
        user_id = data.get("user_id")
        caller = CampaignCaller()
        asyncio.run(caller.start_campaign(campaign_id=campaign_id, user_id=user_id))

        return (
            jsonify({"message": "Campaign calls started", "campaign_id": campaign_id}),
            200,
        )

    except Exception as e:
        print(f"Error starting campaign calls: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stopCampaignCalls", methods=["POST"])
def stop_campaign_calls():
    try:
        data = request.json
        campaign_id = data.get("campaign_id")

        if not campaign_id:
            return jsonify({"error": "Campaign ID required"}), 400

        caller = CampaignCaller()
        caller.stop_campaign(campaign_id)

        return jsonify({"message": "Campaign calls stopped"}), 200

    except Exception as e:
        print(f"Error stopping campaign calls: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaigns/<campaign_id>/update", methods=["PATCH", "OPTIONS"])
def update_campaign(campaign_id):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.json
        print(f"Received update data: {data}")  # Add logging
        response, status_code = updateCampaign(campaign_id, data)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error in update route: {str(e)}")  # Add logging
        return jsonify({"error": str(e)}), 500


@app.route("/api/campaigns/<campaign_id>", methods=["DELETE", "OPTIONS"])
def delete_campaign(campaign_id):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        response, status_code = deleteCampaign(campaign_id)
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error deleting campaign: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/editContact", methods=["PUT"])
def editContact():
    data = request.json
    contact_id = data.get("id")
    response, status_code = updateContactInDB(contact_id, data)
    return jsonify(response), status_code


@app.route("/api/getCampaignStats")
def get_campaign_stats():
    campaign_id = request.args.get("campaign_id")
    response, status_code = get_campaign_cost(campaign_id)
    return jsonify(response), status_code


@app.route("/api/getCampaignLogs", methods=["GET"])
def get_campaign_logs():
    try:
        campaign_id = request.args.get("campaign_id")
        if not campaign_id:
            return jsonify({"error": "Campaign ID required"}), 400

        caller = CampaignCaller()
        logs = caller.get_campaign_logs(campaign_id)

        sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)

        return (
            jsonify(
                {"message": "Campaign logs retrieved successfully", "logs": sorted_logs}
            ),
            200,
        )

    except Exception as e:
        print(f"Error fetching campaign logs: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/getAnalytics", methods=["GET"])
def getAnalytics():
    campaign_id = request.args.get("campaign_id")
    response, status_code = createAnalyticsData(campaign_id)
    return jsonify({"data": response}), status_code


@app.route("/api/getHotLeads")
def getHotLeads():
    campaign_id = request.args.get("campaign_id")
    response, status_code = get_hot_leads(campaign_id)
    return jsonify(response), status_code


@app.route("/api/getProperties", methods=["GET"])
def get_properties():
    try:
        response, status_code = getProperties()
        return jsonify(response), status_code
    except Exception as e:
        print(f"Error fetching properties: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/singleCall", methods=["POST"])
def singleCall():
    user_id = request.json.get("user_id")
    campaign_contact_id = request.json.get("campaign_contact_id")
    user_settings = getUserSettings(user_id)[0]
    print(user_settings)
    phone_number = get_active_phone_number(user_id)[0]["data"][0]
    print(phone_number)
    contact_obj = getCampaignContactContents(campaign_contact_id)[0]["data"][0]
    print(contact_obj)
    campaign_obj = {
        "phone_number_id": phone_number["phone_number_id"],
        "vapi_key": user_settings["vapi_api_key"],
        "assistant_id": user_settings["assistant_id"],
        "active": True,
    }
    caller = CampaignCaller()
    asyncio.run(caller.make_call(contact_obj, campaign_obj, user_id))
    return "done"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
