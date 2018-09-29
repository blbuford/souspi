from flask import Flask, render_template
from anovaMock import AnovaDevice
app = Flask(__name__)

device = AnovaDevice('FF:FF:FF:FF:FF')
device.start()
@app.route('/')
def hello_world():
    return render_template('index.html', device=device)