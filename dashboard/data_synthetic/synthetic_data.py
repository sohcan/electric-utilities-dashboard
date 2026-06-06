import pandas as pd
import numpy as np
import random

# Re-run the exact generator pipeline so we have the clean dataset to inject into
SEED = 541
np.random.seed(SEED)
random.seed(SEED)

fake_utilities = ['GridPower Corp', 'Apex Electric Co.', 'Metro Utility Partners', 'Northern Lights Power', 'Sovereign Energy', 'EcoGrid Utilities']
locations = ['Site Alpha', 'Site Bravo', 'Springfield', 'Echo Training Ground', 'Centerville Training Site', 'Springfield Armory', 'Foxtrot Maneuver Site', 'Fairview Proving Ground']

num_meters = random.randint(11,31)
fake_meters = sorted(random.sample(range(100000, 999999), num_meters))

fake_loc_rows = []
for m in fake_meters:
    util = random.choice(fake_utilities)
    acct = f"ACCT-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
    addr = f"{random.randint(100, 999)} {random.choice(['Quantum Rd', 'Cyber Dr', 'Innovation Way', 'Sector Blvd', 'Fortress Lane'])}"
    loc = random.choice(locations)
    fake_loc_rows.append({
        'Utility_Company': util,
        'Account': acct,
        'Service_Address': addr,
        'Meter_Char': str(m),
        'Meter': m,
        'Location': loc
    })

df_fake_loc = pd.DataFrame(fake_loc_rows)
date_range = pd.date_range(start='2023-10-01', end='2025-12-01', freq='MS')

fake_ts_rows = []
for m in fake_meters:
    base_kwh = np.random.randint(5000, 200000)
    rate = np.random.uniform(0.08, 0.22) 
    
    for d in date_range:
        month = d.month
        season_mult = 1.0 + 0.3 * np.sin(2 * np.pi * (month - 4) / 12) + np.random.normal(scale=0.08)
        kwh = max(100, int(base_kwh * season_mult))
        usd = round(kwh * rate * np.random.uniform(0.97, 1.03), 2)
        
        if random.random() < 0.04:
            kwh = 0
            usd = 0.0
            
        fake_ts_rows.append({
            'Meter': m,
            'Date': d.strftime('%-m/%d/%Y'),
            'KWH': kwh,
            'USD': usd
        })

df_fake_ts = pd.DataFrame(fake_ts_rows)

print(f"Synthesized: {num_meters} fake meters across {len(date_range)} months for {len(df_fake_ts)} readings")

# 'plausible' operational spikes, instead of 'plausible' data-entry error

df_fake_ts["Event_Type"] = "Normal"
df_fake_ts["Event_Note"] = ""

real_event_notes = [
    "Heat Wave",
    "Training Event",
    "Equipment commissioning",
    "Operational Event",
    "Maintenance testing",
]

for i in range(random.randint(2, 5)):
    row_idx = random.randint(0, len(df_fake_ts) - 1)

    original_kwh = df_fake_ts.loc[row_idx, "KWH"]
    original_usd = df_fake_ts.loc[row_idx, "USD"]

    #Skip zero-reading rows so this represents a real high-use event
    if original_kwh <= 0 or original_usd <= 0:
        continue

    event_multiplier = np.random.uniform(1.33, 2.33)

    new_kwh = int(original_kwh * event_multiplier)
    new_usd = round(original_usd * event_multiplier * np.random.uniform(0.98, 1.04), 2)

    df_fake_ts.loc[row_idx, "KWH"] = new_kwh
    df_fake_ts.loc[row_idx, "USD"] = new_usd
    df_fake_ts.loc[row_idx, "Event_Type"] = "Operational Spike"
    df_fake_ts.loc[row_idx, "Event_Note"] = random.choice(real_event_notes)

    event_meter = df_fake_ts.loc[row_idx, "Meter"]
    event_date = df_fake_ts.loc[row_idx, "Date"]
    event_note = df_fake_ts.loc[row_idx, "Event_Note"]

    print(
        f"Spike Injected: Meter {event_meter} on {event_date}. "
        f"KWH changed from {original_kwh} to {new_kwh}. "
        f"USD changed from ${original_usd} to ${new_usd}. "
        f"Reason: {event_note}"
    )

#Missing Decimal Point (Typo)
for i in range(0,random.randint(2,3)):
    row_idx_1 = random.randint(0,len(df_fake_ts)-1)
    original_kwh = df_fake_ts.loc[row_idx_1, 'KWH']
    original_usd = df_fake_ts.loc[row_idx_1, 'USD']
    
    #Simulate missing decimal point by multiplying USD by 100 (eg. 1540.50 -> 154050.00)
    df_fake_ts.loc[row_idx_1, 'USD'] = round(original_usd * 100, 2)
    corrupted_meter_1 = df_fake_ts.loc[row_idx_1, 'Meter']
    corrupted_date_1 = df_fake_ts.loc[row_idx_1, 'Date']

    print(f"Bad Entry Typo Injected: Meter {corrupted_meter_1} on {corrupted_date_1}. USD changed from ${original_usd} to ${df_fake_ts.loc[row_idx_1, 'USD']}")


#Extra Zero on KWH
for i in range(0,random.randint(1,3)):
    row_idx_2 = random.randint(0,len(df_fake_ts)-1)
    original_kwh_2 = df_fake_ts.loc[row_idx_2, 'KWH']
    #Multiply KWH by 10 (ie. adding an extra zero at the end of the number)
    df_fake_ts.loc[row_idx_2, 'KWH'] = original_kwh_2 * 10
    corrupted_meter_2 = df_fake_ts.loc[row_idx_2, 'Meter']
    corrupted_date_2 = df_fake_ts.loc[row_idx_2, 'Date']

    print(f"Bad Entry Typo Injected: Meter {corrupted_meter_2} on {corrupted_date_2}. KWH changed from {original_kwh_2} to {df_fake_ts.loc[row_idx_2, 'KWH']}")



# Save both to local environment (overwriting previous ones)
df_fake_loc.to_csv("Utilities_Fun_Loc.csv", index=False)
df_fake_ts.to_csv("Utilities_Fun.csv", index=False)

