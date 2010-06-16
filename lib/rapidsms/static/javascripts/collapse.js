/* vim:set et ts=4 sw=4 */

jQuery(function() {
    jQuery("div.module.collapsed h2, div.module.expanded h2").each(function() {
        jQuery('<span class="toggler"></span>').click(function() {
            $(this).parents("div.module").toggleClass("collapsed").toggleClass("expanded");
        }).appendTo(this);
    });
});
