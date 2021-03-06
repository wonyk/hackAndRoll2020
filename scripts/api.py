import requests
import os
import logging

# Create a request session for every user
s = requests.Session()
_creatorID = os.getenv("HABITICA_API_USER") + "-RabbitHabitica"


# Preset-headers if env is DEV.
if os.getenv("ENV") == "DEVELOPMENT":
    _uid = os.getenv("HABITICA_API_USER")
    _key = os.getenv("HABITICA_API_KEY")
    s.headers.update(
        {"x-api-user": _uid, "x-api-key": _key, "x-client": _creatorID,}
    )


def _url(path):
    return "https://habitica.com/api/v3" + path


# Start.py
def login(name, pw):
    auth = {"username": name, "password": pw}
    try:
        r = s.post(_url("/user/auth/local/login"), data=auth)
        jsonData = r.json()
        if jsonData["success"] == True:
            s.headers.update(
                {
                    "x-api-user": jsonData["data"]["id"],
                    "x-api-key": jsonData["data"]["apiToken"],
                    "x-client": _creatorID,
                }
            )
        return jsonData
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


# Stats.py
def get_stats():
    try:
        r = s.get("https://habitica.com/export/userdata.json")
        r.raise_for_status()
        res = r.json()["stats"]
        return res
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


# Create.py
def create_task(text, type, description, *args):
    # *args - (optional) Only for Habits which positive or negative is required
    createBody = {"text": text, "type": type, "notes": description, "value": 10}
    # up means positive, thus down is False and vice versa
    if "up" in args:
        createBody["down"] = "false"
    elif "down" in args:
        createBody["up"] = "true"
    try:
        r = s.post(_url("/tasks/user"), data=createBody)
        r.raise_for_status()
        res = r.json()
        return res
    except requests.exceptions.HTTPError:
        logging.error("not authorised")
        return {"success": False}
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


# View.py / Create.py (after creation)
def get_tasks(task_type):
    try:
        r = s.get(_url("/tasks/user"), params={"type": task_type})
        r.raise_for_status()
        res = r.json()
        # Create an array for the tasks as well as a usable keyboard
        if task_type == "habits":
            data = [
                {
                    "text": i["text"],
                    "_id": i["_id"],
                    "notes": i["notes"],
                    "value": i["value"],
                    "up": i["up"],
                    "down": i["down"],
                    "counterUp": i["counterUp"],
                    "counterDown": i["counterDown"],
                }
                for i in res["data"]
            ]
        else:
            data = [
                {
                    "text": i["text"],
                    "_id": i["_id"],
                    "notes": i["notes"],
                    "value": i["value"],
                }
                for i in res["data"]
            ]
        keyboard = []
        for i, task in enumerate(res["data"]):
            # Every string will look like this:
            # 1: Clean the washroom
            text = [str(i + 1) + ": " + task["text"]]
            keyboard.append(text)
        return {"success": True, "data": data, "keyboard": keyboard}
    except requests.exceptions.HTTPError:
        logging.error("not authorised")
        return {"success": False}
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


def mark_task_done(task_id, direction):
    try:
        r = s.post(_url("/tasks/" + task_id + "/score/" + direction))
        r.raise_for_status()
        res = r.json()
        data = res["data"]
        return {
            "success": True,
            "hp": data["hp"],
            "mp": data["mp"],
            "exp": data["exp"],
            "gp": data["gp"],
            "lvl": data["lvl"],
        }
    except requests.exceptions.HTTPError:
        logging.error("not authorised")
        err = r.json()
        if err["message"] == "Not Enough Gold":
            return {
                "success": False,
                "message": "Not enough gold to claim this reward\nUse /stats to check your data!",
            }
        return {"success": False, "message": "Please *login* using /start to continue."}
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


def delete_task(task_id):
    try:
        r = s.delete(_url("/tasks/" + task_id))
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        logging.error("not authorised")
        return False
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False


# alltasks.py
def getAll():
    try:
        data = {"habit": [], "reward": [], "todo": [], "daily": []}
        r = s.get(_url("/tasks/user"))
        r.raise_for_status()
        res = r.json()["data"]
        for task in res:
            data[task["type"]].append({"_id": task["_id"], "text": task["text"]})
        return {"success": True, "data": data}
    except requests.exceptions.HTTPError:
        logging.error("not authorised")
        return {"success": False}
    except requests.exceptions.RequestException as e:
        logging.warning(e)
        return False
