import json
import re
import os

def load_rules():
    # Make sure we can find the rules.json file no matter where the server is run
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rules_path = os.path.join(current_dir, 'rules.json')
    
    with open(rules_path, 'r') as file:
        return json.load(file)

def evaluate_extracted_text(ocr_text: str):
    """
    Takes raw text from the OCR pipeline and checks it against rules.json.
    """
    tender_data = load_rules()
    evaluation_results = []
    overall_status = "VERIFIED"

    for rule in tender_data["mandatory_rules"]:
        # Set a default "Failed" template for each rule
        result = {
            "rule": rule["description"],
            "status": "FAILED",
            "extracted_value": "Evidence not found in document",
            "bounding_box": None, # Will be replaced when Teammate 2 finishes OCR
            "confidence_score": 0.0
        }

        # --- LOGIC 1: Keyword Search (e.g., ISO Certificates) ---
        if rule["operator"] == "contains":
            for keyword in rule["keywords"]:
                if keyword.lower() in ocr_text.lower():
                    result["status"] = "VERIFIED"
                    result["extracted_value"] = f"Found: {keyword}"
                    result["confidence_score"] = 0.98
                    # Mock bounding box for the UI until OCR is connected
                    result["bounding_box"] = {"x_min": 100, "y_min": 200, "x_max": 300, "y_max": 250}
                    break 

        # --- LOGIC 2: Strict Regex Match (e.g., GSTIN Numbers) ---
        elif rule["operator"] == "regex_match":
            pattern = rule["regex_pattern"]
            # Find all things that look like the regex pattern
            matches = re.findall(pattern, ocr_text)
            if matches:
                result["status"] = "VERIFIED"
                result["extracted_value"] = matches[0] # Grab the first valid match
                result["confidence_score"] = 0.99
                result["bounding_box"] = {"x_min": 400, "y_min": 600, "x_max": 550, "y_max": 620}

        # --- LOGIC 3: Financial/Number Extraction (e.g., Turnover >= 50L) ---
        elif rule["operator"] == ">=":
            # Look for numbers in the text (removes commas for safe checking)
            numbers_found = re.findall(r'\d+', ocr_text.replace(',', ''))
            for num_str in numbers_found:
                if int(num_str) >= rule["target_value"]:
                    result["status"] = "VERIFIED"
                    result["extracted_value"] = f"Value found: {num_str}"
                    result["confidence_score"] = 0.95
                    result["bounding_box"] = {"x_min": 150, "y_min": 800, "x_max": 250, "y_max": 820}
                    break

        # If any rule fails, the whole document is flagged for Review
        if result["status"] == "FAILED":
            overall_status = "Review Required"

        evaluation_results.append(result)

    return {
        "overall_status": overall_status,
        "rules_evaluated": evaluation_results
    }