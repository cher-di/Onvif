import zeep_fix

from onvif import ONVIFCamera
from zeep import helpers
from datetime import timedelta

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
    profile_token = main_profile["token"]
    ptz_conf_token = main_profile['PTZConfiguration']['token']

    # Получаем данные для вращения
    ptz_service = mycam.create_ptz_service()
    ptz_configuration = ptz_service.GetConfiguration(ptz_conf_token)
    default_ptz_speed = ptz_configuration.DefaultPTZSpeed
    # default_ptz_timeout = ptz_configuration.DefaultPTZTimeout

    # Делаем ContinuousMove
    moverequest = ptz_service.create_type('ContinuousMove')
    moverequest.ProfileToken = profile_token
    del default_ptz_speed["PanTilt"]["space"]
    del default_ptz_speed["Zoom"]
    moverequest.Velocity = default_ptz_speed
    moverequest.Velocity.PanTilt.x = 0.5
    moverequest.Velocity.PanTilt.y = 0.5
    moverequest.Timeout = timedelta(seconds=2)
    ptz_service.ContinuousMove(moverequest)
