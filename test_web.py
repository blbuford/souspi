import pytest
import web
from anova import TemperatureOutOfRangeException
from freezegun import freeze_time
import time

@pytest.fixture
def client():
    web.app.config['TESTING'] = True
    client = web.app.test_client()
    yield client


def test_status(client):
    rv = client.get('/')
    assert b'Start Time' in rv.data


@freeze_time('2018-01-14 8:00:00')
def test_cancel(client):
    """ Test the cancel scheduled entry endpoint """

    post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert len(web.threads) == 2
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert len(web.threads) == 0

    post_schedule(client, "7:52 AM", "8:52 AM", "130")
    assert len(web.threads) == 1
    assert web.deviceInfo['status'] == 'running'
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert len(web.threads) == 0

    post_schedule(client, "6:52 AM", "7:52 AM", "140")
    time.sleep(5)
    assert len(web.threads) == 0
    assert web.deviceInfo['status'] == 'stopped'
    post_cancel(client)
    assert web.deviceInfo['cookScheduled'] is False
    assert web.deviceInfo['status'] == 'stopped'
    assert len(web.threads) == 0


@freeze_time('2018-01-14 8:00:00')
def test_schedule_time(client):
    """ Test the start and end pieces of the schedule function """

    rv = post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert b'7:52 PM' in rv.data
    assert b'8:52 PM' in rv.data
    post_cancel(client)

    with pytest.raises(ValueError):
        post_schedule(client, "08/20/18 7:52 PM", "8:52 PM", "120")
        post_cancel(client)

    with pytest.raises(ValueError):
        post_schedule(client, "7:52 PM", "08/20/18 8:52 PM", "120")
        post_cancel(client)

    with pytest.raises(ValueError):
        post_schedule(client, "MALICIOUS THINGS", "08/20/18 8:52 PM", "120")
        post_cancel(client)


def test_schedule_temperature(client):
    """ Test the temperature piece of the schedule function """

    rv = post_schedule(client, "7:52 PM", "8:52 PM", "140.0")
    assert b'140.0' in rv.data
    post_cancel(client)

    rv = post_schedule(client, "7:52 PM", "8:52 PM", "120")
    assert b'120.0' in rv.data
    post_cancel(client)

    with pytest.raises(TemperatureOutOfRangeException):
        post_schedule(client, "7:52 PM", "8:52 PM", "30")
        post_cancel(client)

    with pytest.raises(TemperatureOutOfRangeException):
        post_schedule(client, "7:52 PM", "8:52 PM", "210.1")
        post_cancel(client)


def post_schedule(client, start, end, tempurature):
    return client.post("/schedule", data=dict(
        datetimepicker_start=start,
        datetimepicker_end=end,
        temperatureText=tempurature,
        temperatureSlider=tempurature
    ), follow_redirects=True)


def post_cancel(client):
    return client.post("/cancel", follow_redirects=True)
