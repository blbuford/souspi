from flask import Flask, render_template, request
from anova import AnovaDevice
from datetime import datetime, date
import time
from threading import Timer

app = Flask(__name__)

device = AnovaDevice('FF:FF:FF:FF:FF')
threads = []

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
#device.start()
@app.route('/', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        start_time = datetime.strptime(request.form['datetimepicker-start'], "%I:%M %p")
        end_time = datetime.strptime(request.form['datetimepicker-end'], "%I:%M %p")

        start_normalized = datetime.combine(date.today(), start_time.time())
        end_normalized = datetime.combine(date.today(), end_time.time())

        start_stamp = time.mktime(start_normalized.timetuple())
        end_stamp = time.mktime(end_normalized.timetuple())
        now_stamp = time.mktime(datetime.now().timetuple())

        start_delay = start_stamp - now_stamp
        end_delay = end_stamp - now_stamp

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

        return render_template('index.html', device=device)
    else:

        return render_template('index.html', device=device)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)