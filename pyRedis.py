import redis
import os
import json
import logging
from redis.lock import Lock as RedisLock
from threading import Lock as ThreadLock
import random

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


class RedisServiceSingleton:
    _instance = None
    _init_lock = ThreadLock()
    _contact_operation_lock = ThreadLock()
    _phone_number_operation_lock = ThreadLock()

    def __new__(cls):
        if not cls._instance:
            with cls._init_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.host = os.getenv("REDIS_HOST", "localhost")
            self.port = int(os.getenv("REDIS_PORT", 6379))
            self.db = int(os.getenv("REDIS_DB", 0))

            self.client = redis.Redis(
                host=self.host, port=self.port, db=self.db, decode_responses=True
            )

            self.client.ping()
            logger.info(
                f"Redis connection established: {self.host}:{self.port}/{self.db}"
            )

        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise ConnectionError(f"Could not connect to Redis: {e}")

    @classmethod
    def get_instance(cls):
        return cls()

    @staticmethod
    def set_json(key, value, expiry=None):
        try:
            serialized_value = json.dumps(value)
            redis_client.set(key, serialized_value)

            if expiry:
                redis_client.expire(key, expiry)

            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    @staticmethod
    def get_json(key):
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    @staticmethod
    def delete(key):
        try:
            redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")

    @staticmethod
    def add_to_campaign_contacts(contacts_info):
        with RedisServiceSingleton._contact_operation_lock:
            try:
                key = "global_campaign_contact_info"

                if not isinstance(contacts_info, list):
                    contacts_info = [contacts_info]

                serialized_contacts = [json.dumps(contact) for contact in contacts_info]

                if serialized_contacts:
                    redis_client.rpush(key, *serialized_contacts)

                return True
            except Exception as e:
                logger.error(f"Error adding contacts to global campaign contacts: {e}")
                return False

    @staticmethod
    def fetch_random_campaign_contact():
        with RedisServiceSingleton._contact_operation_lock:
            try:
                key = "global_campaign_contact_info"

                list_length = redis_client.llen(key)
                if list_length == 0:
                    logger.info(
                        "No contacts available in the global campaign contacts list"
                    )
                    return None

                random_index = random.randint(0, list_length - 1)

                contact_json = redis_client.lindex(key, random_index)

                if not contact_json:
                    logger.error("Failed to retrieve contact at random index")
                    return None

                contact = json.loads(contact_json)

                redis_client.lrem(key, 1, contact_json)

                return contact

            except Exception as e:
                logger.error(f"Error fetching random campaign contact: {e}")
                return None

    @staticmethod
    def add_to_active_campaigns(campaign_data):
        with RedisServiceSingleton._contact_operation_lock:
            try:
                key = "active_campaigns"

                campaign_id = campaign_data["user_id"]

                serialized_campaign = json.dumps(campaign_data)

                if not redis_client.sismember(key, campaign_id):
                    redis_client.sadd(key, campaign_id)
                    redis_client.hset(
                        f"{key}_details", campaign_id, serialized_campaign
                    )

                    logger.info(f"Campaign {campaign_id} added to active campaigns")
                    return True
                else:
                    logger.info(f"Campaign {campaign_id} already in active campaigns")
                    return False

            except Exception as e:
                logger.error(f"Error adding campaign to active campaigns: {e}")
                return False

    @staticmethod
    def get_active_campaign(campaign_id):
        try:
            key = "active_campaigns"

            if not redis_client.sismember(key, campaign_id):
                logger.info(f"Campaign {campaign_id} not found in active campaigns")
                return None

            serialized_campaign = redis_client.hget(f"{key}_details", campaign_id)

            if serialized_campaign:

                campaign_details = json.loads(
                    serialized_campaign.decode("utf-8")
                    if isinstance(serialized_campaign, bytes)
                    else serialized_campaign
                )
                return campaign_details

            logger.error(f"No details found for campaign {campaign_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving campaign details: {e}")
            return None

    @staticmethod
    def delete_active_campaign(campaign_id):
        with RedisServiceSingleton._contact_operation_lock:
            try:
                key = "active_campaigns"

                if not redis_client.sismember(key, campaign_id):
                    logger.info(f"Campaign {campaign_id} not found in active campaigns")
                    return False

                redis_client.srem(key, campaign_id)

                redis_client.hdel(f"{key}_details", campaign_id)

                logger.info(f"Campaign {campaign_id} deleted from active campaigns")
                return True

            except Exception as e:
                logger.error(f"Error deleting campaign from active campaigns: {e}")
                return False

    @staticmethod
    def store_user_phone_numbers(user_id, data):
        with RedisServiceSingleton._phone_number_operation_lock:
            try:

                key = f"phone_numbers:{user_id}"

                if not isinstance(data, list):
                    logger.error("Data must be a list of JSON objects")
                    return False

                serialized_data = json.dumps(data)

                redis_client.set(key, serialized_data)

                logger.info(f"Data stored for user {user_id}")
                return True

            except Exception as e:
                logger.error(f"Error storing data for user {user_id}: {e}")
                return False

    @staticmethod
    def get_user_phone_numbers(user_id):
        with RedisServiceSingleton._phone_number_operation_lock:
            try:
                key = f"phone_numbers:{user_id}"

                serialized_data = redis_client.get(key)

                if not serialized_data:
                    logger.info(f"No data found for user {user_id}")
                    return None

                data = json.loads(
                    serialized_data.decode("utf-8")
                    if isinstance(serialized_data, bytes)
                    else serialized_data
                )

                return data

            except Exception as e:
                logger.error(f"Error retrieving data for user {user_id}: {e}")
                return None

    @staticmethod
    def delete_user_phone_numbers(user_id):
        with RedisServiceSingleton._phone_number_operation_lock:
            try:
                key = f"phone_numbers:{user_id}"

                if not redis_client.exists(key):
                    logger.info(f"No data found for user {user_id}")
                    return False

                redis_client.delete(key)

                logger.info(f"Data deleted for user {user_id}")
                return True

            except Exception as e:
                logger.error(f"Error deleting data for user {user_id}: {e}")
                return False


def init_redis(app):
    redis_service = RedisServiceSingleton.get_instance()
    return redis_service
