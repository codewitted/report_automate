"""
Configuration Management Module

This module handles loading and validating configuration from config files
and environment variables.
"""

import configparser
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass


class ConfigManager:
    """
    Manager for application configuration.
    
    Supports loading configuration from INI files and environment variables.
    Environment variables take precedence over config file values.
    """
    
    def __init__(self, config_file: str = 'config.ini'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration INI file
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """
        Load configuration from file.
        
        Raises:
            ConfigError: If config file is not found or invalid
        """
        if not os.path.exists(self.config_file):
            logger.warning(f"Config file '{self.config_file}' not found. "
                         "Using environment variables or defaults.")
            return
        
        try:
            self.config.read(self.config_file)
            logger.info(f"Configuration loaded from {self.config_file}")
        except configparser.Error as e:
            raise ConfigError(f"Failed to parse config file: {str(e)}")
    
    def get(self, section: str, key: str, env_var: Optional[str] = None, 
            default: Optional[str] = None) -> str:
        """
        Get configuration value.
        
        Priority order:
        1. Environment variable (if env_var is specified)
        2. Config file value
        3. Default value
        
        Args:
            section: Config file section name
            key: Config file key name
            env_var: Optional environment variable name to check first
            default: Optional default value if not found
            
        Returns:
            Configuration value
            
        Raises:
            ConfigError: If value is not found and no default is provided
        """
        # Check environment variable first
        if env_var:
            env_value = os.getenv(env_var)
            if env_value:
                return env_value
        
        # Check config file
        try:
            if self.config.has_option(section, key):
                return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        
        # Use default if provided
        if default is not None:
            return default
        
        # Value not found
        raise ConfigError(
            f"Configuration value '{section}.{key}' not found. "
            f"Please set it in {self.config_file} or via environment variable "
            f"{env_var if env_var else f'{section.upper()}_{key.upper()}'}"
        )
    
    def get_jira_config(self) -> Dict[str, str]:
        """
        Get Jira-specific configuration.
        
        Returns:
            Dictionary with Jira configuration values
            
        Raises:
            ConfigError: If required configuration is missing
        """
        return {
            'base_url': self.get('jira', 'base_url', 'JIRA_BASE_URL'),
            'email': self.get('jira', 'email', 'JIRA_EMAIL'),
            'api_token': self.get('jira', 'api_token', 'JIRA_API_TOKEN'),
            'project_key': self.get('jira', 'project_key', 'JIRA_PROJECT_KEY')
        }
    
    def get_report_config(self) -> Dict[str, str]:
        """
        Get report-specific configuration.
        
        Returns:
            Dictionary with report configuration values
        """
        return {
            'output_dir': self.get('report', 'output_dir', 'REPORT_OUTPUT_DIR', 'reports'),
            'default_format': self.get('report', 'default_format', 'REPORT_FORMAT', 'csv')
        }
