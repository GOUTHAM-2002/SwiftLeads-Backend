import os, json
from Supabase.utils import register, createInitialUserSettings


def registerProcess(email, password):
    register_response = register(email, password)
    print(register_response)
    if register_response[1] == 200:
        user_id = register_response[0]["user"].id
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        with open(config_path, "r") as file:
            data = json.load(file)["settings_default"]
        data["id"] = user_id
        return createInitialUserSettings(data)
    else:
        return register_response
