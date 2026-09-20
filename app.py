import streamlit as st
import sqlite3
import json

conn = sqlite3.connect("lots.db", check_same_thread=False)

inspection_types = [
        "Temp Meter", "Underground Plumbing", "Floor Slab", "Sheathing",
        "Rough Plumb", "Rough Mech", "Rough Elec", "Framing", "Insulation",
        "Permanent Meter", "Final Plumb", "Final Mech", "Final Elec",
        "Final Building", "Certificate of Occupancy",
]

st.title("Lots Overview")
st.divider()

open_lots = conn.execute(
    "SELECT lot_number, address, inspections FROM lots WHERE closed = 0 ORDER BY lot_number"
).fetchall()

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

