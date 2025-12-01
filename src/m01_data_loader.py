"""
Data loading utilities for the JUNO Automation Engine.
Handles loading JSON configurations and databases.
"""

import json
import os


class DataLoader:
    """Handles loading JSON configurations and Databases."""
    
    @staticmethod
    def load_json(filepath):
        """
        Load a JSON file from the given filepath.
        
        Args:
            filepath (str): Path to the JSON file
            
        Returns:
            dict: Loaded JSON data, or empty dict if file not found or invalid
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ CRITICAL ERROR: Could not find {filepath}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ CRITICAL ERROR: Invalid JSON in {filepath}")
            return {}
    
    @staticmethod
    def load_configs(project_root="."):
        """
        Load all configuration files from the config directory.
        
        Args:
            project_root (str): Root directory of the project
            
        Returns:
            tuple: (intent_config, mock_db, templates) dictionaries
        """
        config_dir = os.path.join(project_root, "config")
        
        intent_config_path = os.path.join(config_dir, "intent_config.json")
        mock_db_path = os.path.join(config_dir, "mock_database.json")
        templates_path = os.path.join(config_dir, "response_templates.json")
        
        intent_config = DataLoader.load_json(intent_config_path)
        mock_db = DataLoader.load_json(mock_db_path)
        templates = DataLoader.load_json(templates_path)
        
        if not intent_config:
            print("⚠️ WARNING: Intent Config is empty. Check 'config/intent_config.json'")
        else:
            print("✅ Configuration & Database Loaded.")
        
        return intent_config, mock_db, templates

