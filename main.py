import os
import asyncio
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel
import json

from google import genai
from google.genai import types
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search


class GameEntry(BaseModel):
    title: str
    description: str

class GamesList(BaseModel):
    games: list[GameEntry]

# Getting the API key for the agent
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

# Creating a GenAI client with specifications
# Agent will use the google search to find the recommended games
# Structure each of the games with game title and then game description in separate lines
# Each entry will be separated by white lines
# Usually formatting and introductory statement like "Here are some games ...", so it is not included to make it easier to format for the output
client = genai.Client(api_key=google_api_key)

# Agent to search for the recommended games
game_search_agent = LlmAgent(
    name="game_search_agent",
    description="Searches for recommended games based on user input",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="You are a game recommender assistant. " \
        "You will use Google search to search up games that relates to the user's prompt." \
        "Return list of games with their title and description",
    tools=[google_search],
    output_key="search_results"
)

# Agent to format the results into list of game entries
format_agent = LlmAgent(
    name="format_agent",
    description="A formatting agent to format result",
    model=Gemini(model="gemini-2.5-flash"),
    instruction="You will receive a list of games. Structure them into a JSON list with the title and description for each game.",
    output_schema=GamesList
)

# A sequential agent that runs the two agents in an order. This is to make the formatting more easier to work with.
game_rec_agent = SequentialAgent(
    name="game_rec_agent",
    sub_agents=[game_search_agent, format_agent]
)

runner = InMemoryRunner(agent=game_rec_agent)

async def main():
    ask_prompt = True
    quit_agent = False
    cur_game = 0
    num_games = 0

    # Clearing the lines for the terminal output and then outputting the current game
    os.system('cls' if os.name == 'nt' else 'clear')

    while(True):
        if (ask_prompt is True):
            # Debug version of the AI agent's response
            prompt = input("Input Prompt: ")
            response = await runner.run_debug(prompt)

            response_text = ""

            # Getting the string version of the response. The response itself is stored as a list[Event] according
            # to the ADK documentation.
            for event in response:
                # Find the final response from the agent
                if (event.is_final_response()):
                    # Extract the conversational message from the event.
                    response_text = event.content.parts[0].text

            # Format the game into the list
            game_data = json.loads(response_text)
            game_list = game_data["games"]

            # Get the number of recommended games
            num_games = len(game_list)
            ask_prompt = False

        # Clearing the lines for the terminal output and then outputting the current game
        os.system('cls' if os.name == 'nt' else 'clear')

        # Print the current game
        print(game_list[cur_game]["title"])
        print(game_list[cur_game]["description"])
        print()

        # Formatting the terminal
        # If we're after the first recommended game, then display the left option
        if (cur_game > 0):
            print("[L]eft")

        # Display the other options
        print("[Q]uit\n[P]rompt")
        
        # If we're before the last recommended game, then display the right option
        if (cur_game < num_games - 1):
            print("[R]ight")

        print()

        # Get user input for option
        option = input()

        # Execute option
        match option:
            case "L":
                # If we're not at the first game, then go left
                if (cur_game > 0):
                    cur_game -= 1
            case "Q":
                # Quit the agent by breaking out of the outer for loop
                quit_agent = True
            case "P":
                # User wants to do another prompt
                ask_prompt = True
            case "R":
                # If we're not at the last game, then go right
                if (cur_game < num_games - 1):
                    cur_game += 1
            case _:
                print("Please type the correct input")
        
        # Break out of the loop if user quits
        if (quit_agent is True):
            print("Thank you for using the game recommender!")
            break

if __name__ == '__main__':
    asyncio.run(main())