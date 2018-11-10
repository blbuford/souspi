from flask import Flask, render_template, request, redirect, url_for
from anovaMock import AnovaDevice
from datetime import datetime, date, timedelta
import time
from threading import Timer
import os


app = Flask(__name__)
app.config.from_pyfile(os.path.join("..", "config/web.conf"), silent=False)

device = AnovaDevice(app.config.get("ANOVA_MAC_ADDRESS"))

start_thread = None
stop_thread = None


deviceInfo = {
    'status': 'stopped',
    'currentTemp': -1,
    'targetTemp': -1,
    'timer': -1,
    'cookScheduled': False,
    'cookStart': "",
    'cookEnd': "",
    'cookStartStamp': 0,
    'cookEndStamp': 0,
    'cookProgress': 0,
    'message': ''
}


def thread_start_device():
    global start_thread
    device.start()
    deviceInfo['status'] = device.getStatus()
    start_thread = None


def thread_stop_device():
    global stop_thread
    device.stop()
    deviceInfo['cookScheduled'] = False
    deviceInfo['status'] = device.getStatus()
    stop_thread = None


@app.route('/', methods=['GET'])
def status():
    try:
        deviceInfo['message'] = ''
        deviceInfo['status'] = device.getStatus()
        deviceInfo['currentTemp'] = device.getCurrentTemp()
        deviceInfo['targetTemp'] = device.getTargetTemp()
        if deviceInfo['status'] == 'running':
            deviceInfo['timer'] = device.getTimer()
        if deviceInfo['cookScheduled']:
            total_time = deviceInfo['cookEndStamp'] - deviceInfo['cookStartStamp']
            elapsed_time = time.mktime(datetime.now().timetuple()) - deviceInfo['cookStartStamp']
            if elapsed_time < 0:
                deviceInfo['cookProgress'] = 0
            else:
                deviceInfo['cookProgress'] = int((elapsed_time/total_time)*100)
    except Exception as err:
        deviceInfo['message'] = err.message
    return render_template('index.html', device=deviceInfo)


@app.route('/schedule', methods=['POST'])
def schedule():
    global start_thread, stop_thread
    if request.method == 'POST':
        start_time = datetime.strptime(request.form['datetimepicker_start'], "%I:%M %p")
        end_time = datetime.strptime(request.form['datetimepicker_end'], "%I:%M %p")
        target_slider = float(request.form['temperatureSlider'])

        if start_time.time() >= datetime.now().time():
            start_normalized = datetime.combine(date.today(), start_time.time())
            if start_time >= end_time:
                end_normalized = datetime.combine(date.today() + timedelta(days=1), end_time.time())
            else:
                end_normalized = datetime.combine(date.today(), end_time.time())
        else:
            start_normalized = datetime.combine(date.today() + timedelta(days=1), start_time.time())
            if start_time >= end_time:
                end_normalized = datetime.combine(date.today() + timedelta(days=2), end_time.time())
            else:
                end_normalized = datetime.combine(date.today() + timedelta(days=1), end_time.time())

        deviceInfo['cookStart'] = start_normalized.strftime("%b %d %I:%M %p")
        deviceInfo['cookEnd'] = end_normalized.strftime("%b %d %I:%M %p")

        start_stamp = time.mktime(start_normalized.timetuple())
        end_stamp = time.mktime(end_normalized.timetuple())
        now_stamp = time.mktime(datetime.now().timetuple())

        deviceInfo['cookStartStamp'] = start_stamp
        deviceInfo['cookEndStamp'] = end_stamp

        start_delay = start_stamp - now_stamp
        end_delay = end_stamp - now_stamp

        device.setTargetTemp(target_slider)

        start_thread = Timer(start_delay, thread_start_device)
        start_thread.setName('startDevice')
        start_thread.start()
        deviceInfo['cookScheduled'] = True

        stop_thread = Timer(end_delay, thread_stop_device)
        stop_thread.setName('stopDevice')
        stop_thread.start()

    return redirect(url_for("status"))


@app.route('/cancel', methods=['POST'])
def cancel():
    global start_thread, stop_thread
    if device.getStatus() == 'running':
        device.stop()

    if start_thread is not None:
        start_thread.cancel()
        start_thread = None

    if stop_thread is not None:
        stop_thread.cancel()
        stop_thread = None

    deviceInfo['cookScheduled'] = False
    return redirect(url_for("status"))

