from Supabase.utils import getUsersSettingsSupabase, changeSettingsSupabase


def getUserSettings(userID):
    settings = getUsersSettingsSupabase(userID)
    if settings is None:
        return {"message": "No settings found for userID {userID}"}, 204
    return settings, 200


def editUserSettings(userID, newData):
    try:
        print("EditUserSettings - UserID:", userID)
        print("EditUserSettings - NewData:", newData)
        
        validateData(newData)
        print("Data validation passed")
        
        result = changeSettingsSupabase(userID, newData)
        print("Supabase result:", result)
        
        return result
    except Exception as e:
        print("Error in editUserSettings:", str(e))
        import traceback
        print("Traceback:", traceback.format_exc())
        return {"error": str(e)}, 500


def validateData(new_data):
    allowed_fields = {
        "vapi_api_key": (str, type(None)),
        "assistant_id": (str, type(None)),
        "phone_number_id": (str, type(None)),
        "model": str,
        "provider": str,
        "first_message": str,
        "system_prompt": str,
        "voice_id": str,
        "voice_provider": str,
        "stability": (float, int),
        "similarity_boost": (float, int),
        "voice_filler_injection_enabled": bool,
        "backchanneling_enabled": bool,
        "background_denoising_enabled": bool,
        "phone_numbers": (type(None), list, str),
    }

    unexpected_fields = set(new_data.keys()) - set(allowed_fields.keys())
    if unexpected_fields:
        raise ValueError(
            f"Unexpected fields found: {unexpected_fields}. Allowed fields are: {list(allowed_fields.keys())}"
        )

    for field, expected_type in allowed_fields.items():
        if field in new_data:
            if not isinstance(new_data[field], expected_type):
                raise ValueError(
                    f"Invalid type for field '{field}'. Expected {expected_type}, got {type(new_data[field])}"
                )

    if "stability" in new_data and not (0 <= new_data["stability"] <= 1):
        raise ValueError("Stability must be between 0 and 1")

    if "similarity_boost" in new_data and not (0 <= new_data["similarity_boost"] <= 1):
        raise ValueError("Similarity boost must be between 0 and 1")

    return True
