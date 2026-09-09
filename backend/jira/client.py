import requests
import os
from typing import Optional

class JiraClient:
    """Client for interacting with Jira API"""
    
    def __init__(self):
        self.host = os.getenv('JIRA_HOST', 'http://localhost:8080')
        self.username = os.getenv('JIRA_USERNAME', 'admin')
        self.api_token = os.getenv('JIRA_API_TOKEN', '')
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'AICR')
    
    def check_connection(self) -> dict:
        """Check if Jira is accessible"""
        try:
            response = requests.get(
                f"{self.host}/rest/api/3/myself",
                auth=(self.username, self.api_token),
                timeout=5
            )
            if response.status_code == 200:
                return {'status': 'connected'}
            else:
                return {'status': 'disconnected', 'error': f'Status {response.status_code}'}
        except Exception as e:
            return {'status': 'disconnected', 'error': str(e)}
    
    def create_issue(self, summary: str, description: str, issue_type: str, severity: str) -> Optional[str]:
        """
        Create a new issue in Jira
        
        Args:
            summary (str): Issue title
            description (str): Issue description
            issue_type (str): Type of issue
            severity (str): Issue severity
        
        Returns:
            str: Jira issue key (e.g., 'AICR-123')
        """
        try:
            # Map our severity to Jira priority
            priority_map = {
                'critical': 'Highest',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low'
            }
            
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": "Task"},
                    "priority": {"name": priority_map.get(severity, 'Medium')},
                    "labels": [f"ai-review", issue_type, severity]
                }
            }
            
            response = requests.post(
                f"{self.host}/rest/api/3/issue",
                json=payload,
                auth=(self.username, self.api_token),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                issue_key = response.json().get('key')
                return issue_key
            else:
                print(f"Failed to create Jira issue: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error creating Jira issue: {e}")
            return None
    
    def get_issue(self, issue_key: str) -> Optional[dict]:
        """
        Get issue details from Jira
        """
        try:
            response = requests.get(
                f"{self.host}/rest/api/3/issue/{issue_key}",
                auth=(self.username, self.api_token),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        
        except Exception as e:
            print(f"Error fetching Jira issue: {e}")
            return None
