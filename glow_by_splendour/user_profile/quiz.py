# glow_by_splendour/user_profile/quiz.py

quiz_questions = [
    {
        "id": "q1",
        "text": "How does your skin feel an hour after cleansing (without applying any products)?",
        "options": {
            "a": "Tight, dry, or flaky",  # Dry
            "b": "Oily or shiny, especially in the T-zone (forehead, nose, chin)", # Oily
            "c": "Comfortable and balanced, not too oily or dry", # Normal
            "d": "Oily in some areas (like the T-zone) and dry or normal in others (like cheeks)" # Combination
        }
    },
    {
        "id": "q2",
        "text": "How often do you experience breakouts or acne?",
        "options": {
            "a": "Rarely, if ever", # Normal / Dry
            "b": "Often, and they can be widespread", # Oily
            "c": "Sometimes, perhaps related to stress or hormonal changes", # Normal / Combination
            "d": "Mostly in the T-zone" # Combination / Oily
        }
    },
    {
        "id": "q3",
        "text": "How does your skin typically react to new skincare products?",
        "options": {
            "a": "Often experiences redness, itching, burning, or rashes", # Sensitive
            "b": "Sometimes experiences mild irritation, but it subsides", # Sensitive / Combination
            "c": "Rarely has any negative reactions", # Normal / Oily / Dry
        }
    },
    {
        "id": "q4",
        "text": "How visible are your pores?",
        "options": {
            "a": "Large, open, and visible all over", # Oily
            "b": "Small and not very noticeable", # Dry / Normal
            "c": "Visible and perhaps larger in the T-zone, but smaller on cheeks", # Combination
            "d": "Noticeable, and skin can sometimes feel congested" # Oily / Combination
        }
    },
    {
        "id": "q5",
        "text": "After washing your face, if you don't apply moisturizer, how long does it take for your skin to feel like it needs hydration?",
        "options": {
            "a": "Immediately or within a few minutes", # Dry
            "b": "After a few hours, or it might not feel like it needs it at all", # Oily
            "c": "It feels fine for a good while, maybe an hour or two", # Normal
            "d": "Cheeks feel tight quickly, but T-zone remains okay or gets oily" # Combination
        }
    },
    {
        "id": "q6", # Added for better sensitive skin detection
        "text": "Does your skin often flush or turn red when exposed to sun, spicy foods, or stress?",
        "options": {
            "a": "Yes, very easily and noticeably", # Sensitive
            "b": "Sometimes, but not excessively", # Sensitive / Normal
            "c": "Rarely or never" # Normal / Oily / Dry
        }
    }
]

def determine_skin_type(answers):
    """
    Determines skin type based on quiz answers.
    This is a simplified rule-based system.
    Input: answers - a dictionary like {'q1': 'a', 'q2': 'b', ...}
    """
    scores = {"Oily": 0, "Dry": 0, "Combination": 0, "Normal": 0, "Sensitive": 0}

    # Question 1: Feel after cleansing
    if answers.get('q1') == 'a':
        scores["Dry"] += 2
    elif answers.get('q1') == 'b':
        scores["Oily"] += 2
    elif answers.get('q1') == 'c':
        scores["Normal"] += 2
    elif answers.get('q1') == 'd':
        scores["Combination"] += 2

    # Question 2: Breakouts
    if answers.get('q2') == 'a':
        scores["Normal"] += 1
        scores["Dry"] += 1
    elif answers.get('q2') == 'b':
        scores["Oily"] += 2
    elif answers.get('q2') == 'c':
        scores["Normal"] += 1
        scores["Combination"] += 1
    elif answers.get('q2') == 'd':
        scores["Combination"] += 1
        scores["Oily"] += 1

    # Question 3: Reaction to new products
    if answers.get('q3') == 'a':
        scores["Sensitive"] += 3 # Strong indicator
    elif answers.get('q3') == 'b':
        scores["Sensitive"] += 1
        # scores["Combination"] += 1 # Mild sensitivity can occur with other types
    elif answers.get('q3') == 'c':
        scores["Normal"] += 1 # Robust skin

    # Question 4: Pore visibility
    if answers.get('q4') == 'a':
        scores["Oily"] += 2
    elif answers.get('q4') == 'b':
        scores["Dry"] += 1
        scores["Normal"] += 1
    elif answers.get('q4') == 'c':
        scores["Combination"] += 2
    elif answers.get('q4') == 'd': # Noticeable and congested
        scores["Oily"] += 1
        scores["Combination"] += 1


    # Question 5: Need for hydration
    if answers.get('q5') == 'a':
        scores["Dry"] += 2
    elif answers.get('q5') == 'b':
        scores["Oily"] += 1 # Oily skin might still need hydration but feels less urgent
    elif answers.get('q5') == 'c':
        scores["Normal"] += 1
    elif answers.get('q5') == 'd':
        scores["Combination"] += 2
        scores["Dry"] += 1 # Cheeks are dry

    # Question 6: Flushing/Redness
    if answers.get('q6') == 'a':
        scores["Sensitive"] += 2
    elif answers.get('q6') == 'b':
        scores["Sensitive"] += 1

    # Determine primary skin type
    # If Sensitive has a high score, it's often a primary concern
    if scores["Sensitive"] >= 3:
        # Check if another type is also prominent along with sensitive
        # Create a copy of scores without "Sensitive" to find the underlying type
        other_scores = {k: v for k, v in scores.items() if k != "Sensitive"}
        if any(v > 0 for v in other_scores.values()): # Check if there are any other scores
            underlying_type = max(other_scores, key=other_scores.get)
            if scores[underlying_type] >= 2 : # Ensure the underlying type is significant enough
                 # Avoid "Sensitive-Sensitive"
                if underlying_type == "Sensitive":
                    return "Sensitive"
                return f"Sensitive - {underlying_type}"
        return "Sensitive" # If no other type is significant

    # If not primarily sensitive, find the highest score among other types
    # Remove sensitive from consideration if it wasn't the primary type
    non_sensitive_scores = {k:v for k,v in scores.items() if k != "Sensitive"}
    if not non_sensitive_scores or all(v == 0 for v in non_sensitive_scores.values()): # handle case where all scores are 0
        return "Normal" # Default or perhaps "Undetermined"

    determined_type = max(non_sensitive_scores, key=non_sensitive_scores.get)

    # Refinement for Combination
    # If Combination is high, but Oily or Dry is also similarly high, it's still Combination.
    # If Oily and Dry are roughly equal and high, it's Combination.
    if determined_type != "Combination":
        if scores["Combination"] >= 2 and (scores["Oily"] > 1 or scores["Dry"] > 1) :
            # If combination score is significant and either oily or dry parts are also significant
             if abs(scores["Oily"] - scores["Dry"]) <=1 and scores["Combination"] >= max(scores["Oily"], scores["Dry"]):
                return "Combination" # More nuanced combination
    
    # If scores are very close for Normal, Oily, Dry, and Combination is not dominant
    if determined_type == "Normal" and scores["Normal"] < 2 : # If normal score is low
        # Check if other types have higher or equal scores
        if scores["Oily"] > scores["Normal"] : return "Oily"
        if scores["Dry"] > scores["Normal"] : return "Dry"
        if scores["Combination"] > scores["Normal"] : return "Combination"


    # Fallback if all scores are very low or zero (should be rare with current scoring)
    if all(score < 1 for score in non_sensitive_scores.values()):
        return "Normal" # Default if no clear indication

    return determined_type
