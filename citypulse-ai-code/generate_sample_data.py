"""
Generates a synthetic starter dataset of community reports so the
CityPulse AI dashboard has data to show immediately, even before any
live submissions come in. Run once: `python generate_sample_data.py`
"""
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

AREAS = ["Adajan", "Vesu", "Katargam", "Varachha", "City Light", "Piplod", "Ghod Dod Road"]
CATEGORIES = ["Roads & Potholes", "Waste Management", "Water Supply", "Street Lighting",
              "Public Safety", "Traffic & Mobility", "Parks & Environment", "Noise/Nuisance"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "In Progress", "Resolved"]

TEMPLATES = [
    "Large pothole causing traffic slowdown near {area} main road",
    "Garbage not collected for 3 days in {area}",
    "Water pipeline leakage flooding the street in {area}",
    "Streetlights not working, area is dark and unsafe at night in {area}",
    "Reports of unsafe stray dog activity near school in {area}",
    "Heavy traffic congestion during peak hours in {area}",
    "Public park in {area} needs maintenance, broken benches",
    "Loud construction noise early morning disturbing residents in {area}",
    "Open manhole is a safety hazard in {area}",
    "Illegal dumping of waste near the drainage in {area}",
]

rows = []
start = datetime.now() - timedelta(days=45)
for i in range(220):
    area = random.choice(AREAS)
    category = random.choice(CATEGORIES)
    template = random.choice(TEMPLATES)
    text = template.format(area=area)
    priority = random.choices(PRIORITIES, weights=[35, 35, 20, 10])[0]
    status = random.choices(STATUSES, weights=[40, 35, 25])[0]
    date = start + timedelta(days=random.randint(0, 45), hours=random.randint(0, 23))
    rows.append({
        "report_id": f"CP{1000+i}",
        "timestamp": date.strftime("%Y-%m-%d %H:%M"),
        "area": area,
        "category": category,
        "description": text,
        "priority": priority,
        "status": status,
    })

df = pd.DataFrame(rows).sort_values("timestamp")
df.to_csv("community_reports.csv", index=False)
print(f"Generated {len(df)} sample reports -> community_reports.csv")
