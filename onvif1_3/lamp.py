import zeep


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

from onvif import ONVIFCamera
from zeep import helpers
from urllib.request import urlopen

IP = '172.18.212.12'
PORT = 80
USER = 'student2020'
PASS = 'student2020'

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

    get_snapshot_uri = media.create_type('GetSnapshotUri')
    get_snapshot_uri.ProfileToken = profile_token

    result = media.GetSnapshotUri(get_snapshot_uri)
    url = result['Uri']
    image = urlopen(url).read()
    with open('image.jpg', 'wb') as file:
        file.write(image)
