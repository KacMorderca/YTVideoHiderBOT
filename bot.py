import os
import re

import discord
from discord import app_commands
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("DISCORD_OWNER_ID", "0"))
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# Regex do wyciągania video ID z różnych formatów URL
VIDEO_ID_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
    r"([a-zA-Z0-9_-]{11})"
    r"|^([a-zA-Z0-9_-]{11})$"
)


def extract_video_id(text: str) -> str | None:
    match = VIDEO_ID_PATTERN.search(text.strip())
    if not match:
        return None
    return match.group(1) or match.group(2)


def get_youtube_service() -> build:
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            "Brak token.json — uruchom najpierw: python auth_setup.py"
        )

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="hide", description="Ukryj film na YouTube (zmień na prywatny)")
@app_commands.describe(video="Link do filmu YouTube lub ID filmu")
async def hide_video(interaction: discord.Interaction, video: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "Nie masz uprawnien do tej komendy.", ephemeral=True
        )
        return

    video_id = extract_video_id(video)
    if not video_id:
        await interaction.response.send_message(
            f"Nie rozpoznano ID filmu z: `{video}`\n"
            "Podaj link YouTube lub samo ID (11 znakow).",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        youtube = get_youtube_service()

        # Pobierz aktualny status filmu
        response = youtube.videos().list(part="status,snippet", id=video_id).execute()

        if not response.get("items"):
            await interaction.followup.send(
                f"Nie znaleziono filmu o ID: `{video_id}`", ephemeral=True
            )
            return

        item = response["items"][0]
        title = item["snippet"]["title"]
        current_status = item["status"]["privacyStatus"]

        if current_status == "private":
            await interaction.followup.send(
                f"Film **{title}** jest juz prywatny.", ephemeral=True
            )
            return

        # Zmień na prywatny
        youtube.videos().update(
            part="status",
            body={"id": video_id, "status": {"privacyStatus": "private"}},
        ).execute()

        await interaction.followup.send(
            f"Film **{title}** zostal ukryty (private).\n"
            f"Poprzedni status: {current_status}",
            ephemeral=True,
        )

    except FileNotFoundError as e:
        await interaction.followup.send(str(e), ephemeral=True)
    except HttpError as e:
        await interaction.followup.send(
            f"Blad YouTube API: {e.reason}", ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"Nieoczekiwany blad: {e}", ephemeral=True
        )


@tree.command(name="hideall", description="Ukryj WSZYSTKIE publiczne filmy na kanale (zmien na prywatne)")
async def hide_all_videos(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "Nie masz uprawnien do tej komendy.", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        youtube = get_youtube_service()

        # Pobierz uploads playlist ID kanalu
        channels = youtube.channels().list(part="contentDetails", mine=True).execute()
        if not channels.get("items"):
            await interaction.followup.send("Nie znaleziono kanalu.", ephemeral=True)
            return

        uploads_id = channels["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Zbierz wszystkie video ID z uploads playlist
        all_video_ids = []
        next_page = None
        while True:
            playlist_response = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_id,
                maxResults=50,
                pageToken=next_page,
            ).execute()

            for item in playlist_response.get("items", []):
                all_video_ids.append(item["contentDetails"]["videoId"])

            next_page = playlist_response.get("nextPageToken")
            if not next_page:
                break

        if not all_video_ids:
            await interaction.followup.send("Brak filmow na kanale.", ephemeral=True)
            return

        # Sprawdz statusy i ukryj publiczne (batche po 50 ID)
        hidden_count = 0
        hidden_titles = []
        for i in range(0, len(all_video_ids), 50):
            batch = all_video_ids[i : i + 50]
            videos_response = youtube.videos().list(
                part="status,snippet", id=",".join(batch)
            ).execute()

            for video in videos_response.get("items", []):
                if video["status"]["privacyStatus"] == "public":
                    youtube.videos().update(
                        part="status",
                        body={
                            "id": video["id"],
                            "status": {"privacyStatus": "private"},
                        },
                    ).execute()
                    hidden_count += 1
                    hidden_titles.append(video["snippet"]["title"])

        if hidden_count == 0:
            await interaction.followup.send(
                "Nie znaleziono publicznych filmow — wszystkie sa juz ukryte.",
                ephemeral=True,
            )
        else:
            titles_list = "\n".join(f"- {t}" for t in hidden_titles[:20])
            extra = f"\n...i {hidden_count - 20} wiecej" if hidden_count > 20 else ""
            await interaction.followup.send(
                f"Ukryto **{hidden_count}** filmow:\n{titles_list}{extra}",
                ephemeral=True,
            )

    except FileNotFoundError as e:
        await interaction.followup.send(str(e), ephemeral=True)
    except HttpError as e:
        await interaction.followup.send(
            f"Blad YouTube API: {e.reason}", ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            f"Nieoczekiwany blad: {e}", ephemeral=True
        )


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot zalogowany jako {client.user}")
    print(f"Owner ID: {OWNER_ID}")
    print("Slash commands: /hide, /hideall")


client.run(DISCORD_TOKEN)
