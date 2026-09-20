import streamlit as st
import sqlite3
import json

# --- Database setup ---
conn = sqlite3.connect("lots.db", check_same_thread=False)
conn.execute("""
    CREATE TABLE IF NOT EXISTS lots (
        lot_number TEXT PRIMARY KEY,
        address TEXT,
        homeowner_name TEXT,
        homeowner_email TEXT,
        inspections TEXT
    )
    """)
conn.commit()
try:
    conn.execute("ALTER TABLE lots ADD COLUMN closed INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

# --- Variables and information ---
st.title("Lot Inspection Tracker")
st.divider()

NEW_LOT_LABEL = "-- New lot --"


# --- Set an array of inspections that we want to store ---
inspection_types = [
    "Temp Meter", "Underground Plumbing", "Floor Slab", "Sheathing",
    "Rough Plumb", "Rough Mech", "Rough Elec", "Framing", "Insulation",
    "Permanent Meter", "Final Plumb", "Final Mech", "Final Elec",
    "Final Building", "Certificate of Occupancy",
]

# --- Pick an existing lot, or start a new one ---
existing_lot_numbers = [row[0] for row in conn.execute("SELECT lot_number FROM lots ORDER BY lot_Number").fetchall()]
selected = st.sidebar.selectbox("Select a lot", [NEW_LOT_LABEL] + existing_lot_numbers, key="lot_selector")

if selected != NEW_LOT_LABEL:
    row = conn.execute(
        "SELECT lot_number, address, homeowner_name, homeowner_email, inspections, closed FROM lots WHERE lot_number = ?",
        (selected,),
    ).fetchone()
else:
    row = None
if row is not None:
    existing_address = row[1]
    existing_name = row[2]
    existing_email = row[3]
    existing_inspections = json.loads(row[4])
else:
    existing_address = ""
    existing_name = ""
    existing_email = ""
    existing_inspections = {name: False for name in inspection_types}

# --- Form fields, keyed by the selected lot so they refresh when selection changes ---
row1 = st.columns(2)
with row1[0]:
    if selected == NEW_LOT_LABEL:
        lot_number = st.text_input("Lot number", value="", key=f"lotnum_{selected}")
    else:
        lot_number = selected
        st.subheader(f"Lot {lot_number}")
with row1[1]:
    address = st.text_input("Address", value=existing_address, key=f"address_{selected}")

row2 = st.columns(2)
with row2[0]:
    homeowner_name = st.text_input("Homeowner name", value=existing_name, key=f"homeowner_name{selected}")
with row2[1]:
    homeowner_email = st.text_input("Homeowner email", value=existing_email, key=f"homeowner_email{selected}")

# --- Create checkboxes for inspections ---
st.subheader("Inspections")
inspections = {}
checklist_cols = st.columns(3)
for i, name in enumerate(inspection_types):
    with checklist_cols[i % 3]:
        inspections[name] = st.checkbox(name, value=existing_inspections.get(name, False), key=f"{name}_{selected}")

completed = sum(inspections.values())
total = len(inspection_types)
st.write(f"{completed} of {total} inspections complete")
st.progress(completed/total)

existing_closed = bool(row[5]) if row is not None else False
closed = st.checkbox("Closed", value=existing_closed, key=f"closed_{selected}")
st.divider()

# --- Save/Delete input information ---
row3 = st.columns([1, 1, 1, 3])
with row3[0]:
    if st.button("Save lot"):
        if lot_number.strip() == "":
            st.error("Please do not try to enter a blank lot number.")

        else:
            conn.execute(
            """
            INSERT OR REPLACE INTO lots (lot_number, address, homeowner_name, homeowner_email, inspections, closed)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (lot_number, address, homeowner_name, homeowner_email, json.dumps(inspections), closed),
            )
            conn.commit()
            st.success(f"Saved lot {lot_number}")
            st.rerun()

with row3[1]:
    if selected != NEW_LOT_LABEL:
        def handle_delete():
            conn.execute("DELETE FROM lots where lot_number = ?", (lot_number,))
            conn.commit()
            st.session_state["lot_selector"] = NEW_LOT_LABEL

        with row3[1]:
            if selected != NEW_LOT_LABEL:
                st.button("Delete lot", on_click=handle_delete)

with row3[2]:
    if st.button("Overview"):
        st.switch_page("app.py")


# --- Raw output ---
#st.write(conn.execute("SELECT * FROM lots").fetchall())