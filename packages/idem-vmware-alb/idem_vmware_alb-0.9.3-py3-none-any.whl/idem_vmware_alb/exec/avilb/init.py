def __init__(hub):
    hub.exec.avilb.ENDPOINT_URLS = ["/api"]
    # The default is the first in the list
    hub.exec.avilb.DEFAULT_ENDPOINT_URL = "/api"

    # This enables acct profiles that begin with "avilb" for avilb modules
    hub.exec.avilb.ACCT = ["avilb"]
