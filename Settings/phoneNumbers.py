from Supabase.utils import addPhoneNum, delPhoneNum, getPhoneNums, changePhoneStatus


def addPhoneNumber(data):
    data["status"] = "ACTIVE"
    print(data)
    return addPhoneNum(data)


def delPhoneNumber(id):
    return delPhoneNum(id)


def getUsersNumbers(userID):
    return getPhoneNums(userID)


def editPhoneNumStatus(id, status):
    return changePhoneStatus(id, status)
