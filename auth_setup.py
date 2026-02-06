"""
Jednorazowy skrypt do autoryzacji OAuth2 z YouTube Data API v3.

Uruchom raz: python auth_setup.py
Otworzy przeglądarkę → zaloguj się na konto Google → zezwól na dostęp.
Token zostanie zapisany do token.json i będzie automatycznie odświeżany.
"""

import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
TOKEN_FILE = "token.json"


def main():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"BLAD: Nie znaleziono pliku {CLIENT_SECRETS_FILE}")
        print("Pobierz go z Google Cloud Console:")
        print("  1. Wejdz na https://console.cloud.google.com/apis/credentials")
        print("  2. Utworz OAuth 2.0 Client ID (typ: Desktop app)")
        print("  3. Pobierz JSON i zapisz jako client_secrets.json")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)

    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())

    print(f"Autoryzacja udana! Token zapisany do {TOKEN_FILE}")


if __name__ == "__main__":
    main()
