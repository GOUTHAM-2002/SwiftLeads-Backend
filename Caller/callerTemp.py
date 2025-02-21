# from Supabase.utils import (
#     get_campaign_details,
#     get_pending_contacts_of_campaign,
#     get_active_phone_number,
# )

# from pyRedis import RedisServiceSingleton

# # from pyCelery import CelerySingleton


# # from Caller.threadedCallManager import ThreadedCaller

# redis = RedisServiceSingleton.get_instance()
# # celery = CelerySingleton._instance


# def onStartCampaign(campaign_id):
#     campaignContactList = get_pending_contacts_of_campaign(campaign_id)[0]["data"]
#     campaignDetails = get_campaign_details(campaign_id)[0]["data"]
#     user_id = campaignDetails["user_id"]
#     phone_numbers_of_user = get_active_phone_number(user_id)[0]["data"]
#     redis.store_user_phone_numbers(user_id, phone_numbers_of_user)
#     if redis.add_to_active_campaigns(campaignDetails):
#         redis.add_to_campaign_contacts(campaignContactList)
#     # ThreadedCaller.start_processing()


# def onStopCampaign(campaign_id):
#     redis.delete_active_campaign(campaign_id)
