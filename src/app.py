import binascii
import logging
import subprocess
from os import path
import aiohttp_jinja2
import jinja2
from aiohttp import web
from file_utils import has_uploaded_file, retrieve_uploaded_file
import logging2

logger = logging.getLogger(__name__)


PWD = path.dirname(path.abspath(__file__))
SUPPORTED_LIDAR_FORMAT = {'.las', '.laz', '.ptx', '.ply'}
routes = web.RouteTableDef()


@routes.get('/')
@aiohttp_jinja2.template('index.html')
async def index(request: web.Request):
    return dict()


@routes.get('/test')
@aiohttp_jinja2.template('viz.html')
async def test(request: web.Request):
    point_cloud = 'http://5.9.65.151/mschuetz/potree/resources/pointclouds/riegl/retz'
    #point_cloud = '/static/temp/f09988b7-810f-4b97-9a05-921c88f1f93a'
    return dict(point_cloud=point_cloud)

@routes.post('/')
@aiohttp_jinja2.template('viz.html')
async def upload_file(request: web.Request):
    """
    :param request:
    :return:
    """
    if not has_uploaded_file(request):
        raise web.HTTPBadRequest(text='No file uploaded')
    else:
        original_filename, filename_on_host, other_data = await retrieve_uploaded_file(request)
        main_name, ext = path.splitext(path.basename(filename_on_host))
        if ext not in SUPPORTED_LIDAR_FORMAT:
            raise web.HTTPBadRequest(text=f'Only support Lidar format: {SUPPORTED_LIDAR_FORMAT}')

        cmd = f'PotreeConverter {filename_on_host} --overwrite -o {PWD}/static/temp/{main_name}'
        subprocess.call(cmd, shell=True)
        return dict(point_cloud=f'/static/temp/{main_name}', title=original_filename)


routes.static('/static', path.join(PWD, 'static'))


async def make_app():
    app = web.Application(logger=logging2.getLogger(__name__),
                          client_max_size=(2**20) * 20)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(path.join(PWD, 'templates')))
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=80, access_log=None)
