"""
Sphinx plugins for RapidSMS documentation.
"""


def setup(app):
    app.add_crossref_type(
        directivename="setting",
        rolename="setting",
        indextemplate="pair: %s; setting",
    )
    app.add_crossref_type(
        directivename="router",
        rolename="router",
        indextemplate="pair: %s; router",
    )
