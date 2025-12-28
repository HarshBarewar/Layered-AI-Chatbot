"""
Preprocessing Layer - Text cleaning and normalization
"""
import re
import string

class PreprocessingLayer:
    """Handles text preprocessing and cleaning"""
    
    def __init__(self):
        self.contractions = {
            "won't": "will not", "can't": "cannot", "n't": " not",
            "'re": " are", "'ve": " have", "'ll": " will",
            "'d": " would", "'m": " am"
        }
    
    def clean_text(self, text):
        """Clean and normalize input text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Expand contractions
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()
    
    def tokenize(self, text):
        """Simple tokenization"""
        cleaned_text = self.clean_text(text)
        tokens = cleaned_text.split()
        return [token for token in tokens if len(token) > 1]
    
    def remove_stopwords(self, tokens):
        """Remove common stopwords"""
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        return [token for token in tokens if token not in stopwords]
    
    def spell_correct(self, text):
        """Basic spell correction (simplified)"""
        # Simple corrections for common mistakes
        corrections = {
            'teh': 'the', 'adn': 'and', 'taht': 'that',
            'waht': 'what', 'hwo': 'how', 'whne': 'when'
        }
        
        words = text.split()
        corrected_words = [corrections.get(word, word) for word in words]
        return ' '.join(corrected_words)
    
    def preprocess(self, text):
        """Main preprocessing pipeline"""
        if not text:
            return {
                'original': '',
                'cleaned': '',
                'tokens': [],
                'filtered_tokens': []
            }
        
        # Step 1: Basic spell correction
        spell_corrected = self.spell_correct(text)
        
        # Step 2: Clean text
        cleaned = self.clean_text(spell_corrected)
        
        # Step 3: Tokenize
        tokens = self.tokenize(cleaned)
        
        # Step 4: Remove stopwords
        filtered_tokens = self.remove_stopwords(tokens)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens
        }