import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import pytz

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


def updateContactInDB(contact_id, data):
    try:
        result = supabase.table("contacts").update(data).eq("id", contact_id).execute()
        if not result.data:
            return {"error": "Contact not found"}, 404
        return {"message": "Contact updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def deleteContactFromDB(contact_id):
    try:
        result = supabase.table("contacts").delete().eq("id", contact_id).execute()
        if not result.data:
            return {"error": "Contact not found"}, 404
        return {"message": "Contact deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def register(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user is None:
            if response.message:
                return ({"error": response.message}), 400
            else:
                return ({"error": "Registration failed. Please try again."}), 400

        return (
            ({"message": "User registered successfully!", "user": response.user}),
            200,
        )
    except Exception as e:
        return ({"error": str(e)}), 500


def createInitialUserSettings(data):
    try:
        supabase.table("settings").insert(data).execute()
        return (
            (
                {
                    "message": "User registered successfully and data inserted",
                    "data": data,
                }
            ),
            200,
        )
    except Exception as e:
        return ({"error": str(e)}), 500


def getUsersSettingsSupabase(userID):
    try:
        response = supabase.table("settings").select("*").eq("id", userID).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None
    except Exception as e:
        return ({"error": str(e)}), 500


def changeSettingsSupabase(userID, data):
    try:
        response = supabase.table("settings").update(data).eq("id", userID).execute()
        return (
            {"message": "user data updated succesfully", "data": response.data},
            200,
        )
    except Exception as e:
        return ({"error": str(e)}), 500


def addPhoneNum(data):
    try:
        response = supabase.table("phonenumbers").insert(data).execute()
        return {"data": response.data[0]}, 200
    except Exception as e:
        return ({"error": str(e)}), 500


def delPhoneNum(id):
    try:
        response = supabase.table("phonenumbers").delete().eq("id", id).execute()
        return {"data": response.data[0]}, 200
    except Exception as e:
        return ({"error": str(e)}), 500


def getPhoneNums(userID):
    try:
        response = (
            supabase.table("phonenumbers").select("*").eq("user_id", userID).execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}), 500


def changePhoneStatus(id, status):
    try:
        response = (
            supabase.table("phonenumbers")
            .update({"status": status})
            .eq("id", id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}), 500


def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if response.user is None:
            return ({"error": "Invalid credentials"}, 401)

        session_data = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_at": response.session.expires_at,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": response.user.created_at,
            },
        }

        return (
            {
                "message": "Login successful",
                "user": response.user.model_dump(),
                "session": session_data,
            },
            200,
        )
    except Exception as e:
        return ({"error": str(e)}, 500)


