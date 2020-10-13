import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

import zeep


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from onvif import ONVIFCamera, ONVIFService
from zeep import helpers

import numpy as np
import requests
import time
import logging

from wand.image import Image
from requests.auth import HTTPBasicAuth
from datetime import datetime

IP = '172.18.212.17'
PORT = 80
USER = 'admin'
PASS = 'Supervisor'


def make_snapshot_uri_request(media_service: ONVIFService, profile_token: str):
    get_snapshot_uri = media_service.create_type('GetSnapshotUri')
    get_snapshot_uri.ProfileToken = profile_token
    return get_snapshot_uri


def get_image_url(media_service: ONVIFService, snapshot_uri_request):
    result = media_service.GetSnapshotUri(snapshot_uri_request)
    return result['Uri']


def get_image(url: str, user: str = None, password: str = None) -> Image:
    if not user:
        data = requests.get(url).content
    else:
        data = requests.get(url, auth=HTTPBasicAuth(user, password)).content
    return Image(blob=data)


def get_brightest_point(image: Image) -> tuple:
    array = np.array(image)
    normalized_image = np.mean(array, axis=2, dtype=np.int)
    center = np.unravel_index(normalized_image.argmax(), normalized_image.shape)
    return center[1], center[0]


def get_image_center(image: Image) -> tuple:
    x_max, y_max = image.size
    return x_max // 2, y_max // 2


def get_pantilt_delta(image: Image) -> tuple:
    xc, yc = get_image_center(image)
    xb, yb = get_brightest_point(image)
    x_max, y_max = image.size
    return (xb - xc) / x_max, (yb - yc) / y_max


def get_current_pantilt(ptz_service: ONVIFService, profile_token: str) -> tuple:
    ptz_status = ptz_service.GetStatus(profile_token)
    ptz_status = helpers.serialize_object(ptz_status)
    ptz_camera_position = ptz_status['Position']['PanTilt']
    return ptz_camera_position['x'], ptz_camera_position['y']


def get_current_zoom(ptz_service: ONVIFService, profile_token: str) -> float:
    ptz_status = ptz_service.GetStatus(profile_token)
    ptz_status = helpers.serialize_object(ptz_status)
    return ptz_status['Position']['Zoom']['x']


def get_pantilt_limits(main_profile: dict):
    ptz_configuration = main_profile['PTZConfiguration']
    ptz_limits = ptz_configuration['PanTiltLimits']['Range']
    return (ptz_limits['XRange']['Min'], ptz_limits['XRange']['Max']), \
           (ptz_limits['YRange']['Min'], ptz_limits['YRange']['Max'])


def make_absolute_move(ptz_service: ONVIFService, x: float, y: float):
    moverequest = ptz_service.create_type('AbsoluteMove')
    moverequest.ProfileToken = profile_token
    moverequest.Position = ptz_service.GetStatus({'ProfileToken': profile_token}).Position
    moverequest.Position.PanTilt.x = x
    moverequest.Position.PanTilt.y = y
    moverequest.Position.Zoom = get_current_zoom(ptz_service, profile_token)
    ptz_service.AbsoluteMove(moverequest)


def set_to_borders(value: float, left: float, right: float) -> float:
    if value > right:
        return right
    if value < left:
        return left
    return value


if __name__ == '__main__':
    before = datetime.now()

    mycam = ONVIFCamera(host=IP,
                        port=PORT,
                        user=USER,
                        passwd=PASS)

    # Получаем сервисы
    media_service = mycam.create_media_service()
    ptz_service = mycam.create_ptz_service()

    # Получаем профили
    profiles = media_service.GetProfiles()
    profiles_dict = helpers.serialize_object(profiles)

    # Берём главный профиль
    main_profile = profiles_dict[0]

    # Получаем токен
    profile_token = main_profile['token']

    snapshot_uri_request = make_snapshot_uri_request(media_service, profile_token)

    (xp_min, xp_max), (yp_min, yp_max) = get_pantilt_limits(main_profile)

    normal = False
    X_DELTA, Y_DELTA = 15, 15
    DELAY = 3
    ALPHA = 0.3
    BETTA = 0.005
    while not normal:
        before_step = datetime.now()

        url = get_image_url(media_service, snapshot_uri_request)
        image = get_image(url, USER, PASS)

        xc, yc = get_image_center(image)
        xb, yb = get_brightest_point(image)

        logging.info(f'Center: {xc}, {yc}')
        logging.info(f'Target: {xb}, {yb}')

        x_delta_abs, y_delta_abs = abs(xc - xb), abs(yc - yb)
        logging.info(f'Delta: {x_delta_abs}, {y_delta_abs}')

        x_curr, y_curr = get_current_pantilt(ptz_service, profile_token)
        logging.info(f'curr: {x_curr}, {x_curr}')

        if x_delta_abs > X_DELTA or y_delta_abs > Y_DELTA:
            x_delta, y_delta = get_pantilt_delta(image)
            x_new = x_curr + x_delta * ALPHA if x_delta_abs > X_DELTA else x_curr
            y_new = y_curr + y_delta * ALPHA if y_delta_abs > Y_DELTA else y_curr

            x_new = set_to_borders(x_new, xp_min, xp_max)
            y_new = set_to_borders(y_new, yp_min, yp_max)

            logging.info(f'new: {x_new}, {y_new}')

            logging.info(f'CurrAlpha: {ALPHA}')
            ALPHA = ALPHA - BETTA
            logging.info(f'NewAlpha: {ALPHA}')

            make_absolute_move(ptz_service, x_new, y_new)
            time.sleep(DELAY)

            logging.info('Absolute move completed')
        else:
            normal = True

        after_step = datetime.now()
        logging.info(f'Step time: {after_step - before_step}')
        logging.info(f'From start: {after_step - before}')

        logging.info('---------------------------------------------')

    after = datetime.now()
    logging.info(f'Time: {after - before}')
