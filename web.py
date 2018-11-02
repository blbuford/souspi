from flask import Flask, render_template, request, redirect, url_for, logging
from anovaMock import AnovaDevice
from datetime import datetime, date
import time
from threading import Timer, Thread
from bluepy.btle import BTLEException

app = Flask(__name__)

device = AnovaDevice("78:A5:04:29:1E:C3")
threads = []

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
    'cookProgress': 0
}


def thread_start_device():
    print "starting device"
    device.start()
    for i in range(len(threads)):
        if threads[i].getName() == 'startDevice':
            threads.remove(threads[i])
            print threads
            break


def thread_stop_device():
    print "stopping device"
    device.stop()
    deviceInfo['cookScheduled'] = False
    for i in range(len(threads)):
        if threads[i].getName() == 'stopDevice':
            threads.remove(threads[i])
            print threads
            break


@app.route('/', methods=['GET'])
def status():
    try:
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
        print err
    return render_template('index.html', device=deviceInfo)


@app.route('/schedule', methods=['POST'])
def schedule():
    if request.method == 'POST':
        start_time = datetime.strptime(request.form['datetimepicker-start'], "%I:%M %p")
        end_time = datetime.strptime(request.form['datetimepicker-end'], "%I:%M %p")
        target_text = request.form['temperatureText']
        target_slider = request.form['temperatureSlider']

        start_normalized = datetime.combine(date.today(), start_time.time())
        end_normalized = datetime.combine(date.today(), end_time.time())
        deviceInfo['cookStart'] = start_normalized.strftime("%I:%M %p")
        deviceInfo['cookEnd'] = end_normalized.strftime("%I:%M %p")

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
        threads.append(start_thread)
        start_thread.start()
        deviceInfo['cookScheduled'] = True

        end_thread = Timer(end_delay, thread_stop_device)
        end_thread.setName('stopDevice')
        threads.append(end_thread)
        end_thread.start()

    return redirect(url_for("status"))


@app.route('/cancel', methods=['POST'])
def cancel():
    global threads
    if device.getStatus() == 'running':
        device.stop()
    if len(threads) > 0:
        for t in threads:
            t.cancel()
        threads = []

    deviceInfo['cookScheduled'] = False
    return redirect(url_for("status"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)