# glow_by_splendour/routines/routine_generator.py
import csv
import os
import random
from glow_by_splendour.products import ingredients as ing_check

PRODUCT_DATABASE_FILE = '/app/glow_by_splendour/data/product_database.csv'

# --- Load Product Database ---
PRODUCTS_BY_CATEGORY = {}

def load_products():
    """Loads products from CSV into a structured dictionary."""
    global PRODUCTS_BY_CATEGORY
    PRODUCTS_BY_CATEGORY = {} # Reset before loading
    if not os.path.exists(PRODUCT_DATABASE_FILE):
        print(f"Warning: Product database file not found at {PRODUCT_DATABASE_FILE}")
        return

    try:
        with open(PRODUCT_DATABASE_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row['category']
                if category not in PRODUCTS_BY_CATEGORY:
                    PRODUCTS_BY_CATEGORY[category] = []
                
                # Convert comma-separated ingredients string to a list
                product_ingredients_list = [item.strip() for item in row.get('ingredients', '').split(',') if item.strip()]
                row['ingredients_list'] = product_ingredients_list
                
                PRODUCTS_BY_CATEGORY[category].append(row)
    except Exception as e:
        print(f"Error loading product database: {e}")

load_products() # Load products when module is imported

# --- Routine Templates (Simpler: just step names/categories now) ---
routine_step_categories = {
    "Oily": {
        "AM": ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"],
        "PM": ["Cleanser", "Toner", "Serum", "Moisturizer"]
    },
    "Dry": {
        "AM": ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"],
        "PM": ["Cleanser", "Toner", "Serum", "Moisturizer"]
    },
    "Combination": {
        "AM": ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"],
        "PM": ["Cleanser", "Toner", "Serum", "Moisturizer"]
    },
    "Normal": {
        "AM": ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"],
        "PM": ["Cleanser", "Toner", "Serum", "Moisturizer"]
    },
    "Sensitive": {
        "AM": ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"],
        "PM": ["Cleanser", "Toner", "Serum", "Moisturizer"]
    }
}

# Generate "Sensitive - <OtherType>" templates
for skin_type_key in list(routine_step_categories.keys()):
    if skin_type_key != "Sensitive" and f"Sensitive - {skin_type_key}" not in routine_step_categories:
        sensitive_variant_key = f"Sensitive - {skin_type_key}"
        # For now, sensitive variants will use the same step categories as the base "Sensitive" type
        # Product selection will later filter by the full "Sensitive - <OtherType>"
        routine_step_categories[sensitive_variant_key] = routine_step_categories["Sensitive"]


def find_suitable_product(category, user_skin_type, current_products_in_routine):
    """
    Finds a suitable product from PRODUCTS_BY_CATEGORY.
    Args:
        category (str): e.g., "Cleanser", "Moisturizer".
        user_skin_type (str): e.g., "Oily", "Sensitive - Dry".
        current_products_in_routine (list of str): product_ids already in this specific routine.
    Returns:
        dict (product) or None
    """
    if not PRODUCTS_BY_CATEGORY: load_products() # Ensure products are loaded

    if category not in PRODUCTS_BY_CATEGORY:
        return None

    suitable_products = []
    user_skin_type_parts = [s.strip().lower() for s in user_skin_type.split(' - ')]
    user_skin_type_parts.append(user_skin_type.lower()) # also check full type "sensitive - dry"

    for product in PRODUCTS_BY_CATEGORY[category]:
        if product['product_id'] in current_products_in_routine:
            continue # Skip if product already used in this routine to avoid duplicates

        # Check skin type suitability
        # Product suitability can be "All" or a comma-separated list
        product_suitability = [s.strip().lower() for s in product['skin_type_suitability'].split(',')]
        
        match = False
        if "all" in product_suitability:
            match = True
        else:
            # Check if any part of the user's skin type matches any part of the product's suitability
            if any(ust_part in product_suitability for ust_part in user_skin_type_parts):
                match = True
            # Specific handling for "Sensitive - <Type>"
            # If user is "Sensitive - Dry", a product for "Sensitive" OR "Dry" should be considered.
            # If user is "Sensitive", product for "Sensitive" or "All"
            elif "sensitive" in user_skin_type_parts and "sensitive" in product_suitability:
                 match = True


        if match:
            suitable_products.append(product)
    
    if suitable_products:
        return random.choice(suitable_products) # Pick a random one
    return None


def generate_routine(skin_type, time_of_day):
    """
    Generates a skincare routine with specific products and ingredient warnings.
    Args:
        skin_type (str): e.g., "Oily", "Sensitive - Dry".
        time_of_day (str): "AM" or "PM".
    Returns:
        list of dicts: [{"step_name": "...", "product": product_dict, "warnings": [...]}, ...] or None
    """
    if not PRODUCTS_BY_CATEGORY:
        load_products()
        if not PRODUCTS_BY_CATEGORY: # Still no products after attempting reload
             print("Warning: Product database is empty. Cannot generate routines with products.")
             return [] # Return empty list if product DB is not loaded

    # Normalize skin_type for template lookup
    normalized_skin_type = skin_type
    skin_type_parts_for_template = skin_type.split(' - ')
    if len(skin_type_parts_for_template) == 2 and skin_type_parts_for_template[0] == "Sensitive":
        # Try to match "Sensitive - Dry", "Sensitive - Normal", etc. for template keys
        # Capitalize the second part if it's a base type
        base_type_capitalized = skin_type_parts_for_template[1].capitalize()
        formatted_template_key = f"Sensitive - {base_type_capitalized}"
        if formatted_template_key in routine_step_categories:
            normalized_skin_type = formatted_template_key
        else: # Fallback to just "Sensitive" if specific combo template not defined
            normalized_skin_type = "Sensitive"
    elif skin_type not in routine_step_categories: # If not a sensitive combo, and not a direct match
        normalized_skin_type = "Normal" # Default to "Normal" if skin_type is unknown

    if time_of_day.upper() not in ["AM", "PM"]:
        return None

    step_categories = routine_step_categories.get(normalized_skin_type, {}).get(time_of_day.upper())
    if not step_categories:
        return [] # No steps defined for this skin type/time

    generated_routine = []
    current_product_ids_in_routine = [] # To avoid suggesting the same product multiple times in one routine

    for category_as_step_name in step_categories:
        product = find_suitable_product(category_as_step_name, skin_type, current_product_ids_in_routine)
        
        if product:
            warnings = ing_check.check_ingredients(product['ingredients_list'], skin_type)
            generated_routine.append({
                "step_name": category_as_step_name, # e.g. "Cleanser"
                "product_name": product['product_name'],
                "brand": product['brand'],
                "product_id": product['product_id'], # For potential future linking
                "warnings": warnings
            })
            current_product_ids_in_routine.append(product['product_id'])
        else:
            # No product found, suggest a generic category type or skip
            generated_routine.append({
                "step_name": category_as_step_name,
                "product_name": f"Suitable {category_as_step_name} for {skin_type}",
                "brand": "Generic/Not Found",
                "product_id": None,
                "warnings": ["Could not find a specific product in the database. Please add more products or check suitability criteria."]
            })
            
    return generated_routine
