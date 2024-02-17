import requests

def assert_scope_existence(base_url, access_token, scope_name):
    response = requests.request(
        "POST",
        base_url + "api/2.0/secrets/scopes/create",
        headers = {
            "Accept": "application/json,text/javascript,*/*",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        },
        params={
            "scope":scope_name
        }
    )
    
    return response.status_code==200 or "RESOURCE_ALREADY_EXISTS" in str(response.content)

def add_secret(base_url, access_token, scope_name, secret_key, secret_value):
    response = requests.request(
        "POST",
        base_url + "api/2.0/secrets/put",
        headers = {
            "Accept": "application/json,text/javascript,*/*",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        },
        params={
            "scope":scope_name,
            "key": secret_key,
            "string_value": secret_value
        }
    )
    
    return response.status_code==200    