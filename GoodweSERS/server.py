# --- API de Simulação GoodWe Smart Solar Home (Versão Final) ---
# Linguagem: Python
# Framework: Flask, Flask-CORS
#
# NOTA: Este servidor agora também serve o ficheiro index.html,
# resolvendo problemas de comunicação (CORS/Failed to fetch).

import threading
import time
import math
import random
import uuid
import requests
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

# --- Inicialização do Flask com CORS ---
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# --- Dados Simulados do Sistema (Estado Global) ---
smart_home_data = {
    "solar_generation_kw": 0.0,
    "battery": {"percentage": 70.0, "capacity_kwh": 10.0, "state": "idle"},
    "grid": {"state": "idle", "power_kw": 0.0},
    "home_consumption_kw": 0.0,
    "devices": {
        "base01": {
            "id": "base01",
            "name": "Consumo Base",
            "state": "on",
            "consumption_kw": 0.3
        }
    }
}


# --- Lógica de Simulação de Energia (Executa em background) ---
def simulate_energy_flow():
    """ Simula o fluxo de energia da casa de forma contínua e segura. """
    while True:
        try:
            # Simulação de Geração Solar
            seconds_in_a_day = 120
            current_second = time.time() % seconds_in_a_day
            angle = (current_second / seconds_in_a_day) * 2 * math.pi
            solar_generation = max(0, 5 * math.sin(angle - math.pi / 2) + 4.5)
            smart_home_data["solar_generation_kw"] = round(solar_generation, 2)

            # Calcular Consumo Total
            total_consumption = 0
            for device in list(smart_home_data["devices"].values()):
                if device["state"] == "on":
                    total_consumption += device["consumption_kw"]
            smart_home_data["home_consumption_kw"] = round(total_consumption, 2)

            # Balanço Energético
            balance = solar_generation - total_consumption
            battery_charge = smart_home_data["battery"]["percentage"]
            if balance > 0:
                smart_home_data["grid"]["state"] = "idle";
                smart_home_data["grid"]["power_kw"] = 0
                if battery_charge < 100:
                    smart_home_data["battery"]["state"] = "charging"
                    charge_rate = (balance / smart_home_data["battery"]["capacity_kwh"]) * 100 / 360
                    smart_home_data["battery"]["percentage"] = min(100, battery_charge + charge_rate)
                else:
                    smart_home_data["battery"]["state"] = "idle";
                    smart_home_data["grid"]["state"] = "injecting";
                    smart_home_data["grid"]["power_kw"] = round(balance, 2)
            elif balance < 0:
                power_needed = abs(balance)
                if battery_charge > 0:
                    smart_home_data["battery"]["state"] = "discharging"
                    discharge_rate = (power_needed / smart_home_data["battery"]["capacity_kwh"]) * 100 / 360
                    smart_home_data["battery"]["percentage"] = max(0, battery_charge - discharge_rate)
                else:
                    smart_home_data["battery"]["state"] = "idle";
                    smart_home_data["grid"]["state"] = "drawing";
                    smart_home_data["grid"]["power_kw"] = round(power_needed, 2)
            else:
                smart_home_data["battery"]["state"] = "idle";
                smart_home_data["grid"]["state"] = "idle";
                smart_home_data["grid"]["power_kw"] = 0
            smart_home_data["battery"]["percentage"] = round(smart_home_data["battery"]["percentage"], 2)

        except Exception as e:
            print(f"!!! ERRO no loop de simulação: {e}")

        time.sleep(2)


# --- Endpoints da API ---

# NOVO: Rota principal para servir o index.html
@app.route("/")
def serve_index():
    print(">>> Servindo a página principal (index.html)")
    return render_template('index.html')


@app.route("/api/status", methods=['GET'])
def get_status():
    print(">>> Pedido recebido para /api/status")
    return jsonify(smart_home_data)


@app.route("/api/devices", methods=['POST'])
def add_device():
    print(f">>> Pedido recebido para ADICIONAR dispositivo com dados: {request.json}")
    data = request.json
    if not data or 'name' not in data or 'consumption_kw' not in data:
        return jsonify({"error": "Dados inválidos"}), 400
    device_id = str(uuid.uuid4())
    new_device = {"id": device_id, "name": data['name'], "state": "off",
                  "consumption_kw": float(data['consumption_kw'])}
    smart_home_data["devices"][device_id] = new_device
    return jsonify({"message": "Dispositivo adicionado!", "device": new_device}), 201


@app.route("/api/devices/<device_id>", methods=['DELETE'])
def delete_device(device_id):
    print(f">>> Pedido recebido para APAGAR dispositivo: {device_id}")
    if device_id in smart_home_data["devices"]:
        del smart_home_data["devices"][device_id]
        return jsonify({"message": f"Dispositivo removido."})
    return jsonify({"error": "Dispositivo não encontrado."}), 404


@app.route("/api/devices/<device_id>/<action>", methods=['POST'])
def control_device(device_id, action):
    print(f">>> Pedido recebido para CONTROLAR dispositivo: {device_id}, Ação: {action}")
    if device_id not in smart_home_data["devices"] or action not in ["turn_on", "turn_off"]:
        return jsonify({"error": "Ação ou dispositivo inválido."}), 400
    new_state = "on" if action == "turn_on" else "off"
    smart_home_data["devices"][device_id]["state"] = new_state
    device_name = smart_home_data['devices'][device_id]['name']
    message = f"{device_name} foi {'ligado' if new_state == 'on' else 'desligado'}."
    return jsonify({"message": message, "new_state": new_state})


@app.route("/api/recommendation", methods=['GET'])
def get_recommendation_from_gemini():
    print(">>> Pedido recebido para /api/recommendation (IA)")
    prompt = (
        f"Aja como um assistente de eficiência energética para uma casa inteligente. Com base nos seguintes dados em tempo real, forneça uma recomendação clara e útil para o morador em português do Brasil. Seja breve (uma ou duas frases) e direto. Use uma linguagem amigável.\n\nDADOS ATUAIS:\n- Geração Solar: {smart_home_data['solar_generation_kw']:.2f} kW\n- Consumo da Casa: {smart_home_data['home_consumption_kw']:.2f} kW\n- Nível da Bateria: {smart_home_data['battery']['percentage']:.1f}%\n- Estado da Bateria: {smart_home_data['battery']['state']}\n- Situação da Rede Elétrica: {smart_home_data['grid']['state']} (consumindo {smart_home_data['grid']['power_kw']:.2f} kW da rede)\n\nRECOMENDAÇÃO:")
    try:
        api_key = "AIzaSyBeQ4DRTQgswpirKxnawAIxJjY-hFCDAGQ"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates'][0]['content']['parts'][0]['text']:
            recommendation = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"recommendation": recommendation.strip()})
        else:
            return jsonify({"recommendation": "A IA retornou uma resposta inesperada. Tente novamente."}), 500
    except requests.exceptions.RequestException as e:
        print(f"!!! ERRO de rede ao chamar a API Gemini: {e}")
        return jsonify({"recommendation": "Não foi possível contatar a IA. Verifique a conexão de rede."}), 500
    except Exception as e:
        print(f"!!! ERRO ao processar a resposta da IA: {e}")
        if "API key not valid" in str(e):
            return jsonify({"recommendation": "Chave de API inválida. Verifique a chave no Google AI Studio."}), 401
        return jsonify({"recommendation": "Ocorreu um erro ao obter a recomendação da IA."}), 500


# --- Inicialização ---
if __name__ == '__main__':
    simulation_thread = threading.Thread(target=simulate_energy_flow)
    simulation_thread.daemon = True
    simulation_thread.start()
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
