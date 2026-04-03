from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

flow = InstalledAppFlow.from_client_secrets_file(
    "/root/.areal-neva-core/client_secret.json",
    SCOPES
)

creds = flow.run_local_server(
    host="127.0.0.1",
    port=8081,
    open_browser=False
)

with open("/root/.areal-neva-core/token.json", "w") as f:
    f.write(creds.to_json())

print("OAUTH_OK")
