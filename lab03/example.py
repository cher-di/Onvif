import zeep_fix

from onvif import ONVIFCamera
from zeep import helpers

from credentials import *

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
    imaging_conf_token = main_profile['VideoSourceConfiguration']['SourceToken']

    # Получаем данные для изменения яркости и контрастности
    imaging_service = mycam.create_imaging_service()
    imaging_configuration = imaging_service.GetImagingSettings(imaging_conf_token)

    # Меняем яркость и контранстность
    set_imaging_conf_request = imaging_service.create_type("SetImagingSettings")
    set_imaging_conf_request.VideoSourceToken = imaging_conf_token
    for key in tuple(imaging_configuration):
        if key not in ('Brightness', 'Contrast'):
            del imaging_configuration[key]
    imaging_configuration.Brightness = 85.0
    imaging_configuration.Contrast = 85.0
    set_imaging_conf_request.ImagingSettings = imaging_configuration
    imaging_service.SetImagingSettings(set_imaging_conf_request)
