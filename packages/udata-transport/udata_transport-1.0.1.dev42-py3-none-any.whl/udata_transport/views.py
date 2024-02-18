from flask import Blueprint

from udata_front import theme
from udata.frontend import template_hook


blueprint = Blueprint('transport', __name__, template_folder='templates')


def has_transport_url(ctx):
    dataset = ctx['dataset']
    return dataset and dataset.extras.get('transport:url', '')


@template_hook('dataset.display.transport-banner', when=has_transport_url)
def dataset_transport(ctx):
    transport_url = ctx['dataset'].extras.get('transport:url', '')
    return theme.render('dataset-transport.html', transport_url=transport_url)
