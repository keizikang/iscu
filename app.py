from flask import Flask, request, jsonify
import math
import random
import time

app = Flask(__name__)

# ==========================================
# 1. Data Recovery (Function Data)
# URL: /api/evaluate?x=...
# ==========================================
@app.route('/api/evaluate', methods=['GET'])
def evaluate():
    x_str = request.args.get('x')
    if x_str is None:
        return jsonify({"error": "x parameter is required"}), 400
        
    try:
        x = float(x_str)
    except ValueError:
        return jsonify({"error": "x must be a number"}), 400

    time.sleep(0.5) 
    
    rand_val = random.random()
    if rand_val < 0.05:
        return jsonify({"error": "Internal Server Error"}), 500
    elif rand_val < 0.15:
        return jsonify({"result": "SERVER_BUSY"})
        
    result = x * math.sin(x)
    
    if rand_val < 0.20:
        result = result * 10000.0
        
    return jsonify({"result": result})

# ==========================================
# 2. Wind Tunnel (Optimal Angle)
# URL: /api/windtunnel?angle=...
# ==========================================
@app.route('/api/windtunnel', methods=['GET'])
def windtunnel():
    angle_str = request.args.get('angle')
    
    if angle_str is None:
        return jsonify({"error": "angle parameter is required"}), 400
        
    try:
        angle = float(angle_str)
    except ValueError:
        return jsonify({"error": "angle must be a number"}), 400

    if angle < 0 or angle > 90:
        return jsonify({"result": 0.0})

    # Base equation with aerodynamic drag penalty
    base_range = 100.0 * math.sin(math.radians(2 * angle)) * (1 - 0.005 * angle)

    # Gaussian noise
    noise = random.gauss(0, 2.0)
    final_range = base_range + noise
    final_range = max(0.0, final_range)

    return jsonify({"result": final_range})

# ==========================================
# 3. Motor Velocity Control (PI Control)
# URL: /api/motor?vel=...&v=...
# ==========================================
@app.route('/api/motor', methods=['GET'])
def motor():
    vel_str = request.args.get('vel')
    v_str = request.args.get('v')
    
    if vel_str is None or v_str is None:
        return jsonify({"error": "vel and v parameters are required"}), 400
        
    try:
        current_vel = float(vel_str)
        voltage = float(v_str)
    except ValueError:
        return jsonify({"error": "parameters must be numbers"}), 400

    # Trap 1: Packet Loss (Timeout)
    if random.random() < 0.05:
        # 의도적으로 응답을 주지 않고 에러 발생
        return jsonify({"error": "Gateway Timeout"}), 504

    # Trap 2: Sensor Failure (String return)
    if random.random() < 0.05:
        return jsonify({"new_velocity": "SENSOR_FAIL"})

    # Trap 3: Actuator Saturation (Voltage clipping)
    # 모터에 인가되는 voltage를 -24V ~ +24V 로 제한
    voltage = max(-24.0, min(24.0, voltage))

    # Trap 4: First-order system dynamics & Steady-state error
    # P-control만으로는 target velocity에 완벽히 도달할 수 없도록 설계된 동역학 모델
    new_vel = (0.95 * current_vel) + (1.0 * voltage)
    
    # Sensor noise 추가
    new_vel += random.gauss(0, 0.3)

    return jsonify({"new_velocity": new_vel})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
