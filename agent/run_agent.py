from langchain_openai import ChatOpenAI
from agent import CheckovReportAgent
import os

def main():
    # Initialize the LLM (make sure you have OPENAI_API_KEY in your environment)
    llm = ChatOpenAI(temperature=0)
    
    # Initialize the agent with the project path
    agent = CheckovReportAgent(llm=llm, project_path="../gcp")
    
    # Print the raw report first
    # print("\n=== Raw Checkov Report ===")
    # with open("../gcp/checkov-report.json", "r") as f:
    #     print(f.read())
    
    # Process the Checkov report
    results = agent.process_report("../gcp/checkov-report.json")
    
    # print("\n=== Project Context ===")
    # print(results["project_context"])
    
    # print("\n=== Summary ===")
    # print(results["summary"])
    
    print("\n=== Detailed Results ===")
    for i, result in enumerate(results["detailed_results"], 1):
        print(f"\nFinding {i}:")
        print(result)

if __name__ == "__main__":
    main() 