import os
import asyncio
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

async def main():
    # Getting the Google API Key
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # Creating a GenAI client with specifications
    client = genai.Client(api_key=google_api_key)
    game_rec_agent = LlmAgent(
        name="game_recommender_agent",
        description="Recommends games to users based on specific prompts",
        model=Gemini(model="gemini-2.5-flash-lite"),
        instruction="You are a game recommender assistant. " \
            "You will use Google search to search up games that relates to the user's prompt." \
            "Format each of the games with the game title, game rating, and description, all in different lines.",
        tools=[google_search]
    )
    runner = InMemoryRunner(agent=game_rec_agent)

    # Debug version of the AI agent's response
    prompt = input("Input Prompt: ")
    response = await runner.run_debug(prompt)

    response_text = ""

    # Getting the string version of the response. The response itself is stored as a list[Event] according
    # to the ADK documentation.
    for event in response:
        # Find the final response from the agent
        if event.is_final_response():
            # Extract the conversational message from the event.
            response_text = event.content.parts[0].text

    # Print out the extracted AI response
    print("\n\n\n")
    print("AI Response in Text Form: \n")
    print(response_text)


if __name__ == '__main__':
    asyncio.run(main())