"""
Sphinx plugins for RapidSMS documentation.
"""

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            from django.utils import simplejson as json
        except ImportError:
            json = None

from sphinx import addnodes, roles
from sphinx.util.compat import Directive


def setup(app):
    app.add_crossref_type(
        directivename = "setting",
        rolename      = "setting",
        indextemplate = "pair: %s; setting",
    )
    app.add_crossref_type(
        directivename = "templatetag",
        rolename      = "ttag",
        indextemplate = "pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename = "templatefilter",
        rolename      = "tfilter",
        indextemplate = "pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename = "router",
        rolename      = "router",
        indextemplate = "pair: %s; router",
    )
    app.add_config_value('rapidsms_next_version', '0.0', True)
    app.add_directive('versionadded', VersionDirective)
    app.add_directive('versionchanged', VersionDirective)


class VersionDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        arg0 = self.arguments[0]
        is_nextversion = env.config.rapidsms_next_version == arg0
        ret = []
        node = addnodes.versionmodified()
        ret.append(node)
        if not is_nextversion:
            if len(self.arguments) == 1:
                linktext = 'Please, see the release notes </releases/%s>' % (arg0)
                xrefs = roles.XRefRole()('doc', linktext, linktext,
                                         self.lineno, self.state)
                node.extend(xrefs[0])
            node['version'] = arg0
        else:
            node['version'] = "Development version"
        node['type'] = self.name
        if len(self.arguments) == 2:
            inodes, messages = self.state.inline_text(self.arguments[1],
                                                      self.lineno+1)
            node.extend(inodes)
            if self.content:
                self.state.nested_parse(self.content, self.content_offset,
                                        node)
            ret = ret + messages
        env.note_versionchange(node['type'], node['version'], node,
                               self.lineno)
        return ret
