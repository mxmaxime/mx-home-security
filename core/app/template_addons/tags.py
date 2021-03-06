import os

from django import template
from django.utils.html import format_html
from django.conf import settings

from template_addons.assets_helper import AssetsHelper

register = template.Library()


assets_uri = os.getenv('ASSETS_DEV_SERVER', None)
public_asset = os.getenv('PUBLIC_ASSET', None)
env = os.getenv('ENV', 'prod')

if env == 'prod' and public_asset is None:
    raise ValueError('For production environment the env variable PUBLIC_ASSET have to be defined')

if env == 'dev' and assets_uri is None:
    raise ValueError('For dev environment the env variable ASSETS_DEV_SERVER have to be defined')

assets_helper = AssetsHelper(env, 'manifest.json', public_asset, assets_uri)

def _inject_vite_dev():
    return f'<script type="module" src="{assets_uri}/@vite/client"></script>'

INIT = False

@register.simple_tag()
def assets(filename: str):
    global INIT
    to_inject = ''

    if INIT is False and settings.ENV == 'dev':
        INIT = True
        to_inject += _inject_vite_dev()

    paths = assets_helper.path(filename)

    for path in paths:
        ext = path.split('.')[-1]

        # prod: it's file to be served on the same host.
        # dev: it's another host (dev server).
        path = f'/{path}' if settings.ENV == 'prod' else path

        if ext == 'css':
            to_inject += f'<link rel="stylesheet" media="screen" href="{path}">'

        if ext == 'js':
            to_inject += f'<script type="module" src="{path}" defer></script>'

    return format_html(to_inject)


@register.simple_tag()
def svg_icon(name: str, class_names: str = ''):
    return format_html(f"""
    <svg class="icon icon-{name} {class_names}">
      <use xlink:href="/public/svg/sprite.svg#{name}"></use>
    </svg>
    """)


@register.filter
def get_obj_attr(obj, attr):
    """
    Allows us to access property by variable value inside our templates.
    Example: `data={'monday': True}`, `day='monday'`, then we can do: `{{ data|get_obj_attr:day }}`


    Parameters
    ----------
    obj
    attr

    Returns
    -------
    Attribute of obj
    """
    return getattr(obj, attr)
