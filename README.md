# Terraform Security Analysis Assistant

An intelligent security analysis tool that processes Checkov vulnerability scan results for Terraform configurations, providing context-aware remediation recommendations by combining infrastructure context with security findings.

## Overview

This tool enhances standard Checkov security scans by:
- Analyzing the full context of your Terraform infrastructure
- Understanding network topology and resource relationships
- Providing detailed, actionable remediation steps for each security finding
- Considering the broader architectural impact of security issues

## Components

- `CheckovReportAgent`: LLM-powered agent that analyzes security findings
- `TerraformProjectContext`: Parser that builds a comprehensive view of your infrastructure
- Integration with Checkov for security scanning

## How It Works

1. The tool first analyzes your Terraform project structure using `TerraformProjectContext`
2. It processes Checkov scan results through an LLM-powered agent
3. For each security finding, it:
   - Analyzes the specific vulnerability
   - Considers the infrastructure context
   - Provides detailed remediation steps
   - Evaluates architectural impact

## Usage

```python
from langchain_openai import ChatOpenAI
from agent import CheckovReportAgent

# Initialize with OpenAI API key in environment
llm = ChatOpenAI(temperature=0)
agent = CheckovReportAgent(llm=llm, project_path="./terraform")
results = agent.process_report("checkov-report.json")
```

## Requirements

- Python 3.7+
- OpenAI API key
- Terraform configurations
- Checkov security scanner
