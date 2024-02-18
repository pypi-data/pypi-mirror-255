def test_write_r1(tmp_path):
    from protozfits import ProtobufZOFits, File
    from protozfits.R1v1_pb2 import Event, CameraConfiguration
    from protozfits.R1v1_debug_pb2 import DebugEvent, DebugCameraConfiguration

    path = tmp_path / "foo.fits.fz"

    with ProtobufZOFits() as f:
        f.open(str(path))
        f.move_to_new_table("CameraConfiguration")
        f.write_message(CameraConfiguration(local_run_id=1, debug=DebugCameraConfiguration(evb_version="1.0.0")))
        f.move_to_new_table("Events")

        for i in range(1, 11):
            e = Event(event_id=i, debug=DebugEvent(extdevices_presence=0b11))
            f.write_message(e)

    assert path.is_file()

    with File(str(path)) as f:
        camera_config = f.CameraConfiguration[0]
        assert camera_config.local_run_id == 1
        assert camera_config.debug.evb_version == "1.0.0"

        i = 0
        for e in f.Events:
            i += 1
            assert e.event_id == i
            assert e.debug.extdevices_presence == 0b11

        assert i == 10

def test_write_dl0(tmp_path):
    from protozfits import ProtobufZOFits, File
    from protozfits.DL0v1_Subarray_pb2 import (
        Event as SubarrayEvent,
        DataStream as SubarrayDataStream,
    )
    from protozfits.DL0v1_Telescope_pb2 import (
        Event as TelescopeEvent,
        DataStream as TelescopeDataStream,
        CameraConfiguration,
    )

    path = tmp_path / "foo.fits.fz"

    with ProtobufZOFits() as f:
        f.open(str(path))
        f.move_to_new_table("CameraConfiguration")
        f.write_message(CameraConfiguration(tel_id=3))
        f.move_to_new_table("DataStream")
        f.write_message(TelescopeDataStream(sb_id=1, obs_id=2, tel_id=3))
        f.move_to_new_table("Events")

        for i in range(1, 11):
            e = TelescopeEvent(event_id=i, tel_id=3)
            f.write_message(e)

    assert path.is_file()

    with File(str(path)) as f:
        camera_config = f.CameraConfiguration[0]
        assert camera_config.tel_id == 3

        data_stream = f.DataStream[0]
        assert data_stream.sb_id == 1
        assert data_stream.obs_id == 2
        assert data_stream.tel_id == 3

        i = 0
        for e in f.Events:
            i += 1
            assert e.event_id == i
            assert e.tel_id == 3

        assert i == 10

def test_write_proto_r1(tmp_path):
    from protozfits import ProtobufZOFits, File
    from protozfits.ProtoR1_pb2 import CameraEvent, CameraConfiguration

    path = tmp_path / "foo.fits.fz"

    with ProtobufZOFits() as f:
        f.open(str(path))
        f.move_to_new_table("CameraConfiguration")
        f.write_message(CameraConfiguration(configuration_id=1))
        f.move_to_new_table("Events")

        for i in range(1, 11):
            e = CameraEvent(event_id=i)
            f.write_message(e)

    assert path.is_file()
    
    with File(str(path)) as f:
        camera_config = f.CameraConfiguration[0]
        assert camera_config.configuration_id == 1

        i = 0
        for e in f.Events:
            i += 1
            assert e.event_id == i

        assert i == 10
