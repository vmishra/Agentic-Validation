from google.adk import Agent
from google.adk.tools import google_search
root_agent = Agent(model="gemini-3.5-flash", name="x", tools=[google_search])
