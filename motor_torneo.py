import pandas as pd
import requests
import time
import random
import json
import os

# 🔑 Reemplaza con tu API token de Brawl Stars
API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjEyNzhkMTliLTk3MWMtNDc4OS04NDY5LTQ2NzRjMzYyMWFhMiIsImlhdCI6MTc1MTAwNzA5Miwic3ViIjoiZGV2ZWxvcGVyLzliMDcxMjczLWY1MDYtYWM4OS00MWRkLTE4YjY5ZTJlNWE1ZiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiODguMS45NS4yMDYiXSwidHlwZSI6ImNsaWVudCJ9XX0.fv7tZurKSAILoZBnjuY7vJL_pPHqzUQv0XNq3Zkyyg_j4Vc-XAGDL6QigM2AT_WeiPYcMJdf6ooepMMU4--fJQ'
API_URL = "https://api.brawlstars.com/v1/players/%23{player_tag}/battlelog"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# ================================
# 📌 Funciones auxiliares
# ================================

def cargar_jugadores(excel_path="jugadores.xlsx"):
    """Lee los jugadores desde un Excel con columnas: Nombre, ID"""
    df = pd.read_excel(excel_path)
    jugadores = [f"{row['Nombre']} (#{row['ID']})" for _, row in df.iterrows()]
    ids = [f"#{row['ID']}" for _, row in df.iterrows()]
    return list(zip(jugadores, ids))

def crear_bracket(jugadores):
    """Crea el bracket inicial con emparejamientos aleatorios"""
    random.shuffle(jugadores)
    ronda = []
    for i in range(0, len(jugadores), 2):
        if i+1 < len(jugadores):
            ronda.append({
                "jugador1": jugadores[i][0],
                "id1": jugadores[i][1],
                "jugador2": jugadores[i+1][0],
                "id2": jugadores[i+1][1],
                "ganador": "⏳ Esperando"
            })
    return [ronda]  # bracket con 1 ronda inicial

def guardar_estado(bracket, path="torneo.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"rondas": bracket}, f, ensure_ascii=False, indent=2)

def cargar_estado(path="torneo.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["rondas"]
    return []

def obtener_ultimo_resultado(player_id):
    """Obtiene el último resultado de un jugador desde la API"""
    url = API_URL.format(player_tag=player_id.replace("#", ""))
    try:
        resp = requests.get(url, headers=HEADERS)
        data = resp.json()
        return data.get("items", [])[0]  # último match
    except Exception:
        return None

def determinar_ganador(match, id1, id2):
    """Revisa si ambos jugadores estaban en el mismo match y devuelve el ganador"""
    try:
        battle = match.get("battle", {})
        teams = battle.get("teams", [])
        if not teams:
            return None

        # Busca nombres dentro de los equipos
        jugadores = {p["tag"]: p["name"] for team in teams for p in team}

        if id1 in jugadores and id2 in jugadores:
            result = battle.get("result", "unknown")
            if result == "victory":
                return jugadores[id1]
            elif result == "defeat":
                return jugadores[id2]
        return None
    except:
        return None

# ================================
# 🚀 Motor principal
# ================================

def motor_torneo(excel_path="jugadores.xlsx"):
    # Cargar jugadores y estado previo si existe
    jugadores = cargar_jugadores(excel_path)
    bracket = cargar_estado()

    if not bracket:  # Si no hay torneo, crear uno nuevo
        bracket = crear_bracket(jugadores)
        guardar_estado(bracket)

    print("🏆 Motor de torneo iniciado...")

    while True:
        actualizado = False

        # Recorre rondas
        for ronda in bracket:
            for match in ronda:
                if match["ganador"] == "⏳ Esperando":
                    # Revisa si ya jugaron
                    res1 = obtener_ultimo_resultado(match["id1"])
                    res2 = obtener_ultimo_resultado(match["id2"])

                    if res1 and res1 == res2:  # Ambos en el mismo match
                        ganador = determinar_ganador(res1, match["id1"], match["id2"])
                        if ganador:
                            match["ganador"] = ganador
                            print(f"✅ Match resuelto: {match['jugador1']} vs {match['jugador2']} -> {ganador}")
                            actualizado = True

        # Si se terminó una ronda, crear la siguiente
        if all(m["ganador"] != "⏳ Esperando" for m in bracket[-1]):
            ganadores = [(m["ganador"], m["id1"] if m["ganador"] in m["jugador1"] else m["id2"])
                         for m in bracket[-1]]
            if len(ganadores) > 1:
                nueva_ronda = []
                for i in range(0, len(ganadores), 2):
                    if i+1 < len(ganadores):
                        nueva_ronda.append({
                            "jugador1": ganadores[i][0],
                            "id1": ganadores[i][1],
                            "jugador2": ganadores[i+1][0],
                            "id2": ganadores[i+1][1],
                            "ganador": "⏳ Esperando"
                        })
                bracket.append(nueva_ronda)
                actualizado = True

        if actualizado:
            guardar_estado(bracket)

        time.sleep(120)  # Espera 2 minutos
