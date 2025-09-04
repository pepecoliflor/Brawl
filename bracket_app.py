import streamlit as st
import json
import graphviz

st.set_page_config(page_title="Torneo Brawl Stars", layout="wide")

st.title("🏆 Torneo Brawl Stars - Bracket en Vivo")

# Cargar estado del torneo
try:
    with open("torneo.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    rondas = data["rondas"]
except FileNotFoundError:
    st.error("No se encontró el archivo torneo.json. Ejecuta primero el motor.")
    st.stop()

# Dibujar el bracket con Graphviz
dot = graphviz.Digraph()
dot.attr(rankdir="LR", splines="polyline")

# Recorremos rondas y partidos
for r, ronda in enumerate(rondas, start=1):
    with st.expander(f"🔹 Ronda {r}", expanded=True):
        for i, match in enumerate(ronda, start=1):
            j1 = match["jugador1"]
            j2 = match["jugador2"]
            ganador = match["ganador"]

            st.write(f"**Match {i}:** {j1} 🆚 {j2} → **Ganador:** {ganador}")

            # Nodos únicos por ronda/partido
            nodo1 = f"R{r}M{i}J1"
            nodo2 = f"R{r}M{i}J2"
            nodo_g = f"R{r}M{i}G"

            dot.node(nodo1, j1, shape="box", style="filled", fillcolor="lightblue")
            dot.node(nodo2, j2, shape="box", style="filled", fillcolor="lightpink")
            dot.node(nodo_g, ganador, shape="ellipse", style="filled", fillcolor="lightgreen")

            dot.edge(nodo1, nodo_g)
            dot.edge(nodo2, nodo_g)

# Mostrar diagrama
st.graphviz_chart(dot)
