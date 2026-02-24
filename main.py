from google import genai
from google.genai import types
from steam.webapi import WebAPI
from steam.steamid import SteamID

api = WebAPI(key="") # will get the steam key later on

accountLink = input("Enter your Steam profile link: ")
accountId = int(accountLink)