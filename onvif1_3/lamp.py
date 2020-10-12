import zeep


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from onvif import ONVIFCamera, ONVIFService
from zeep import helpers

import numpy as np
import requests

from wand.image import Image
from requests.auth import HTTPBasicAuth

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


if __name__ == '__main__':
    mycam = ONVIFCamera(host=IP,
                        port=PORT,
                        user=USER,
                        passwd=PASS)

    # Получаем профили
    media = mycam.create_media_service()
    profiles = media.GetProfiles()
    profiles_dict = helpers.serialize_object(profiles)

    # Берём главный профиль
    main_profile = profiles_dict[0]

    # Получаем токен
    profile_token = main_profile['token']

    snapshot_uri_request = make_snapshot_uri_request(media, profile_token)
    url = get_image_url(media, snapshot_uri_request)
    image = get_image(url, USER, PASS)

    array = np.array(image)
    print(array)
