/* vim:set et ts=4 sw=4 */

jQuery(function() {

    /* allow module h2s with the 'collapsed' or 'expanded' classes to
     * collapse or expand the module. (see modules.css for more.) */
    jQuery("div.module.collapsed h2, div.module.expanded h2").each(function() {
        jQuery('<span class="toggler"></span>').click(function() {
            jQuery(this).parents("div.module").toggleClass("collapsed").toggleClass("expanded");
        }).appendTo(this);
    });
});
