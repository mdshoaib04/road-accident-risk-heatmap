from flask import Flask, render_template, request
import numpy as np
import urllib.request
import urllib.parse
import joblib
import threading

app = Flask(__name__)
model = joblib.load('litemodel.sav')

def sendSMS(apikey, numbers, sender, message):
    try:
        data = urllib.parse.urlencode({
            'apikey': apikey,
            'numbers': numbers,
            'message': message,
            'sender': sender
        }).encode('utf-8')
        req = urllib.request.Request("https://api.textlocal.in/send/?")
        with urllib.request.urlopen(req, data) as f:
            return f.read()
    except Exception as e:
        print("SMS error:", e)
        return None

def cal(ip):
    Did_Police_Officer_Attend = ip['Did_Police_Officer_Attend']
    age_of_driver = ip['age_of_driver']
    vehicle_type = ip['vehicle_type']
    age_of_vehicle = ip['age_of_vehicle']
    engine_cc = ip['engine_cc']
    day = ip['day']
    weather = ip['weather']
    light = ip['light']
    roadsc = ip['roadsc']
    gender = ip['gender']
    speedl = ip['speedl']

    data = np.array([
        Did_Police_Officer_Attend, age_of_driver, vehicle_type,
        age_of_vehicle, engine_cc, day, weather, roadsc,
        light, gender, speedl
    ], dtype=float).reshape(1, -1)

    try:
        result = model.predict(data)
        return str(result[0])  # "1"/"2"/"3"
    except Exception as e:
        return f"Error: {e}"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/visual/', methods=['GET'])
def visual():
    # Flask route (agar tum static visual.html use kar rahe ho to isse bhi serve ho jayega)
    return render_template('visual.html')

@app.route('/sms/', methods=['POST'])
def sms():
    # pehle prediction nikaalo
    res = cal(request.form)

    # SMS ko background thread se bhejo taaki response immediately aa jaye (no infinite loading)
    def _bg_sms(msg):
        sendSMS(
            'UwYs16dD3zM-DKuzZKQYolAJkoba1j0BmRGompsNRs',
            '9618205648',
            'TXTLCL',
            msg
        )

    try:
        msg = f'Accident Severity Predicted: {res}'
        threading.Thread(target=_bg_sms, args=(msg,), daemon=True).start()
    except Exception as e:
        print("BG SMS thread error:", e)

    # frontend ko seedha prediction text de do
    return res

@app.route('/', methods=['POST'])
def get():
    return cal(request.form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=4000)
