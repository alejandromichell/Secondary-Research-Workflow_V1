import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
RESEARCH_ENDPOINT = "/start-research"


def run_interactive_session():
    """
    Conducts a simplified interactive session to get the research topic.
    """
    print("\n--- Simplified Research Intake ---")
    
    research_request = {}
    
    answer = ""
    while not answer:
        answer = input("\033[1mWhat is the topic you want to research?\033[0m\n> ")
        if not answer:
            print("\033[91mThis field is required. Please provide a topic.\033[0m")
    research_request["topic"] = answer
    print()

    return research_request

def start_research(research_request: dict):
    """
    Sends the collected research topic to the FastAPI backend.
    """
    try:
        print("Submitting your research request to the research workflow...")
        response = requests.post(f"{BASE_URL}{RESEARCH_ENDPOINT}", json=research_request)
        response.raise_for_status()
        
        print("\033[92m\nResearch process initiated successfully!\033[0m")
        print("You can monitor the backend server logs for progress.")
        print(f"Response from server: \n{json.dumps(response.json(), indent=2)}")

    except requests.exceptions.RequestException as e:
        print(f"\033[91m\nError: Could not connect to the research workflow backend at {BASE_URL}.\033[0m", file=sys.stderr)
        print("Please ensure the backend server is running. You can start it with: ./scripts/run-local.sh", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    request_data = run_interactive_session()
    start_research(request_data)
