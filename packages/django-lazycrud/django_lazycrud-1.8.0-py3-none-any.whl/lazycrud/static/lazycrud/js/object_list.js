$(function() {
    var object_list_js_url = $('#object-list-script').attr('src');
    var object_list_js_dir = object_list_js_url.substr(0, object_list_js_url.lastIndexOf("/"))

    var lang = $('html').attr('lang');
    if (lang != 'en') {
        $.extend(true, $.fn.dataTable.defaults, {
            oLanguage: {
                sUrl: object_list_js_dir + '/dataTables/i18n/' + lang + '.js'
            }
        });
    }

    moment.locale(lang)

    $.fn.dataTable.moment(moment.localeData().longDateFormat('L'));
    $.fn.dataTable.moment(moment.localeData().longDateFormat('L') + ' ' + moment.localeData().longDateFormat('LT'));

    $('body').off('mousedown contextmenu', '.clickable_row');
    $('body').on('mousedown', '.clickable_row', function(e) {
        var url = $(this).data('url');
        if ($(this).data('target') == '_blank' || e.button == 2) {
            // data-target="_blank" o click con tasto destro: nuova finestra
            window.open(url);
        } else {
            // qualunque altro tasto: stessa finestra
            window.location.href = url;
        }
    });

    $('.table-datatables').each(function() {
        var dt_options = {};
        if ($(this).data('datatables-options') !== undefined) {
            dt_options = $(this).data('datatables-options');
        }
        $(this).dataTable(dt_options);
    });
});
