import tls_client, browser_db

browsers = browser_db.get_database()

def Session(browser="chrome120", random_tls_extension_order=True, header_order=None, cloudflare_uam=True):
    return tls_client.Session(
        client_identifier=browser,
        random_tls_extension_order=random_tls_extension_order,
        header_order=header_order)