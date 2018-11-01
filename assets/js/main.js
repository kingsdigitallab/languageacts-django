$(document).ready(function()
{   
    $(document).foundation();

    // LAWM Cookie
    if (!Cookies.get('lawm-cookie')) {
        $("#cookie-disclaimer").removeClass('hide');
        }
        // Set cookie
        $('#cookie-disclaimer .closeme').on("click", function() {
            Cookies.set('lawm-cookie', 'lawm-cookie-set', { expires: 30 });
        });

    // Instafeed
    if ($('#instafeed').length) {
        var feed = new Instafeed({
            get: 'user',
            userId: '4755811294',
            accessToken: '4755811294.dd6559f.d035b5c4fe104bf68d57b6c6887dc2ca',
            template: '<div class="medium-6 large-3 columns"><a href="{{link}}" target="_blank" title="Open on Instagram site in a new window"><img src="{{image}}" alt="{{caption}}"></a></div>',

            // clientId: 'dd6559f3262d4ff4b533c15451b54817',
            resolution: 'standard_resolution',
            limit: '4'
        });

        feed.run();
    }
});