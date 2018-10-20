from flask import Flask, render_template, request
from anovaMock import AnovaDevice
from datetime import datetime, date
import time
from threading import Timer, Thread
from bluepy.btle import BTLEException

app = Flask(__name__)

device = AnovaDevice("78:A5:04:29:1E:C3")
threads = []
status_thread = None

deviceInfo = {
    'status': 'stopped',
    'currentTemp': -1,
    'targetTemp': -1,
    'timer': -1
}

def statusThread():
    global deviceInfo
    while True:
        try:
            deviceInfo['status'] = device.getStatus()
            deviceInfo['currentTemp'] = device.getCurrentTemp()
            deviceInfo['targetTemp'] = device.getTargetTemp()
            if deviceInfo['status'] == 'running':
                deviceInfo['timer'] = device.getTimer()
            print "Thread proc: ", deviceInfo['status'], deviceInfo['currentTemp'], deviceInfo['targetTemp'], deviceInfo['timer']
        except Exception as err:
            print err
        time.sleep(30)


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
    for i in range(len(threads)):
        if threads[i].getName() == 'stopDevice':
            threads.remove(threads[i])
            print threads
            break

@app.route('/', methods=['GET', 'POST'])
def status():
    global status_thread
    global deviceInfo
    if status_thread is None:
        status_thread = Thread(target=statusThread)
        status_thread.start()

    if request.method == 'POST':
        start_time = datetime.strptime(request.form['datetimepicker-start'], "%I:%M %p")
        end_time = datetime.strptime(request.form['datetimepicker-end'], "%I:%M %p")
        target_text = request.form['temperatureText']
        target_slider = request.form['temperatureSlider']

        start_normalized = datetime.combine(date.today(), start_time.time())
        end_normalized = datetime.combine(date.today(), end_time.time())

        start_stamp = time.mktime(start_normalized.timetuple())
        end_stamp = time.mktime(end_normalized.timetuple())
        now_stamp = time.mktime(datetime.now().timetuple())

        start_delay = start_stamp - now_stamp
        end_delay = end_stamp - now_stamp

        device.setTargetTemp(target_slider)


        start_thread = Timer(start_delay, thread_start_device)
        start_thread.setName('startDevice')
        threads.append(start_thread)
        start_thread.start()
        print "start thread queued for {} seconds from now".format(start_delay)

        end_thread = Timer(end_delay, thread_stop_device)
        end_thread.setName('stopDevice')
        threads.append(end_thread)
        end_thread.start()
        print "stop thread queued for {} seconds from now".format(end_delay)


        return render_template('index.html', device=deviceInfo)
    else:

        return render_template('index.html', device=deviceInfo)


if __name__ == "__main__":
    status_thread = Thread( target=statusThread)
    status_thread.start()
    app.run(host="0.0.0.0", port=8080)