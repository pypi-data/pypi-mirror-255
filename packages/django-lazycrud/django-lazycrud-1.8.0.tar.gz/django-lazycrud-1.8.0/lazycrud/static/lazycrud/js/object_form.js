function lazycrud_form_init(form_id) {
    var lang = $('html').attr('lang');

    var datetimepicker_icons = {
        time: "fa fa-clock-o",
        date: "fa fa-calendar",
        previous: "fa fa-chevron-left",
        next: "fa fa-chevron-right",
        up: "fa fa-chevron-circle-up",
        down: "fa fa-chevron-circle-down",
        close: "fa fa-times",
    };

    $(form_id + ' .dateinput').datetimepicker({
        format: 'L',
        locale: lang,
        icons: datetimepicker_icons,
    });

    $(form_id + ' .timeinput').datetimepicker({
        format: 'LT',
        locale: lang,
        icons: datetimepicker_icons,
        stepping: 15,
    });

    $(form_id + ' .datetimeinput').datetimepicker({
        format: 'L LT',
        locale: lang,
        icons: datetimepicker_icons,
        stepping: 15,
        showClose: true,
    });
}

$(function() {
    lazycrud_form_init('form');
});
