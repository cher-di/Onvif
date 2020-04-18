import zeep_fix
from onvif import ONVIFCamera, ONVIFService
from zeep import helpers

from credentials import *

if __name__ == '__main__':
    mycam = ONVIFCamera(IP, PORT, USER, PASS)
    print(mycam.devicemgmt.GetDeviceInformation())

    # Получаем профили
    media = mycam.create_media_service()
    profiles = media.GetProfiles()
    profiles_dict = helpers.serialize_object(profiles)

    # Берём главный профиль
    main_profile = profiles_dict[0]

    # Получаем данные о PTZ
    ptz_configuration = main_profile['PTZConfiguration']
    ptz_limits = ptz_configuration['PanTiltLimits']['Range']
    ptz_limits = {'x': ptz_limits['XRange'], 'y': ptz_limits['YRange']}
    ptz_zoom_limits = ptz_configuration['ZoomLimits']['Range']['XRange']

    # Получаем токены
    tokens = {
        "Profile": main_profile['token'],
        "VideoSourceConfiguration": main_profile['VideoSourceConfiguration']['token'],
        "VideoSourceConfigurationSourceToken": main_profile['VideoSourceConfiguration']['SourceToken'],
        "AudioSourceConfiguration": main_profile["AudioSourceConfiguration"]['token'],
        "AudioSourceConfigurationSourceToken": main_profile['AudioSourceConfiguration']['SourceToken'],
        "VideoEncoderConfiguration": main_profile["VideoEncoderConfiguration"]['token'],
        "AudioEncoderConfiguration": main_profile["AudioEncoderConfiguration"]['token'],
        "VideoAnalyticsConfiguration": main_profile["VideoAnalyticsConfiguration"]['token'],
        "PTZConfiguration": main_profile['PTZConfiguration']['token']
    }

    # Выводим токены
    for key, value in tokens.items():
        print(key, value)
    print()

    # Выводим 1 пункт
    print(f'PTZLimits: {ptz_limits}')
    print(f'PTZZoomLimits: {ptz_zoom_limits}\n')

    # Подключаемся к сервису Imaging
    imaging_service = mycam.create_imaging_service()

    # Получаем данные о фокусе
    imaging_settings = imaging_service.GetImagingSettings(tokens["VideoSourceConfigurationSourceToken"])
    imaging_settings = helpers.serialize_object(imaging_settings)
    focus = imaging_settings['Focus']

    # Выводим данные о фокусе
    print(f"Focus: {focus}\n")

    # Получаем данные об изменении фокуса
    imaging_move_options = imaging_service.GetMoveOptions(tokens["VideoSourceConfigurationSourceToken"])
    imaging_move_options = helpers.serialize_object(imaging_move_options)

    # Получаем данные об изменении фокуса
    print("GetMoveOptions")
    for key, value in imaging_move_options.items():
        print(key, value)
    print()

    # Подключаемся к сервису PTZ
    ptz_service = mycam.create_ptz_service()

    # Получаем данные о положении камеры и зума
    ptz_status = ptz_service.GetStatus(tokens["Profile"])
    ptz_status = helpers.serialize_object(ptz_status)

    ptz_camera_position = ptz_status['Position']['PanTilt']
    ptz_camera_position = {'x': ptz_camera_position['x'], 'y': ptz_camera_position['y']}
    ptz_zoom_position = ptz_status['Position']['Zoom']['x']

    # Выводим данные о положении камеры и зума
    print(f"Camera position: {ptz_camera_position}")
    print(f"Zoom position: {ptz_zoom_position}")

    # Получаем данные о том, пддерживает ли камера AbsoluteMove
    ptz_configuration_options = ptz_service.GetConfigurationOptions(tokens["PTZConfiguration"])
    ptz_configuration_options = helpers.serialize_object(ptz_configuration_options)

    # Выводим данные о том, поддерживает ли камера AbsoluteMove
    for key, value in ptz_configuration_options.items():
        print(key, value)
