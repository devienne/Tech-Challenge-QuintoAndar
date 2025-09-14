"""
Data models for QuintoAndar scraper
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import re


@dataclass
class PropertyInfo:
    """Data class to hold property information"""
    
    # Basic info
    url: str
    title: Optional[str] = None
    address_street: Optional[str] = None
    area: Optional[str] = None
    
    # Property details
    quartos: Optional[int] = None
    suite: int = 0
    banheiros: Optional[int] = None
    vagas: Optional[int] = None
    andar: Optional[str] = None
    
    # Features
    pet: str = "não"
    mobiliado: str = "sim"
    metro_proximo: str = "não"
    
    # Prices
    prices: Dict[str, str] = field(default_factory=dict)
    
    # Status
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame"""
        result = {
            "url": self.url,
            "status": self.status,
            "title": self.title,
            "address_street": self.address_street,
            "area": self.area,
            "quartos": self.quartos,
            "suite": self.suite,
            "banheiros": self.banheiros,
            "vagas": self.vagas,
            "andar": self.andar,
            "pet": self.pet,
            "mobiliado": self.mobiliado,
            "metro_proximo": self.metro_proximo,
        }
        
        # Add price information
        result.update(self.prices)
        
        return result
    
    @staticmethod
    def parse_number(text: str) -> Optional[int]:
        """Extract number from text"""
        if not text:
            return None
        m = re.search(r"(\d+)", text)
        return int(m.group(1)) if m else None
    
    @staticmethod
    def clean_area(text: str) -> Optional[str]:
        """Clean area text to standard format"""
        if not text:
            return None
        # Handle both regular space and non-breaking space
        text = text.replace("\xa0", " ")
        m = re.search(r"(\d+)\s*m²", text)
        return f"{m.group(1)} m²" if m else None
    
    def update_from_text(self, text: str) -> None:
        """Update property info from parsed text"""
        if not text:
            return
            
        text_lower = text.lower()
        
        # Area
        if "m²" in text and not self.area:
            self.area = self.clean_area(text)
        
        # Rooms
        elif "quarto" in text_lower:
            q = self.parse_number(text)
            if q is not None:
                self.quartos = q
            # Check for suite
            if "suíte" in text_lower or "suite" in text_lower:
                s_match = re.search(r"\((\d+)\s*su[ií]te", text, flags=re.IGNORECASE)
                self.suite = int(s_match.group(1)) if s_match else 1
        
        # Bathrooms
        elif "banheiro" in text_lower:
            b = self.parse_number(text)
            if b is not None:
                self.banheiros = b
        
        # Parking spots
        elif "vaga" in text_lower:
            v = self.parse_number(text)
            if v is not None:
                self.vagas = v
        
        # Floor
        elif "andar" in text_lower and self.andar is None:
            self.andar = text
        
        # Pet policy
        elif "aceita pet" in text_lower:
            self.pet = "sim"
        
        # Furniture
        elif "sem mobília" in text_lower or "sem mobiliá" in text_lower:
            self.mobiliado = "não"
        
        # Metro proximity
        elif "metrô" in text_lower:
            self.metro_proximo = "sim"

            