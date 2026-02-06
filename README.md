# YTHideVideos — Bot Discord do ukrywania filmow YouTube

Bot Discord, ktory pozwala ukryc (ustawic jako prywatne) filmy na Twoim kanale YouTube za pomoca slash komend.

## Komendy

- `/hide video:<link lub ID>` — ukrywa pojedynczy film
- `/hideall` — ukrywa WSZYSTKIE publiczne filmy na kanale

---

## Konfiguracja krok po kroku

### 1. Utworz projekt w Google Cloud Console

1. Wejdz na https://console.cloud.google.com
2. Na gorze kliknij nazwe projektu → **Nowy projekt** → wpisz nazwe (np. "YTHideVideos") → **Utworz**
3. Upewnij sie, ze nowy projekt jest wybrany na gorze strony

### 2. Wlacz YouTube Data API

1. W menu po lewej: **Interfejsy API i uslugi** → **Biblioteka**
2. Wyszukaj **YouTube Data API v3**
3. Kliknij na wynik → **Wlacz**

### 3. Skonfiguruj ekran zgody OAuth

1. W menu po lewej: **Interfejsy API i uslugi** → **Ekran zgody OAuth**
2. Wybierz typ **Zewnetrzny** → **Utworz**
3. Wypelnij wymagane pola:
   - Nazwa aplikacji: np. "YTHideVideos"
   - Adres email pomocy: Twoj email
   - Dane kontaktowe dewelopera: Twoj email
4. Kliknij **Zapisz i kontynuuj**
5. Na stronie **Zakresy** kliknij **Dodaj lub usun zakresy**:
   - Wyszukaj `youtube` i zaznacz **YouTube Data API v3** → `.../auth/youtube`
   - Kliknij **Aktualizuj** → **Zapisz i kontynuuj**
6. Na stronie **Uzytkownicy testowi** kliknij **Dodaj uzytkownikow**:
   - Wpisz adres email konta Google, na ktorym masz kanal YouTube
   - Kliknij **Dodaj** → **Zapisz i kontynuuj**

### 4. Utworz dane logowania OAuth

1. W menu po lewej: **Interfejsy API i uslugi** → **Dane logowania**
2. Kliknij **Utworz dane logowania** → **Identyfikator klienta OAuth**
3. Typ aplikacji: **Aplikacja komputerowa**
4. Nazwa: np. "YTHideVideos"
5. Kliknij **Utworz**
6. Kliknij **Pobierz JSON**
7. Zapisz pobrany plik jako `client_secrets.json` w folderze projektu (`c:\skrypty\YTHideVideos\`)

### 5. Utworz bota Discord

1. Wejdz na https://discord.com/developers/applications
2. Kliknij **New Application** → wpisz nazwe → **Create**
3. W menu po lewej kliknij **Bot**
4. Kliknij **Reset Token** → **Yes, do it!** → skopiuj token (zapisz go, nie pokaze sie ponownie)
5. Wylacz **Public Bot** (zeby nikt inny nie mogl dodac bota)
6. W menu po lewej kliknij **OAuth2** → **URL Generator**:
   - Zaznacz scope: **bot** i **applications.commands**
   - W sekcji Bot Permissions zaznacz: **Send Messages**
   - Skopiuj wygenerowany URL na dole strony
7. Wklej URL do przegladarki i dodaj bota na swoj serwer Discord

### 6. Znajdz swoje Discord User ID

1. W Discord wejdz w **Ustawienia** → **Zaawansowane** → wlacz **Tryb dewelopera**
2. Kliknij prawym przyciskiem myszy na swoj nick (np. na liscie czlonkow serwera)
3. Kliknij **Kopiuj ID uzytkownika**

### 7. Skonfiguruj plik .env

1. W folderze projektu skopiuj plik `.env.example` i zmien nazwe kopii na `.env`
2. Otworz `.env` w notatniku i wypelnij:

```
DISCORD_TOKEN=tutaj_wklej_token_bota
DISCORD_OWNER_ID=tutaj_wklej_swoje_discord_id
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
```

### 8. Zainstaluj Pythona (jesli nie masz)

1. Pobierz Pythona z https://www.python.org/downloads/
2. Podczas instalacji zaznacz **Add Python to PATH**

### 9. Zainstaluj zaleznosci

Otworz terminal (cmd lub PowerShell) w folderze projektu i wpisz:

```
cd c:\skrypty\YTHideVideos
pip install -r requirements.txt
```

### 10. Autoryzuj YouTube (jednorazowo)

```
python auth_setup.py
```

Otworzy sie przegladarka:
1. Zaloguj sie na konto Google z kanalem YouTube
2. Kliknij **Kontynuuj** (moze pokazac ostrzezenie — kliknij **Zaawansowane** → **Przejdz do...**)
3. Zaznacz wszystkie uprawnienia → **Kontynuuj**
4. W terminalu pojawi sie: "Autoryzacja udana!"

### 11. Uruchom bota

```
python bot.py
```

Powinno pojawic sie:
```
Bot zalogowany jako NazwaBota#1234
Slash commands: /hide, /hideall
```

Bot jest gotowy. Wejdz na Discord i uzyj `/hide` lub `/hideall`.

---

## Rozwiazywanie problemow

| Problem | Rozwiazanie |
|---|---|
| `403: access_denied` przy autoryzacji | Dodaj swoj email w Google Cloud → Ekran zgody OAuth → Uzytkownicy testowi |
| `ModuleNotFoundError: discord` | Uruchom `pip install discord.py` |
| Slash komendy nie widac na Discord | Poczekaj do 1h (Discord cache'uje komendy) lub zrestartuj Discorda |
| `Brak token.json` | Uruchom `python auth_setup.py` |
| `HttpError 403 forbidden` | Sprawdz czy YouTube Data API v3 jest wlaczone w Google Cloud Console |
