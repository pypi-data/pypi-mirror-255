'''Module that provides a simple way to decode a packet
Usage:
    retcode, size = adhawkapi.decode(PacketType.BLOB_SIZE, response[1:])
'''
import copy
import struct

from adhawkapi import (
    AckCodes, Events, EyeMask, EyeTrackingStreamData, EyeTrackingStreamTypes,
    FeatureStreamData, FeatureStreamTypes, PacketType, PropertyType, SystemInfo)

try:
    from ..internal_codec import decoders as internal_decoders
except ImportError:
    internal_decoders = None


def decode(packet_type, data, eye_mask):
    '''Decode the message given a specific packet type
    Returns:
        The decoded packet or None if the packet cannot be decoded
    '''
    try:
        if eye_mask == EyeMask.BINOCULAR:
            decoder = _DECODERS_BINOCULAR[packet_type]
        else:
            decoder = _DECODERS_MONOCULAR[packet_type]
    except KeyError:
        decoder = None
        if internal_decoders:
            decoder = internal_decoders.get_decoder(packet_type, data, eye_mask)

    try:
        if not decoder:
            return struct.unpack('<B', data)
        return decoder(data)
    except Exception as exc:  # pylint: disable=broad-except
        if data[0] != AckCodes.SUCCESS:
            # The only time the decoder format won't match is in the
            # case of an error response (ex: timeout)
            return (data[0],)
        raise ValueError(f'No decoder defined for {hex(packet_type)}') from exc


def _decode_blob_data(data):
    if len(data) > 1:
        return data[0], data[1:]
    # Response for the setter should just be the request result
    return struct.unpack('<B', data)


def _decode_blob_size(data):
    if len(data) > 1:
        return struct.unpack('<BH', data)
    # Response for a setter should just be the request result
    return struct.unpack('<B', data)


def _decode_property_get(data):
    '''Expected response format for property get: (AckCode, PropertyType, data..)'''
    parser = None
    if data[1] == PropertyType.STREAM_CONTROL:
        parser = '<BBf'
    elif data[1] == PropertyType.COMPONENT_OFFSETS:
        parser = '<BB6f'
    elif data[1] == PropertyType.EVENT_CONTROL:
        parser = '<BBB'
    elif data[1] == PropertyType.NOMINAL_EYE_OFFSETS:
        parser = '<BB6f'
    elif data[1] == PropertyType.EYETRACKING_RATE:
        parser = '<BBf'
    elif data[1] == PropertyType.EYETRACKING_STREAMS:
        parser = '<BBL'
    elif data[1] == PropertyType.FEATURE_STREAMS:
        parser = '<BBL'

    if not parser and internal_decoders:
        parser = internal_decoders.get_property_parser(data[1])

    if parser is not None:
        return struct.unpack(parser, data)

    raise ValueError(f'No decoder defined for {PacketType.PROPERTY_GET.name}:{PropertyType(data[1]).name}')


def _decode_request_backend_version(data):
    ackcode, backend_version = struct.unpack_from(f'<B{len(data) - 2}s', data)
    return ackcode, backend_version.decode('utf-8')


def _decode_request_system_info(data):
    ackcode, _sys_info_type = struct.unpack_from('<BB', data)
    data_temp = copy.copy(data[2:])
    info = []
    if ackcode != AckCodes.SUCCESS:
        return ackcode, info
    while len(data_temp) > 0:
        assert len(data_temp) != 1  # multi-request data should always come in sets of 2 (or 3 in the case of a string)
        if data_temp[0] in (SystemInfo.DEVICE_SERIAL, SystemInfo.FIRMWARE_VERSION):
            # if it is a string, grab the length of the string first:
            _info_type, str_length = struct.unpack_from('<BB', data_temp)
            info.append(data_temp[2:str_length + 2].decode('utf-8').split('\0', 1)[0])
            data_temp = data_temp[str_length + 2:]
        elif data_temp[0] == SystemInfo.FIRMWARE_API:
            _info_type, data_len = struct.unpack_from('<BB', data_temp)
            if data_len == 4:
                # Old versions of tros sent this as just a single version, not the string we expect
                version, = struct.unpack('<I', data_temp[2:6])
                info.append(f'0.{version}.0')
                data_temp = data_temp[6:]
            else:
                info.append(data_temp[2:data_len + 2].decode('utf-8').split('\0', 1)[0])
                data_temp = data_temp[data_len + 2:]
        else:
            # it will be an infotype followed by a 1 followed by a byte, requester knows order so just pack it in.
            _info_type, _len, byte_info = struct.unpack_from('<BBB', data_temp)
            assert _len == 1
            info.append(byte_info)
            data_temp = data_temp[3:]

    return ackcode, info


def _decode_start_log_session(data):
    err, data = struct.unpack(f'<B{len(data) - 1}s', data)
    return err, data.decode('utf-8')


