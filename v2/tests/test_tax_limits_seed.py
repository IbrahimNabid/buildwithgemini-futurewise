import os
from google.cloud import firestore

PROJECT_ID = os.environ.get("PROJECT_ID", "qwiklabs-gcp-04-7459370ad109")
db = firestore.Client(project=PROJECT_ID)

tax_limits = {
    "year": 2026,
    "ira_limit": 7500.0,
    "ira_catchup_limit": 8500.0,
    "hsa_individual_limit": 4400.0,
    "hsa_family_limit": 8750.0,
    "401k_elective_limit": 23500.0,
    "standard_deduction_single": 15000.0,
    "standard_deduction_married": 30000.0,
    "source": "IRS Cost of Living Adjustments (Tax Year 2026)"
}

db.collection("tax_limits").document("2026").set(tax_limits)
print("tax_limits 2026 seeded successfully into Firestore!")
