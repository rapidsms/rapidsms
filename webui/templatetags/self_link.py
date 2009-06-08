#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


class SelfLinkNode(template.Node):
    def __init__(self, *args):
        self.args = args

    def render(self, context):
        
        # resolve all arguments to their
        # values in the current context
        args = [template.resolve_variable(arg, context) for arg in self.args]
        
        # the output defaults to exactly the same url as we're
        # currently viewing, including the GET parameters
        try:
            kwargs = context["request"].GET.copy()
        
        # the exception handling during template rendering is kind of
        # crappy in django, since it masks the type of exceptions raised
        # within templatetags. if the context["request"] above raises a 
        # KeyError, it's very difficult to figure out what's going on -
        # so wrap it in our own (very verbose) exception
        except KeyError, err:
            raise(template.TemplateSyntaxError(
                "Where {% self_link %} is called, the context must contain an " +
                "HttpRequest object (named \"request\"), to access GET params"))
        
        # iterate the arguments to this token,
        # which come in pairs of: K,V,K,V,K,V
        while len(args):
            k = args.pop(0)
            v = args.pop(0)
            kwargs[k] = v
        
        # rebuild the new url: same as we're currently
        # viewing, with some GET arguments overridden
        return "%s?%s" % (context["request"].path, kwargs.urlencode())


@register.tag
def self_link(parser, token):
    args = token.split_contents()
    tag_name = args.pop(0)
    
    # this requires an even number of args, so they
    # can be converted into a dict without ambiguity
    if len(args) % 2:
        raise(template.TemplateSyntaxError(
            "The {%% self_link %%} tag requires an even number of arguments"))
    
    return SelfLinkNode(*args)


class SelfLinkFieldsNode(template.Node):
    def __init__(self, *args):
        self.omit = args
        
    def render(self, context):
        get = context["request"].GET
        
        # render ALL of the GET parameters,
        # except for those given in args
        return "".join([
            '<input type="hidden" name="%s" value="%s" />' % (k, get[k])
            for k in get.keys()
            if k not in self.omit
        ])

@register.tag
def self_link_fields(parser, token):
    args = token.split_contents()
    return SelfLinkFieldsNode(*args[1:])
