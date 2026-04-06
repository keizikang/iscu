from flask import Flask, request, jsonify
import math
import random
import time

app = Flask(__name__)

@app.route('/api/evaluate', methods=['GET'])
def evaluate():
    # URL에서 x 값을 읽어옵니다. 예: /api/evaluate?x=1.5
    x_str = request.args.get('x')
    
    if x_str is None:
        return jsonify({"error": "x parameter is required"}), 400
        
    try:
        x = float(x_str)
    except ValueError:
        return jsonify({"error": "x must be a number"}), 400

    time.sleep(0.5) # 의도된 delay
    
    # 에러 및 노이즈 발생 로직 (위의 mock 코드와 동일하게 구성)
    rand_val = random.random()
    if rand_val < 0.05:
        return jsonify({"error": "Internal Server Error"}), 500
    elif rand_val < 0.15:
        return jsonify({"result": "SERVER_BUSY"})
        
    result = x * math.sin(x)
    
    if rand_val < 0.20:
        result = result * 10000.0
        
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
