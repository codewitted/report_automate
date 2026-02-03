"""
Jira API Client Module

This module provides functionality to authenticate and interact with Jira API.
It handles authentication, ticket retrieval, and error handling for common API issues.
"""

import requests
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JiraAPIError(Exception):
    """Custom exception for Jira API errors"""
    pass


class JiraClient:
    """
    Client for interacting with Jira API.
    
    Handles authentication, ticket retrieval, and error handling for common API issues
    like authentication errors, timeouts, and data parsing problems.
    """
    
    def __init__(self, base_url: str, email: str, api_token: str, timeout: int = 30):
        """
        Initialize Jira API client.
        
        Args:
            base_url: Jira instance URL (e.g., https://your-company.atlassian.net)
            email: User email for authentication
            api_token: Jira API token for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def test_connection(self) -> bool:
        """
        Test the connection to Jira API.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Raises:
            JiraAPIError: If authentication fails or connection cannot be established
        """
        try:
            url = f"{self.base_url}/rest/api/3/myself"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 401:
                raise JiraAPIError("Authentication failed. Please check your email and API token.")
            elif response.status_code == 403:
                raise JiraAPIError("Access forbidden. Please check your permissions.")
            
            response.raise_for_status()
            logger.info("Successfully connected to Jira API")
            return True
            
        except requests.exceptions.Timeout:
            raise JiraAPIError(f"Connection timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise JiraAPIError(f"Could not connect to {self.base_url}. Please check the URL.")
        except requests.exceptions.RequestException as e:
            raise JiraAPIError(f"API request failed: {str(e)}")
    
    def get_project_tickets(self, project_key: str, max_results: int = 100, 
                           fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Retrieve tickets from a specific Jira project.
        
        Args:
            project_key: The project key (e.g., 'PROJ', 'DEV')
            max_results: Maximum number of tickets to retrieve (default: 100)
            fields: List of fields to retrieve. If None, retrieves default fields.
        
        Returns:
            List of ticket dictionaries containing requested fields
            
        Raises:
            JiraAPIError: If the API request fails
        """
        # Default fields to retrieve if none specified
        if fields is None:
            fields = [
                'summary', 'status', 'assignee', 'reporter', 'priority',
                'created', 'updated', 'resolutiondate', 'description',
                'issuetype', 'labels', 'components'
            ]
        
        try:
            # Build JQL query
            jql = f"project = {project_key} ORDER BY created DESC"
            
            url = f"{self.base_url}/rest/api/3/search"
            params = {
                'jql': jql,
                'maxResults': max_results,
                'fields': ','.join(fields)
            }
            
            logger.info(f"Retrieving tickets from project: {project_key}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 400:
                raise JiraAPIError("Invalid request. Please check the project key and parameters.")
            elif response.status_code == 401:
                raise JiraAPIError("Authentication failed. Please check your credentials.")
            elif response.status_code == 404:
                raise JiraAPIError(f"Project '{project_key}' not found.")
            
            response.raise_for_status()
            
            data = response.json()
            tickets = data.get('issues', [])
            
            logger.info(f"Successfully retrieved {len(tickets)} tickets from project {project_key}")
            return tickets
            
        except requests.exceptions.Timeout:
            raise JiraAPIError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise JiraAPIError("Connection error. Please check your network connection.")
        except requests.exceptions.JSONDecodeError:
            raise JiraAPIError("Failed to parse API response. The server returned invalid JSON.")
        except requests.exceptions.RequestException as e:
            raise JiraAPIError(f"API request failed: {str(e)}")
    
    def get_custom_fields(self) -> List[Dict]:
        """
        Retrieve all custom fields available in the Jira instance.
        
        Returns:
            List of custom field dictionaries
            
        Raises:
            JiraAPIError: If the API request fails
        """
        try:
            url = f"{self.base_url}/rest/api/3/field"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            fields = response.json()
            # Filter to only custom fields (they start with 'customfield_')
            custom_fields = [f for f in fields if f['id'].startswith('customfield_')]
            
            logger.info(f"Retrieved {len(custom_fields)} custom fields")
            return custom_fields
            
        except requests.exceptions.RequestException as e:
            raise JiraAPIError(f"Failed to retrieve custom fields: {str(e)}")
