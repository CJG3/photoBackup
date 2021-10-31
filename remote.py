from datetime import datetime
from communication import *


def unix_to_human_time(unixtime, fmt="%Y-%m-%d"):
    try:
        return datetime.utcfromtimestamp(int(unixtime)).strftime(fmt)
    except Exception as e:
        print(e)
        send_email(sender="geyer.house2018@gmail.com", to="charles.geyer1@gmail.com",
                   subject="[Urgent] Photo backup failed", message_text=str(e))
        return None