_EVENTS_DECODE = {
    Events.BLINK: '<ff',  # timestamp, duration
    Events.SACCADE: '<f4f',  # timestamp, duration, amplitude, angle, peak_vel
    Events.SACCADE_START: '<fB',  # timestamp, eye_idx
    Events.SACCADE_END: '<fB4f',  # timestamp, eye_idx, duration, amplitude, angle, peak_vel
    Events.EYE_CLOSED: '<fB',  # timestamp, eye_idx
    Events.EYE_OPENED: '<fB',  # timestamp, eye_idx
    Events.TRACKLOSS_START: '<fB',  # timestamp, eye_idx
    Events.TRACKLOSS_END: '<fB',  # timestamp, eye_idx
    Events.VALIDATION_SAMPLE: '<f8f',  # timestamp, ref_x, ref_y, ref_z, gaze_x, gaze_y, gaze_z, vergence, precision
    Events.VALIDATION_SUMMARY: '<ff',  # timestamp, mae
    Events.PROCEDURE_STARTED: '<f',  # timestamp
    Events.PROCEDURE_ENDED: '<fB',  # timestamp, results
    Events.EXTERNAL_TRIGGER: '<fB',  # timestamp, trigger_id
}


def _decode_events(data):
    event_type = data[0]
    unpack_str = _EVENTS_DECODE.get(event_type)
    if unpack_str:
        return event_type, *struct.unpack_from(unpack_str, data, 1)
    raise ValueError(f'No decoder defined for event: {event_type}')


_MONOCULAR_ET_DECODE = {
    EyeTrackingStreamTypes.GAZE: '<4f',
    EyeTrackingStreamTypes.PER_EYE_GAZE: '<3f',
    EyeTrackingStreamTypes.EYE_CENTER: '<3f',
    EyeTrackingStreamTypes.PUPIL_POSITION: '<3f',
    EyeTrackingStreamTypes.PUPIL_DIAMETER: '<f',
    EyeTrackingStreamTypes.GAZE_IN_IMAGE: '<4f',
    EyeTrackingStreamTypes.GAZE_IN_SCREEN: '<2f',
    EyeTrackingStreamTypes.IMU_QUATERNION: '<4f',
}

_BINOCULAR_ET_DECODE = {
    EyeTrackingStreamTypes.GAZE: '<4f',
    EyeTrackingStreamTypes.PER_EYE_GAZE: '<6f',
    EyeTrackingStreamTypes.EYE_CENTER: '<6f',
    EyeTrackingStreamTypes.PUPIL_POSITION: '<6f',
    EyeTrackingStreamTypes.PUPIL_DIAMETER: '<2f',
    EyeTrackingStreamTypes.GAZE_IN_IMAGE: '<4f',
    EyeTrackingStreamTypes.GAZE_IN_SCREEN: '<2f',
    EyeTrackingStreamTypes.IMU_QUATERNION: '<4f',
}


def _add_struct_size_to_et_decode(decode_dict):
    for key, format_str in decode_dict.items():
        decode_dict[key] = (format_str, struct.calcsize(format_str))


_add_struct_size_to_et_decode(_MONOCULAR_ET_DECODE)
_add_struct_size_to_et_decode(_BINOCULAR_ET_DECODE)

# mapping of stream types to fields from EyeTrackingStreamData
_ET_STREAM_TYPES = {
    EyeTrackingStreamTypes.GAZE: 'gaze',
    EyeTrackingStreamTypes.PER_EYE_GAZE: 'per_eye_gaze',
    EyeTrackingStreamTypes.EYE_CENTER: 'eye_center',
    EyeTrackingStreamTypes.PUPIL_POSITION: 'pupil_pos',
    EyeTrackingStreamTypes.PUPIL_DIAMETER: 'pupil_diameter',
    EyeTrackingStreamTypes.GAZE_IN_IMAGE: 'gaze_in_image',
    EyeTrackingStreamTypes.GAZE_IN_SCREEN: 'gaze_in_screen',
    EyeTrackingStreamTypes.IMU_QUATERNION: 'imu_quaternion',
}


def _decode_et_stream(data):
    timestamp, eye_mask = struct.unpack_from('<QB', data, 0)
    et_data = EyeTrackingStreamData(timestamp * 1e-9, EyeMask(eye_mask), None, None, None,
                                    None, None, None, None, None)
    offset = struct.calcsize('<QB')
    decode_map = _BINOCULAR_ET_DECODE if eye_mask == 3 else _MONOCULAR_ET_DECODE
    while offset < len(data):
        stream_type, = struct.unpack_from('<B', data, offset)
        offset += 1
        field_name = _ET_STREAM_TYPES.get(stream_type)
        if field_name:
            format_str, struct_size = decode_map[stream_type]
            setattr(et_data, field_name, struct.unpack_from(format_str, data, offset))
            offset += struct_size
        else:
            raise ValueError(f'Unknown or unsupported et stream type {stream_type}')
    return et_data


