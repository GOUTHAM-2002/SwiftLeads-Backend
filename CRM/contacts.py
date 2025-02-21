import json, os
from Supabase.utils import addContactsOfUser, getContactsOfUser


def addContacts(user_id, data):
    toAddContactList = []
    for contact in data:
        contact = dict(contact)
        contact["user_id"] = user_id
        verifiedContact = verifyContactInfo(contact)
        if verifiedContact is not None:
            toAddContactList.append(verifiedContact)
    return addContactsOfUser(toAddContactList)


def getUserContacts(user_id):
    return getContactsOfUser(user_id)


def verifyContactInfo(contactObj):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    with open(config_path, "r") as file:
        data = json.load(file)["contactDefault"]

    required_fields = ["user_id", "phone", "name"]

    for field in required_fields:
        if field not in contactObj or not contactObj[field]:
            return None

    verified_info = {}

    for field in required_fields:
        verified_info[field] = contactObj[field]

    for key, default_value in data.items():
        if key in contactObj:
            input_value = contactObj[key]

            if input_value not in [None, "", [], 0, False]:
                verified_info[key] = input_value
            else:
                verified_info[key] = default_value
        else:
            verified_info[key] = default_value

    return verified_info
