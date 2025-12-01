"""
Template Engine Module for JUNO Automation Engine.
Wraps Jinja2 to handle dynamic email generation based on Mood and Data.
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateEngine:
    """
    Handles loading and rendering of Jinja2 templates.
    """
    def __init__(self, template_dir="templates"):
        """
        Initialize the Jinja2 environment.
        
        Args:
            template_dir (str): Path to the templates directory.
        """
        # Resolve absolute path relative to project root if needed
        if not os.path.isabs(template_dir):
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(base_path, template_dir)
            
        print(f"🎨 Loading Templates from: {template_dir}")
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render(self, template_name, context):
        """
        Render a specific template with the given context.
        
        Args:
            template_name (str): Name of the template file (e.g., 'order_status.j2')
            context (dict): Dictionary of variables to inject (mood, data, etc.)
            
        Returns:
            str: Rendered text
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            print(f"❌ Template Rendering Error ({template_name}): {e}")
            return "System Error: Unable to generate response."

if __name__ == "__main__":
    # Test Logic
    engine = TemplateEngine()
    
    # Mock Context
    ctx = {
        "user_name": "John",
        "mood": "Happy",
        "data": {"status": "Shipped", "delivery_date": "Monday"}
    }
    
    # We haven't created templates yet, so this would fail if we ran it now.
    print("Template Engine Initialized.")