def _decode_feature_stream(data):
    timestamp, tracker_id = struct.unpack_from('<QB', data, 0)
    offset = struct.calcsize('<QB')
    feature_data = FeatureStreamData(timestamp * 1e-9, tracker_id, None, None, None)
    glints = []
    while offset < len(data):
        stream_type, = struct.unpack_from('<B', data, offset)
        offset += 1
        if stream_type == FeatureStreamTypes.GLINT:
            glint = struct.unpack_from('<B2f', data, offset)
            offset += struct.calcsize('<B2f')
            glints.append(glint)
        elif stream_type == FeatureStreamTypes.FUSED:
            feature_data.fused = struct.unpack_from('<2f', data, offset)
            offset += struct.calcsize('<2f')
        elif stream_type == FeatureStreamTypes.PUPIL_ELLIPSE:
            feature_data.ellipse = struct.unpack_from('<5f', data, offset)
            offset += struct.calcsize('<5f')
        else:
            raise ValueError(f'Unknown or unsupported feature stream type {stream_type}')
    if len(glints) > 0:
        feature_data.glints = glints
    return feature_data


def _decode_get_tracker_time(data):
    result, tracker_time_ns = struct.unpack('<Bq', data)
    return result, tracker_time_ns / 1e9


def _decode_get_unix_time(data):
    result, unix_time_ns = struct.unpack('<Bq', data)
    return result, unix_time_ns / 1e9


_DECODERS = {
    # streams
    PacketType.EYETRACKING_STREAM: _decode_et_stream,
    PacketType.FEATURE_STREAM: _decode_feature_stream,
    PacketType.PULSE: (lambda data: struct.unpack('<B5fB', data)),
    PacketType.GLINT: (lambda data: struct.unpack('<B3fB', data)),
    PacketType.FUSE: (lambda data: struct.unpack('<B3fB', data)),
    PacketType.GAZE: (lambda data: struct.unpack('<5f', data)),
    PacketType.PUPIL_CENTER: (lambda data: struct.unpack('<B3f', data)),
    PacketType.PUPIL_ELLIPSE: (lambda data: struct.unpack('<B6f', data)),
    PacketType.IMU: (lambda data: struct.unpack('<7f', data)),
    PacketType.IMU_ROTATION: (lambda data: struct.unpack('<4f', data)),
    PacketType.IRIS_IMAGE_DATA_STREAM: (lambda data: struct.unpack('<BI100B', data)),
    PacketType.EVENTS: _decode_events,
    PacketType.GAZE_IN_IMAGE: (lambda data: struct.unpack('<5f', data)),
    PacketType.GAZE_IN_SCREEN: (lambda data: struct.unpack('<3f', data)),
    PacketType.MCU_TEMPERATURE: (lambda data: struct.unpack('<2f', data)),

    # responses
    PacketType.TRACKER_READY: (lambda data: tuple()),
    PacketType.TRACKER_STATE: (lambda data: data),
    PacketType.CALIBRATION_ERROR: (lambda data: struct.unpack('<ff', data)),
    PacketType.BLOB_SIZE: _decode_blob_size,
    PacketType.BLOB_DATA: _decode_blob_data,
    PacketType.SAVE_BLOB: (lambda data: struct.unpack('<BI', data)),
    PacketType.START_LOG_SESSION: _decode_start_log_session,
    PacketType.REQUEST_SYSTEM_INFO: _decode_request_system_info,
    PacketType.REQUEST_BACKEND_VERSION: _decode_request_backend_version,
    PacketType.PROPERTY_SET: (lambda data: struct.unpack('<BB', data)),
    PacketType.PROPERTY_GET: _decode_property_get,
    PacketType.SYSTEM_CONTROL: (lambda data: struct.unpack('<BB', data)),
    PacketType.PROCEDURE_START: (lambda data: struct.unpack('<BB', data)),
    PacketType.PROCEDURE_STATUS: (lambda data: struct.unpack('<3B', data)),
    PacketType.GET_TRACKER_TIME: _decode_get_tracker_time,
    PacketType.GET_UNIX_TIME: _decode_get_unix_time,
}

_DECODERS_BINOCULAR = {
    PacketType.PER_EYE_GAZE: (lambda data: struct.unpack('<7f', data)),
    PacketType.PUPIL_POSITION: (lambda data: struct.unpack('<7f', data)),
    PacketType.PUPIL_DIAMETER: (lambda data: struct.unpack('<3f', data)),
    **_DECODERS
}

_DECODERS_MONOCULAR = {
    PacketType.PER_EYE_GAZE: (lambda data: struct.unpack('<4f', data)),
    PacketType.PUPIL_POSITION: (lambda data: struct.unpack('<4f', data)),
    PacketType.PUPIL_DIAMETER: (lambda data: struct.unpack('<2f', data)),
    **_DECODERS
}
