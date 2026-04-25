"""
HITL Routing Logic
Implements preemptive_review & confidence-based routing as described in the manuscript.
"""
class HITLRouter:
    THRESHOLD_LOW = 0.5
    THRESHOLD_HIGH = 0.8

    @classmethod
    def should_route(cls, confidence: float, risk_level: str = "medium") -> dict:
        """Returns routing decision & rationale."""
        if risk_level == "high" or confidence < cls.THRESHOLD_LOW:
            return {
                "route_to_human": True,
                "pattern": "preemptive_review",
                "rationale": "High risk or low confidence triggers mandatory human oversight."
            }
        elif confidence < cls.THRESHOLD_HIGH:
            return {
                "route_to_human": True,
                "pattern": "confidence_based_routing",
                "rationale": "Moderate confidence requires expert validation before automation."
            }
        return {
            "route_to_human": False,
            "pattern": "auto_approved",
            "rationale": "High confidence & low risk. Proceeds automatically."
        }

if __name__ == "__main__":
    print(HITLRouter.should_route(0.4, risk_level="high"))
    print(HITLRouter.should_route(0.7, risk_level="medium"))
    print(HITLRouter.should_route(0.9, risk_level="low"))