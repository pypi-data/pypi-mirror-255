'''This module defines all of the APIs to Adhawk's embedded devices'''

from .error import CommunicationError, Error, RecoverableCommunicationError
from .publicapi import (
    REQUEST_TIMEOUT,
    AckCodes,
    APIRequestError,
    BlobType,
    BlobVersion,
    CameraResolution,
    CameraType,
    CameraUserSettings,
    EventControlBit,
    Events,
    EyeTrackingStreamBits,
    EyeTrackingStreamData,
    EyeTrackingStreamTypes,
    FeatureStreamBits,
    FeatureStreamData,
    FeatureStreamTypes,
    EyeMask,
    LogMode,
    MarkerSequenceMode,
    PacketType,
    ProcedureType,
    PropertyType,
    StreamControlBit,
    StreamRates,
    SystemControlType,
    SystemInfo,
    errormsg
)
