import os
import requests
from datetime import datetime, time
import pytz
import asyncio
import json
import random
from Supabase.utils import (
    get_pending_contacts_of_campaign,
    update_contact_status,
    get_active_campaigns,
    update_campaign_info,
    get_user_settings,
    get_active_phone_number,
)

from CRM.campaigns import editCampaign, get_campaign_cost, update_campaign_cost

from Settings.settings import getUserSettings

from Caller.mailer import send_email


class CampaignCaller:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CampaignCaller, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Prevent re-initialization
            self.running_campaigns = []
            self.active_campaigns = {}
            self.logs = {}  # Store logs in memory, organized by campaign_id
            self.initialized = True  # Mark as initialized

    async def start_campaign(self, user_id, campaign_id):
        try:
            if campaign_id in self.running_campaigns:
                return False
            self.running_campaigns.append(campaign_id)
            user_settings_response = get_user_settings(user_id)
            user_settings = user_settings_response[0]["data"]

            phone_response = get_active_phone_number(user_id)
            print(phone_response)
            active_phone = phone_response[0]["data"][0]
            print(1)
            if not active_phone:
                raise Exception("No active phone number found")

            self.active_campaigns[campaign_id] = {
                "phone_number_id": active_phone["phone_number_id"],
                "vapi_key": user_settings["vapi_api_key"],
                "assistant_id": user_settings["assistant_id"],
                "active": True,
            }

            await self.run_campaign(campaign_id, user_id)

        except Exception as e:
            print(f"Campaign {campaign_id} error: {str(e)}")
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id]["active"] = False
            raise e

    def stop_campaign(self, campaign_id):
        """Stop a running campaign"""
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id]["active"] = False
            self.running_campaigns.remove(campaign_id)

    async def run_campaign(self, campaign_id, user_id):
        """Run the campaign and process calls synchronously"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return

        if campaign["active"]:
            try:
                # Get pending contacts
                print(2)
                contacts_response = get_pending_contacts_of_campaign(campaign_id)
                print(contacts_response)
                contacts = contacts_response[0]["data"]
                print(2)
                if not contacts:
                    print(f"No pending calls for campaign {campaign_id}")
                    self.stop_campaign(campaign_id)

                # Process each contact
                for contact in contacts:
                    if campaign_id not in self.running_campaigns:
                        return

                    if not campaign["active"]:
                        print(f"Campaign {campaign_id} stopped")
                        return

                    success = await self.make_call(contact, campaign, user_id)
                    status = "completed" if success else "failed"
                    update_contact_status(contact["id"], status)
                    await asyncio.sleep(2)

            except Exception as e:
                print(f"Error in campaign {campaign_id}: {str(e)}")
                await asyncio.sleep(5)

    async def log_call_event(self, campaign_id, message, phone_number=None):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

        if phone_number:
            message = f"Call {message} for {phone_number}"

        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "campaign_id": campaign_id,
        }

        # Initialize list for campaign if it doesn't exist
        if campaign_id not in self.logs:
            self.logs[campaign_id] = []

        # Add log entry
        self.logs[campaign_id].append(log_entry)
        print(self.logs[campaign_id])

    def get_campaign_logs(self, campaign_id):
        """Fetch all logs for a specific campaign"""
        try:
            logs = self.logs.pop(campaign_id, [])
            sorted_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
            return sorted_logs
        except Exception as e:
            print(f"Error fetching campaign logs: {str(e)}")
            return []

    async def make_call(self, contact, campaign, user_id):
        print("Contact - ", contact)
        print(
            "----------------------------------------------------------------------------"
        )
        print("Campaign - ", campaign)
        print(
            "-----------------------------------------------------------------------------"
        )
        print("user_id - ", user_id)
        print(
            "------------------------------------------------------------------------------"
        )
        try:
            # Log call initiation
            await self.log_call_event(
                contact["campaign_id"], "initiated", contact["phone"]
            )
            headers = {
                "Authorization": f"Bearer {campaign['vapi_key']}",
                "Content-Type": "application/json",
            }

            phone_number = contact["phone"].strip()
            if not phone_number.startswith("+"):
                phone_number = f"+{phone_number}"

            settings = getUserSettings(user_id)[0]
            print(3)

            payload = {
                "phoneNumberId": campaign["phone_number_id"],
                "assistantId": campaign["assistant_id"],
                "customer": {"number": phone_number},
                "assistantOverrides": {
                    "firstMessageMode": "assistant-speaks-first",
                    "firstMessage": settings.get("first_message") + contact["address"],
                    "model": {
                        "provider": settings.get("provider", "openai"),
                        "model": settings.get("model", "gpt-4"),
                        "messages": [
                            {
                                "content": settings.get("system_prompt", ""),
                                "role": "system",
                            }
                        ],
                        "tools": [{"type": "voicemail"}],
                    },
                    "voice": {
                        "voiceId": settings.get("voice_id", "aTxZrSrp47xsP6Ot4Kgd"),
                        "provider": settings.get("voice_provider", "11labs"),
                        "stability": float(settings.get("stability", 0.5)),
                        "similarityBoost": float(
                            settings.get("similarity_boost", 0.75)
                        ),
                        "fillerInjectionEnabled": bool(
                            settings.get("voice_filler_injection_enabled", False)
                        ),
                    },
                    "endCallFunctionEnabled": True,
                    "endCallMessage": "Goodbye, have a nice day!",
                    "transcriber": {
                        "model": "nova-2-phonecall",
                        "language": "en",
                        "provider": "deepgram",
                    },
                    "clientMessages": ["hang", "tool-calls", "tool-calls-result"],
                    "serverMessages": [
                        "end-of-call-report",
                        "hang",
                        "tool-calls",
                        "phone-call-control",
                    ],
                    "endCallPhrases": [
                        "Bye",
                        "quality and training purposes",
                        "recorded for quality",
                        "monitored for quality",
                        "quality assurance",
                        "leave a message",
                        "not available",
                        "after the tone",
                        "please record",
                        "Google Voice",
                        "at the tone",
                        "is not available to take your call",
                        "is unavailable",
                        "cannot take your call",
                        "record your message",
                        "leave your message",
                        "voicemail box",
                        "mailbox",
                    ],
                    "backgroundSound": "office",
                    "backchannelingEnabled": bool(
                        settings.get("backchanneling_enabled", False)
                    ),
                    "backgroundDenoisingEnabled": bool(
                        settings.get("background_denoising_enabled", True)
                    ),
                    "messagePlan": {
                        "idleMessages": [
                            "Feel free to ask me any questions.",
                            "I'm here to help if you need anything.",
                            "Let me know if you have any questions.",
                            "Is there anything specific you'd like to know?",
                            "I'm listening if you'd like to continue.",
                        ],
                        "idleTimeoutSeconds": 7.0,
                        "idleMessageMaxSpokenCount": 3,
                    },
                    "voicemailDetection": {
                        "provider": "twilio",
                        "voicemailDetectionTypes": [
                            "machine_start",
                            "machine_end_silence",
                            "machine_end_other",
                        ],
                        "enabled": True,
                        "machineDetectionTimeout": 10,
                        "machineDetectionSpeechThreshold": 1000,
                        "machineDetectionSpeechEndThreshold": 500,
                        "machineDetectionSilenceTimeout": 2000,
                    },
                    "voicemailMessage": "",
                    "artifactPlan": {
                        "recordingEnabled": True,
                        "videoRecordingEnabled": False,
                        "transcriptPlan": {"enabled": True},
                    },
                    "startSpeakingPlan": {
                        "waitSeconds": 3,
                        "smartEndpointingEnabled": True,
                        "transcriptionEndpointingPlan": {
                            "onPunctuationSeconds": 2,
                            "onNoPunctuationSeconds": 2,
                            "onNumberSeconds": 2,
                        },
                    },
                    "stopSpeakingPlan": {
                        "numWords": 3,
                        "voiceSeconds": 0.5,
                        "backoffSeconds": 5,
                    },
                    "monitorPlan": {"listenEnabled": True, "controlEnabled": False},
                    "analysisPlan": {
                        "successEvaluationRubric": "PassFail",
                        "successEvaluationPrompt": "You are given a transcript of a call between a customer and a AI. You need to evaluate the call and determine if the customer was happy or ready to buy and seem interested from the call . If the Ai passed the call, return true. If the AI failed the call, return false. remember to not return any false positives.",
                    },
                },
            }

            response = requests.post(
                "https://api.vapi.ai/call/phone", headers=headers, json=payload
            )

            if response.status_code == 201:
                call_details = response.json()
                call_id = call_details.get("id")

                while True:
                    await asyncio.sleep(random.uniform(20, 40))
                    call_response = requests.get(
                        f"https://api.vapi.ai/call/{call_id}", headers=headers
                    )

                    if call_response.status_code == 200:
                        call_info = call_response.json()
                        if call_info.get("status") == "ended":
                            print(
                                "-------------------------------------------------------------------------------------------------------"
                            )
                            await self.log_call_event(
                                contact["campaign_id"], "completed", contact["phone"]
                            )
                            campaign_cost = self.calculate_campaign_cost(call_info)
                            updated_campaign_obj = process_campaign_costs(
                                campaign_cost, contact["campaign_id"]
                            )
                            if campaign_cost:
                                cost_result = update_campaign_cost(
                                    contact["campaign_id"], updated_campaign_obj
                                )
                                print(
                                    "-------------------------------------------------------------------------------------------------------"
                                )
                                print(f"Cost update result: {cost_result}")

                                if cost_result[1] != 200:
                                    print(
                                        f"Failed to update campaign cost: {cost_result[0]}"
                                    )

                            new_campaign = self.map_call_info_to_campaign_info(
                                call_info
                            )
                            new_campaign["campaign_id"] = contact["campaign_id"]
                            success_evaluation = str(
                                call_info.get("analysis", {}).get("successEvaluation")
                            ).lower()
                            if success_evaluation == "true":
                                new_campaign["hot_lead"] = True
                                send_email(str(phone_number) + str(new_campaign))
                            else:
                                new_campaign["hot_lead"] = False
                            print(new_campaign)
                            update_campaign_info(contact["id"], new_campaign)
                            break
                        else:
                            continue

                return True
            return False

        except Exception as e:
            await self.log_call_event(
                contact["campaign_id"], f"failed: {str(e)}", contact["phone"]
            )
            return False

    async def get_active_campaigns(self):
        """Fetch active campaigns within call window"""
        try:
            response = get_active_campaigns()
            campaigns = response[0]["data"]
            active_campaigns = []

            now = datetime.now(pytz.UTC)
            current_time = now.time()

            for campaign in campaigns:
                start_time = time.fromisoformat(str(campaign["call_window_start"]))
                end_time = time.fromisoformat(str(campaign["call_window_end"]))

                if start_time <= current_time <= end_time:
                    active_campaigns.append(campaign["id"])

            return active_campaigns

        except Exception as e:
            print(f"Error getting active campaigns: {str(e)}")
            return []

    def map_call_info_to_campaign_info(self, call_info):

        campaign_info = {
            "email": "",
            "company": "",
            "business_name": "",
            "title": "",
            "website": "",
            "linkedin": "",
            "source": "",
            "timezone": "",
            "address": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "country": "",
            "pipeline_stage": "",
            "status": "",
            "notes": "",
            "last_called": None,
            "total_calls": 0,
            "successful_calls": 0,
            "total_call_duration": 0,
            "voicemail_count": 0,
            "last_voicemail_date": None,
            "total_voicemail_duration": 0,
            "call_summary": "",
            "call_transcript": "",
            "success_evaluation": "",
            "end_reason": "",
            "recording_urls": [],
            "duration_seconds": 0,
            "total_cost": 0,
            "speech_to_text_cost": 0,
            "llm_cost": 0,
            "text_to_speech_cost": 0,
            "vapi_cost": 0,
            "hot_lead": False,
        }

        # Map available call information
        if call_info:
            # Status and Call Details
            campaign_info["status"] = call_info.get("status", "")
            if campaign_info["status"] == "ended":
                campaign_info["status"] = "completed"
            campaign_info["end_reason"] = call_info.get("endedReason", "")

            # Timestamps
            campaign_info["last_called"] = (
                call_info.get("endedAt")
                or call_info.get("startedAt")
                or datetime.now().isoformat()
            )

            # Call Tracking
            campaign_info["total_calls"] = 1
            campaign_info["successful_calls"] = (
                1 if call_info.get("status") == "ended" else 0
            )

            # Duration
            campaign_info["duration_seconds"] = int(call_info.get("duration", 0))
            campaign_info["total_call_duration"] = int(call_info.get("duration", 0))

            # Transcripts and Summaries
            campaign_info["call_transcript"] = call_info.get("transcript", "")
            campaign_info["call_summary"] = call_info.get("summary", "")

            # Recording URLs
            recording_urls = []
            if call_info.get("recordingUrl"):
                recording_urls.append(call_info["recordingUrl"])
            if call_info.get("stereoRecordingUrl"):
                recording_urls.append(call_info["stereoRecordingUrl"])
            campaign_info["recording_urls"] = recording_urls

            # Cost Tracking
            campaign_info["total_cost"] = float(call_info.get("cost", 0))

            # Detailed Cost Breakdown
            if call_info.get("costs"):
                for cost_item in call_info["costs"]:
                    if cost_item.get("type") == "transcriber":
                        campaign_info["speech_to_text_cost"] = float(
                            cost_item.get("cost", 0)
                        )
                    elif cost_item.get("type") == "model":
                        campaign_info["llm_cost"] = float(cost_item.get("cost", 0))
                    elif cost_item.get("type") == "voice":
                        campaign_info["text_to_speech_cost"] = float(
                            cost_item.get("cost", 0)
                        )
                    elif cost_item.get("type") == "vapi":
                        campaign_info["vapi_cost"] = float(cost_item.get("cost", 0))

        return campaign_info

    def calculate_campaign_cost(self, call_info):
        """Calculate campaign cost based on call information"""
        try:
            base_cost = float(call_info.get("cost", 0))
            created_at = datetime.fromisoformat(
                call_info["createdAt"].replace("Z", "+00:00")
            )
            updated_at = datetime.fromisoformat(
                call_info["updatedAt"].replace("Z", "+00:00")
            )
            duration = updated_at - created_at
            total_duration_seconds = duration.total_seconds()
            total_duration_seconds = int(duration.total_seconds())
            hot_lead = 0
            success_evaluation = str(
                call_info.get("analysis", {}).get("successEvaluation")
            ).lower()
            if success_evaluation == "true" or success_evaluation == "pass":
                hot_lead = True
            else:
                hot_lead = False

            # Initialize cost breakdown
            campaign_cost = {
                "total_cost": base_cost,
                "total_duration": total_duration_seconds,
                "total_calls": 1,
                "voicemail_count": (
                    1 if call_info.get("endedReason") == "voicemail" else 0
                ),
                "hot_lead": hot_lead,  # Default value
                "last_updated": datetime.now(pytz.UTC).isoformat(),
            }

            print(f"Calculated campaign cost object: {campaign_cost}")  # Debug log
            return campaign_cost

        except Exception as e:
            print(f"Error calculating campaign cost: {str(e)}")
            return None


def process_campaign_costs(campaign_info, campaign_id):
    try:

        # Fetch existing campaign costs
        existing_costs = get_campaign_cost(campaign_id)
        existing_costs = existing_costs[0]["data"]

        if not existing_costs:
            # If no existing costs, create a new cost entry
            existing_costs = {
                "campaign_id": campaign_id,
                "total_calls": 0,
                "voicemail_count": 0,
                "hot_leads": 0,
                "total_duration": "00:00:00",
                "total_cost": 0,
                "avg_cost_per_call": 0,
            }
        print("Existing costs are - ", existing_costs)
        # Convert existing total duration to seconds
        existing_duration_seconds = convert_duration_to_seconds(
            existing_costs.get("total_duration", "00:00:00")
        )

        # Update campaign costs
        updated_costs = {
            "campaign_id": campaign_id,
            "total_calls": existing_costs.get("total_calls", 0) + 1,
            "voicemail_count": (
                existing_costs.get("voicemail_count", 0)
                + (1 if campaign_info.get("voicemail_count", 0) > 0 else 0)
            ),
            "hot_leads": (existing_costs.get("hot_leads", 0))
            + (1 if campaign_info["hot_lead"] is True else 0),
            "total_duration": format_seconds_to_duration(
                existing_duration_seconds + campaign_info.get("total_duration", 0)
            ),
            "total_cost": (
                existing_costs.get("total_cost", 0) + campaign_info.get("total_cost", 0)
            ),
            "avg_cost_per_call": calculate_avg_cost_per_call(
                existing_costs.get("total_calls", 0) + 1,
                existing_costs.get("total_cost", 0)
                + campaign_info.get("total_cost", 0),
            ),
        }
        print("Updated costs are - ", updated_costs)
        return updated_costs

    except KeyError as e:
        print(f"Key error: {e}")
        return None
    except ValueError as e:
        print(f"Value error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def convert_duration_to_seconds(duration_str):
    """Convert HH:MM:SS format to total seconds."""
    hours, minutes, seconds = map(int, duration_str.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def format_seconds_to_duration(total_seconds):
    """Convert total seconds to HH:MM:SS format."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def calculate_avg_cost_per_call(total_calls, total_cost):

    return total_cost / total_calls if total_calls > 0 else 0


def calculate_total_duration(existing_duration, new_seconds):
    duration_parts = existing_duration.split(":")
    existing_seconds = (
        int(duration_parts[0]) * 3600
        + int(duration_parts[1]) * 60
        + int(duration_parts[2])
    )

    # Add new seconds
    total_seconds = existing_seconds + new_seconds

    # Convert back to HH:MM:SS
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# Usage
if __name__ == "__main__":
    caller = CampaignCaller()
    asyncio.run(caller.run())
