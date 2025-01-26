from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models.base import BaseLanguageModel
from typing import List, Dict
import json
from project_context import TerraformProjectContext

class CheckovReportAgent:
    def __init__(self, llm: BaseLanguageModel, project_path: str):
        self.llm = llm
        self.project_context = TerraformProjectContext(project_path)
        self.project_context.analyze_project()
        self.project_summary = self.project_context.get_project_summary()
        
        # Define tools
        self.tools = [
            Tool(
                name="analyze_failed_check",
                func=self._analyze_failed_check,
                description="Analyzes a single failed check from the Checkov report"
            ),
            Tool(
                name="get_summary",
                func=self._get_summary,
                description="Gets a summary of all failed checks"
            ),
            Tool(
                name="get_project_context",
                func=self._get_project_context,
                description="Gets the context about the Terraform project structure"
            )
        ]
        
        # Define prompt
        prompt = PromptTemplate.from_template(
            """You are a security analysis assistant that helps process Checkov scan results.
            
            Project Context:
            {project_context}
            
            Given the following failed check, analyze the issue and provide remediation steps:
            {input}
            
            Consider:
            1. What is the security risk?
            2. What is the recommended fix?
            3. What resources are affected?
            4. How does this impact the overall project architecture?
            
            Available tools: {tools}
            Tool names: {tool_names}
            
            To analyze the issue, you should:
            1. Use the analyze_failed_check tool to get detailed information about the check
            2. Use the get_project_context tool to understand the infrastructure context
            3. Provide your analysis based on the information gathered
            
            {agent_scratchpad}
            
            Response should be clear and actionable.
            """
        )
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def _get_project_context(self) -> str:
        """Returns relevant project context information"""
        return f"""
        Project Overview:
        - Providers: {', '.join(self.project_summary['providers'])}
        - Resource Types: {', '.join(self.project_summary['resource_types'])}
        - Network Components: {json.dumps(self.project_summary['network_components'], indent=2)}
        """

    def _analyze_failed_check(self, check: Dict) -> str:
        """Analyzes a single failed check and returns recommendations"""
        analysis = {
            "check_id": check.get("check_id"),
            "check_name": check.get("check_name"),
            "resource": check.get("resource"),
            "file_path": check.get("file_path"),
            "guideline": check.get("guideline")
        }
        
        # Get relevant network topology information
        resource_type = check.get("resource_type", "")
        resource_name = check.get("resource_name", "")
        network_context = ""
        
        if resource_type in self.project_context.network_topology:
            components = self.project_context.network_topology[resource_type]
            if resource_name in components:
                network_context = f"\nNetwork Context: {json.dumps(components[resource_name], indent=2)}"
        
        return f"""
        Issue: {analysis['check_name']}
        Resource: {analysis['resource']}
        Location: {analysis['file_path']}
        Reference: {analysis['guideline']}
        {network_context}
        Project Context: {self._get_project_context()}
        """

    def _get_summary(self, report_data: Dict) -> str:
        """Generates a summary of all failed checks"""
        failed_checks = report_data.get("results", {}).get("failed_checks", [])
        summary = {
            "total_failed": len(failed_checks),
            "affected_resources": set(check.get("resource") for check in failed_checks),
            "affected_files": set(check.get("file_path") for check in failed_checks)
        }
        
        return f"""
        Total Failed Checks: {summary['total_failed']}
        Affected Resources: {', '.join(summary['affected_resources'])}
        Affected Files: {', '.join(summary['affected_files'])}
        """

    def process_report(self, report_path: str):
        """Main method to process the Checkov report"""
        # Load report
        with open(report_path) as f:
            report_data = json.load(f)
        
        failed_checks = report_data.get("results", {}).get("failed_checks", [])
        
        # Process each failed check with project context in prompt
        results = []
        for check in failed_checks:
            result = self.agent_executor.invoke({
                "input": check,
                "project_context": self._get_project_context()
            })
            results.append(result)
            
        # Get overall summary
        summary = self._get_summary(report_data)
        
        return {
            "detailed_results": results,
            "summary": summary,
            "project_context": self._get_project_context()
        }