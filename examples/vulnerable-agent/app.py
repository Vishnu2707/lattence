from chromadb import Client
from crewai import Agent
from langchain.tools import tool


@tool
def delete_customer_record(record_id: str) -> str:
    return f"fixture deletion requested for {record_id}"


records = Client().get_or_create_collection()
primary_agent = Agent()
primary_agent.delegate()
primary_agent.memory.save()
retrieved_context = records.similarity_search()
