# glow_by_splendour/products/ingredients.py

ingredient_database = [
    {
        "ingredient_name": "Salicylic Acid",
        "good_for": ["Oily", "Acne-Prone", "Combination"],
        "bad_for": ["Dry", "Sensitive"],
        "warning_message": "May cause dryness or irritation for sensitive or dry skin. Start with low concentration and less frequent use."
    },
    {
        "ingredient_name": "Benzoyl Peroxide",
        "good_for": ["Acne-Prone", "Oily"],
        "bad_for": ["Dry", "Sensitive"],
        "warning_message": "Can be very drying and may bleach fabrics. Introduce slowly. Not usually recommended for sensitive skin."
    },
    {
        "ingredient_name": "Alcohol Denat.",
        "good_for": ["Oily"], # Sometimes used in toners for quick drying
        "bad_for": ["Dry", "Sensitive", "Normal"], # Can be sensitizing for many
        "warning_message": "Can be drying and irritating, especially for dry, sensitive, or normal skin types. May disrupt skin barrier."
    },
    {
        "ingredient_name": "Fragrance",
        "good_for": [], # Generally not "good" for any specific type, but tolerated by some
        "bad_for": ["Sensitive", "All"], # Potential sensitizer for all, especially sensitive
        "warning_message": "Common sensitizer and can cause irritation or allergic reactions, especially for sensitive skin."
    },
    {
        "ingredient_name": "Retinol",
        "good_for": ["Oily", "Acne-Prone", "Normal", "Combination"], # Anti-aging, cell turnover
        "bad_for": ["Sensitive", "Dry"], # Requires careful introduction
        "warning_message": "Powerful ingredient. May cause irritation, redness, and peeling, especially when first starting or for sensitive/dry skin. Use SPF daily. Not recommended during pregnancy/breastfeeding without doctor's advice."
    },
    {
        "ingredient_name": "Hyaluronic Acid",
        "good_for": ["All", "Dry", "Oily", "Combination", "Normal", "Sensitive"],
        "bad_for": [],
        "warning_message": ""
    },
    {
        "ingredient_name": "Niacinamide",
        "good_for": ["All", "Oily", "Acne-Prone", "Sensitive", "Combination", "Normal"],
        "bad_for": [], # Generally well-tolerated, some may experience flushing at high concentrations
        "warning_message": "Generally well-tolerated, but high concentrations might cause temporary flushing in some individuals."
    },
    {
        "ingredient_name": "Vitamin C", # L-Ascorbic Acid and derivatives
        "good_for": ["All", "Oily", "Normal", "Combination", "Dry"],
        "bad_for": ["Sensitive"], # Pure L-Ascorbic Acid can be irritating
        "warning_message": "Potent forms (like L-Ascorbic Acid) can be irritating to sensitive skin. Consider gentler derivatives if sensitive."
    },
    {
        "ingredient_name": "Glycolic Acid",
        "good_for": ["Oily", "Normal", "Combination"], # Exfoliant
        "bad_for": ["Sensitive", "Dry"],
        "warning_message": "AHA; can cause irritation, sun sensitivity. Use with SPF. Not recommended for very sensitive skin or daily use initially for dry skin."
    },
    {
        "ingredient_name": "Lactic Acid",
        "good_for": ["Dry", "Normal", "Sensitive", "Combination"], # Milder AHA
        "bad_for": [], # Generally gentler than glycolic
        "warning_message": "Milder AHA, but still an exfoliant. Use with SPF. Patch test if very sensitive."
    },
    {
        "ingredient_name": "Sulfates", # e.g., Sodium Lauryl Sulfate (SLS), Sodium Laureth Sulfate (SLES)
        "good_for": ["Oily"], # Effective cleansers
        "bad_for": ["Dry", "Sensitive"],
        "warning_message": "Can be stripping and drying for the skin, potentially causing irritation for dry or sensitive types."
    },
    {
        "ingredient_name": "Parabens",
        "good_for": [],
        "bad_for": ["Sensitive", "All"], # Some concerns over endocrine disruption, though regulatory bodies deem many safe in cosmetics at current levels
        "warning_message": "Preservatives that some prefer to avoid due to potential for skin irritation and broader health concerns (though many are considered safe by regulatory agencies)."
    },
    {
        "ingredient_name": "Mineral Oil",
        "good_for": ["Dry", "Sensitive"], # Good occlusive
        "bad_for": ["Oily", "Acne-Prone"], # Can be comedogenic for some
        "warning_message": "Highly refined and generally safe, but can feel heavy and may be comedogenic for some oily or acne-prone skin types."
    },
    {
        "ingredient_name": "Tea Tree Oil",
        "good_for": ["Oily", "Acne-Prone"],
        "bad_for": ["Sensitive", "Dry"], # Can be sensitizing if used undiluted or in high concentrations
        "warning_message": "Can be effective for acne but may cause irritation or allergic reactions in some, especially if used undiluted or on sensitive/dry skin."
    },
    {
        "ingredient_name": "Shea Butter",
        "good_for": ["Dry", "Normal", "Sensitive"],
        "bad_for": ["Oily", "Acne-Prone"], # Can be comedogenic for some
        "warning_message": "Very moisturizing, but can be heavy and potentially comedogenic for oily or acne-prone skin."
    }
]

def check_ingredients(product_ingredients_list, user_skin_type):
    """
    Checks a list of product ingredients against the user's skin type for potential issues.
    Args:
        product_ingredients_list (list of str): A list of ingredient names.
        user_skin_type (str): The user's determined skin type (e.g., "Oily", "Sensitive - Dry").
    Returns:
        list of str: A list of warning messages for problematic ingredients.
    """
    warnings = []
    
    # Normalize user_skin_type for checking (e.g., "Sensitive - Dry" should check against "Sensitive" and "Dry")
    skin_type_parts = [s.strip() for s in user_skin_type.split(' - ')]
    skin_type_parts.append(user_skin_type) # Check against the full combined type as well if it exists as a category
    skin_type_parts.append("All") # "All" is a category for universal warnings like Fragrance

    for ingredient_name_in_product in product_ingredients_list:
        for db_entry in ingredient_database:
            # Case-insensitive matching for ingredient names
            if ingredient_name_in_product.lower() == db_entry["ingredient_name"].lower():
                # Check if any part of the user's skin type is in the bad_for list
                for part in skin_type_parts:
                    if part in db_entry["bad_for"]:
                        warning_msg = f"'{db_entry['ingredient_name']}': {db_entry['warning_message']}"
                        if warning_msg not in warnings: # Avoid duplicate warnings for the same ingredient
                            warnings.append(warning_msg)
                        break # Found a reason this ingredient is bad for this skin type part
    return warnings
