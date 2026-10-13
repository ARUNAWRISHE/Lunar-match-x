def make_decision(verification_results):
    inliers = verification_results.get("inliers", 0)
    ratio = verification_results.get("inlier_ratio", 0)
    
    reasons = []
    if inliers > 50 and ratio > 0.4:
        decision = "ACCEPT"
        reasons.append("Strong geometric consensus")
    elif inliers > 15:
        decision = "FLAG"
        reasons.append("Moderate geometric consensus, human review recommended")
    else:
        decision = "REFUSE"
        reasons.append("Insufficient geometrically verified inliers")
        
    return {
        "decision": decision,
        "reasons": reasons
    }
