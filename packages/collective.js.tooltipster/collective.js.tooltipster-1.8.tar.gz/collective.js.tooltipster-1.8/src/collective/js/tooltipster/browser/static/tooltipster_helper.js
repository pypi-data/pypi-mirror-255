function tooltipster_helper(selector,
                            view_name,
                            data_parameters=[],
                            options={}) {

    jQuery(function($){
    $(selector).tooltipster({
        // zIndex 11000 will make it work correctly with overlays
        zIndex: options.zIndex || 11000,
        content: "...",
        contentAsHTML: true,
        interactive: true,
        theme: options.theme || 'tooltipster-shadow',
        arrow: options.arrow === undefined && true || options.arrow,
        position: options.position || 'bottom',
        trackTooltip: options.trackTooltip || false,
        animationDuration: options.animationDuration || 100,
        delay: options.delay || 50,
        animation: options.animation || 'fade',
        updateAnimation: options.updateAnimation || 'fade',
        trigger: options.trigger || 'custom',
        triggerOpen: options.triggerOpen || {mouseenter: true, click: true, tap: true},
        triggerClose: options.triggerClose || {mouseleave: true, click: true, tap: true, },
        maxWidth: options.maxWidth || null,
        minWidth: options.minWidth || 0,
        reposition: options.reposition || false,
        positionTracker: options.positionTracker || false,
        passInstanceToCallback: options.passInstanceToCallback || false,
        functionBefore: function (instance, helper) {
            // force async false if we have a functionReady_callback
            async = !(options.functionReady_callback || null) && (options.async || true) || false;

            // close every other tips if relevant
            close_other_tips = options.close_other_tips || null;
            if (close_other_tips === true) {
                $('.tooltipstered').tooltipster('hide');
            }

            // manage new tooltispter
            var $origin = $(helper.origin);
            if ($origin.data('loaded') !== true) {
                // data_parameters
                parameters = {};
                for (i = 0, len = data_parameters.length; i < len; i++) {
                    value = $($origin).attr('data-'+ data_parameters[i]);
                    parameters[data_parameters[i]] = value;
                }
                // base_url
                var base_url = $($origin).attr('data-base_url');
                if (!base_url) {
                  base_url = document.baseURI;
                }
                parameters.ajax_load = new Date().getTime();

                $.ajax({
                    type: 'GET',
                    url: base_url + '/' + view_name,
                    data: parameters,
                    // set async: false so content is loaded when functionReady is called
                    async: async,
                    success: function (data) {
                        instance.content(data);
                        $origin.data('loaded', true);
                    }
                });

        }
    },

    functionReady: function (instance, helper) {
        functionReady_callback = options.functionReady_callback || null;
        if (functionReady_callback != null) {
            if (options.passInstanceToCallback) {functionReady_callback(instance);}
            else {functionReady_callback();}
        }
    },

    functionPosition: function (instance, helper, position) {
        functionPosition_callback = options.functionPosition_callback || null;
        if (functionPosition_callback != null) {
            return functionPosition_callback(instance, helper, position);
        }
    },

});
});

}
