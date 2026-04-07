from flask import Flask, request, jsonify
import math
import random
import time

app = Flask(__name__)
# 파일 최상단에 전역 변수 선언 (각 학생의 모터 속도를 저장할 공간)
motor_states = {}

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
# URL: /api/motor?id=...&v=... (구동)
# URL: /api/motor?id=...&reset=1 (초기화)
# ==========================================
@app.route('/api/motor', methods=['GET'])
def motor():
    student_id = request.args.get('id')
    v_str = request.args.get('v')
    reset_str = request.args.get('reset')
    
    if student_id is None:
        return jsonify({"error": "id parameter is required"}), 400

    # [추가된 로직] 초기화 요청이 들어온 경우
    if reset_str == '1' or reset_str.lower() == 'true':
        motor_states[student_id] = 0.0
        return jsonify({"velocity": 0.0, "message": "Motor has been reset to 0.0"})

    # 구동 요청일 경우 v 파라미터 확인
    if v_str is None:
        return jsonify({"error": "v parameter is required unless resetting"}), 400
        
    try:
        voltage = float(v_str)
    except ValueError:
        return jsonify({"error": "v must be a number"}), 400

    if student_id not in motor_states:
        motor_states[student_id] = 0.0

    current_vel = motor_states[student_id]

    # Trap 1: Packet Loss
    if random.random() < 0.05:
        return jsonify({"error": "Gateway Timeout"}), 504

    # Trap 2: Actuator Saturation (-24V ~ 24V)
    voltage = max(-24.0, min(24.0, voltage))

    # Plant dynamics 업데이트
    new_vel = (0.95 * current_vel) + (1.0 * voltage)
    motor_states[student_id] = new_vel 
    
    # Trap 3: Sensor Failure
    if random.random() < 0.05:
        return jsonify({"velocity": "SENSOR_FAIL"})

    # Sensor noise
    noisy_vel = new_vel + random.gauss(0, 0.3)

    return jsonify({"velocity": noisy_vel})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
