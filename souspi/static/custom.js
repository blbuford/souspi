$.fn.datetimepicker.Constructor.Default = $.extend({}, $.fn.datetimepicker.Constructor.Default, {
    icons: {
        time: 'far fa-clock',
        date: 'far fa-calendar',
        up: 'fas fa-arrow-up',
        down: 'fas fa-arrow-down',
        previous: 'far fa-chevron-left',
        next: 'far fa-chevron-right',
        today: 'far fa-calendar-check-o',
        clear: 'far fa-trash',
        close: 'far fa-times'
    } });
$(function () {
    $('#datetimepicker1').datetimepicker({
        format: 'LT'
    });
});

$(function () {
    $('#datetimepicker2').datetimepicker({
        format: 'LT'
    });
});

function updateTextInput(val) {
    document.getElementById('temperatureInput').value=val;
}

function updateSliderInput(val) {
    document.getElementById('targetTemperatureSelector').value=val;
}
var tempInput = document.getElementById("temperatureInput");
var tempSlider = document.getElementById("targetTemperatureSelector");
tempInput.value = tempSlider.value;