def createCampaignObj(campaignData):
    try:
        response = supabase.table("campaigns").insert(campaignData).execute()
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def addCampaignContactInfo(campaignInfoData):
    try:
        response = (
            supabase.table("campaign_contact_info").insert(campaignInfoData).execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def getCampaignsOfUser(user_id):
    try:
        response = (
            supabase.table("campaigns").select("*").eq("user_id", user_id).execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def getFullCampaignContactInfo(campaign_id):
    try:
        response = (
            supabase.table("campaign_contact_info")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def getCampaignContactContents(campaign_contact_id):
    try:
        response = (
            supabase.table("campaign_contact_info")
            .select("*")
            .eq("id", campaign_contact_id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def addContactsOfUser(contacts):
    try:
        response = supabase.table("contacts").insert(contacts).execute()
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def getContactsOfUser(user_id):
    try:
        response = (
            supabase.table("contacts").select("*").eq("user_id", user_id).execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return ({"error": str(e)}, 500)


def updateCampaign(campaign_id, data):
    try:

        # Update campaign with the new data
        result = (
            supabase.table("campaigns")
            .update(
                {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "call_window_start": data.get("call_window_start"),
                    "call_window_end": data.get("call_window_end"),
                }
            )
            .eq("id", campaign_id)
            .execute()
        )

        if not result.data:
            print("No data returned from update")  # Debug log
            return {"error": "Campaign not found"}, 404

        print("Update successful:", result.data)  # Debug log
        return {"data": result.data[0]}, 200

    except Exception as e:
        print(f"Error in updateCampaign: {str(e)}")  # Debug log
        return {"error": str(e)}, 500


def deleteCampaign(campaign_id):
    try:
        result = supabase.table("campaigns").delete().eq("id", campaign_id).execute()

        if not result.data:
            return {"error": "Campaign not found"}, 404

        return {"message": "Campaign deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def update_campaign_contact(contact_id, new_campaign_contact):
    """Update contact status in database"""
    try:
        response = (
            supabase.table("campaign_contact_info")
            .update(new_campaign_contact)
            .eq("id", contact_id)
            .execute()
        )
        return {"data": response.data[0]}, 200
    except Exception as e:
        print(f"Error updating contact status: {str(e)}")
        return {"error": str(e)}, 500


def create_campaign_metrics_obj(campaign_metrics_obj):
    try:
        response = (
            supabase.table("campaign_metrics").insert(campaign_metrics_obj).execute()
        )
        return {"data": response.data[0]}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def fetch_campaign_metrics_obj(campaign_id):
    try:
        response = (
            supabase.table("campaign_metrics")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )

        if response.data:
            return {"data": response.data[0]}, 200  # Return the first matching record
        else:
            return {"message": "No campaign cost found for the given campaign_id."}, 404
    except Exception as e:
        return {"error": str(e)}, 500


def get_pending_contacts_of_campaign(campaign_id):
    """Fetch pending calls for a campaign"""
    try:
        response = (
            supabase.table("campaign_contact_info")
            .select("*")
            .eq("campaign_id", campaign_id)
            .eq("status", "pending")
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def update_contact_status(contact_id, status):
    """Update contact status in campaign_contact_info"""
    try:
        response = (
            supabase.table("campaign_contact_info")
            .update({"status": status})
            .eq("id", contact_id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_active_campaigns():
    """Fetch active campaigns within call window"""
    try:
        response = supabase.table("campaigns").select("*").execute()
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def update_call_info(contact_id, call_info):
    """Update call information in campaign_contact_info"""
    try:
        response = (
            supabase.table("campaign_contact_info")
            .update(call_info)
            .eq("id", contact_id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_campaign_details(campaign_id):
    try:
        response = (
            supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
        )
        return {"data": response.data[0] if response.data else None}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def update_campaign_metrics_obj(campaign_id, updated_cost_obj):
    try:
        response = (
            supabase.table("campaign_metrics")
            .update(updated_cost_obj)
            .eq("campaign_id", campaign_id)
            .execute()
        )
        return {"data": response.data[0]}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_campaign_cost(campaign_id):
    """Get campaign cost information"""
    try:
        response = (
            supabase.table("campaign_metrics")
            .select("*")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        return {"data": response.data[0]}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def update_campaign_info(contact_id, campaign_contact_info):
    try:
        response = (
            supabase.table("campaign_contact_info")
            .update(campaign_contact_info)
            .eq("id", contact_id)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_user_settings(user_id):
    """Get user settings including API keys"""
    try:
        response = supabase.table("settings").select("*").eq("id", user_id).execute()
        return {"data": response.data[0] if response.data else None}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_active_phone_number(user_id):
    """Get active phone number for user"""
    try:
        response = (
            supabase.table("phonenumbers")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "ACTIVE")
            .execute()
        )
        return {"data": response.data if response.data else None}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_campaign_hot_leads(campaign_id):
    try:
        response = (
            supabase.table("campaign_contact_info")
            .select("*")
            .eq("campaign_id", campaign_id)
            .eq("hot_lead", True)
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def getProperties():
    try:
        response = (
            supabase.table("properties")
            .select("*")
            .order("date", desc=True)  # Sort by date in descending order
            .execute()
        )
        return {"data": response.data}, 200
    except Exception as e:
        return {"error": str(e)}, 500
