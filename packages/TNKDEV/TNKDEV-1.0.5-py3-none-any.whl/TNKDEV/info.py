from datetime import datetime
def __github__():
    return "https://github.com/TNK-ADMIN"

def __facebook__():
    return "https://facebook.com/100009412734381"

def __telegram__():
    return "https://t.me/tnkdev"

def __TG__():
    return "https://t.me/tnk_k07vn"

def __zalo__():
    return "https://zalo.me/0964243159"


def calculate_age(birthdate):
    birthdate = datetime.strptime(birthdate, "%d/%m/%Y")
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def __day__():
    return "03"

def __month__():
    return "09"

def __year__():
    return "2007"

def __age__():
    birthdate = f"{__day__()}/{__month__()}/{__year__()}"
    return str(calculate_age(birthdate))

