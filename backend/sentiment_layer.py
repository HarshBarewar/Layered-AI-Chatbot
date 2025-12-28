"""
Sentiment & Emotion Analysis Layer - Polarity detection and emotion classification
"""
from textblob import TextBlob

class SentimentLayer:
    """Handles sentiment analysis and emotion detection"""
    
    def __init__(self):
        # Emotion keyword mappings
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'love', 'enjoy'],
            'sadness': ['sad', 'depressed', 'unhappy', 'disappointed', 'upset', 'down', 'miserable'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'hate'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified', 'panic'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'unexpected', 'wow'],
            'disgust': ['disgusted', 'sick', 'revolted', 'appalled', 'repulsed', 'gross']
        }
    
    def analyze_polarity(self, text):
        """Analyze sentiment polarity using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Classify sentiment
        if polarity > 0.1:
            sentiment_label = 'positive'
        elif polarity < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment_label,
            'confidence': abs(polarity) if abs(polarity) > 0.1 else 0.5
        }
    
    def detect_emotions(self, text):
        """Detect specific emotions in text"""
        text_lower = text.lower()
        detected_emotions = []
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                emotion_scores[emotion] = score / len(keywords)
                detected_emotions.append(emotion)
        
        primary_emotion = max(emotion_scores.keys(), key=emotion_scores.get) if emotion_scores else None
        
        return {
            'emotions': detected_emotions,
            'emotion_scores': emotion_scores,
            'primary_emotion': primary_emotion
        }
    
    def get_tone_suggestions(self, sentiment_data):
        """Get tone suggestions for response based on sentiment"""
        sentiment = sentiment_data['sentiment']
        emotions = sentiment_data.get('emotions', [])
        
        tone_suggestions = {
            'empathy_level': 'medium',
            'enthusiasm_level': 'medium',
            'formality_level': 'medium',
            'supportiveness': 'medium'
        }
        
        # Adjust based on sentiment
        if sentiment == 'negative':
            tone_suggestions['empathy_level'] = 'high'
            tone_suggestions['supportiveness'] = 'high'
            tone_suggestions['enthusiasm_level'] = 'low'
        elif sentiment == 'positive':
            tone_suggestions['enthusiasm_level'] = 'high'
            tone_suggestions['empathy_level'] = 'medium'
        
        # Adjust based on specific emotions
        if 'anger' in emotions:
            tone_suggestions['empathy_level'] = 'high'
            tone_suggestions['formality_level'] = 'high'
            tone_suggestions['enthusiasm_level'] = 'low'
        elif 'sadness' in emotions:
            tone_suggestions['empathy_level'] = 'high'
            tone_suggestions['supportiveness'] = 'high'
        elif 'joy' in emotions:
            tone_suggestions['enthusiasm_level'] = 'high'
        elif 'fear' in emotions:
            tone_suggestions['supportiveness'] = 'high'
            tone_suggestions['empathy_level'] = 'high'
        
        return tone_suggestions
    
    def analyze(self, text):
        """Main sentiment analysis pipeline"""
        # Analyze polarity
        polarity_data = self.analyze_polarity(text)
        
        # Detect emotions
        emotion_data = self.detect_emotions(text)
        
        # Combine results
        sentiment_result = {
            'polarity': polarity_data['polarity'],
            'subjectivity': polarity_data['subjectivity'],
            'sentiment': polarity_data['sentiment'],
            'confidence': polarity_data['confidence'],
            'emotions': emotion_data['emotions'],
            'primary_emotion': emotion_data['primary_emotion'],
            'emotion_scores': emotion_data['emotion_scores']
        }
        
        # Get tone suggestions
        tone_suggestions = self.get_tone_suggestions(sentiment_result)
        sentiment_result['tone_suggestions'] = tone_suggestions
        
        return sentiment_result