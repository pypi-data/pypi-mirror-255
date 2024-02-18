import useragent_api

def get_database():
    try:
        useragent_api.fetch_useragents()
    except:
        pass
    return "A database of browser fingerprints."