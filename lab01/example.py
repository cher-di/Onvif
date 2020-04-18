from collections import OrderedDict
from datetime import timedelta

import zeep
from onvif import ONVIFCamera, ONVIFService
from zeep import helpers
import json


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

IP = "172.18.212.17"  # Camera IP address
PORT = 80  # Port
USER = "laba2102"  # Username
PASS = "TMPpassword"  # Password


def delete_rec(element):
    if type(element) == OrderedDict:
        for key, value in element.items():
            if key in ['_value_1'] and type(element[key]) not in [OrderedDict]:
                element[key] = str(element[key])
            elif type(value) in [timedelta]:
                element[key] = str(element[key])
            else:
                delete_rec(element[key])
            if type(element[key]) in (tuple, list):
                for i in element[key]:
                    delete_rec(i)


if __name__ == '__main__':
    mycam = ONVIFCamera(IP, PORT, USER, PASS)
    print(mycam.devicemgmt.GetDeviceInformation())

    mycam = ONVIFCamera(IP, PORT, USER, PASS)
    media = mycam.create_media_service()

    # Получаем профили
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

    # Делаем AbsoluteMove
    moverequest = ptz_service.create_type('AbsoluteMove')
    moverequest.ProfileToken = tokens["Profile"]
    moverequest.Position = ptz_service.GetStatus({'ProfileToken': tokens["Profile"]}).Position
    moverequest.Position.PanTilt.x = 0.7
    moverequest.Position.PanTilt.y = 0.7
    moverequest.Position.Zoom = 0
    ptz_service.AbsoluteMove(moverequest)

    # # Делаем ContinuousMove
    # moverequest = ptz_service.create_type('ContinuousMove')
    # moverequest.Pro   fileToken = tokens["Profile"]
    # moverequest.Velocity = ptz_service.GetStatus({'ProfileToken': tokens["Profile"]}).Position
    # moverequest.Velocity.PanTilt.x = 0
    # moverequest.Velocity.PanTilt.y = -1
    # moverequest.Velocity.Zoom.x = 0
    # moverequest.Velocity.PanTilt.space = ''
    # moverequest.Velocity.Zoom.space = ''
    # ptz_service.ContinuousMove(moverequest)
    #
    # # Меняем фокус
    # moverequest = imaging_service.create_type('Move')
    # moverequest.VideoSourceToken = tokens["VideoSourceConfigurationSourceToken"]
    # moverequest.Focus = imaging_service.GetMoveOptions(
    #     {'VideoSourceToken': tokens["VideoSourceConfigurationSourceToken"]}).Continuous
    # print(moverequest.Focus)
    # imaging_service.Move(moverequest)

    # for profile in profiles_dict:
    #     delete_rec(profile)
    #
    # with open("onvif.json", "wt") as file:
    #     json.dump(profiles_dict[0], file, indent=4)
