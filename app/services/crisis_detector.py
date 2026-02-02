import json 
import re 
from typing import List, Tuple, Optional
from pathlib import Path

class CrisisDetector:
    """Service to detect crisis-related content in messages."""

    _instance = None
    _keywords = None

    PRIORITY = {
         "mental_health": 1,      # Highest - immediate danger
        "violence_abuse": 2,     # High - safety concern
        "substance_abuse": 3,    # Medium-high
        "infidelity": 4,         # Medium
        "communication_breakdown": 5  # Lower - recommend therapy
    }
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_keywords()
        return cls._instance
    
    def _load_keywords(self):
        """Load crisis keywords from JSON file."""
        try:
            keywords_path = Path(__file__).parent.parent.parent / "resources" / "crisis_keywords.json"
            with open(keywords_path, 'r') as f:
                self._keywords = json.load(f)
        except Exception as e:
            print(f"Error loading crisis keywords: {e}")
            self._keywords = {}
    
    def scan_message(self, content: str) -> Optional[Tuple[str, List[str]]]:
        """
        Scan a message for crisis keywords.
        
        Returns:
            Tuple of (category, matched_keywords) if crisis detected, None otherwise
        """
        if not self._keywords or not content:
            return None
        
        content_lower = content.lower()
        
        # Check each category in priority order
        sorted_categories = sorted(
            self._keywords.keys(),
            key=lambda x: self.PRIORITY.get(x, 99)
        )
        
        for category in sorted_categories:
            keywords = self._keywords[category]
            matched = []
            
            for keyword in keywords:
                # Use word boundary matching for better accuracy
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, content_lower):
                    matched.append(keyword)
            
            if matched:
                return (category, matched)
        
        return None
    
    def get_category_severity(self, category: str) -> str:
        """Get severity level for a category."""
        priority = self.PRIORITY.get(category, 99)
        if priority <= 2:
            return "critical"
        elif priority <= 3:
            return "high"
        else:
            return "moderate"

crisis_detector = CrisisDetector()