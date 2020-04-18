import zeep_fix

from onvif import ONVIFCamera, ONVIFService
from zeep import helpers

from credentials import *


if __name__ == '__main__':
    mycam = ONVIFCamera(IP, PORT, USER, PASS)

    # Получаем профили
    media = mycam.create_media_service()
    profiles = media.GetProfiles()
    profiles_dict = helpers.serialize_object(profiles)

    # Берём главный профиль
    main_profile = profiles_dict[0]

    # Получаем токен
    profile_token = main_profile["token"]

    # Делаем AbsoluteMove
    ptz_service = mycam.create_ptz_service()
    moverequest = ptz_service.create_type('AbsoluteMove')
    moverequest.ProfileToken = profile_token
    moverequest.Position = ptz_service.GetStatus({'ProfileToken': profile_token}).Position
    moverequest.Position.PanTilt.x = 0.7
    moverequest.Position.PanTilt.y = 0.7
    moverequest.Position.Zoom = 0
    ptz_service.AbsoluteMove(moverequest)
