from __future__ import annotations

from typing import Dict


class NutrientScoredLayer:
    def recommend(self, disease: str, risk_level: str) -> Dict[str, list[str]]:
        plans = {
            "Common Cold": {
                "recommended": ["Warm soups", "Citrus fruits", "Ginger tea", "Protein-rich dal"],
                "avoid": ["Deep-fried foods", "Sugary drinks"],
                "notes": ["Prioritize hydration", "Increase vitamin C intake"],
            },
            "Influenza": {
                "recommended": ["Electrolyte fluids", "Oats", "Boiled vegetables", "Yogurt"],
                "avoid": ["Processed meat", "Cold sugary beverages"],
                "notes": ["Soft food for sore throat", "Adequate rest + fluids"],
            },
            "COVID-19": {
                "recommended": ["High-protein meals", "Vitamin D sources", "Zinc-rich nuts", "Anti-inflammatory foods"],
                "avoid": ["Highly processed foods", "Excess sugar"],
                "notes": ["Monitor hydration", "Small frequent meals if fatigued"],
            },
            "Gastroenteritis": {
                "recommended": ["ORS", "Banana", "Rice", "Steamed apple"],
                "avoid": ["Spicy foods", "Milk (acute phase)", "High-fat meals"],
                "notes": ["Low-fiber bland diet initially", "Rehydrate aggressively"],
            },
            "Migraine": {
                "recommended": ["Magnesium-rich seeds", "Whole grains", "Leafy greens"],
                "avoid": ["Aged cheese", "Excess caffeine", "Alcohol"],
                "notes": ["Keep regular meal timings", "Track trigger foods"],
            },
            "Type 2 Diabetes Alert": {
                "recommended": ["Low-GI grains", "Lean proteins", "Legumes", "Non-starchy vegetables"],
                "avoid": ["Refined sugar", "Sweetened beverages", "Trans fats"],
                "notes": ["Balanced carbohydrate distribution", "Portion control"],
            },
        }

        selected = plans.get(disease, {
            "recommended": ["Balanced plate", "Seasonal fruits", "Adequate protein"],
            "avoid": ["Ultra-processed foods"],
            "notes": ["Consult a registered dietitian for personalization"],
        })

        if risk_level in {"High", "Critical"}:
            selected = {
                "recommended": selected["recommended"] + ["Easily digestible meals"],
                "avoid": selected["avoid"] + ["Large heavy meals"],
                "notes": selected["notes"] + ["Seek medical supervision promptly"],
            }

        return selected
