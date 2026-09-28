# backend/services/ai_reporter.py
import httpx
import json
import os
from typing import Dict, List

class AIReporter:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.model = "openai/gpt-oss-120b"
        self.url = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key:
            print("⚠️ GROQ_API_KEY not set - AI reports will use demo mode")

    async def _call(self, prompt: str, max_tokens: int = 500) -> str:
        if not self.api_key:
            return self._demo_response(prompt)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self.url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": max_tokens
                    }
                )
                result = resp.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[AI Report unavailable: {str(e)}]"
    
    def _demo_response(self, prompt: str) -> str:
        return """
        🤖 AI Analysis (Demo Mode - Add GROQ_API_KEY for real analysis):
        
        This match promises to be an intense encounter between two 
        well-matched sides. Based on recent form and statistical data,
        we expect a competitive match with goals likely at both ends.
        
        Key factors: Home advantage, current form trajectory, and 
        head-to-head history all suggest a closely contested affair.
        
        Prediction: Both teams to score, with the home side having 
        a slight edge due to familiar surroundings.
        """
    
    async def generate_match_preview(
        self,
        home_team: str,
        away_team: str,
        prediction: Dict,
        h2h: Dict,
        home_form: str,
        away_form: str
    ) -> str:
        prompt = f"""
        You are an expert football analyst. Write a professional 
        match preview (150 words max) for:
        
        {home_team} vs {away_team}
        
        Data:
        - Home xG: {prediction.get('home_xg', 'N/A')}
        - Away xG: {prediction.get('away_xg', 'N/A')}
        - Home win: {prediction.get('home_win_prob', 0)*100:.0f}%
        - Draw: {prediction.get('draw_prob', 0)*100:.0f}%
        - Away win: {prediction.get('away_win_prob', 0)*100:.0f}%
        - Predicted: {prediction.get('predicted_score', 'N/A')}
        - Home form: {home_form}
        - Away form: {away_form}
        - H2H (last {h2h.get('total', 0)}): 
          {home_team} {h2h.get('home_wins', 0)}W - 
          {h2h.get('draws', 0)}D - 
          {h2h.get('away_wins', 0)}L
        
        Include: context, tactical analysis, key players, prediction.
        Be professional and data-driven.
        """
        return await self._call(prompt, max_tokens=300)
    
    async def generate_player_report(
        self, 
        player_data: Dict
    ) -> Dict:
        prompt = f"""
        Analyze this football player and return a JSON scout report.
        
        Player: {player_data.get('name', 'Unknown')}
        Team: {player_data.get('club', 'Unknown')}
        Position: {player_data.get('position', 'Unknown')}
        Season stats - Goals: {player_data.get('goals', 0)}, 
        Assists: {player_data.get('assists', 0)},
        Appearances: {player_data.get('appearances', 0)},
        Rating: {player_data.get('rating', 'N/A')}
        Form score: {player_data.get('form_score', 50)}/100
        
        Return ONLY valid JSON:
        {{
            "overall_rating": <1-100>,
            "potential": <1-100>,
            "strengths": ["str1", "str2"],
            "weaknesses": ["weak1"],
            "analysis": "<3 sentence analysis>",
            "recommendation": "Recommended/Monitor/Pass",
            "market_value": "<Xm€>"
        }}
        """
        result = await self._call(prompt, max_tokens=400)
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except Exception:
            pass
        return {
            "overall_rating": 72,
            "potential": 78,
            "strengths": ["Technical ability", "Goal scoring"],
            "weaknesses": ["Consistency"],
            "analysis": result[:200] if result else "Analysis pending",
            "recommendation": "Monitor",
            "market_value": "N/A"
        }