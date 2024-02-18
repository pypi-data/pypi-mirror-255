from flask import Flask, jsonify
from waitress	import serve
from threading import Thread

is_healthy = True
app = Flask(__name__)

# HEALTH CHECK
@app.route('/health', methods=['GET'])
def health():
    global is_healthy
    if is_healthy:
            return jsonify(success=True, status_code=200)
    else:
            return jsonify(success=False, status_code=500)
    
def init_health_check():
    serve(app, host='0.0.0.0', port=3000)

def start_health_check():
    t = Thread(target=init_health_check)
    t.start()

def set_health_to_false():
    global is_healthy
    is_healthy = False