# backend/services/player_form.py
import numpy as np
from typing import List, Dict

class PlayerFormAnalyzer:
    
    def calculate_form_score(
        self, 
        recent_matches: List[Dict]
    ) -> Dict:
        if not recent_matches:
            return {
                "form_score": 50.0,
                "trend": "stable",
                "category": "Average",
                "emoji": "😐"
            }
        
        scores = []
        details = []
        
        for i, match in enumerate(recent_matches[-5:]):
            score = self._score_match(match)
            weight = 1.0 + (i * 0.15)
            scores.append(score * weight)
            
            details.append({
                "match_number": i + 1,
                "goals": match.get("goals", 0),
                "assists": match.get("assists", 0),
                "rating": match.get("rating", 6.5),
                "minutes": match.get("minutes", 90),
                "score": round(score, 1)
            })
        
        avg_score = np.mean(scores) if scores else 50.0
        form_score = float(min(max(avg_score, 0), 100))
        
        return {
            "form_score": round(form_score, 1),
            "trend": self._trend(scores),
            "category": self._category(form_score),
            "emoji": self._emoji(form_score),
            "last_matches": details,
            "goals_last5": sum(
                m.get("goals", 0) for m in recent_matches[-5:]
            ),
            "assists_last5": sum(
                m.get("assists", 0) for m in recent_matches[-5:]
            ),
            "avg_rating": round(
                np.mean([
                    m.get("rating", 6.5) 
                    for m in recent_matches[-5:]
                ]), 2
            )
        }
    
    def _score_match(self, match: Dict) -> float:
        score = 50.0
        score += min(match.get("goals", 0) * 15, 30)
        score += min(match.get("assists", 0) * 8, 15)
        
        rating = float(match.get("rating") or 6.5)
        score += (rating - 6.0) * 7
        
        minutes = match.get("minutes", 90)
        if minutes < 30: score *= 0.4
        elif minutes < 60: score *= 0.7
        elif minutes < 75: score *= 0.9
        
        score -= match.get("yellow_cards", 0) * 8
        score -= match.get("red_cards", 0) * 25
        
        return float(min(max(score, 0), 100))
    
    def _trend(self, scores: List[float]) -> str:
        if len(scores) < 2:
            return "stable"
        mid = len(scores) // 2
        first = np.mean(scores[:mid]) if mid > 0 else scores[0]
        second = np.mean(scores[mid:])
        diff = second - first
        if diff > 8: return "improving 📈"
        if diff < -8: return "declining 📉"
        return "stable ➡️"
    
    def _category(self, score: float) -> str:
        if score >= 80: return "Excellent"
        if score >= 65: return "Good"
        if score >= 50: return "Average"
        if score >= 35: return "Poor"
        return "Very Poor"
    
    def _emoji(self, score: float) -> str:
        if score >= 80: return "🔥"
        if score >= 65: return "✅"
        if score >= 50: return "😐"
        if score >= 35: return "⚠️"
        return "❌"