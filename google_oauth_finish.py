from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/drive"]

flow = Flow.from_client_secrets_file(
    "/root/.areal-neva-core/client_secret.json",
    scopes=SCOPES,
    redirect_uri="urn:ietf:wg:oauth:2.0:oob"
)

flow.fetch_token(code="4/1Aci98E9oHcZQ5s4gBRnroafGIqGCxMO-FB6ysGQqSM90OOFyqu1eJgskBKM")

with open("/root/.areal-neva-core/token.json", "w") as f:
    f.write(flow.credentials.to_json())

print("OAUTH_OK")
