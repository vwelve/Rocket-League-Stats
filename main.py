import os.path
import discord
from typing import List, Optional
from discord import Message, Member
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

Row = List[str]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def get_stats(username: str) -> Optional[Row]:
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=os.getenv("SPREADSHEET_ID"),
                                range=os.getenv("RANGE_NAME")).execute()
    values = result.get('values', [])

    if rows := [val for val in values if len(val) == 13 and val[0] == username]:
        return rows[0]
    else:
        return None


def format_stats(username: str, stats: Row) -> str:
    return '```{:^10}|{:^10}|{:^10}\n{:10}|{:10}|{:10}\n{:10}|{:10}|{:10}\n{:10}|{:10}|{:10}\n{:10}|{:10}|{:10}\n{:10}|{:10}|{:10}```'.format(
        username, 'Overall', 'Per Game', 'Goals', stats[1], stats[2], 'Assists', stats[3], stats[4], 'Saves', stats[5],
        stats[6], 'Shots', stats[7], stats[8], 'Score', stats[9], stats[10])

@client.event
async def on_message(message: Message):
    if message.author.bot or not message.guild:
        return

    if message.content.startswith('.rlstats'):
        username = " ".join(message.content.split(" ")[1:]) if len(message.content.split(" ")) > 1 else message.author.name
        stats = get_stats(username)

        if stats:
            embed = discord.Embed(color=8388736, description=f"Here is the stat sheet for {username}")
            embed.add_field(name="Stats", value=format_stats(username, stats), inline=False)
            embed.add_field(name="Shot %", value=stats[11])
            embed.add_field(name="# of games", value=stats[12])

            await message.channel.send(embed=embed)
        else:
            await message.channel.send("No user with that username!")


if "__main__" == __name__:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, throw exception and quit.
    if not creds or not creds.valid:
        raise Exception("Invalid token credentials")

    client.run(os.getenv("DISCORD_TOKEN"))
