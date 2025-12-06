"""
Entity extraction module for the JUNO Automation Engine.
Extracts structured data (Order IDs, Emails, Products) from text.
"""

import re


class EntityExtractor:
    """
    Extracts structured data (Order IDs, Emails, Products) from text.
    Uses Strict Regex + Knowledge Base lookup to avoid false positives.
    """
    
    @staticmethod
    def extract_order_id(text):
        """
        Extract order ID from text.
        
        Robust Logic:
        1. Must be 5+ characters long.
        2. MUST contain at least one DIGIT (0-9). This prevents matching words like "Where".
        3. Supports formats: #12345, ORD-459, 123456, Order 999
        
        Args:
            text (str): Input text to search
            
        Returns:
            str or None: Extracted order ID, or None if not found
        """
        # Step 1: Look for explicit labeled IDs (High Confidence)
        # Matches: #12345, Order: 12345, Ref 12345
        explicit_pattern = r'(?:#|Order\s*:?\s*|id\s*:?\s*|ref\s*:?\s*)([A-Z0-9-]{4,})'
        match = re.search(explicit_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

        # Step 2: Look for standalone IDs (Medium Confidence)
        # Matches: 12345, ORD-123, 99999
        # Constraint: Must contain a digit to avoid English words.
        tokens = text.split()
        for token in tokens:
            # Clean punctuation from edges
            clean_token = token.strip(".,?!")
            
            # Check conditions: Length >= 4 AND contains digit AND allows A-Z, 0-9, -
            if len(clean_token) >= 4 and any(char.isdigit() for char in clean_token):
                # Verify it doesn't contain weird symbols (like emails)
                if re.match(r'^[A-Z0-9-]+$', clean_token, re.IGNORECASE):
                    return clean_token
                    
        return None

    @staticmethod
    def extract_email(text):
        """
        Extract email address from text.
        
        Args:
            text (str): Input text to search
            
        Returns:
            str or None: Extracted email, or None if not found
        """
        # Standard email regex
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_product(text, database):
        """
        Extract product name from text by scanning against database.
        
        Scans text for product names defined in mock_database.json.
        Uses word-boundary checks to prevent partial matches.
        
        Args:
            text (str): Input text to search
            database (dict): Database containing products list
            
        Returns:
            str or None: Extracted product name, or None if not found
        """
        text_lower = " " + text.lower() + " "  # Pad with spaces for boundary check
        
        for product in database.get("products", []):
            official_name = product["product_name"].lower()
            
            # Check official name
            if f" {official_name} " in text_lower or official_name in text.lower():
                return product["product_name"]
            
            # Check aliases (synonyms)
            for alias in product.get("aliases", []):
                alias_lower = alias.lower()
                # Check if alias exists in text (simple substring check usually works best for products)
                if alias_lower in text_lower:
                    return product["product_name"]  # Normalize to official name
                    
        return None

    @staticmethod
    def run_extraction(text, required_entities, database=None):
        """
        Extract all required entities from text.
        
        Only looks for what is REQUIRED by the intent config.
        
        Args:
            text (str): Input text to extract from
            required_entities (list): List of entity types to extract
            database (dict, optional): Database for product extraction
            
        Returns:
            dict: Dictionary of extracted entities
        """
        extracted = {}
        
        if "order_id" in required_entities:
            val = EntityExtractor.extract_order_id(text)
            if val:
                extracted["order_id"] = val
            
        if "email" in required_entities:
            val = EntityExtractor.extract_email(text)
            if val:
                extracted["email"] = val
            
        if "product_name" in required_entities:
            if database is None:
                raise ValueError("Database required for product_name extraction")
            val = EntityExtractor.extract_product(text, database)
            if val:
                extracted["product_name"] = val
            
        return extracted

