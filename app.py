# app.py
from asyncio import wait
import json
from time import time
import networkx as nx
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile

st.set_page_config(layout="wide", page_title="DSAI Cliques")

# ---- Load JSON data ----
with open("network.json", "r", encoding="utf-8") as f:
    data = json.load(f)

people = data["people"]
rels = data["relationships"]

# ---- Build graph ----
G = nx.Graph()

for person in people:
    G.add_node(
        person["id"],
        label=person["name"],
        origin=person.get("origin", "")
    )

for rel in rels:
    G.add_edge(
        rel["source"],
        rel["target"],
        type=rel.get("type", ""),
        weight=rel.get("weight", 1)
    )

# ---- Sidebar: title, instructions, search, details ----
name_by_id = {p["id"]: p["name"] for p in people}
id_by_name = {p["name"]: p["id"] for p in people}

st.sidebar.title("DSAI Cliques: A Network Graph")
st.sidebar.write("Select a person to see their description and connections.")

selected_name = st.sidebar.selectbox(
    "Select a person",
    ["(none)"] + sorted(id_by_name.keys())
)

selected_id = None if selected_name == "(none)" else id_by_name[selected_name]

def update_selection(selected_id):
    st.sidebar.markdown(f"## <span style='color:lightblue'>{name_by_id[selected_id]}</span>", unsafe_allow_html=True) 
    origin = G.nodes[selected_id].get("origin", "")
    language = G.nodes[selected_id].get("language", "")
    st.sidebar.write(f"**Origin:** {origin}")
    st.sidebar.write(f"**Native language:** {language}")

    st.sidebar.markdown("**Connections**")
    for nbr in G.neighbors(selected_id):
        rel_type = G.edges[selected_id, nbr].get("type", "")
        st.sidebar.write(f"- {name_by_id[nbr]} ({rel_type})")
    
if selected_id:
    update_selection(selected_id)

# ---- Main area: full-screen graph ----
net = Network(
    height="100vh",
    width="100%",
    bgcolor="#242222EC",
    font_color="#FFFFFF"
)

net.from_nx(G)
net.toggle_physics(True)

# Highlight selected node
if selected_id:
    for n in net.nodes:
        if n["id"] == selected_id:
            n["size"] = 16

with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
    net.save_graph(tmp.name)
    html = open(tmp.name, "r", encoding="utf-8").read()

# Remove default Streamlit padding for full-screen graph
st.markdown(
    "<style>#MainMenu {visibility:hidden;} footer {visibility:hidden;} "
    "section.main > div {padding:0;} .block-container {padding:0 !important; max-width:100% !important;}</style>",
    unsafe_allow_html=True,
)
components.html(html, height=900, scrolling=True)
