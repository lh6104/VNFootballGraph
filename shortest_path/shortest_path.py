import pandas as pd
import networkx as nx

# Load nodes
players = pd.read_csv("nodes_player.csv")
coaches = pd.read_csv("nodes_coach.csv")
clubs = pd.read_csv("nodes_club.csv")
tournaments = pd.read_csv("nodes_tournament.csv")
edges = pd.read_csv("rels_LinkTo.csv")

players.rename(columns={"id:ID": "id", "name": "name", ":LABEL": "label"}, inplace=True)
coaches.rename(columns={"id:ID": "id", "name": "name", ":LABEL": "label"}, inplace=True)
clubs.rename(columns={"id:ID": "id", "name": "name", ":LABEL": "label"}, inplace=True)
tournaments.rename(columns={"id:ID": "id", "name": "name", ":LABEL": "label"}, inplace=True)
edges.rename(columns={":START_ID": "source", ":END_ID": "target", ":TYPE": "type"}, inplace=True)

nodes = pd.concat([players, coaches, clubs, tournaments], ignore_index=True)

# Build graph
G = nx.Graph()
for _, r in nodes.iterrows():
    G.add_node(r["id"], label=r["label"], name=r["name"])

for _, r in edges.iterrows():
    G.add_edge(r["source"], r["target"])

# Shortest path example (chọn 2 node trong cùng component)
start_node = "P215"
end_node = "CL432"

try:
    path = nx.shortest_path(G, start_node, end_node)
    print("Shortest path:", path)
except nx.NetworkXNoPath:
    print("No path exists between the selected nodes.")
