from Supabase.utils import (
    get_campaign_cost,
    getCampaignContactContents,
    get_campaign_hot_leads,
)


def createAnalyticsData(campaign_id):
    campaign_contents = getCampaignContactContents(campaign_id)[0]["data"]
    campaign_metrics = get_campaign_cost(campaign_id)[0]["data"]

    analytics_data = {
        "total_calls": campaign_metrics["total_calls"],
        "total_duration": int(
            convert_duration_to_minutes(campaign_metrics["total_duration"])
        ),
        "total_cost": campaign_metrics["total_cost"],
        "hot_leads": campaign_metrics["hot_leads"],
        "end_reason_counts": {},
    }

    for entry in campaign_contents:
        end_reason = entry["end_reason"]

        if end_reason not in analytics_data["end_reason_counts"]:
            analytics_data["end_reason_counts"][end_reason] = 0

        analytics_data["end_reason_counts"][end_reason] += 1

    return analytics_data, 200


def get_hot_leads(campaign_id):
    return get_campaign_hot_leads(campaign_id)


def convert_duration_to_minutes(duration):
    if duration:
        hours, minutes, seconds = map(int, duration.split(":"))
        total_minutes = hours * 60 + minutes + seconds / 60
        return total_minutes
    return 0
