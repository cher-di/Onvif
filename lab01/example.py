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
