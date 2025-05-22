import streamlit as st
import pandas as pd

# -------------------------------------------
# Streamlit App: Dashboard Dati SAP
# -------------------------------------------
st.set_page_config(page_title="Dashboard Dati SAP", layout="wide")

# Custom CSS (optional)
st.markdown(
    """
    <style>
      .main > .block-container { padding:1rem 2rem; }
      h1 { font-size:2rem; color:#4B5563; margin-bottom:0.5rem; }
      .sidebar .sidebar-content { background-color:#F9FAFB; padding:1rem; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------
# Sidebar: Upload del file SAP
# -------------------------------------------
with st.sidebar:
    st.markdown("## 📤 Carica File Dati SAP")
    sap_file = st.file_uploader("Excel Dati SAP", type=["xlsx", "xls"])

if not sap_file:
    st.sidebar.warning("Carica l'Excel Dati SAP nella sidebar per procedere.")
    st.stop()

# -------------------------------------------
# Caching data load
# -------------------------------------------
@st.cache_data
def load_excel(file):
    df = pd.read_excel(file, dtype=str)
    # Normalize column names
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace('[^0-9a-zA-Z_]', '', regex=True)
    )
    return df

# Load SAP data
df_sap = load_excel(sap_file)

# Identify material code column
def find_material_col(columns):
    for col in columns:
        if 'material' in col and 'code' in col:
            return col
    return None

material_col = find_material_col(df_sap.columns)

# -------------------------------------------
# Main: Filtri e visualizzazione
# -------------------------------------------
st.title("Dashboard Dati SAP")

# Prepare filtered dataframe
df_filtered = df_sap.copy()

st.markdown("### Filtri Dati SAP")

# Material Code first
if material_col:
    mat_label = material_col.replace('_', ' ').title()
    mat_vals = df_sap[material_col].dropna().unique().tolist()
    sel_mat = st.multiselect(f"Filtra {mat_label}", options=sorted(mat_vals), key="filter_material_code")
    if sel_mat:
        df_filtered = df_filtered[df_filtered[material_col].isin(sel_mat)]

# Other filters
for col in df_sap.columns:
    if col == material_col:
        continue
    vals = df_sap[col].dropna().unique().tolist()
    if 1 < len(vals) <= 100:
        label = col.replace('_', ' ').title()
        sel = st.multiselect(f"Filtra {label}", options=sorted(vals), key=f"filter_{col}")
        if sel:
            df_filtered = df_filtered[df_filtered[col].isin(sel)]

# Display results
st.dataframe(
    df_filtered.reset_index(drop=True),
    use_container_width=True
)
