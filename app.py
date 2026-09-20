import streamlit as st
import psycopg2
import json

conn = psycopg2.connect(
    host=st.secrets["postgres"]["host"],
    port=st.secrets["postgres"]["port"],
    dbname=st.secrets["postgres"]["dbname"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
)

cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS lots (
        lot_number TEXT PRIMARY KEY,
        address TEXT,
        homeowner_name TEXT,
        homeowner_email TEXT,
        inspections TEXT,
        closed BOOLEAN DEFAULT FALSE
    )
""")
conn.commit()

inspection_types = [
        "Temp Meter", "Underground Plumbing", "Floor Slab", "Sheathing",
        "Rough Plumb", "Rough Mech", "Rough Elec", "Framing", "Insulation",
        "Permanent Meter", "Final Plumb", "Final Mech", "Final Elec",
        "Final Building", "Certificate of Occupancy",
]

st.title("Lots Overview")
st.divider()

cur.execute(
    "SELECT lot_number, address, inspections FROM lots WHERE NOT closed ORDER BY lot_number"
)
open_lots = cur.fetchall()

if not open_lots:
    st.write("No open lots right now.")
else:
    cols = st.columns(3)
    for i, (lot_number, address, inspections_json) in enumerate(open_lots):
        inspections = json.loads(inspections_json)
        completed = sum(inspections.values())
        total = len(inspection_types)

        with cols[i % 3]:
            st.subheader(f"Lot {lot_number}")
            st.write(address)
            st.progress(completed / total)
            st.write(f"{completed} or {total} inspections complete")
            if st.button("Open", key=f"view_{lot_number}"):
                st.session_state["lot_selector"] = lot_number
                st.switch_page("pages/1_Lot_Details.py")
            st.divider()

