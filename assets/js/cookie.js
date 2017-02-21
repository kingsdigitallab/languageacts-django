define([
    'module',
    'jquery',
    'jscookie'
], function(module, $, cookie) {
    'use strict';

    $(document).ready(function() {
        if (!cookie.get('lawm-cookie')) {
            $("#cookie-disclaimer").removeClass('hide');
        }
        // Set cookie
        $('#cookie-disclaimer .closeme').on("click", function() {
            cookie.set('lawm-cookie', 'lawm-cookie-set', { expires: 30 });
        });
    });

    return module;
});
