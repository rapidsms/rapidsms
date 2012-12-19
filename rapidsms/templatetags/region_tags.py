#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
from django.template.loader import get_template
from ..conf import settings

register = template.Library()


class RegionNode(template.Node):
    def __init__(self, region_name):
        self.region_name = template.Variable(region_name)

    def _render_to_string(self, template_name, context):
        try:
            tmpl = get_template(template_name)
            return tmpl.render(context)

        # it's okay if the template couldn't be loaded; most regions
        # are never used. just ignore it, to be filtered out later.
        # allow all other exceptions to propagate
        except template.TemplateDoesNotExist:
            return None

    def render(self, context):
        region_name = self.region_name.resolve(context)

        short_module_names = [
            module_name.split(".")[-1]
            for module_name in settings.INSTALLED_APPS]

        template_names = [
            "%s/regions/%s.html" % (short_module_name, region_name)
            for short_module_name in short_module_names]

        strings = filter(None, [
            self._render_to_string(template_name, context)
            for template_name in template_names])

        if len(strings) == 0:
            return ""

        return '<div class="%s-region">%s</div>' % (
            region_name, "".join(strings))


@register.tag
def region(parser, token):
    """
    TODO: docs
    """

    args = token.contents.split()
    tag_name = args.pop(0)

    if len(args) != 1:
        raise template.TemplateSyntaxError(
            "The {%% %s %%} tag requires one argument" % (tag_name))

    return RegionNode(args[0])
