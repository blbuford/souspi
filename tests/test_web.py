import pytest
from souspi import web
from souspi.exc import TemperatureOutOfRangeException
from freezegun import freeze_time


@pytest.fixture
def client():
    web.app.config['TESTING'] = True
    client = web.app.test_client()
    yield client


def test_status(client):
    """ Test that the status page shows and allows a user to setup schedule times """

    rv = client.get('/')
    assert b'Start Time' in rv.data
    assert b'End Time' in rv.data


@freeze_time('2018-01-14 8:00:00')
def test_cancel_running(client):
    """ Test that the cook can be canceled once its running """

    post_schedule(client, "8:00 AM", "8:52 AM", "120")
    assert web.start_thread is None
    assert web.deviceInfo['status'] == 'running'
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None


@freeze_time('2018-01-14 8:00:00')
def test_cancel(client):
    """ Test the cancel scheduled entry endpoint """

    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None

    post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert web.start_thread is not None
    assert web.stop_thread is not None
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None

    post_schedule(client, "7:52 AM", "8:52 AM", "130")
    assert web.start_thread is not None
    assert web.stop_thread is not None
    assert web.deviceInfo['status'] == 'stopped'
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None

    post_schedule(client, "6:52 AM", "7:52 AM", "140")
    assert web.start_thread is not None
    assert web.stop_thread is not None
    assert web.deviceInfo['status'] == 'stopped'
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert web.start_thread is None
    assert web.stop_thread is None


def test_device_start_stop(client):
    """ Test that the thread functions work as intended """

    web.thread_start_device()
    assert web.deviceInfo['status'] == 'running'
    web.thread_stop_device()
    assert web.deviceInfo['status'] == 'stopped'


@freeze_time('2018-01-14 8:00:00')
def test_schedule_time(client):
    """ Test the start and end pieces of the schedule function """

    # Normal schedule test
    rv = post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert b'Jan 14 07:52 PM' in rv.data
    assert b'Jan 14 08:52 PM' in rv.data
    post_cancel(client)

    # Unexpected start time formatting
    with pytest.raises(ValueError):
        post_schedule(client, "08/20/18 7:52 PM", "8:52 PM", "130")

    # Unexpected stop time formatting
    with pytest.raises(ValueError):
        post_schedule(client, "7:52 PM", "08/20/18 8:52 PM", "140")

    # Stop before start
    rv = post_schedule(client, "7:52 PM", "6:52 PM", "150")
    assert b'Jan 14 07:52 PM' in rv.data
    assert b'Jan 15 06:52 PM' in rv.data
    post_cancel(client)

    # Start before datetime.now() and end is before start
    rv = post_schedule(client, "7:52 AM", "6:52 AM", "150")
    assert b'Jan 15 07:52 AM' in rv.data
    assert b'Jan 16 06:52 AM' in rv.data
    post_cancel(client)


def test_schedule_temperature(client):
    """ Test the temperature piece of the schedule function """

    # Normal float temperature
    rv = post_schedule(client, "7:52 PM", "8:52 PM", "140.0")
    assert b'140.0' in rv.data
    post_cancel(client)

    # Leaving the decimal point off
    rv = post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert b'120.0' in rv.data
    post_cancel(client)

    # Make sure we can't go below 32
    with pytest.raises(TemperatureOutOfRangeException):
        post_schedule(client, "7:52 PM", "8:52 PM", "31.9")

    # Make sure we can't go above 210
    with pytest.raises(TemperatureOutOfRangeException):
        post_schedule(client, "7:52 PM", "8:52 PM", "210.1")

    # Negative temp...
    with pytest.raises(TemperatureOutOfRangeException):
        post_schedule(client, "7:52 PM", "8:52 PM", "-100")

    # Non-number
    with pytest.raises(ValueError):
        post_schedule(client, "7:52 PM", "8:52 PM", "Shenanigans")


def post_schedule(client, start, end, temperature):
    return client.post("/schedule", data=dict(
        datetimepicker_start=start,
        datetimepicker_end=end,
        temperatureText=temperature,
        temperatureSlider=temperature
    ), follow_redirects=True)


def post_cancel(client):
    return client.post("/cancel", follow_redirects=True)
