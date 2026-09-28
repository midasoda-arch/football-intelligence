# backend/services/xg_calculator.py
import numpy as np
from typing import Dict, List, Optional

class XGCalculator:
    
    def predict_match_xg(
        self,
        home_features: Dict,
        away_features: Dict,
        h2h_data: List = None
    ) -> Dict:
        
        # xG de base
        home_xg = self._base_xg(home_features, is_home=True)
        away_xg = self._base_xg(away_features, is_home=False)
        
        # Ajustement H2H
        if h2h_data and len(h2h_data) >= 3:
            h2h_adj = self._h2h_adjustment(h2h_data)
            home_xg *= h2h_adj["home"]
            away_xg *= h2h_adj["away"]
        
        # Garde des valeurs réalistes
        home_xg = max(0.3, min(home_xg, 4.5))
        away_xg = max(0.2, min(away_xg, 4.0))
        
        # Probabilités Poisson
        probs = self._poisson_probs(home_xg, away_xg)
        
        return {
            "home_xg": round(home_xg, 2),
            "away_xg": round(away_xg, 2),
            "home_win_prob": round(probs["home_win"], 3),
            "draw_prob": round(probs["draw"], 3),
            "away_win_prob": round(probs["away_win"], 3),
            "predicted_score": f"{round(home_xg)}-{round(away_xg)}",
            "most_likely_scores": probs["top_scores"],
            "confidence": self._confidence(home_features, away_features),
            "key_factors": self._key_factors(home_features, away_features)
        }
    
    def _base_xg(self, features: Dict, is_home: bool) -> float:
        base = features.get("goals_for_avg", 1.5)
        shot_q = (
            features.get("shots_on_target_avg", 4.5) /
            max(features.get("shots_avg", 12), 1)
        )
        form = features.get("form_points", 6) / 15
        home_bonus = 0.12 if is_home else 0
        
        return base * (0.7 + 0.3 * shot_q) * (0.8 + 0.4 * form) + home_bonus
    
    def _h2h_adjustment(self, h2h_data: List) -> Dict:
        if not h2h_data:
            return {"home": 1.0, "away": 1.0}
        
        total = len(h2h_data)
        home_total_goals = sum(
            m.get("goals", {}).get("home") or 0 for m in h2h_data
        )
        away_total_goals = sum(
            m.get("goals", {}).get("away") or 0 for m in h2h_data
        )
        
        avg_home = home_total_goals / total
        avg_away = away_total_goals / total
        
        home_adj = 1.0 + (avg_home - 1.5) * 0.1
        away_adj = 1.0 + (avg_away - 1.2) * 0.1
        
        return {
            "home": max(0.85, min(home_adj, 1.15)),
            "away": max(0.85, min(away_adj, 1.15))
        }
    
    def _poisson_probs(
        self, 
        home_xg: float, 
        away_xg: float
    ) -> Dict:
        try:
            from scipy.stats import poisson
            
            max_g = 7
            home_win = draw = away_win = 0.0
            score_probs = {}
            
            for i in range(max_g + 1):
                for j in range(max_g + 1):
                    p = (
                        poisson.pmf(i, home_xg) * 
                        poisson.pmf(j, away_xg)
                    )
                    score_probs[f"{i}-{j}"] = round(float(p), 4)
                    if i > j: home_win += p
                    elif i == j: draw += p
                    else: away_win += p
            
            top_scores = sorted(
                score_probs.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                "home_win": float(home_win),
                "draw": float(draw),
                "away_win": float(away_win),
                "top_scores": [
                    {"score": s, "probability": p}
                    for s, p in top_scores
                ]
            }
        except ImportError:
            # Sans scipy - approximation simple
            total = home_xg + away_xg
            hw = home_xg / total * 0.6 + 0.15
            aw = away_xg / total * 0.6 + 0.05
            d = 1 - hw - aw
            
            return {
                "home_win": round(hw, 3),
                "draw": round(max(d, 0.1), 3),
                "away_win": round(aw, 3),
                "top_scores": [
                    {"score": f"{round(home_xg)}-{round(away_xg)}", 
                     "probability": 0.18}
                ]
            }
    
    def _confidence(
        self, 
        home_f: Dict, 
        away_f: Dict
    ) -> float:
        form_cert = (
            home_f.get("form_points", 6) + 
            away_f.get("form_points", 6)
        ) / 30
        return round(0.55 + 0.45 * form_cert, 2)
    
    def _key_factors(
        self, 
        home_f: Dict, 
        away_f: Dict
    ) -> List[str]:
        factors = []
        
        if home_f.get("form_points", 0) >= 12:
            factors.append("🔥 Home team in excellent form")
        elif home_f.get("form_points", 0) <= 3:
            factors.append("❄️ Home team in poor form")
        
        if away_f.get("form_points", 0) <= 3:
            factors.append("📉 Away team struggling")
        elif away_f.get("form_points", 0) >= 12:
            factors.append("⚡ Strong away team")
        
        if home_f.get("clean_sheets_pct", 0) >= 0.5:
            factors.append("🛡️ Solid home defense")
        
        if home_f.get("goals_for_avg", 0) >= 2.5:
            factors.append("⚽ High-scoring home team")
        
        if away_f.get("goals_against_avg", 0) >= 2.0:
            factors.append("🎯 Vulnerable away defense")
        
        if not factors:
            factors.append("⚖️ Balanced match expected")
        
        return factors