# -*- coding: utf-8 -*-
#
# TARGET arch is: ['-I/usr/lib/gcc/x86_64-linux-gnu/14/include']
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                type_ = type_._type_
                if hasattr(type_, 'as_dict'):
                    value = [type_.as_dict(v) for v in value]
                else:
                    value = [i for i in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



_libraries = {}
_libraries['libminiaudio.so'] = ctypes.CDLL('libminiaudio.so')
class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  ctypes.CDLL('FIXME_STUB')


ma_int8 = ctypes.c_byte
ma_uint8 = ctypes.c_ubyte
ma_int16 = ctypes.c_int16
ma_uint16 = ctypes.c_uint16
ma_int32 = ctypes.c_int32
ma_uint32 = ctypes.c_uint32
ma_int64 = ctypes.c_int64
ma_uint64 = ctypes.c_uint64
ma_uintptr = ctypes.c_uint64
ma_bool8 = ctypes.c_ubyte
ma_bool32 = ctypes.c_uint32
ma_float = ctypes.c_float
ma_double = ctypes.c_double
ma_handle = ctypes.POINTER(None)
ma_ptr = ctypes.POINTER(None)
ma_proc = ctypes.CFUNCTYPE(None)
ma_pthread_t = ctypes.c_uint64
class union_pthread_mutex_t(Union):
    pass

class struct___pthread_mutex_s(Structure):
    pass

class struct___pthread_internal_list(Structure):
    pass

struct___pthread_internal_list._pack_ = 1 # source:False
struct___pthread_internal_list._fields_ = [
    ('__prev', ctypes.POINTER(struct___pthread_internal_list)),
    ('__next', ctypes.POINTER(struct___pthread_internal_list)),
]

struct___pthread_mutex_s._pack_ = 1 # source:False
struct___pthread_mutex_s._fields_ = [
    ('__lock', ctypes.c_int32),
    ('__count', ctypes.c_uint32),
    ('__owner', ctypes.c_int32),
    ('__nusers', ctypes.c_uint32),
    ('__kind', ctypes.c_int32),
    ('__spins', ctypes.c_int16),
    ('__elision', ctypes.c_int16),
    ('__list', struct___pthread_internal_list),
]

union_pthread_mutex_t._pack_ = 1 # source:False
union_pthread_mutex_t._fields_ = [
    ('__data', struct___pthread_mutex_s),
    ('__size', ctypes.c_char * 40),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 32),
]

ma_pthread_mutex_t = union_pthread_mutex_t
class union_pthread_cond_t(Union):
    pass

class struct___pthread_cond_s(Structure):
    pass

class union___atomic_wide_counter(Union):
    pass

class struct___atomic_wide_counter___value32(Structure):
    pass

struct___atomic_wide_counter___value32._pack_ = 1 # source:False
struct___atomic_wide_counter___value32._fields_ = [
    ('__low', ctypes.c_uint32),
    ('__high', ctypes.c_uint32),
]

union___atomic_wide_counter._pack_ = 1 # source:False
union___atomic_wide_counter._fields_ = [
    ('__value64', ctypes.c_uint64),
    ('__value32', struct___atomic_wide_counter___value32),
]

struct___pthread_cond_s._pack_ = 1 # source:False
struct___pthread_cond_s._fields_ = [
    ('__wseq', union___atomic_wide_counter),
    ('__g1_start', union___atomic_wide_counter),
    ('__g_refs', ctypes.c_uint32 * 2),
    ('__g_size', ctypes.c_uint32 * 2),
    ('__g1_orig_size', ctypes.c_uint32),
    ('__wrefs', ctypes.c_uint32),
    ('__g_signals', ctypes.c_uint32 * 2),
]

union_pthread_cond_t._pack_ = 1 # source:False
union_pthread_cond_t._fields_ = [
    ('__data', struct___pthread_cond_s),
    ('__size', ctypes.c_char * 48),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 40),
]

ma_pthread_cond_t = union_pthread_cond_t
ma_wchar_win32 = ctypes.c_uint16

# values for enumeration 'ma_log_level'
ma_log_level__enumvalues = {
    4: 'MA_LOG_LEVEL_DEBUG',
    3: 'MA_LOG_LEVEL_INFO',
    2: 'MA_LOG_LEVEL_WARNING',
    1: 'MA_LOG_LEVEL_ERROR',
}
MA_LOG_LEVEL_DEBUG = 4
MA_LOG_LEVEL_INFO = 3
MA_LOG_LEVEL_WARNING = 2
MA_LOG_LEVEL_ERROR = 1
ma_log_level = ctypes.c_uint32 # enum
class struct_ma_context(Structure):
    pass

class struct_ma_log(Structure):
    pass

class struct_ma_device_info(Structure):
    pass

class struct_ma_backend_callbacks(Structure):
    pass


# values for enumeration 'ma_result'
ma_result__enumvalues = {
    0: 'MA_SUCCESS',
    -1: 'MA_ERROR',
    -2: 'MA_INVALID_ARGS',
    -3: 'MA_INVALID_OPERATION',
    -4: 'MA_OUT_OF_MEMORY',
    -5: 'MA_OUT_OF_RANGE',
    -6: 'MA_ACCESS_DENIED',
    -7: 'MA_DOES_NOT_EXIST',
    -8: 'MA_ALREADY_EXISTS',
    -9: 'MA_TOO_MANY_OPEN_FILES',
    -10: 'MA_INVALID_FILE',
    -11: 'MA_TOO_BIG',
    -12: 'MA_PATH_TOO_LONG',
    -13: 'MA_NAME_TOO_LONG',
    -14: 'MA_NOT_DIRECTORY',
    -15: 'MA_IS_DIRECTORY',
    -16: 'MA_DIRECTORY_NOT_EMPTY',
    -17: 'MA_AT_END',
    -18: 'MA_NO_SPACE',
    -19: 'MA_BUSY',
    -20: 'MA_IO_ERROR',
    -21: 'MA_INTERRUPT',
    -22: 'MA_UNAVAILABLE',
    -23: 'MA_ALREADY_IN_USE',
    -24: 'MA_BAD_ADDRESS',
    -25: 'MA_BAD_SEEK',
    -26: 'MA_BAD_PIPE',
    -27: 'MA_DEADLOCK',
    -28: 'MA_TOO_MANY_LINKS',
    -29: 'MA_NOT_IMPLEMENTED',
    -30: 'MA_NO_MESSAGE',
    -31: 'MA_BAD_MESSAGE',
    -32: 'MA_NO_DATA_AVAILABLE',
    -33: 'MA_INVALID_DATA',
    -34: 'MA_TIMEOUT',
    -35: 'MA_NO_NETWORK',
    -36: 'MA_NOT_UNIQUE',
    -37: 'MA_NOT_SOCKET',
    -38: 'MA_NO_ADDRESS',
    -39: 'MA_BAD_PROTOCOL',
    -40: 'MA_PROTOCOL_UNAVAILABLE',
    -41: 'MA_PROTOCOL_NOT_SUPPORTED',
    -42: 'MA_PROTOCOL_FAMILY_NOT_SUPPORTED',
    -43: 'MA_ADDRESS_FAMILY_NOT_SUPPORTED',
    -44: 'MA_SOCKET_NOT_SUPPORTED',
    -45: 'MA_CONNECTION_RESET',
    -46: 'MA_ALREADY_CONNECTED',
    -47: 'MA_NOT_CONNECTED',
    -48: 'MA_CONNECTION_REFUSED',
    -49: 'MA_NO_HOST',
    -50: 'MA_IN_PROGRESS',
    -51: 'MA_CANCELLED',
    -52: 'MA_MEMORY_ALREADY_MAPPED',
    -100: 'MA_CRC_MISMATCH',
    -200: 'MA_FORMAT_NOT_SUPPORTED',
    -201: 'MA_DEVICE_TYPE_NOT_SUPPORTED',
    -202: 'MA_SHARE_MODE_NOT_SUPPORTED',
    -203: 'MA_NO_BACKEND',
    -204: 'MA_NO_DEVICE',
    -205: 'MA_API_NOT_FOUND',
    -206: 'MA_INVALID_DEVICE_CONFIG',
    -207: 'MA_LOOP',
    -208: 'MA_BACKEND_NOT_ENABLED',
    -300: 'MA_DEVICE_NOT_INITIALIZED',
    -301: 'MA_DEVICE_ALREADY_INITIALIZED',
    -302: 'MA_DEVICE_NOT_STARTED',
    -303: 'MA_DEVICE_NOT_STOPPED',
    -400: 'MA_FAILED_TO_INIT_BACKEND',
    -401: 'MA_FAILED_TO_OPEN_BACKEND_DEVICE',
    -402: 'MA_FAILED_TO_START_BACKEND_DEVICE',
    -403: 'MA_FAILED_TO_STOP_BACKEND_DEVICE',
}
MA_SUCCESS = 0
MA_ERROR = -1
MA_INVALID_ARGS = -2
MA_INVALID_OPERATION = -3
MA_OUT_OF_MEMORY = -4
MA_OUT_OF_RANGE = -5
MA_ACCESS_DENIED = -6
MA_DOES_NOT_EXIST = -7
MA_ALREADY_EXISTS = -8
MA_TOO_MANY_OPEN_FILES = -9
MA_INVALID_FILE = -10
MA_TOO_BIG = -11
MA_PATH_TOO_LONG = -12
MA_NAME_TOO_LONG = -13
MA_NOT_DIRECTORY = -14
MA_IS_DIRECTORY = -15
MA_DIRECTORY_NOT_EMPTY = -16
MA_AT_END = -17
MA_NO_SPACE = -18
MA_BUSY = -19
MA_IO_ERROR = -20
MA_INTERRUPT = -21
MA_UNAVAILABLE = -22
MA_ALREADY_IN_USE = -23
MA_BAD_ADDRESS = -24
MA_BAD_SEEK = -25
MA_BAD_PIPE = -26
MA_DEADLOCK = -27
MA_TOO_MANY_LINKS = -28
MA_NOT_IMPLEMENTED = -29
MA_NO_MESSAGE = -30
MA_BAD_MESSAGE = -31
MA_NO_DATA_AVAILABLE = -32
MA_INVALID_DATA = -33
MA_TIMEOUT = -34
MA_NO_NETWORK = -35
MA_NOT_UNIQUE = -36
MA_NOT_SOCKET = -37
MA_NO_ADDRESS = -38
MA_BAD_PROTOCOL = -39
MA_PROTOCOL_UNAVAILABLE = -40
MA_PROTOCOL_NOT_SUPPORTED = -41
MA_PROTOCOL_FAMILY_NOT_SUPPORTED = -42
MA_ADDRESS_FAMILY_NOT_SUPPORTED = -43
MA_SOCKET_NOT_SUPPORTED = -44
MA_CONNECTION_RESET = -45
MA_ALREADY_CONNECTED = -46
MA_NOT_CONNECTED = -47
MA_CONNECTION_REFUSED = -48
MA_NO_HOST = -49
MA_IN_PROGRESS = -50
MA_CANCELLED = -51
MA_MEMORY_ALREADY_MAPPED = -52
MA_CRC_MISMATCH = -100
MA_FORMAT_NOT_SUPPORTED = -200
MA_DEVICE_TYPE_NOT_SUPPORTED = -201
MA_SHARE_MODE_NOT_SUPPORTED = -202
MA_NO_BACKEND = -203
MA_NO_DEVICE = -204
MA_API_NOT_FOUND = -205
MA_INVALID_DEVICE_CONFIG = -206
MA_LOOP = -207
MA_BACKEND_NOT_ENABLED = -208
MA_DEVICE_NOT_INITIALIZED = -300
MA_DEVICE_ALREADY_INITIALIZED = -301
MA_DEVICE_NOT_STARTED = -302
MA_DEVICE_NOT_STOPPED = -303
MA_FAILED_TO_INIT_BACKEND = -400
MA_FAILED_TO_OPEN_BACKEND_DEVICE = -401
MA_FAILED_TO_START_BACKEND_DEVICE = -402
MA_FAILED_TO_STOP_BACKEND_DEVICE = -403
ma_result = ctypes.c_int32 # enum
class struct_ma_context_config(Structure):
    pass


# values for enumeration 'ma_device_type'
ma_device_type__enumvalues = {
    1: 'ma_device_type_playback',
    2: 'ma_device_type_capture',
    3: 'ma_device_type_duplex',
    4: 'ma_device_type_loopback',
}
ma_device_type_playback = 1
ma_device_type_capture = 2
ma_device_type_duplex = 3
ma_device_type_loopback = 4
ma_device_type = ctypes.c_uint32 # enum
class union_ma_device_id(Union):
    pass

class struct_ma_device(Structure):
    pass

class struct_ma_device_config(Structure):
    pass

class struct_ma_device_descriptor(Structure):
    pass

struct_ma_backend_callbacks._pack_ = 1 # source:False
struct_ma_backend_callbacks._fields_ = [
    ('onContextInit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_context), ctypes.POINTER(struct_ma_context_config), ctypes.POINTER(struct_ma_backend_callbacks))),
    ('onContextUninit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_context))),
    ('onContextEnumerateDevices', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_context), ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(struct_ma_context), ma_device_type, ctypes.POINTER(struct_ma_device_info), ctypes.POINTER(None)), ctypes.POINTER(None))),
    ('onContextGetDeviceInfo', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_context), ma_device_type, ctypes.POINTER(union_ma_device_id), ctypes.POINTER(struct_ma_device_info))),
    ('onDeviceInit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device), ctypes.POINTER(struct_ma_device_config), ctypes.POINTER(struct_ma_device_descriptor), ctypes.POINTER(struct_ma_device_descriptor))),
    ('onDeviceUninit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device))),
    ('onDeviceStart', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device))),
    ('onDeviceStop', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device))),
    ('onDeviceRead', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32))),
    ('onDeviceWrite', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32))),
    ('onDeviceDataLoop', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device))),
    ('onDeviceDataLoopWakeup', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device))),
    ('onDeviceGetInfo', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_device), ma_device_type, ctypes.POINTER(struct_ma_device_info))),
]

ma_backend_callbacks = struct_ma_backend_callbacks

# values for enumeration 'ma_backend'
ma_backend__enumvalues = {
    0: 'ma_backend_wasapi',
    1: 'ma_backend_dsound',
    2: 'ma_backend_winmm',
    3: 'ma_backend_coreaudio',
    4: 'ma_backend_sndio',
    5: 'ma_backend_audio4',
    6: 'ma_backend_oss',
    7: 'ma_backend_pulseaudio',
    8: 'ma_backend_alsa',
    9: 'ma_backend_jack',
    10: 'ma_backend_aaudio',
    11: 'ma_backend_opensl',
    12: 'ma_backend_webaudio',
    13: 'ma_backend_custom',
    14: 'ma_backend_null',
}
ma_backend_wasapi = 0
ma_backend_dsound = 1
ma_backend_winmm = 2
ma_backend_coreaudio = 3
ma_backend_sndio = 4
ma_backend_audio4 = 5
ma_backend_oss = 6
ma_backend_pulseaudio = 7
ma_backend_alsa = 8
ma_backend_jack = 9
ma_backend_aaudio = 10
ma_backend_opensl = 11
ma_backend_webaudio = 12
ma_backend_custom = 13
ma_backend_null = 14
ma_backend = ctypes.c_uint32 # enum
class struct_ma_log_callback(Structure):
    pass

struct_ma_log_callback._pack_ = 1 # source:False
struct_ma_log_callback._fields_ = [
    ('onLog', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(ctypes.c_char))),
    ('pUserData', ctypes.POINTER(None)),
]

class struct_ma_allocation_callbacks(Structure):
    pass

struct_ma_allocation_callbacks._pack_ = 1 # source:False
struct_ma_allocation_callbacks._fields_ = [
    ('pUserData', ctypes.POINTER(None)),
    ('onMalloc', ctypes.CFUNCTYPE(ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None))),
    ('onRealloc', ctypes.CFUNCTYPE(ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None))),
    ('onFree', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None))),
]

ma_allocation_callbacks = struct_ma_allocation_callbacks
ma_mutex = union_pthread_mutex_t
struct_ma_log._pack_ = 1 # source:False
struct_ma_log._fields_ = [
    ('callbacks', struct_ma_log_callback * 4),
    ('callbackCount', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('lock', ma_mutex),
]

ma_log = struct_ma_log

# values for enumeration 'ma_thread_priority'
ma_thread_priority__enumvalues = {
    -5: 'ma_thread_priority_idle',
    -4: 'ma_thread_priority_lowest',
    -3: 'ma_thread_priority_low',
    -2: 'ma_thread_priority_normal',
    -1: 'ma_thread_priority_high',
    0: 'ma_thread_priority_highest',
    1: 'ma_thread_priority_realtime',
    0: 'ma_thread_priority_default',
}
ma_thread_priority_idle = -5
ma_thread_priority_lowest = -4
ma_thread_priority_low = -3
ma_thread_priority_normal = -2
ma_thread_priority_high = -1
ma_thread_priority_highest = 0
ma_thread_priority_realtime = 1
ma_thread_priority_default = 0
ma_thread_priority = ctypes.c_int32 # enum
class union_ma_context_0(Union):
    pass

class struct_ma_context_0_alsa(Structure):
    pass

struct_ma_context_0_alsa._pack_ = 1 # source:False
struct_ma_context_0_alsa._fields_ = [
    ('asoundSO', ctypes.POINTER(None)),
    ('snd_pcm_open', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_close', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_sizeof', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_any', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_format', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_format_first', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_format_mask', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_channels', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_channels_near', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_channels_minmax', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_rate_resample', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_rate', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_rate_near', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_buffer_size_near', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_periods_near', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_set_access', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_format', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_channels', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_channels_min', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_channels_max', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_rate', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_rate_min', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_rate_max', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_buffer_size', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_periods', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_get_access', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_test_format', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_test_channels', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params_test_rate', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_hw_params', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_sizeof', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_current', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_get_boundary', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_set_avail_min', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_set_start_threshold', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params_set_stop_threshold', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_sw_params', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_format_mask_sizeof', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_format_mask_test', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_get_chmap', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_state', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_prepare', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_start', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_drop', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_drain', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_reset', ctypes.CFUNCTYPE(None)),
    ('snd_device_name_hint', ctypes.CFUNCTYPE(None)),
    ('snd_device_name_get_hint', ctypes.CFUNCTYPE(None)),
    ('snd_card_get_index', ctypes.CFUNCTYPE(None)),
    ('snd_device_name_free_hint', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_mmap_begin', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_mmap_commit', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_recover', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_readi', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_writei', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_avail', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_avail_update', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_wait', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_nonblock', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_info', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_info_sizeof', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_info_get_name', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_poll_descriptors', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_poll_descriptors_count', ctypes.CFUNCTYPE(None)),
    ('snd_pcm_poll_descriptors_revents', ctypes.CFUNCTYPE(None)),
    ('snd_config_update_free_global', ctypes.CFUNCTYPE(None)),
    ('internalDeviceEnumLock', ma_mutex),
    ('useVerboseDeviceEnumeration', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_context_0_pulse(Structure):
    pass

struct_ma_context_0_pulse._pack_ = 1 # source:False
struct_ma_context_0_pulse._fields_ = [
    ('pulseSO', ctypes.POINTER(None)),
    ('pa_mainloop_new', ctypes.CFUNCTYPE(None)),
    ('pa_mainloop_free', ctypes.CFUNCTYPE(None)),
    ('pa_mainloop_quit', ctypes.CFUNCTYPE(None)),
    ('pa_mainloop_get_api', ctypes.CFUNCTYPE(None)),
    ('pa_mainloop_iterate', ctypes.CFUNCTYPE(None)),
    ('pa_mainloop_wakeup', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_new', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_free', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_start', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_stop', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_lock', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_unlock', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_wait', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_signal', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_accept', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_get_retval', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_get_api', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_in_thread', ctypes.CFUNCTYPE(None)),
    ('pa_threaded_mainloop_set_name', ctypes.CFUNCTYPE(None)),
    ('pa_context_new', ctypes.CFUNCTYPE(None)),
    ('pa_context_unref', ctypes.CFUNCTYPE(None)),
    ('pa_context_connect', ctypes.CFUNCTYPE(None)),
    ('pa_context_disconnect', ctypes.CFUNCTYPE(None)),
    ('pa_context_set_state_callback', ctypes.CFUNCTYPE(None)),
    ('pa_context_get_state', ctypes.CFUNCTYPE(None)),
    ('pa_context_get_sink_info_list', ctypes.CFUNCTYPE(None)),
    ('pa_context_get_source_info_list', ctypes.CFUNCTYPE(None)),
    ('pa_context_get_sink_info_by_name', ctypes.CFUNCTYPE(None)),
    ('pa_context_get_source_info_by_name', ctypes.CFUNCTYPE(None)),
    ('pa_operation_unref', ctypes.CFUNCTYPE(None)),
    ('pa_operation_get_state', ctypes.CFUNCTYPE(None)),
    ('pa_channel_map_init_extend', ctypes.CFUNCTYPE(None)),
    ('pa_channel_map_valid', ctypes.CFUNCTYPE(None)),
    ('pa_channel_map_compatible', ctypes.CFUNCTYPE(None)),
    ('pa_stream_new', ctypes.CFUNCTYPE(None)),
    ('pa_stream_unref', ctypes.CFUNCTYPE(None)),
    ('pa_stream_connect_playback', ctypes.CFUNCTYPE(None)),
    ('pa_stream_connect_record', ctypes.CFUNCTYPE(None)),
    ('pa_stream_disconnect', ctypes.CFUNCTYPE(None)),
    ('pa_stream_get_state', ctypes.CFUNCTYPE(None)),
    ('pa_stream_get_sample_spec', ctypes.CFUNCTYPE(None)),
    ('pa_stream_get_channel_map', ctypes.CFUNCTYPE(None)),
    ('pa_stream_get_buffer_attr', ctypes.CFUNCTYPE(None)),
    ('pa_stream_set_buffer_attr', ctypes.CFUNCTYPE(None)),
    ('pa_stream_get_device_name', ctypes.CFUNCTYPE(None)),
    ('pa_stream_set_write_callback', ctypes.CFUNCTYPE(None)),
    ('pa_stream_set_read_callback', ctypes.CFUNCTYPE(None)),
    ('pa_stream_set_suspended_callback', ctypes.CFUNCTYPE(None)),
    ('pa_stream_set_moved_callback', ctypes.CFUNCTYPE(None)),
    ('pa_stream_is_suspended', ctypes.CFUNCTYPE(None)),
    ('pa_stream_flush', ctypes.CFUNCTYPE(None)),
    ('pa_stream_drain', ctypes.CFUNCTYPE(None)),
    ('pa_stream_is_corked', ctypes.CFUNCTYPE(None)),
    ('pa_stream_cork', ctypes.CFUNCTYPE(None)),
    ('pa_stream_trigger', ctypes.CFUNCTYPE(None)),
    ('pa_stream_begin_write', ctypes.CFUNCTYPE(None)),
    ('pa_stream_write', ctypes.CFUNCTYPE(None)),
    ('pa_stream_peek', ctypes.CFUNCTYPE(None)),
    ('pa_stream_drop', ctypes.CFUNCTYPE(None)),
    ('pa_stream_writable_size', ctypes.CFUNCTYPE(None)),
    ('pa_stream_readable_size', ctypes.CFUNCTYPE(None)),
    ('pMainLoop', ctypes.POINTER(None)),
    ('pPulseContext', ctypes.POINTER(None)),
    ('pApplicationName', ctypes.POINTER(ctypes.c_char)),
    ('pServerName', ctypes.POINTER(ctypes.c_char)),
]

class struct_ma_context_0_jack(Structure):
    pass

struct_ma_context_0_jack._pack_ = 1 # source:False
struct_ma_context_0_jack._fields_ = [
    ('jackSO', ctypes.POINTER(None)),
    ('jack_client_open', ctypes.CFUNCTYPE(None)),
    ('jack_client_close', ctypes.CFUNCTYPE(None)),
    ('jack_client_name_size', ctypes.CFUNCTYPE(None)),
    ('jack_set_process_callback', ctypes.CFUNCTYPE(None)),
    ('jack_set_buffer_size_callback', ctypes.CFUNCTYPE(None)),
    ('jack_on_shutdown', ctypes.CFUNCTYPE(None)),
    ('jack_get_sample_rate', ctypes.CFUNCTYPE(None)),
    ('jack_get_buffer_size', ctypes.CFUNCTYPE(None)),
    ('jack_get_ports', ctypes.CFUNCTYPE(None)),
    ('jack_activate', ctypes.CFUNCTYPE(None)),
    ('jack_deactivate', ctypes.CFUNCTYPE(None)),
    ('jack_connect', ctypes.CFUNCTYPE(None)),
    ('jack_port_register', ctypes.CFUNCTYPE(None)),
    ('jack_port_name', ctypes.CFUNCTYPE(None)),
    ('jack_port_get_buffer', ctypes.CFUNCTYPE(None)),
    ('jack_free', ctypes.CFUNCTYPE(None)),
    ('pClientName', ctypes.POINTER(ctypes.c_char)),
    ('tryStartServer', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_context_0_null_backend(Structure):
    pass

struct_ma_context_0_null_backend._pack_ = 1 # source:False
struct_ma_context_0_null_backend._fields_ = [
    ('_unused', ctypes.c_int32),
]

union_ma_context_0._pack_ = 1 # source:False
union_ma_context_0._fields_ = [
    ('alsa', struct_ma_context_0_alsa),
    ('pulse', struct_ma_context_0_pulse),
    ('jack', struct_ma_context_0_jack),
    ('null_backend', struct_ma_context_0_null_backend),
    ('PADDING_0', ctypes.c_ubyte * 580),
]

class union_ma_context_1(Union):
    pass

class struct_ma_context_1_posix(Structure):
    pass

struct_ma_context_1_posix._pack_ = 1 # source:False
struct_ma_context_1_posix._fields_ = [
    ('_unused', ctypes.c_int32),
]

union_ma_context_1._pack_ = 1 # source:False
union_ma_context_1._fields_ = [
    ('posix', struct_ma_context_1_posix),
    ('_unused', ctypes.c_int32),
]

struct_ma_context._pack_ = 1 # source:False
struct_ma_context._anonymous_ = ('_0', '_1',)
struct_ma_context._fields_ = [
    ('callbacks', ma_backend_callbacks),
    ('backend', ma_backend),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pLog', ctypes.POINTER(struct_ma_log)),
    ('log', ma_log),
    ('threadPriority', ma_thread_priority),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('threadStackSize', ctypes.c_uint64),
    ('pUserData', ctypes.POINTER(None)),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('deviceEnumLock', ma_mutex),
    ('deviceInfoLock', ma_mutex),
    ('deviceInfoCapacity', ctypes.c_uint32),
    ('playbackDeviceInfoCount', ctypes.c_uint32),
    ('captureDeviceInfoCount', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('pDeviceInfos', ctypes.POINTER(struct_ma_device_info)),
    ('_0', union_ma_context_0),
    ('_1', union_ma_context_1),
    ('PADDING_3', ctypes.c_ubyte * 4),
]

ma_context = struct_ma_context
class struct_ma_atomic_device_state(Structure):
    pass


# values for enumeration 'ma_device_state'
ma_device_state__enumvalues = {
    0: 'ma_device_state_uninitialized',
    1: 'ma_device_state_stopped',
    2: 'ma_device_state_started',
    3: 'ma_device_state_starting',
    4: 'ma_device_state_stopping',
}
ma_device_state_uninitialized = 0
ma_device_state_stopped = 1
ma_device_state_started = 2
ma_device_state_starting = 3
ma_device_state_stopping = 4
ma_device_state = ctypes.c_uint32 # enum
struct_ma_atomic_device_state._pack_ = 1 # source:False
struct_ma_atomic_device_state._fields_ = [
    ('value', ma_device_state),
]

ma_atomic_device_state = struct_ma_atomic_device_state
class struct_ma_device_notification(Structure):
    pass

class struct_ma_event(Structure):
    pass

struct_ma_event._pack_ = 1 # source:False
struct_ma_event._fields_ = [
    ('value', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('lock', ma_pthread_mutex_t),
    ('cond', ma_pthread_cond_t),
]

ma_event = struct_ma_event
class struct_ma_atomic_float(Structure):
    pass

struct_ma_atomic_float._pack_ = 1 # source:False
struct_ma_atomic_float._fields_ = [
    ('value', ctypes.c_float),
]

ma_atomic_float = struct_ma_atomic_float
class struct_ma_duplex_rb(Structure):
    pass

class struct_ma_pcm_rb(Structure):
    pass

class struct_ma_data_source_base(Structure):
    pass

class struct_ma_data_source_vtable(Structure):
    pass

struct_ma_data_source_base._pack_ = 1 # source:False
struct_ma_data_source_base._fields_ = [
    ('vtable', ctypes.POINTER(struct_ma_data_source_vtable)),
    ('rangeBegInFrames', ctypes.c_uint64),
    ('rangeEndInFrames', ctypes.c_uint64),
    ('loopBegInFrames', ctypes.c_uint64),
    ('loopEndInFrames', ctypes.c_uint64),
    ('pCurrent', ctypes.POINTER(None)),
    ('pNext', ctypes.POINTER(None)),
    ('onGetNext', ctypes.CFUNCTYPE(ctypes.POINTER(None), ctypes.POINTER(None))),
    ('isLooping', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_data_source_base = struct_ma_data_source_base
class struct_ma_rb(Structure):
    pass

struct_ma_rb._pack_ = 1 # source:False
struct_ma_rb._fields_ = [
    ('pBuffer', ctypes.POINTER(None)),
    ('subbufferSizeInBytes', ctypes.c_uint32),
    ('subbufferCount', ctypes.c_uint32),
    ('subbufferStrideInBytes', ctypes.c_uint32),
    ('encodedReadOffset', ctypes.c_uint32),
    ('encodedWriteOffset', ctypes.c_uint32),
    ('ownsBuffer', ctypes.c_ubyte),
    ('clearOnWriteAcquire', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('allocationCallbacks', ma_allocation_callbacks),
]

ma_rb = struct_ma_rb

# values for enumeration 'ma_format'
ma_format__enumvalues = {
    0: 'ma_format_unknown',
    1: 'ma_format_u8',
    2: 'ma_format_s16',
    3: 'ma_format_s24',
    4: 'ma_format_s32',
    5: 'ma_format_f32',
    6: 'ma_format_count',
}
ma_format_unknown = 0
ma_format_u8 = 1
ma_format_s16 = 2
ma_format_s24 = 3
ma_format_s32 = 4
ma_format_f32 = 5
ma_format_count = 6
ma_format = ctypes.c_uint32 # enum
struct_ma_pcm_rb._pack_ = 1 # source:False
struct_ma_pcm_rb._fields_ = [
    ('ds', ma_data_source_base),
    ('rb', ma_rb),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_pcm_rb = struct_ma_pcm_rb
struct_ma_duplex_rb._pack_ = 1 # source:False
struct_ma_duplex_rb._fields_ = [
    ('rb', ma_pcm_rb),
]

ma_duplex_rb = struct_ma_duplex_rb
class struct_ma_device_resampling(Structure):
    pass

class struct_ma_resampling_backend_vtable(Structure):
    pass


# values for enumeration 'ma_resample_algorithm'
ma_resample_algorithm__enumvalues = {
    0: 'ma_resample_algorithm_linear',
    1: 'ma_resample_algorithm_custom',
}
ma_resample_algorithm_linear = 0
ma_resample_algorithm_custom = 1
ma_resample_algorithm = ctypes.c_uint32 # enum
class struct_ma_device_0_linear(Structure):
    pass

struct_ma_device_0_linear._pack_ = 1 # source:False
struct_ma_device_0_linear._fields_ = [
    ('lpfOrder', ctypes.c_uint32),
]

struct_ma_device_resampling._pack_ = 1 # source:False
struct_ma_device_resampling._fields_ = [
    ('algorithm', ma_resample_algorithm),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pBackendVTable', ctypes.POINTER(struct_ma_resampling_backend_vtable)),
    ('pBackendUserData', ctypes.POINTER(None)),
    ('linear', struct_ma_device_0_linear),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

class struct_ma_device_playback(Structure):
    pass

class union_ma_device_id_custom(Union):
    pass

union_ma_device_id_custom._pack_ = 1 # source:False
union_ma_device_id_custom._fields_ = [
    ('i', ctypes.c_int32),
    ('s', ctypes.c_char * 256),
    ('p', ctypes.POINTER(None)),
    ('PADDING_0', ctypes.c_ubyte * 248),
]

union_ma_device_id._pack_ = 1 # source:False
union_ma_device_id._fields_ = [
    ('wasapi', ctypes.c_uint16 * 64),
    ('dsound', ctypes.c_ubyte * 16),
    ('winmm', ctypes.c_uint32),
    ('alsa', ctypes.c_char * 256),
    ('pulse', ctypes.c_char * 256),
    ('jack', ctypes.c_int32),
    ('coreaudio', ctypes.c_char * 256),
    ('sndio', ctypes.c_char * 256),
    ('audio4', ctypes.c_char * 256),
    ('oss', ctypes.c_char * 64),
    ('aaudio', ctypes.c_int32),
    ('opensl', ctypes.c_uint32),
    ('webaudio', ctypes.c_char * 32),
    ('custom', union_ma_device_id_custom),
    ('nullbackend', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 252),
]

ma_device_id = union_ma_device_id

# values for enumeration 'ma_share_mode'
ma_share_mode__enumvalues = {
    0: 'ma_share_mode_shared',
    1: 'ma_share_mode_exclusive',
}
ma_share_mode_shared = 0
ma_share_mode_exclusive = 1
ma_share_mode = ctypes.c_uint32 # enum

# values for enumeration 'ma_channel_mix_mode'
ma_channel_mix_mode__enumvalues = {
    0: 'ma_channel_mix_mode_rectangular',
    1: 'ma_channel_mix_mode_simple',
    2: 'ma_channel_mix_mode_custom_weights',
    0: 'ma_channel_mix_mode_default',
}
ma_channel_mix_mode_rectangular = 0
ma_channel_mix_mode_simple = 1
ma_channel_mix_mode_custom_weights = 2
ma_channel_mix_mode_default = 0
ma_channel_mix_mode = ctypes.c_uint32 # enum
class struct_ma_data_converter(Structure):
    pass


# values for enumeration 'ma_dither_mode'
ma_dither_mode__enumvalues = {
    0: 'ma_dither_mode_none',
    1: 'ma_dither_mode_rectangle',
    2: 'ma_dither_mode_triangle',
}
ma_dither_mode_none = 0
ma_dither_mode_rectangle = 1
ma_dither_mode_triangle = 2
ma_dither_mode = ctypes.c_uint32 # enum

# values for enumeration 'ma_data_converter_execution_path'
ma_data_converter_execution_path__enumvalues = {
    0: 'ma_data_converter_execution_path_passthrough',
    1: 'ma_data_converter_execution_path_format_only',
    2: 'ma_data_converter_execution_path_channels_only',
    3: 'ma_data_converter_execution_path_resample_only',
    4: 'ma_data_converter_execution_path_resample_first',
    5: 'ma_data_converter_execution_path_channels_first',
}
ma_data_converter_execution_path_passthrough = 0
ma_data_converter_execution_path_format_only = 1
ma_data_converter_execution_path_channels_only = 2
ma_data_converter_execution_path_resample_only = 3
ma_data_converter_execution_path_resample_first = 4
ma_data_converter_execution_path_channels_first = 5
ma_data_converter_execution_path = ctypes.c_uint32 # enum
class struct_ma_channel_converter(Structure):
    pass


# values for enumeration 'ma_channel_conversion_path'
ma_channel_conversion_path__enumvalues = {
    0: 'ma_channel_conversion_path_unknown',
    1: 'ma_channel_conversion_path_passthrough',
    2: 'ma_channel_conversion_path_mono_out',
    3: 'ma_channel_conversion_path_mono_in',
    4: 'ma_channel_conversion_path_shuffle',
    5: 'ma_channel_conversion_path_weights',
}
ma_channel_conversion_path_unknown = 0
ma_channel_conversion_path_passthrough = 1
ma_channel_conversion_path_mono_out = 2
ma_channel_conversion_path_mono_in = 3
ma_channel_conversion_path_shuffle = 4
ma_channel_conversion_path_weights = 5
ma_channel_conversion_path = ctypes.c_uint32 # enum
class union_ma_channel_converter_weights(Union):
    pass

union_ma_channel_converter_weights._pack_ = 1 # source:False
union_ma_channel_converter_weights._fields_ = [
    ('f32', ctypes.POINTER(ctypes.POINTER(ctypes.c_float))),
    ('s16', ctypes.POINTER(ctypes.POINTER(ctypes.c_int32))),
]

struct_ma_channel_converter._pack_ = 1 # source:False
struct_ma_channel_converter._fields_ = [
    ('format', ma_format),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('mixingMode', ma_channel_mix_mode),
    ('conversionPath', ma_channel_conversion_path),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pChannelMapIn', ctypes.POINTER(ctypes.c_ubyte)),
    ('pChannelMapOut', ctypes.POINTER(ctypes.c_ubyte)),
    ('pShuffleTable', ctypes.POINTER(ctypes.c_ubyte)),
    ('weights', union_ma_channel_converter_weights),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_channel_converter = struct_ma_channel_converter
class struct_ma_resampler(Structure):
    pass

class union_ma_resampler_state(Union):
    pass

class struct_ma_linear_resampler(Structure):
    pass

class struct_ma_linear_resampler_config(Structure):
    pass

struct_ma_linear_resampler_config._pack_ = 1 # source:False
struct_ma_linear_resampler_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRateIn', ctypes.c_uint32),
    ('sampleRateOut', ctypes.c_uint32),
    ('lpfOrder', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('lpfNyquistFactor', ctypes.c_double),
]

ma_linear_resampler_config = struct_ma_linear_resampler_config
class union_ma_linear_resampler_x0(Union):
    pass

union_ma_linear_resampler_x0._pack_ = 1 # source:False
union_ma_linear_resampler_x0._fields_ = [
    ('f32', ctypes.POINTER(ctypes.c_float)),
    ('s16', ctypes.POINTER(ctypes.c_int16)),
]

class union_ma_linear_resampler_x1(Union):
    pass

union_ma_linear_resampler_x1._pack_ = 1 # source:False
union_ma_linear_resampler_x1._fields_ = [
    ('f32', ctypes.POINTER(ctypes.c_float)),
    ('s16', ctypes.POINTER(ctypes.c_int16)),
]

class struct_ma_lpf(Structure):
    pass

class struct_ma_lpf1(Structure):
    pass

class struct_ma_lpf2(Structure):
    pass

struct_ma_lpf._pack_ = 1 # source:False
struct_ma_lpf._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('lpf1Count', ctypes.c_uint32),
    ('lpf2Count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pLPF1', ctypes.POINTER(struct_ma_lpf1)),
    ('pLPF2', ctypes.POINTER(struct_ma_lpf2)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_lpf = struct_ma_lpf
struct_ma_linear_resampler._pack_ = 1 # source:False
struct_ma_linear_resampler._fields_ = [
    ('config', ma_linear_resampler_config),
    ('inAdvanceInt', ctypes.c_uint32),
    ('inAdvanceFrac', ctypes.c_uint32),
    ('inTimeInt', ctypes.c_uint32),
    ('inTimeFrac', ctypes.c_uint32),
    ('x0', union_ma_linear_resampler_x0),
    ('x1', union_ma_linear_resampler_x1),
    ('lpf', ma_lpf),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_linear_resampler = struct_ma_linear_resampler
union_ma_resampler_state._pack_ = 1 # source:False
union_ma_resampler_state._fields_ = [
    ('linear', ma_linear_resampler),
]

struct_ma_resampler._pack_ = 1 # source:False
struct_ma_resampler._fields_ = [
    ('pBackend', ctypes.POINTER(None)),
    ('pBackendVTable', ctypes.POINTER(struct_ma_resampling_backend_vtable)),
    ('pBackendUserData', ctypes.POINTER(None)),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRateIn', ctypes.c_uint32),
    ('sampleRateOut', ctypes.c_uint32),
    ('state', union_ma_resampler_state),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_resampler = struct_ma_resampler
struct_ma_data_converter._pack_ = 1 # source:False
struct_ma_data_converter._fields_ = [
    ('formatIn', ma_format),
    ('formatOut', ma_format),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('sampleRateIn', ctypes.c_uint32),
    ('sampleRateOut', ctypes.c_uint32),
    ('ditherMode', ma_dither_mode),
    ('executionPath', ma_data_converter_execution_path),
    ('channelConverter', ma_channel_converter),
    ('resampler', ma_resampler),
    ('hasPreFormatConversion', ctypes.c_ubyte),
    ('hasPostFormatConversion', ctypes.c_ubyte),
    ('hasChannelConverter', ctypes.c_ubyte),
    ('hasResampler', ctypes.c_ubyte),
    ('isPassthrough', ctypes.c_ubyte),
    ('_ownsHeap', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('_pHeap', ctypes.POINTER(None)),
]

ma_data_converter = struct_ma_data_converter
struct_ma_device_playback._pack_ = 1 # source:False
struct_ma_device_playback._fields_ = [
    ('pID', ctypes.POINTER(union_ma_device_id)),
    ('id', ma_device_id),
    ('name', ctypes.c_char * 256),
    ('shareMode', ma_share_mode),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('channelMap', ctypes.c_ubyte * 254),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('internalFormat', ma_format),
    ('internalChannels', ctypes.c_uint32),
    ('internalSampleRate', ctypes.c_uint32),
    ('internalChannelMap', ctypes.c_ubyte * 254),
    ('PADDING_1', ctypes.c_ubyte * 2),
    ('internalPeriodSizeInFrames', ctypes.c_uint32),
    ('internalPeriods', ctypes.c_uint32),
    ('channelMixMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('converter', ma_data_converter),
    ('pIntermediaryBuffer', ctypes.POINTER(None)),
    ('intermediaryBufferCap', ctypes.c_uint32),
    ('intermediaryBufferLen', ctypes.c_uint32),
    ('pInputCache', ctypes.POINTER(None)),
    ('inputCacheCap', ctypes.c_uint64),
    ('inputCacheConsumed', ctypes.c_uint64),
    ('inputCacheRemaining', ctypes.c_uint64),
]

class struct_ma_device_capture(Structure):
    pass

struct_ma_device_capture._pack_ = 1 # source:False
struct_ma_device_capture._fields_ = [
    ('pID', ctypes.POINTER(union_ma_device_id)),
    ('id', ma_device_id),
    ('name', ctypes.c_char * 256),
    ('shareMode', ma_share_mode),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('channelMap', ctypes.c_ubyte * 254),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('internalFormat', ma_format),
    ('internalChannels', ctypes.c_uint32),
    ('internalSampleRate', ctypes.c_uint32),
    ('internalChannelMap', ctypes.c_ubyte * 254),
    ('PADDING_1', ctypes.c_ubyte * 2),
    ('internalPeriodSizeInFrames', ctypes.c_uint32),
    ('internalPeriods', ctypes.c_uint32),
    ('channelMixMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('converter', ma_data_converter),
    ('pIntermediaryBuffer', ctypes.POINTER(None)),
    ('intermediaryBufferCap', ctypes.c_uint32),
    ('intermediaryBufferLen', ctypes.c_uint32),
]

class union_ma_device_3(Union):
    pass

class struct_ma_device_3_alsa(Structure):
    pass

struct_ma_device_3_alsa._pack_ = 1 # source:False
struct_ma_device_3_alsa._fields_ = [
    ('pPCMPlayback', ctypes.POINTER(None)),
    ('pPCMCapture', ctypes.POINTER(None)),
    ('pPollDescriptorsPlayback', ctypes.POINTER(None)),
    ('pPollDescriptorsCapture', ctypes.POINTER(None)),
    ('pollDescriptorCountPlayback', ctypes.c_int32),
    ('pollDescriptorCountCapture', ctypes.c_int32),
    ('wakeupfdPlayback', ctypes.c_int32),
    ('wakeupfdCapture', ctypes.c_int32),
    ('isUsingMMapPlayback', ctypes.c_ubyte),
    ('isUsingMMapCapture', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 6),
]

class struct_ma_device_3_pulse(Structure):
    pass

struct_ma_device_3_pulse._pack_ = 1 # source:False
struct_ma_device_3_pulse._fields_ = [
    ('pMainLoop', ctypes.POINTER(None)),
    ('pPulseContext', ctypes.POINTER(None)),
    ('pStreamPlayback', ctypes.POINTER(None)),
    ('pStreamCapture', ctypes.POINTER(None)),
]

class struct_ma_device_3_jack(Structure):
    pass

struct_ma_device_3_jack._pack_ = 1 # source:False
struct_ma_device_3_jack._fields_ = [
    ('pClient', ctypes.POINTER(None)),
    ('ppPortsPlayback', ctypes.POINTER(ctypes.POINTER(None))),
    ('ppPortsCapture', ctypes.POINTER(ctypes.POINTER(None))),
    ('pIntermediaryBufferPlayback', ctypes.POINTER(ctypes.c_float)),
    ('pIntermediaryBufferCapture', ctypes.POINTER(ctypes.c_float)),
]

class struct_ma_device_3_null_device(Structure):
    pass

class struct_ma_semaphore(Structure):
    pass

struct_ma_semaphore._pack_ = 1 # source:False
struct_ma_semaphore._fields_ = [
    ('value', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('lock', ma_pthread_mutex_t),
    ('cond', ma_pthread_cond_t),
]

ma_semaphore = struct_ma_semaphore
class union_ma_timer(Union):
    pass

union_ma_timer._pack_ = 1 # source:False
union_ma_timer._fields_ = [
    ('counter', ctypes.c_int64),
    ('counterD', ctypes.c_double),
]

ma_timer = union_ma_timer
class struct_ma_atomic_bool32(Structure):
    pass

struct_ma_atomic_bool32._pack_ = 1 # source:False
struct_ma_atomic_bool32._fields_ = [
    ('value', ctypes.c_uint32),
]

ma_atomic_bool32 = struct_ma_atomic_bool32
struct_ma_device_3_null_device._pack_ = 1 # source:False
struct_ma_device_3_null_device._fields_ = [
    ('deviceThread', ctypes.c_uint64),
    ('operationEvent', ma_event),
    ('operationCompletionEvent', ma_event),
    ('operationSemaphore', ma_semaphore),
    ('operation', ctypes.c_uint32),
    ('operationResult', ma_result),
    ('timer', ma_timer),
    ('priorRunTime', ctypes.c_double),
    ('currentPeriodFramesRemainingPlayback', ctypes.c_uint32),
    ('currentPeriodFramesRemainingCapture', ctypes.c_uint32),
    ('lastProcessedFramePlayback', ctypes.c_uint64),
    ('lastProcessedFrameCapture', ctypes.c_uint64),
    ('isStarted', ma_atomic_bool32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

union_ma_device_3._pack_ = 1 # source:False
union_ma_device_3._fields_ = [
    ('alsa', struct_ma_device_3_alsa),
    ('pulse', struct_ma_device_3_pulse),
    ('jack', struct_ma_device_3_jack),
    ('null_device', struct_ma_device_3_null_device),
]

struct_ma_device._pack_ = 1 # source:False
struct_ma_device._anonymous_ = ('_0',)
struct_ma_device._fields_ = [
    ('pContext', ctypes.POINTER(struct_ma_context)),
    ('type', ma_device_type),
    ('sampleRate', ctypes.c_uint32),
    ('state', ma_atomic_device_state),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('onData', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)),
    ('onNotification', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device_notification))),
    ('onStop', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device))),
    ('pUserData', ctypes.POINTER(None)),
    ('startStopLock', ma_mutex),
    ('wakeupEvent', ma_event),
    ('startEvent', ma_event),
    ('stopEvent', ma_event),
    ('thread', ctypes.c_uint64),
    ('workResult', ma_result),
    ('isOwnerOfContext', ctypes.c_ubyte),
    ('noPreSilencedOutputBuffer', ctypes.c_ubyte),
    ('noClip', ctypes.c_ubyte),
    ('noDisableDenormals', ctypes.c_ubyte),
    ('noFixedSizedCallback', ctypes.c_ubyte),
    ('PADDING_1', ctypes.c_ubyte * 3),
    ('masterVolumeFactor', ma_atomic_float),
    ('duplexRB', ma_duplex_rb),
    ('resampling', struct_ma_device_resampling),
    ('playback', struct_ma_device_playback),
    ('capture', struct_ma_device_capture),
    ('_0', union_ma_device_3),
]

ma_device = struct_ma_device
ma_channel = ctypes.c_ubyte

# values for enumeration '_ma_channel_position'
_ma_channel_position__enumvalues = {
    0: 'MA_CHANNEL_NONE',
    1: 'MA_CHANNEL_MONO',
    2: 'MA_CHANNEL_FRONT_LEFT',
    3: 'MA_CHANNEL_FRONT_RIGHT',
    4: 'MA_CHANNEL_FRONT_CENTER',
    5: 'MA_CHANNEL_LFE',
    6: 'MA_CHANNEL_BACK_LEFT',
    7: 'MA_CHANNEL_BACK_RIGHT',
    8: 'MA_CHANNEL_FRONT_LEFT_CENTER',
    9: 'MA_CHANNEL_FRONT_RIGHT_CENTER',
    10: 'MA_CHANNEL_BACK_CENTER',
    11: 'MA_CHANNEL_SIDE_LEFT',
    12: 'MA_CHANNEL_SIDE_RIGHT',
    13: 'MA_CHANNEL_TOP_CENTER',
    14: 'MA_CHANNEL_TOP_FRONT_LEFT',
    15: 'MA_CHANNEL_TOP_FRONT_CENTER',
    16: 'MA_CHANNEL_TOP_FRONT_RIGHT',
    17: 'MA_CHANNEL_TOP_BACK_LEFT',
    18: 'MA_CHANNEL_TOP_BACK_CENTER',
    19: 'MA_CHANNEL_TOP_BACK_RIGHT',
    20: 'MA_CHANNEL_AUX_0',
    21: 'MA_CHANNEL_AUX_1',
    22: 'MA_CHANNEL_AUX_2',
    23: 'MA_CHANNEL_AUX_3',
    24: 'MA_CHANNEL_AUX_4',
    25: 'MA_CHANNEL_AUX_5',
    26: 'MA_CHANNEL_AUX_6',
    27: 'MA_CHANNEL_AUX_7',
    28: 'MA_CHANNEL_AUX_8',
    29: 'MA_CHANNEL_AUX_9',
    30: 'MA_CHANNEL_AUX_10',
    31: 'MA_CHANNEL_AUX_11',
    32: 'MA_CHANNEL_AUX_12',
    33: 'MA_CHANNEL_AUX_13',
    34: 'MA_CHANNEL_AUX_14',
    35: 'MA_CHANNEL_AUX_15',
    36: 'MA_CHANNEL_AUX_16',
    37: 'MA_CHANNEL_AUX_17',
    38: 'MA_CHANNEL_AUX_18',
    39: 'MA_CHANNEL_AUX_19',
    40: 'MA_CHANNEL_AUX_20',
    41: 'MA_CHANNEL_AUX_21',
    42: 'MA_CHANNEL_AUX_22',
    43: 'MA_CHANNEL_AUX_23',
    44: 'MA_CHANNEL_AUX_24',
    45: 'MA_CHANNEL_AUX_25',
    46: 'MA_CHANNEL_AUX_26',
    47: 'MA_CHANNEL_AUX_27',
    48: 'MA_CHANNEL_AUX_28',
    49: 'MA_CHANNEL_AUX_29',
    50: 'MA_CHANNEL_AUX_30',
    51: 'MA_CHANNEL_AUX_31',
    2: 'MA_CHANNEL_LEFT',
    3: 'MA_CHANNEL_RIGHT',
    52: 'MA_CHANNEL_POSITION_COUNT',
}
MA_CHANNEL_NONE = 0
MA_CHANNEL_MONO = 1
MA_CHANNEL_FRONT_LEFT = 2
MA_CHANNEL_FRONT_RIGHT = 3
MA_CHANNEL_FRONT_CENTER = 4
MA_CHANNEL_LFE = 5
MA_CHANNEL_BACK_LEFT = 6
MA_CHANNEL_BACK_RIGHT = 7
MA_CHANNEL_FRONT_LEFT_CENTER = 8
MA_CHANNEL_FRONT_RIGHT_CENTER = 9
MA_CHANNEL_BACK_CENTER = 10
MA_CHANNEL_SIDE_LEFT = 11
MA_CHANNEL_SIDE_RIGHT = 12
MA_CHANNEL_TOP_CENTER = 13
MA_CHANNEL_TOP_FRONT_LEFT = 14
MA_CHANNEL_TOP_FRONT_CENTER = 15
MA_CHANNEL_TOP_FRONT_RIGHT = 16
MA_CHANNEL_TOP_BACK_LEFT = 17
MA_CHANNEL_TOP_BACK_CENTER = 18
MA_CHANNEL_TOP_BACK_RIGHT = 19
MA_CHANNEL_AUX_0 = 20
MA_CHANNEL_AUX_1 = 21
MA_CHANNEL_AUX_2 = 22
MA_CHANNEL_AUX_3 = 23
MA_CHANNEL_AUX_4 = 24
MA_CHANNEL_AUX_5 = 25
MA_CHANNEL_AUX_6 = 26
MA_CHANNEL_AUX_7 = 27
MA_CHANNEL_AUX_8 = 28
MA_CHANNEL_AUX_9 = 29
MA_CHANNEL_AUX_10 = 30
MA_CHANNEL_AUX_11 = 31
MA_CHANNEL_AUX_12 = 32
MA_CHANNEL_AUX_13 = 33
MA_CHANNEL_AUX_14 = 34
MA_CHANNEL_AUX_15 = 35
MA_CHANNEL_AUX_16 = 36
MA_CHANNEL_AUX_17 = 37
MA_CHANNEL_AUX_18 = 38
MA_CHANNEL_AUX_19 = 39
MA_CHANNEL_AUX_20 = 40
MA_CHANNEL_AUX_21 = 41
MA_CHANNEL_AUX_22 = 42
MA_CHANNEL_AUX_23 = 43
MA_CHANNEL_AUX_24 = 44
MA_CHANNEL_AUX_25 = 45
MA_CHANNEL_AUX_26 = 46
MA_CHANNEL_AUX_27 = 47
MA_CHANNEL_AUX_28 = 48
MA_CHANNEL_AUX_29 = 49
MA_CHANNEL_AUX_30 = 50
MA_CHANNEL_AUX_31 = 51
MA_CHANNEL_LEFT = 2
MA_CHANNEL_RIGHT = 3
MA_CHANNEL_POSITION_COUNT = 52
_ma_channel_position = ctypes.c_uint32 # enum

# values for enumeration 'ma_stream_format'
ma_stream_format__enumvalues = {
    0: 'ma_stream_format_pcm',
}
ma_stream_format_pcm = 0
ma_stream_format = ctypes.c_uint32 # enum

# values for enumeration 'ma_stream_layout'
ma_stream_layout__enumvalues = {
    0: 'ma_stream_layout_interleaved',
    1: 'ma_stream_layout_deinterleaved',
}
ma_stream_layout_interleaved = 0
ma_stream_layout_deinterleaved = 1
ma_stream_layout = ctypes.c_uint32 # enum

# values for enumeration 'ma_standard_sample_rate'
ma_standard_sample_rate__enumvalues = {
    48000: 'ma_standard_sample_rate_48000',
    44100: 'ma_standard_sample_rate_44100',
    32000: 'ma_standard_sample_rate_32000',
    24000: 'ma_standard_sample_rate_24000',
    22050: 'ma_standard_sample_rate_22050',
    88200: 'ma_standard_sample_rate_88200',
    96000: 'ma_standard_sample_rate_96000',
    176400: 'ma_standard_sample_rate_176400',
    192000: 'ma_standard_sample_rate_192000',
    16000: 'ma_standard_sample_rate_16000',
    11025: 'ma_standard_sample_rate_11025',
    8000: 'ma_standard_sample_rate_8000',
    352800: 'ma_standard_sample_rate_352800',
    384000: 'ma_standard_sample_rate_384000',
    8000: 'ma_standard_sample_rate_min',
    384000: 'ma_standard_sample_rate_max',
    14: 'ma_standard_sample_rate_count',
}
ma_standard_sample_rate_48000 = 48000
ma_standard_sample_rate_44100 = 44100
ma_standard_sample_rate_32000 = 32000
ma_standard_sample_rate_24000 = 24000
ma_standard_sample_rate_22050 = 22050
ma_standard_sample_rate_88200 = 88200
ma_standard_sample_rate_96000 = 96000
ma_standard_sample_rate_176400 = 176400
ma_standard_sample_rate_192000 = 192000
ma_standard_sample_rate_16000 = 16000
ma_standard_sample_rate_11025 = 11025
ma_standard_sample_rate_8000 = 8000
ma_standard_sample_rate_352800 = 352800
ma_standard_sample_rate_384000 = 384000
ma_standard_sample_rate_min = 8000
ma_standard_sample_rate_max = 384000
ma_standard_sample_rate_count = 14
ma_standard_sample_rate = ctypes.c_uint32 # enum

# values for enumeration 'ma_standard_channel_map'
ma_standard_channel_map__enumvalues = {
    0: 'ma_standard_channel_map_microsoft',
    1: 'ma_standard_channel_map_alsa',
    2: 'ma_standard_channel_map_rfc3551',
    3: 'ma_standard_channel_map_flac',
    4: 'ma_standard_channel_map_vorbis',
    5: 'ma_standard_channel_map_sound4',
    6: 'ma_standard_channel_map_sndio',
    3: 'ma_standard_channel_map_webaudio',
    0: 'ma_standard_channel_map_default',
}
ma_standard_channel_map_microsoft = 0
ma_standard_channel_map_alsa = 1
ma_standard_channel_map_rfc3551 = 2
ma_standard_channel_map_flac = 3
ma_standard_channel_map_vorbis = 4
ma_standard_channel_map_sound4 = 5
ma_standard_channel_map_sndio = 6
ma_standard_channel_map_webaudio = 3
ma_standard_channel_map_default = 0
ma_standard_channel_map = ctypes.c_uint32 # enum

# values for enumeration 'ma_performance_profile'
ma_performance_profile__enumvalues = {
    0: 'ma_performance_profile_low_latency',
    1: 'ma_performance_profile_conservative',
}
ma_performance_profile_low_latency = 0
ma_performance_profile_conservative = 1
ma_performance_profile = ctypes.c_uint32 # enum
class struct_ma_lcg(Structure):
    pass

struct_ma_lcg._pack_ = 1 # source:False
struct_ma_lcg._fields_ = [
    ('state', ctypes.c_int32),
]

ma_lcg = struct_ma_lcg
class struct_ma_atomic_uint32(Structure):
    pass

struct_ma_atomic_uint32._pack_ = 1 # source:False
struct_ma_atomic_uint32._fields_ = [
    ('value', ctypes.c_uint32),
]

ma_atomic_uint32 = struct_ma_atomic_uint32
class struct_ma_atomic_int32(Structure):
    pass

struct_ma_atomic_int32._pack_ = 1 # source:False
struct_ma_atomic_int32._fields_ = [
    ('value', ctypes.c_int32),
]

ma_atomic_int32 = struct_ma_atomic_int32
class struct_ma_atomic_uint64(Structure):
    pass

struct_ma_atomic_uint64._pack_ = 1 # source:False
struct_ma_atomic_uint64._fields_ = [
    ('value', ctypes.c_uint64),
]

ma_atomic_uint64 = struct_ma_atomic_uint64
ma_spinlock = ctypes.c_uint32
ma_thread = ctypes.c_uint64
try:
    ma_version = _libraries['libminiaudio.so'].ma_version
    ma_version.restype = None
    ma_version.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_version_string = _libraries['libminiaudio.so'].ma_version_string
    ma_version_string.restype = ctypes.POINTER(ctypes.c_char)
    ma_version_string.argtypes = []
except AttributeError:
    pass
ma_log_callback_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(ctypes.c_char))
ma_log_callback = struct_ma_log_callback
try:
    ma_log_callback_init = _libraries['libminiaudio.so'].ma_log_callback_init
    ma_log_callback_init.restype = ma_log_callback
    ma_log_callback_init.argtypes = [ma_log_callback_proc, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_log_init = _libraries['libminiaudio.so'].ma_log_init
    ma_log_init.restype = ma_result
    ma_log_init.argtypes = [ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_log)]
except AttributeError:
    pass
try:
    ma_log_uninit = _libraries['libminiaudio.so'].ma_log_uninit
    ma_log_uninit.restype = None
    ma_log_uninit.argtypes = [ctypes.POINTER(struct_ma_log)]
except AttributeError:
    pass
try:
    ma_log_register_callback = _libraries['libminiaudio.so'].ma_log_register_callback
    ma_log_register_callback.restype = ma_result
    ma_log_register_callback.argtypes = [ctypes.POINTER(struct_ma_log), ma_log_callback]
except AttributeError:
    pass
try:
    ma_log_unregister_callback = _libraries['libminiaudio.so'].ma_log_unregister_callback
    ma_log_unregister_callback.restype = ma_result
    ma_log_unregister_callback.argtypes = [ctypes.POINTER(struct_ma_log), ma_log_callback]
except AttributeError:
    pass
try:
    ma_log_post = _libraries['libminiaudio.so'].ma_log_post
    ma_log_post.restype = ma_result
    ma_log_post.argtypes = [ctypes.POINTER(struct_ma_log), ma_uint32, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
class struct___va_list_tag(Structure):
    pass

struct___va_list_tag._pack_ = 1 # source:False
struct___va_list_tag._fields_ = [
    ('gp_offset', ctypes.c_uint32),
    ('fp_offset', ctypes.c_uint32),
    ('overflow_arg_area', ctypes.POINTER(None)),
    ('reg_save_area', ctypes.POINTER(None)),
]

va_list = struct___va_list_tag * 1
try:
    ma_log_postv = _libraries['libminiaudio.so'].ma_log_postv
    ma_log_postv.restype = ma_result
    ma_log_postv.argtypes = [ctypes.POINTER(struct_ma_log), ma_uint32, ctypes.POINTER(ctypes.c_char), va_list]
except AttributeError:
    pass
try:
    ma_log_postf = _libraries['libminiaudio.so'].ma_log_postf
    ma_log_postf.restype = ma_result
    ma_log_postf.argtypes = [ctypes.POINTER(struct_ma_log), ma_uint32, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
class union_ma_biquad_coefficient(Union):
    pass

union_ma_biquad_coefficient._pack_ = 1 # source:False
union_ma_biquad_coefficient._fields_ = [
    ('f32', ctypes.c_float),
    ('s32', ctypes.c_int32),
]

ma_biquad_coefficient = union_ma_biquad_coefficient
class struct_ma_biquad_config(Structure):
    pass

struct_ma_biquad_config._pack_ = 1 # source:False
struct_ma_biquad_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('b0', ctypes.c_double),
    ('b1', ctypes.c_double),
    ('b2', ctypes.c_double),
    ('a0', ctypes.c_double),
    ('a1', ctypes.c_double),
    ('a2', ctypes.c_double),
]

ma_biquad_config = struct_ma_biquad_config
try:
    ma_biquad_config_init = _libraries['libminiaudio.so'].ma_biquad_config_init
    ma_biquad_config_init.restype = ma_biquad_config
    ma_biquad_config_init.argtypes = [ma_format, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_biquad(Structure):
    pass

struct_ma_biquad._pack_ = 1 # source:False
struct_ma_biquad._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('b0', ma_biquad_coefficient),
    ('b1', ma_biquad_coefficient),
    ('b2', ma_biquad_coefficient),
    ('a1', ma_biquad_coefficient),
    ('a2', ma_biquad_coefficient),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pR1', ctypes.POINTER(union_ma_biquad_coefficient)),
    ('pR2', ctypes.POINTER(union_ma_biquad_coefficient)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_biquad = struct_ma_biquad
try:
    ma_biquad_get_heap_size = _libraries['libminiaudio.so'].ma_biquad_get_heap_size
    ma_biquad_get_heap_size.restype = ma_result
    ma_biquad_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_biquad_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_biquad_init_preallocated = _libraries['libminiaudio.so'].ma_biquad_init_preallocated
    ma_biquad_init_preallocated.restype = ma_result
    ma_biquad_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_biquad_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_biquad)]
except AttributeError:
    pass
try:
    ma_biquad_init = _libraries['libminiaudio.so'].ma_biquad_init
    ma_biquad_init.restype = ma_result
    ma_biquad_init.argtypes = [ctypes.POINTER(struct_ma_biquad_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_biquad)]
except AttributeError:
    pass
try:
    ma_biquad_uninit = _libraries['libminiaudio.so'].ma_biquad_uninit
    ma_biquad_uninit.restype = None
    ma_biquad_uninit.argtypes = [ctypes.POINTER(struct_ma_biquad), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_biquad_reinit = _libraries['libminiaudio.so'].ma_biquad_reinit
    ma_biquad_reinit.restype = ma_result
    ma_biquad_reinit.argtypes = [ctypes.POINTER(struct_ma_biquad_config), ctypes.POINTER(struct_ma_biquad)]
except AttributeError:
    pass
try:
    ma_biquad_clear_cache = _libraries['libminiaudio.so'].ma_biquad_clear_cache
    ma_biquad_clear_cache.restype = ma_result
    ma_biquad_clear_cache.argtypes = [ctypes.POINTER(struct_ma_biquad)]
except AttributeError:
    pass
try:
    ma_biquad_process_pcm_frames = _libraries['libminiaudio.so'].ma_biquad_process_pcm_frames
    ma_biquad_process_pcm_frames.restype = ma_result
    ma_biquad_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_biquad), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_biquad_get_latency = _libraries['libminiaudio.so'].ma_biquad_get_latency
    ma_biquad_get_latency.restype = ma_uint32
    ma_biquad_get_latency.argtypes = [ctypes.POINTER(struct_ma_biquad)]
except AttributeError:
    pass
class struct_ma_lpf1_config(Structure):
    pass

struct_ma_lpf1_config._pack_ = 1 # source:False
struct_ma_lpf1_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('q', ctypes.c_double),
]

ma_lpf1_config = struct_ma_lpf1_config
ma_lpf2_config = struct_ma_lpf1_config
try:
    ma_lpf1_config_init = _libraries['libminiaudio.so'].ma_lpf1_config_init
    ma_lpf1_config_init.restype = ma_lpf1_config
    ma_lpf1_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double]
except AttributeError:
    pass
try:
    ma_lpf2_config_init = _libraries['libminiaudio.so'].ma_lpf2_config_init
    ma_lpf2_config_init.restype = ma_lpf2_config
    ma_lpf2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
struct_ma_lpf1._pack_ = 1 # source:False
struct_ma_lpf1._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('a', ma_biquad_coefficient),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pR1', ctypes.POINTER(union_ma_biquad_coefficient)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_lpf1 = struct_ma_lpf1
try:
    ma_lpf1_get_heap_size = _libraries['libminiaudio.so'].ma_lpf1_get_heap_size
    ma_lpf1_get_heap_size.restype = ma_result
    ma_lpf1_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_lpf1_init_preallocated = _libraries['libminiaudio.so'].ma_lpf1_init_preallocated
    ma_lpf1_init_preallocated.restype = ma_result
    ma_lpf1_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_lpf1)]
except AttributeError:
    pass
try:
    ma_lpf1_init = _libraries['libminiaudio.so'].ma_lpf1_init
    ma_lpf1_init.restype = ma_result
    ma_lpf1_init.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_lpf1)]
except AttributeError:
    pass
try:
    ma_lpf1_uninit = _libraries['libminiaudio.so'].ma_lpf1_uninit
    ma_lpf1_uninit.restype = None
    ma_lpf1_uninit.argtypes = [ctypes.POINTER(struct_ma_lpf1), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_lpf1_reinit = _libraries['libminiaudio.so'].ma_lpf1_reinit
    ma_lpf1_reinit.restype = ma_result
    ma_lpf1_reinit.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(struct_ma_lpf1)]
except AttributeError:
    pass
try:
    ma_lpf1_clear_cache = _libraries['libminiaudio.so'].ma_lpf1_clear_cache
    ma_lpf1_clear_cache.restype = ma_result
    ma_lpf1_clear_cache.argtypes = [ctypes.POINTER(struct_ma_lpf1)]
except AttributeError:
    pass
try:
    ma_lpf1_process_pcm_frames = _libraries['libminiaudio.so'].ma_lpf1_process_pcm_frames
    ma_lpf1_process_pcm_frames.restype = ma_result
    ma_lpf1_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_lpf1), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_lpf1_get_latency = _libraries['libminiaudio.so'].ma_lpf1_get_latency
    ma_lpf1_get_latency.restype = ma_uint32
    ma_lpf1_get_latency.argtypes = [ctypes.POINTER(struct_ma_lpf1)]
except AttributeError:
    pass
struct_ma_lpf2._pack_ = 1 # source:False
struct_ma_lpf2._fields_ = [
    ('bq', ma_biquad),
]

ma_lpf2 = struct_ma_lpf2
try:
    ma_lpf2_get_heap_size = _libraries['libminiaudio.so'].ma_lpf2_get_heap_size
    ma_lpf2_get_heap_size.restype = ma_result
    ma_lpf2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_lpf2_init_preallocated = _libraries['libminiaudio.so'].ma_lpf2_init_preallocated
    ma_lpf2_init_preallocated.restype = ma_result
    ma_lpf2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_lpf2)]
except AttributeError:
    pass
try:
    ma_lpf2_init = _libraries['libminiaudio.so'].ma_lpf2_init
    ma_lpf2_init.restype = ma_result
    ma_lpf2_init.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_lpf2)]
except AttributeError:
    pass
try:
    ma_lpf2_uninit = _libraries['libminiaudio.so'].ma_lpf2_uninit
    ma_lpf2_uninit.restype = None
    ma_lpf2_uninit.argtypes = [ctypes.POINTER(struct_ma_lpf2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_lpf2_reinit = _libraries['libminiaudio.so'].ma_lpf2_reinit
    ma_lpf2_reinit.restype = ma_result
    ma_lpf2_reinit.argtypes = [ctypes.POINTER(struct_ma_lpf1_config), ctypes.POINTER(struct_ma_lpf2)]
except AttributeError:
    pass
try:
    ma_lpf2_clear_cache = _libraries['libminiaudio.so'].ma_lpf2_clear_cache
    ma_lpf2_clear_cache.restype = ma_result
    ma_lpf2_clear_cache.argtypes = [ctypes.POINTER(struct_ma_lpf2)]
except AttributeError:
    pass
try:
    ma_lpf2_process_pcm_frames = _libraries['libminiaudio.so'].ma_lpf2_process_pcm_frames
    ma_lpf2_process_pcm_frames.restype = ma_result
    ma_lpf2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_lpf2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_lpf2_get_latency = _libraries['libminiaudio.so'].ma_lpf2_get_latency
    ma_lpf2_get_latency.restype = ma_uint32
    ma_lpf2_get_latency.argtypes = [ctypes.POINTER(struct_ma_lpf2)]
except AttributeError:
    pass
class struct_ma_lpf_config(Structure):
    pass

struct_ma_lpf_config._pack_ = 1 # source:False
struct_ma_lpf_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('order', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_lpf_config = struct_ma_lpf_config
try:
    ma_lpf_config_init = _libraries['libminiaudio.so'].ma_lpf_config_init
    ma_lpf_config_init.restype = ma_lpf_config
    ma_lpf_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
try:
    ma_lpf_get_heap_size = _libraries['libminiaudio.so'].ma_lpf_get_heap_size
    ma_lpf_get_heap_size.restype = ma_result
    ma_lpf_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_lpf_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_lpf_init_preallocated = _libraries['libminiaudio.so'].ma_lpf_init_preallocated
    ma_lpf_init_preallocated.restype = ma_result
    ma_lpf_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_lpf_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_lpf)]
except AttributeError:
    pass
try:
    ma_lpf_init = _libraries['libminiaudio.so'].ma_lpf_init
    ma_lpf_init.restype = ma_result
    ma_lpf_init.argtypes = [ctypes.POINTER(struct_ma_lpf_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_lpf)]
except AttributeError:
    pass
try:
    ma_lpf_uninit = _libraries['libminiaudio.so'].ma_lpf_uninit
    ma_lpf_uninit.restype = None
    ma_lpf_uninit.argtypes = [ctypes.POINTER(struct_ma_lpf), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_lpf_reinit = _libraries['libminiaudio.so'].ma_lpf_reinit
    ma_lpf_reinit.restype = ma_result
    ma_lpf_reinit.argtypes = [ctypes.POINTER(struct_ma_lpf_config), ctypes.POINTER(struct_ma_lpf)]
except AttributeError:
    pass
try:
    ma_lpf_clear_cache = _libraries['libminiaudio.so'].ma_lpf_clear_cache
    ma_lpf_clear_cache.restype = ma_result
    ma_lpf_clear_cache.argtypes = [ctypes.POINTER(struct_ma_lpf)]
except AttributeError:
    pass
try:
    ma_lpf_process_pcm_frames = _libraries['libminiaudio.so'].ma_lpf_process_pcm_frames
    ma_lpf_process_pcm_frames.restype = ma_result
    ma_lpf_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_lpf), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_lpf_get_latency = _libraries['libminiaudio.so'].ma_lpf_get_latency
    ma_lpf_get_latency.restype = ma_uint32
    ma_lpf_get_latency.argtypes = [ctypes.POINTER(struct_ma_lpf)]
except AttributeError:
    pass
class struct_ma_hpf1_config(Structure):
    pass

struct_ma_hpf1_config._pack_ = 1 # source:False
struct_ma_hpf1_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('q', ctypes.c_double),
]

ma_hpf1_config = struct_ma_hpf1_config
ma_hpf2_config = struct_ma_hpf1_config
try:
    ma_hpf1_config_init = _libraries['libminiaudio.so'].ma_hpf1_config_init
    ma_hpf1_config_init.restype = ma_hpf1_config
    ma_hpf1_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double]
except AttributeError:
    pass
try:
    ma_hpf2_config_init = _libraries['libminiaudio.so'].ma_hpf2_config_init
    ma_hpf2_config_init.restype = ma_hpf2_config
    ma_hpf2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_hpf1(Structure):
    pass

struct_ma_hpf1._pack_ = 1 # source:False
struct_ma_hpf1._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('a', ma_biquad_coefficient),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pR1', ctypes.POINTER(union_ma_biquad_coefficient)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_hpf1 = struct_ma_hpf1
try:
    ma_hpf1_get_heap_size = _libraries['libminiaudio.so'].ma_hpf1_get_heap_size
    ma_hpf1_get_heap_size.restype = ma_result
    ma_hpf1_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_hpf1_init_preallocated = _libraries['libminiaudio.so'].ma_hpf1_init_preallocated
    ma_hpf1_init_preallocated.restype = ma_result
    ma_hpf1_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_hpf1)]
except AttributeError:
    pass
try:
    ma_hpf1_init = _libraries['libminiaudio.so'].ma_hpf1_init
    ma_hpf1_init.restype = ma_result
    ma_hpf1_init.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hpf1)]
except AttributeError:
    pass
try:
    ma_hpf1_uninit = _libraries['libminiaudio.so'].ma_hpf1_uninit
    ma_hpf1_uninit.restype = None
    ma_hpf1_uninit.argtypes = [ctypes.POINTER(struct_ma_hpf1), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_hpf1_reinit = _libraries['libminiaudio.so'].ma_hpf1_reinit
    ma_hpf1_reinit.restype = ma_result
    ma_hpf1_reinit.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(struct_ma_hpf1)]
except AttributeError:
    pass
try:
    ma_hpf1_process_pcm_frames = _libraries['libminiaudio.so'].ma_hpf1_process_pcm_frames
    ma_hpf1_process_pcm_frames.restype = ma_result
    ma_hpf1_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_hpf1), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_hpf1_get_latency = _libraries['libminiaudio.so'].ma_hpf1_get_latency
    ma_hpf1_get_latency.restype = ma_uint32
    ma_hpf1_get_latency.argtypes = [ctypes.POINTER(struct_ma_hpf1)]
except AttributeError:
    pass
class struct_ma_hpf2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_hpf2 = struct_ma_hpf2
try:
    ma_hpf2_get_heap_size = _libraries['libminiaudio.so'].ma_hpf2_get_heap_size
    ma_hpf2_get_heap_size.restype = ma_result
    ma_hpf2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_hpf2_init_preallocated = _libraries['libminiaudio.so'].ma_hpf2_init_preallocated
    ma_hpf2_init_preallocated.restype = ma_result
    ma_hpf2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_hpf2)]
except AttributeError:
    pass
try:
    ma_hpf2_init = _libraries['libminiaudio.so'].ma_hpf2_init
    ma_hpf2_init.restype = ma_result
    ma_hpf2_init.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hpf2)]
except AttributeError:
    pass
try:
    ma_hpf2_uninit = _libraries['libminiaudio.so'].ma_hpf2_uninit
    ma_hpf2_uninit.restype = None
    ma_hpf2_uninit.argtypes = [ctypes.POINTER(struct_ma_hpf2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_hpf2_reinit = _libraries['libminiaudio.so'].ma_hpf2_reinit
    ma_hpf2_reinit.restype = ma_result
    ma_hpf2_reinit.argtypes = [ctypes.POINTER(struct_ma_hpf1_config), ctypes.POINTER(struct_ma_hpf2)]
except AttributeError:
    pass
try:
    ma_hpf2_process_pcm_frames = _libraries['libminiaudio.so'].ma_hpf2_process_pcm_frames
    ma_hpf2_process_pcm_frames.restype = ma_result
    ma_hpf2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_hpf2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_hpf2_get_latency = _libraries['libminiaudio.so'].ma_hpf2_get_latency
    ma_hpf2_get_latency.restype = ma_uint32
    ma_hpf2_get_latency.argtypes = [ctypes.POINTER(struct_ma_hpf2)]
except AttributeError:
    pass
class struct_ma_hpf_config(Structure):
    pass

struct_ma_hpf_config._pack_ = 1 # source:False
struct_ma_hpf_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('order', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_hpf_config = struct_ma_hpf_config
try:
    ma_hpf_config_init = _libraries['libminiaudio.so'].ma_hpf_config_init
    ma_hpf_config_init.restype = ma_hpf_config
    ma_hpf_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
class struct_ma_hpf(Structure):
    pass

struct_ma_hpf._pack_ = 1 # source:False
struct_ma_hpf._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('hpf1Count', ctypes.c_uint32),
    ('hpf2Count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pHPF1', ctypes.POINTER(struct_ma_hpf1)),
    ('pHPF2', ctypes.POINTER(struct_ma_hpf2)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_hpf = struct_ma_hpf
try:
    ma_hpf_get_heap_size = _libraries['libminiaudio.so'].ma_hpf_get_heap_size
    ma_hpf_get_heap_size.restype = ma_result
    ma_hpf_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_hpf_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_hpf_init_preallocated = _libraries['libminiaudio.so'].ma_hpf_init_preallocated
    ma_hpf_init_preallocated.restype = ma_result
    ma_hpf_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_hpf_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_hpf)]
except AttributeError:
    pass
try:
    ma_hpf_init = _libraries['libminiaudio.so'].ma_hpf_init
    ma_hpf_init.restype = ma_result
    ma_hpf_init.argtypes = [ctypes.POINTER(struct_ma_hpf_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hpf)]
except AttributeError:
    pass
try:
    ma_hpf_uninit = _libraries['libminiaudio.so'].ma_hpf_uninit
    ma_hpf_uninit.restype = None
    ma_hpf_uninit.argtypes = [ctypes.POINTER(struct_ma_hpf), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_hpf_reinit = _libraries['libminiaudio.so'].ma_hpf_reinit
    ma_hpf_reinit.restype = ma_result
    ma_hpf_reinit.argtypes = [ctypes.POINTER(struct_ma_hpf_config), ctypes.POINTER(struct_ma_hpf)]
except AttributeError:
    pass
try:
    ma_hpf_process_pcm_frames = _libraries['libminiaudio.so'].ma_hpf_process_pcm_frames
    ma_hpf_process_pcm_frames.restype = ma_result
    ma_hpf_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_hpf), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_hpf_get_latency = _libraries['libminiaudio.so'].ma_hpf_get_latency
    ma_hpf_get_latency.restype = ma_uint32
    ma_hpf_get_latency.argtypes = [ctypes.POINTER(struct_ma_hpf)]
except AttributeError:
    pass
class struct_ma_bpf2_config(Structure):
    pass

struct_ma_bpf2_config._pack_ = 1 # source:False
struct_ma_bpf2_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('q', ctypes.c_double),
]

ma_bpf2_config = struct_ma_bpf2_config
try:
    ma_bpf2_config_init = _libraries['libminiaudio.so'].ma_bpf2_config_init
    ma_bpf2_config_init.restype = ma_bpf2_config
    ma_bpf2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_bpf2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_bpf2 = struct_ma_bpf2
try:
    ma_bpf2_get_heap_size = _libraries['libminiaudio.so'].ma_bpf2_get_heap_size
    ma_bpf2_get_heap_size.restype = ma_result
    ma_bpf2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_bpf2_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_bpf2_init_preallocated = _libraries['libminiaudio.so'].ma_bpf2_init_preallocated
    ma_bpf2_init_preallocated.restype = ma_result
    ma_bpf2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_bpf2_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_bpf2)]
except AttributeError:
    pass
try:
    ma_bpf2_init = _libraries['libminiaudio.so'].ma_bpf2_init
    ma_bpf2_init.restype = ma_result
    ma_bpf2_init.argtypes = [ctypes.POINTER(struct_ma_bpf2_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_bpf2)]
except AttributeError:
    pass
try:
    ma_bpf2_uninit = _libraries['libminiaudio.so'].ma_bpf2_uninit
    ma_bpf2_uninit.restype = None
    ma_bpf2_uninit.argtypes = [ctypes.POINTER(struct_ma_bpf2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_bpf2_reinit = _libraries['libminiaudio.so'].ma_bpf2_reinit
    ma_bpf2_reinit.restype = ma_result
    ma_bpf2_reinit.argtypes = [ctypes.POINTER(struct_ma_bpf2_config), ctypes.POINTER(struct_ma_bpf2)]
except AttributeError:
    pass
try:
    ma_bpf2_process_pcm_frames = _libraries['libminiaudio.so'].ma_bpf2_process_pcm_frames
    ma_bpf2_process_pcm_frames.restype = ma_result
    ma_bpf2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_bpf2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_bpf2_get_latency = _libraries['libminiaudio.so'].ma_bpf2_get_latency
    ma_bpf2_get_latency.restype = ma_uint32
    ma_bpf2_get_latency.argtypes = [ctypes.POINTER(struct_ma_bpf2)]
except AttributeError:
    pass
class struct_ma_bpf_config(Structure):
    pass

struct_ma_bpf_config._pack_ = 1 # source:False
struct_ma_bpf_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cutoffFrequency', ctypes.c_double),
    ('order', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_bpf_config = struct_ma_bpf_config
try:
    ma_bpf_config_init = _libraries['libminiaudio.so'].ma_bpf_config_init
    ma_bpf_config_init.restype = ma_bpf_config
    ma_bpf_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
class struct_ma_bpf(Structure):
    pass

struct_ma_bpf._pack_ = 1 # source:False
struct_ma_bpf._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('bpf2Count', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pBPF2', ctypes.POINTER(struct_ma_bpf2)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_bpf = struct_ma_bpf
try:
    ma_bpf_get_heap_size = _libraries['libminiaudio.so'].ma_bpf_get_heap_size
    ma_bpf_get_heap_size.restype = ma_result
    ma_bpf_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_bpf_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_bpf_init_preallocated = _libraries['libminiaudio.so'].ma_bpf_init_preallocated
    ma_bpf_init_preallocated.restype = ma_result
    ma_bpf_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_bpf_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_bpf)]
except AttributeError:
    pass
try:
    ma_bpf_init = _libraries['libminiaudio.so'].ma_bpf_init
    ma_bpf_init.restype = ma_result
    ma_bpf_init.argtypes = [ctypes.POINTER(struct_ma_bpf_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_bpf)]
except AttributeError:
    pass
try:
    ma_bpf_uninit = _libraries['libminiaudio.so'].ma_bpf_uninit
    ma_bpf_uninit.restype = None
    ma_bpf_uninit.argtypes = [ctypes.POINTER(struct_ma_bpf), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_bpf_reinit = _libraries['libminiaudio.so'].ma_bpf_reinit
    ma_bpf_reinit.restype = ma_result
    ma_bpf_reinit.argtypes = [ctypes.POINTER(struct_ma_bpf_config), ctypes.POINTER(struct_ma_bpf)]
except AttributeError:
    pass
try:
    ma_bpf_process_pcm_frames = _libraries['libminiaudio.so'].ma_bpf_process_pcm_frames
    ma_bpf_process_pcm_frames.restype = ma_result
    ma_bpf_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_bpf), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_bpf_get_latency = _libraries['libminiaudio.so'].ma_bpf_get_latency
    ma_bpf_get_latency.restype = ma_uint32
    ma_bpf_get_latency.argtypes = [ctypes.POINTER(struct_ma_bpf)]
except AttributeError:
    pass
class struct_ma_notch2_config(Structure):
    pass

struct_ma_notch2_config._pack_ = 1 # source:False
struct_ma_notch2_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('q', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_notch2_config = struct_ma_notch2_config
ma_notch_config = struct_ma_notch2_config
try:
    ma_notch2_config_init = _libraries['libminiaudio.so'].ma_notch2_config_init
    ma_notch2_config_init.restype = ma_notch2_config
    ma_notch2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_notch2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_notch2 = struct_ma_notch2
try:
    ma_notch2_get_heap_size = _libraries['libminiaudio.so'].ma_notch2_get_heap_size
    ma_notch2_get_heap_size.restype = ma_result
    ma_notch2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_notch2_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_notch2_init_preallocated = _libraries['libminiaudio.so'].ma_notch2_init_preallocated
    ma_notch2_init_preallocated.restype = ma_result
    ma_notch2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_notch2_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_notch2)]
except AttributeError:
    pass
try:
    ma_notch2_init = _libraries['libminiaudio.so'].ma_notch2_init
    ma_notch2_init.restype = ma_result
    ma_notch2_init.argtypes = [ctypes.POINTER(struct_ma_notch2_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_notch2)]
except AttributeError:
    pass
try:
    ma_notch2_uninit = _libraries['libminiaudio.so'].ma_notch2_uninit
    ma_notch2_uninit.restype = None
    ma_notch2_uninit.argtypes = [ctypes.POINTER(struct_ma_notch2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_notch2_reinit = _libraries['libminiaudio.so'].ma_notch2_reinit
    ma_notch2_reinit.restype = ma_result
    ma_notch2_reinit.argtypes = [ctypes.POINTER(struct_ma_notch2_config), ctypes.POINTER(struct_ma_notch2)]
except AttributeError:
    pass
try:
    ma_notch2_process_pcm_frames = _libraries['libminiaudio.so'].ma_notch2_process_pcm_frames
    ma_notch2_process_pcm_frames.restype = ma_result
    ma_notch2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_notch2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_notch2_get_latency = _libraries['libminiaudio.so'].ma_notch2_get_latency
    ma_notch2_get_latency.restype = ma_uint32
    ma_notch2_get_latency.argtypes = [ctypes.POINTER(struct_ma_notch2)]
except AttributeError:
    pass
class struct_ma_peak2_config(Structure):
    pass

struct_ma_peak2_config._pack_ = 1 # source:False
struct_ma_peak2_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('gainDB', ctypes.c_double),
    ('q', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_peak2_config = struct_ma_peak2_config
ma_peak_config = struct_ma_peak2_config
try:
    ma_peak2_config_init = _libraries['libminiaudio.so'].ma_peak2_config_init
    ma_peak2_config_init.restype = ma_peak2_config
    ma_peak2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_peak2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_peak2 = struct_ma_peak2
try:
    ma_peak2_get_heap_size = _libraries['libminiaudio.so'].ma_peak2_get_heap_size
    ma_peak2_get_heap_size.restype = ma_result
    ma_peak2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_peak2_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_peak2_init_preallocated = _libraries['libminiaudio.so'].ma_peak2_init_preallocated
    ma_peak2_init_preallocated.restype = ma_result
    ma_peak2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_peak2_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_peak2)]
except AttributeError:
    pass
try:
    ma_peak2_init = _libraries['libminiaudio.so'].ma_peak2_init
    ma_peak2_init.restype = ma_result
    ma_peak2_init.argtypes = [ctypes.POINTER(struct_ma_peak2_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_peak2)]
except AttributeError:
    pass
try:
    ma_peak2_uninit = _libraries['libminiaudio.so'].ma_peak2_uninit
    ma_peak2_uninit.restype = None
    ma_peak2_uninit.argtypes = [ctypes.POINTER(struct_ma_peak2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_peak2_reinit = _libraries['libminiaudio.so'].ma_peak2_reinit
    ma_peak2_reinit.restype = ma_result
    ma_peak2_reinit.argtypes = [ctypes.POINTER(struct_ma_peak2_config), ctypes.POINTER(struct_ma_peak2)]
except AttributeError:
    pass
try:
    ma_peak2_process_pcm_frames = _libraries['libminiaudio.so'].ma_peak2_process_pcm_frames
    ma_peak2_process_pcm_frames.restype = ma_result
    ma_peak2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_peak2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_peak2_get_latency = _libraries['libminiaudio.so'].ma_peak2_get_latency
    ma_peak2_get_latency.restype = ma_uint32
    ma_peak2_get_latency.argtypes = [ctypes.POINTER(struct_ma_peak2)]
except AttributeError:
    pass
class struct_ma_loshelf2_config(Structure):
    pass

struct_ma_loshelf2_config._pack_ = 1 # source:False
struct_ma_loshelf2_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('gainDB', ctypes.c_double),
    ('shelfSlope', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_loshelf2_config = struct_ma_loshelf2_config
ma_loshelf_config = struct_ma_loshelf2_config
try:
    ma_loshelf2_config_init = _libraries['libminiaudio.so'].ma_loshelf2_config_init
    ma_loshelf2_config_init.restype = ma_loshelf2_config
    ma_loshelf2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_loshelf2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_loshelf2 = struct_ma_loshelf2
try:
    ma_loshelf2_get_heap_size = _libraries['libminiaudio.so'].ma_loshelf2_get_heap_size
    ma_loshelf2_get_heap_size.restype = ma_result
    ma_loshelf2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_loshelf2_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_loshelf2_init_preallocated = _libraries['libminiaudio.so'].ma_loshelf2_init_preallocated
    ma_loshelf2_init_preallocated.restype = ma_result
    ma_loshelf2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_loshelf2_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_loshelf2)]
except AttributeError:
    pass
try:
    ma_loshelf2_init = _libraries['libminiaudio.so'].ma_loshelf2_init
    ma_loshelf2_init.restype = ma_result
    ma_loshelf2_init.argtypes = [ctypes.POINTER(struct_ma_loshelf2_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_loshelf2)]
except AttributeError:
    pass
try:
    ma_loshelf2_uninit = _libraries['libminiaudio.so'].ma_loshelf2_uninit
    ma_loshelf2_uninit.restype = None
    ma_loshelf2_uninit.argtypes = [ctypes.POINTER(struct_ma_loshelf2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_loshelf2_reinit = _libraries['libminiaudio.so'].ma_loshelf2_reinit
    ma_loshelf2_reinit.restype = ma_result
    ma_loshelf2_reinit.argtypes = [ctypes.POINTER(struct_ma_loshelf2_config), ctypes.POINTER(struct_ma_loshelf2)]
except AttributeError:
    pass
try:
    ma_loshelf2_process_pcm_frames = _libraries['libminiaudio.so'].ma_loshelf2_process_pcm_frames
    ma_loshelf2_process_pcm_frames.restype = ma_result
    ma_loshelf2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_loshelf2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_loshelf2_get_latency = _libraries['libminiaudio.so'].ma_loshelf2_get_latency
    ma_loshelf2_get_latency.restype = ma_uint32
    ma_loshelf2_get_latency.argtypes = [ctypes.POINTER(struct_ma_loshelf2)]
except AttributeError:
    pass
class struct_ma_hishelf2_config(Structure):
    pass

struct_ma_hishelf2_config._pack_ = 1 # source:False
struct_ma_hishelf2_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('gainDB', ctypes.c_double),
    ('shelfSlope', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_hishelf2_config = struct_ma_hishelf2_config
ma_hishelf_config = struct_ma_hishelf2_config
try:
    ma_hishelf2_config_init = _libraries['libminiaudio.so'].ma_hishelf2_config_init
    ma_hishelf2_config_init.restype = ma_hishelf2_config
    ma_hishelf2_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_hishelf2(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('bq', ma_biquad),
     ]

ma_hishelf2 = struct_ma_hishelf2
try:
    ma_hishelf2_get_heap_size = _libraries['libminiaudio.so'].ma_hishelf2_get_heap_size
    ma_hishelf2_get_heap_size.restype = ma_result
    ma_hishelf2_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_hishelf2_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_hishelf2_init_preallocated = _libraries['libminiaudio.so'].ma_hishelf2_init_preallocated
    ma_hishelf2_init_preallocated.restype = ma_result
    ma_hishelf2_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_hishelf2_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_hishelf2)]
except AttributeError:
    pass
try:
    ma_hishelf2_init = _libraries['libminiaudio.so'].ma_hishelf2_init
    ma_hishelf2_init.restype = ma_result
    ma_hishelf2_init.argtypes = [ctypes.POINTER(struct_ma_hishelf2_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hishelf2)]
except AttributeError:
    pass
try:
    ma_hishelf2_uninit = _libraries['libminiaudio.so'].ma_hishelf2_uninit
    ma_hishelf2_uninit.restype = None
    ma_hishelf2_uninit.argtypes = [ctypes.POINTER(struct_ma_hishelf2), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_hishelf2_reinit = _libraries['libminiaudio.so'].ma_hishelf2_reinit
    ma_hishelf2_reinit.restype = ma_result
    ma_hishelf2_reinit.argtypes = [ctypes.POINTER(struct_ma_hishelf2_config), ctypes.POINTER(struct_ma_hishelf2)]
except AttributeError:
    pass
try:
    ma_hishelf2_process_pcm_frames = _libraries['libminiaudio.so'].ma_hishelf2_process_pcm_frames
    ma_hishelf2_process_pcm_frames.restype = ma_result
    ma_hishelf2_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_hishelf2), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_hishelf2_get_latency = _libraries['libminiaudio.so'].ma_hishelf2_get_latency
    ma_hishelf2_get_latency.restype = ma_uint32
    ma_hishelf2_get_latency.argtypes = [ctypes.POINTER(struct_ma_hishelf2)]
except AttributeError:
    pass
class struct_ma_delay_config(Structure):
    pass

struct_ma_delay_config._pack_ = 1 # source:False
struct_ma_delay_config._fields_ = [
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('delayInFrames', ctypes.c_uint32),
    ('delayStart', ctypes.c_uint32),
    ('wet', ctypes.c_float),
    ('dry', ctypes.c_float),
    ('decay', ctypes.c_float),
]

ma_delay_config = struct_ma_delay_config
try:
    ma_delay_config_init = _libraries['libminiaudio.so'].ma_delay_config_init
    ma_delay_config_init.restype = ma_delay_config
    ma_delay_config_init.argtypes = [ma_uint32, ma_uint32, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
class struct_ma_delay(Structure):
    pass

struct_ma_delay._pack_ = 1 # source:False
struct_ma_delay._fields_ = [
    ('config', ma_delay_config),
    ('cursor', ctypes.c_uint32),
    ('bufferSizeInFrames', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pBuffer', ctypes.POINTER(ctypes.c_float)),
]

ma_delay = struct_ma_delay
try:
    ma_delay_init = _libraries['libminiaudio.so'].ma_delay_init
    ma_delay_init.restype = ma_result
    ma_delay_init.argtypes = [ctypes.POINTER(struct_ma_delay_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_delay)]
except AttributeError:
    pass
try:
    ma_delay_uninit = _libraries['libminiaudio.so'].ma_delay_uninit
    ma_delay_uninit.restype = None
    ma_delay_uninit.argtypes = [ctypes.POINTER(struct_ma_delay), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_delay_process_pcm_frames = _libraries['libminiaudio.so'].ma_delay_process_pcm_frames
    ma_delay_process_pcm_frames.restype = ma_result
    ma_delay_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_delay), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_delay_set_wet = _libraries['libminiaudio.so'].ma_delay_set_wet
    ma_delay_set_wet.restype = None
    ma_delay_set_wet.argtypes = [ctypes.POINTER(struct_ma_delay), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_get_wet = _libraries['libminiaudio.so'].ma_delay_get_wet
    ma_delay_get_wet.restype = ctypes.c_float
    ma_delay_get_wet.argtypes = [ctypes.POINTER(struct_ma_delay)]
except AttributeError:
    pass
try:
    ma_delay_set_dry = _libraries['libminiaudio.so'].ma_delay_set_dry
    ma_delay_set_dry.restype = None
    ma_delay_set_dry.argtypes = [ctypes.POINTER(struct_ma_delay), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_get_dry = _libraries['libminiaudio.so'].ma_delay_get_dry
    ma_delay_get_dry.restype = ctypes.c_float
    ma_delay_get_dry.argtypes = [ctypes.POINTER(struct_ma_delay)]
except AttributeError:
    pass
try:
    ma_delay_set_decay = _libraries['libminiaudio.so'].ma_delay_set_decay
    ma_delay_set_decay.restype = None
    ma_delay_set_decay.argtypes = [ctypes.POINTER(struct_ma_delay), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_get_decay = _libraries['libminiaudio.so'].ma_delay_get_decay
    ma_delay_get_decay.restype = ctypes.c_float
    ma_delay_get_decay.argtypes = [ctypes.POINTER(struct_ma_delay)]
except AttributeError:
    pass
class struct_ma_gainer_config(Structure):
    pass

struct_ma_gainer_config._pack_ = 1 # source:False
struct_ma_gainer_config._fields_ = [
    ('channels', ctypes.c_uint32),
    ('smoothTimeInFrames', ctypes.c_uint32),
]

ma_gainer_config = struct_ma_gainer_config
try:
    ma_gainer_config_init = _libraries['libminiaudio.so'].ma_gainer_config_init
    ma_gainer_config_init.restype = ma_gainer_config
    ma_gainer_config_init.argtypes = [ma_uint32, ma_uint32]
except AttributeError:
    pass
class struct_ma_gainer(Structure):
    pass

struct_ma_gainer._pack_ = 1 # source:False
struct_ma_gainer._fields_ = [
    ('config', ma_gainer_config),
    ('t', ctypes.c_uint32),
    ('masterVolume', ctypes.c_float),
    ('pOldGains', ctypes.POINTER(ctypes.c_float)),
    ('pNewGains', ctypes.POINTER(ctypes.c_float)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_gainer = struct_ma_gainer
try:
    ma_gainer_get_heap_size = _libraries['libminiaudio.so'].ma_gainer_get_heap_size
    ma_gainer_get_heap_size.restype = ma_result
    ma_gainer_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_gainer_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_gainer_init_preallocated = _libraries['libminiaudio.so'].ma_gainer_init_preallocated
    ma_gainer_init_preallocated.restype = ma_result
    ma_gainer_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_gainer_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_gainer)]
except AttributeError:
    pass
try:
    ma_gainer_init = _libraries['libminiaudio.so'].ma_gainer_init
    ma_gainer_init.restype = ma_result
    ma_gainer_init.argtypes = [ctypes.POINTER(struct_ma_gainer_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_gainer)]
except AttributeError:
    pass
try:
    ma_gainer_uninit = _libraries['libminiaudio.so'].ma_gainer_uninit
    ma_gainer_uninit.restype = None
    ma_gainer_uninit.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_gainer_process_pcm_frames = _libraries['libminiaudio.so'].ma_gainer_process_pcm_frames
    ma_gainer_process_pcm_frames.restype = ma_result
    ma_gainer_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_gainer_set_gain = _libraries['libminiaudio.so'].ma_gainer_set_gain
    ma_gainer_set_gain.restype = ma_result
    ma_gainer_set_gain.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_gainer_set_gains = _libraries['libminiaudio.so'].ma_gainer_set_gains
    ma_gainer_set_gains.restype = ma_result
    ma_gainer_set_gains.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_gainer_set_master_volume = _libraries['libminiaudio.so'].ma_gainer_set_master_volume
    ma_gainer_set_master_volume.restype = ma_result
    ma_gainer_set_master_volume.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_gainer_get_master_volume = _libraries['libminiaudio.so'].ma_gainer_get_master_volume
    ma_gainer_get_master_volume.restype = ma_result
    ma_gainer_get_master_volume.argtypes = [ctypes.POINTER(struct_ma_gainer), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass

# values for enumeration 'ma_pan_mode'
ma_pan_mode__enumvalues = {
    0: 'ma_pan_mode_balance',
    1: 'ma_pan_mode_pan',
}
ma_pan_mode_balance = 0
ma_pan_mode_pan = 1
ma_pan_mode = ctypes.c_uint32 # enum
class struct_ma_panner_config(Structure):
    pass

struct_ma_panner_config._pack_ = 1 # source:False
struct_ma_panner_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('mode', ma_pan_mode),
    ('pan', ctypes.c_float),
]

ma_panner_config = struct_ma_panner_config
try:
    ma_panner_config_init = _libraries['libminiaudio.so'].ma_panner_config_init
    ma_panner_config_init.restype = ma_panner_config
    ma_panner_config_init.argtypes = [ma_format, ma_uint32]
except AttributeError:
    pass
class struct_ma_panner(Structure):
    pass

struct_ma_panner._pack_ = 1 # source:False
struct_ma_panner._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('mode', ma_pan_mode),
    ('pan', ctypes.c_float),
]

ma_panner = struct_ma_panner
try:
    ma_panner_init = _libraries['libminiaudio.so'].ma_panner_init
    ma_panner_init.restype = ma_result
    ma_panner_init.argtypes = [ctypes.POINTER(struct_ma_panner_config), ctypes.POINTER(struct_ma_panner)]
except AttributeError:
    pass
try:
    ma_panner_process_pcm_frames = _libraries['libminiaudio.so'].ma_panner_process_pcm_frames
    ma_panner_process_pcm_frames.restype = ma_result
    ma_panner_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_panner), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_panner_set_mode = _libraries['libminiaudio.so'].ma_panner_set_mode
    ma_panner_set_mode.restype = None
    ma_panner_set_mode.argtypes = [ctypes.POINTER(struct_ma_panner), ma_pan_mode]
except AttributeError:
    pass
try:
    ma_panner_get_mode = _libraries['libminiaudio.so'].ma_panner_get_mode
    ma_panner_get_mode.restype = ma_pan_mode
    ma_panner_get_mode.argtypes = [ctypes.POINTER(struct_ma_panner)]
except AttributeError:
    pass
try:
    ma_panner_set_pan = _libraries['libminiaudio.so'].ma_panner_set_pan
    ma_panner_set_pan.restype = None
    ma_panner_set_pan.argtypes = [ctypes.POINTER(struct_ma_panner), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_panner_get_pan = _libraries['libminiaudio.so'].ma_panner_get_pan
    ma_panner_get_pan.restype = ctypes.c_float
    ma_panner_get_pan.argtypes = [ctypes.POINTER(struct_ma_panner)]
except AttributeError:
    pass
class struct_ma_fader_config(Structure):
    pass

struct_ma_fader_config._pack_ = 1 # source:False
struct_ma_fader_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
]

ma_fader_config = struct_ma_fader_config
try:
    ma_fader_config_init = _libraries['libminiaudio.so'].ma_fader_config_init
    ma_fader_config_init.restype = ma_fader_config
    ma_fader_config_init.argtypes = [ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
class struct_ma_fader(Structure):
    pass

struct_ma_fader._pack_ = 1 # source:False
struct_ma_fader._fields_ = [
    ('config', ma_fader_config),
    ('volumeBeg', ctypes.c_float),
    ('volumeEnd', ctypes.c_float),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('lengthInFrames', ctypes.c_uint64),
    ('cursorInFrames', ctypes.c_int64),
]

ma_fader = struct_ma_fader
try:
    ma_fader_init = _libraries['libminiaudio.so'].ma_fader_init
    ma_fader_init.restype = ma_result
    ma_fader_init.argtypes = [ctypes.POINTER(struct_ma_fader_config), ctypes.POINTER(struct_ma_fader)]
except AttributeError:
    pass
try:
    ma_fader_process_pcm_frames = _libraries['libminiaudio.so'].ma_fader_process_pcm_frames
    ma_fader_process_pcm_frames.restype = ma_result
    ma_fader_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_fader), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_fader_get_data_format = _libraries['libminiaudio.so'].ma_fader_get_data_format
    ma_fader_get_data_format.restype = None
    ma_fader_get_data_format.argtypes = [ctypes.POINTER(struct_ma_fader), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_fader_set_fade = _libraries['libminiaudio.so'].ma_fader_set_fade
    ma_fader_set_fade.restype = None
    ma_fader_set_fade.argtypes = [ctypes.POINTER(struct_ma_fader), ctypes.c_float, ctypes.c_float, ma_uint64]
except AttributeError:
    pass
try:
    ma_fader_set_fade_ex = _libraries['libminiaudio.so'].ma_fader_set_fade_ex
    ma_fader_set_fade_ex.restype = None
    ma_fader_set_fade_ex.argtypes = [ctypes.POINTER(struct_ma_fader), ctypes.c_float, ctypes.c_float, ma_uint64, ma_int64]
except AttributeError:
    pass
try:
    ma_fader_get_current_volume = _libraries['libminiaudio.so'].ma_fader_get_current_volume
    ma_fader_get_current_volume.restype = ctypes.c_float
    ma_fader_get_current_volume.argtypes = [ctypes.POINTER(struct_ma_fader)]
except AttributeError:
    pass
class struct_ma_vec3f(Structure):
    pass

struct_ma_vec3f._pack_ = 1 # source:False
struct_ma_vec3f._fields_ = [
    ('x', ctypes.c_float),
    ('y', ctypes.c_float),
    ('z', ctypes.c_float),
]

ma_vec3f = struct_ma_vec3f
class struct_ma_atomic_vec3f(Structure):
    pass

struct_ma_atomic_vec3f._pack_ = 1 # source:False
struct_ma_atomic_vec3f._fields_ = [
    ('v', ma_vec3f),
    ('lock', ctypes.c_uint32),
]

ma_atomic_vec3f = struct_ma_atomic_vec3f

# values for enumeration 'ma_attenuation_model'
ma_attenuation_model__enumvalues = {
    0: 'ma_attenuation_model_none',
    1: 'ma_attenuation_model_inverse',
    2: 'ma_attenuation_model_linear',
    3: 'ma_attenuation_model_exponential',
}
ma_attenuation_model_none = 0
ma_attenuation_model_inverse = 1
ma_attenuation_model_linear = 2
ma_attenuation_model_exponential = 3
ma_attenuation_model = ctypes.c_uint32 # enum

# values for enumeration 'ma_positioning'
ma_positioning__enumvalues = {
    0: 'ma_positioning_absolute',
    1: 'ma_positioning_relative',
}
ma_positioning_absolute = 0
ma_positioning_relative = 1
ma_positioning = ctypes.c_uint32 # enum

# values for enumeration 'ma_handedness'
ma_handedness__enumvalues = {
    0: 'ma_handedness_right',
    1: 'ma_handedness_left',
}
ma_handedness_right = 0
ma_handedness_left = 1
ma_handedness = ctypes.c_uint32 # enum
class struct_ma_spatializer_listener_config(Structure):
    pass

struct_ma_spatializer_listener_config._pack_ = 1 # source:False
struct_ma_spatializer_listener_config._fields_ = [
    ('channelsOut', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pChannelMapOut', ctypes.POINTER(ctypes.c_ubyte)),
    ('handedness', ma_handedness),
    ('coneInnerAngleInRadians', ctypes.c_float),
    ('coneOuterAngleInRadians', ctypes.c_float),
    ('coneOuterGain', ctypes.c_float),
    ('speedOfSound', ctypes.c_float),
    ('worldUp', ma_vec3f),
]

ma_spatializer_listener_config = struct_ma_spatializer_listener_config
try:
    ma_spatializer_listener_config_init = _libraries['libminiaudio.so'].ma_spatializer_listener_config_init
    ma_spatializer_listener_config_init.restype = ma_spatializer_listener_config
    ma_spatializer_listener_config_init.argtypes = [ma_uint32]
except AttributeError:
    pass
class struct_ma_spatializer_listener(Structure):
    pass

struct_ma_spatializer_listener._pack_ = 1 # source:False
struct_ma_spatializer_listener._fields_ = [
    ('config', ma_spatializer_listener_config),
    ('position', ma_atomic_vec3f),
    ('direction', ma_atomic_vec3f),
    ('velocity', ma_atomic_vec3f),
    ('isEnabled', ctypes.c_uint32),
    ('_ownsHeap', ctypes.c_uint32),
    ('_pHeap', ctypes.POINTER(None)),
]

ma_spatializer_listener = struct_ma_spatializer_listener
try:
    ma_spatializer_listener_get_heap_size = _libraries['libminiaudio.so'].ma_spatializer_listener_get_heap_size
    ma_spatializer_listener_get_heap_size.restype = ma_result
    ma_spatializer_listener_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_init_preallocated = _libraries['libminiaudio.so'].ma_spatializer_listener_init_preallocated
    ma_spatializer_listener_init_preallocated.restype = ma_result
    ma_spatializer_listener_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_init = _libraries['libminiaudio.so'].ma_spatializer_listener_init
    ma_spatializer_listener_init.restype = ma_result
    ma_spatializer_listener_init.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_uninit = _libraries['libminiaudio.so'].ma_spatializer_listener_uninit
    ma_spatializer_listener_uninit.restype = None
    ma_spatializer_listener_uninit.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_channel_map = _libraries['libminiaudio.so'].ma_spatializer_listener_get_channel_map
    ma_spatializer_listener_get_channel_map.restype = ctypes.POINTER(ctypes.c_ubyte)
    ma_spatializer_listener_get_channel_map.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_cone = _libraries['libminiaudio.so'].ma_spatializer_listener_set_cone
    ma_spatializer_listener_set_cone.restype = None
    ma_spatializer_listener_set_cone.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_cone = _libraries['libminiaudio.so'].ma_spatializer_listener_get_cone
    ma_spatializer_listener_get_cone.restype = None
    ma_spatializer_listener_get_cone.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_position = _libraries['libminiaudio.so'].ma_spatializer_listener_set_position
    ma_spatializer_listener_set_position.restype = None
    ma_spatializer_listener_set_position.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_position = _libraries['libminiaudio.so'].ma_spatializer_listener_get_position
    ma_spatializer_listener_get_position.restype = ma_vec3f
    ma_spatializer_listener_get_position.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_direction = _libraries['libminiaudio.so'].ma_spatializer_listener_set_direction
    ma_spatializer_listener_set_direction.restype = None
    ma_spatializer_listener_set_direction.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_direction = _libraries['libminiaudio.so'].ma_spatializer_listener_get_direction
    ma_spatializer_listener_get_direction.restype = ma_vec3f
    ma_spatializer_listener_get_direction.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_velocity = _libraries['libminiaudio.so'].ma_spatializer_listener_set_velocity
    ma_spatializer_listener_set_velocity.restype = None
    ma_spatializer_listener_set_velocity.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_velocity = _libraries['libminiaudio.so'].ma_spatializer_listener_get_velocity
    ma_spatializer_listener_get_velocity.restype = ma_vec3f
    ma_spatializer_listener_get_velocity.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_speed_of_sound = _libraries['libminiaudio.so'].ma_spatializer_listener_set_speed_of_sound
    ma_spatializer_listener_set_speed_of_sound.restype = None
    ma_spatializer_listener_set_speed_of_sound.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_speed_of_sound = _libraries['libminiaudio.so'].ma_spatializer_listener_get_speed_of_sound
    ma_spatializer_listener_get_speed_of_sound.restype = ctypes.c_float
    ma_spatializer_listener_get_speed_of_sound.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_world_up = _libraries['libminiaudio.so'].ma_spatializer_listener_set_world_up
    ma_spatializer_listener_set_world_up.restype = None
    ma_spatializer_listener_set_world_up.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_listener_get_world_up = _libraries['libminiaudio.so'].ma_spatializer_listener_get_world_up
    ma_spatializer_listener_get_world_up.restype = ma_vec3f
    ma_spatializer_listener_get_world_up.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
try:
    ma_spatializer_listener_set_enabled = _libraries['libminiaudio.so'].ma_spatializer_listener_set_enabled
    ma_spatializer_listener_set_enabled.restype = None
    ma_spatializer_listener_set_enabled.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener), ma_bool32]
except AttributeError:
    pass
try:
    ma_spatializer_listener_is_enabled = _libraries['libminiaudio.so'].ma_spatializer_listener_is_enabled
    ma_spatializer_listener_is_enabled.restype = ma_bool32
    ma_spatializer_listener_is_enabled.argtypes = [ctypes.POINTER(struct_ma_spatializer_listener)]
except AttributeError:
    pass
class struct_ma_spatializer_config(Structure):
    pass

struct_ma_spatializer_config._pack_ = 1 # source:False
struct_ma_spatializer_config._fields_ = [
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('pChannelMapIn', ctypes.POINTER(ctypes.c_ubyte)),
    ('attenuationModel', ma_attenuation_model),
    ('positioning', ma_positioning),
    ('handedness', ma_handedness),
    ('minGain', ctypes.c_float),
    ('maxGain', ctypes.c_float),
    ('minDistance', ctypes.c_float),
    ('maxDistance', ctypes.c_float),
    ('rolloff', ctypes.c_float),
    ('coneInnerAngleInRadians', ctypes.c_float),
    ('coneOuterAngleInRadians', ctypes.c_float),
    ('coneOuterGain', ctypes.c_float),
    ('dopplerFactor', ctypes.c_float),
    ('directionalAttenuationFactor', ctypes.c_float),
    ('minSpatializationChannelGain', ctypes.c_float),
    ('gainSmoothTimeInFrames', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_spatializer_config = struct_ma_spatializer_config
try:
    ma_spatializer_config_init = _libraries['libminiaudio.so'].ma_spatializer_config_init
    ma_spatializer_config_init.restype = ma_spatializer_config
    ma_spatializer_config_init.argtypes = [ma_uint32, ma_uint32]
except AttributeError:
    pass
class struct_ma_spatializer(Structure):
    pass

struct_ma_spatializer._pack_ = 1 # source:False
struct_ma_spatializer._fields_ = [
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('pChannelMapIn', ctypes.POINTER(ctypes.c_ubyte)),
    ('attenuationModel', ma_attenuation_model),
    ('positioning', ma_positioning),
    ('handedness', ma_handedness),
    ('minGain', ctypes.c_float),
    ('maxGain', ctypes.c_float),
    ('minDistance', ctypes.c_float),
    ('maxDistance', ctypes.c_float),
    ('rolloff', ctypes.c_float),
    ('coneInnerAngleInRadians', ctypes.c_float),
    ('coneOuterAngleInRadians', ctypes.c_float),
    ('coneOuterGain', ctypes.c_float),
    ('dopplerFactor', ctypes.c_float),
    ('directionalAttenuationFactor', ctypes.c_float),
    ('gainSmoothTimeInFrames', ctypes.c_uint32),
    ('position', ma_atomic_vec3f),
    ('direction', ma_atomic_vec3f),
    ('velocity', ma_atomic_vec3f),
    ('dopplerPitch', ctypes.c_float),
    ('minSpatializationChannelGain', ctypes.c_float),
    ('gainer', ma_gainer),
    ('pNewChannelGainsOut', ctypes.POINTER(ctypes.c_float)),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_spatializer = struct_ma_spatializer
try:
    ma_spatializer_get_heap_size = _libraries['libminiaudio.so'].ma_spatializer_get_heap_size
    ma_spatializer_get_heap_size.restype = ma_result
    ma_spatializer_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_spatializer_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_spatializer_init_preallocated = _libraries['libminiaudio.so'].ma_spatializer_init_preallocated
    ma_spatializer_init_preallocated.restype = ma_result
    ma_spatializer_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_spatializer_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_init = _libraries['libminiaudio.so'].ma_spatializer_init
    ma_spatializer_init.restype = ma_result
    ma_spatializer_init.argtypes = [ctypes.POINTER(struct_ma_spatializer_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_uninit = _libraries['libminiaudio.so'].ma_spatializer_uninit
    ma_spatializer_uninit.restype = None
    ma_spatializer_uninit.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_spatializer_process_pcm_frames = _libraries['libminiaudio.so'].ma_spatializer_process_pcm_frames
    ma_spatializer_process_pcm_frames.restype = ma_result
    ma_spatializer_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.POINTER(struct_ma_spatializer_listener), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_spatializer_set_master_volume = _libraries['libminiaudio.so'].ma_spatializer_set_master_volume
    ma_spatializer_set_master_volume.restype = ma_result
    ma_spatializer_set_master_volume.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_master_volume = _libraries['libminiaudio.so'].ma_spatializer_get_master_volume
    ma_spatializer_get_master_volume.restype = ma_result
    ma_spatializer_get_master_volume.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_spatializer_get_input_channels = _libraries['libminiaudio.so'].ma_spatializer_get_input_channels
    ma_spatializer_get_input_channels.restype = ma_uint32
    ma_spatializer_get_input_channels.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_get_output_channels = _libraries['libminiaudio.so'].ma_spatializer_get_output_channels
    ma_spatializer_get_output_channels.restype = ma_uint32
    ma_spatializer_get_output_channels.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_attenuation_model = _libraries['libminiaudio.so'].ma_spatializer_set_attenuation_model
    ma_spatializer_set_attenuation_model.restype = None
    ma_spatializer_set_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_spatializer), ma_attenuation_model]
except AttributeError:
    pass
try:
    ma_spatializer_get_attenuation_model = _libraries['libminiaudio.so'].ma_spatializer_get_attenuation_model
    ma_spatializer_get_attenuation_model.restype = ma_attenuation_model
    ma_spatializer_get_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_positioning = _libraries['libminiaudio.so'].ma_spatializer_set_positioning
    ma_spatializer_set_positioning.restype = None
    ma_spatializer_set_positioning.argtypes = [ctypes.POINTER(struct_ma_spatializer), ma_positioning]
except AttributeError:
    pass
try:
    ma_spatializer_get_positioning = _libraries['libminiaudio.so'].ma_spatializer_get_positioning
    ma_spatializer_get_positioning.restype = ma_positioning
    ma_spatializer_get_positioning.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_rolloff = _libraries['libminiaudio.so'].ma_spatializer_set_rolloff
    ma_spatializer_set_rolloff.restype = None
    ma_spatializer_set_rolloff.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_rolloff = _libraries['libminiaudio.so'].ma_spatializer_get_rolloff
    ma_spatializer_get_rolloff.restype = ctypes.c_float
    ma_spatializer_get_rolloff.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_min_gain = _libraries['libminiaudio.so'].ma_spatializer_set_min_gain
    ma_spatializer_set_min_gain.restype = None
    ma_spatializer_set_min_gain.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_min_gain = _libraries['libminiaudio.so'].ma_spatializer_get_min_gain
    ma_spatializer_get_min_gain.restype = ctypes.c_float
    ma_spatializer_get_min_gain.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_max_gain = _libraries['libminiaudio.so'].ma_spatializer_set_max_gain
    ma_spatializer_set_max_gain.restype = None
    ma_spatializer_set_max_gain.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_max_gain = _libraries['libminiaudio.so'].ma_spatializer_get_max_gain
    ma_spatializer_get_max_gain.restype = ctypes.c_float
    ma_spatializer_get_max_gain.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_min_distance = _libraries['libminiaudio.so'].ma_spatializer_set_min_distance
    ma_spatializer_set_min_distance.restype = None
    ma_spatializer_set_min_distance.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_min_distance = _libraries['libminiaudio.so'].ma_spatializer_get_min_distance
    ma_spatializer_get_min_distance.restype = ctypes.c_float
    ma_spatializer_get_min_distance.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_max_distance = _libraries['libminiaudio.so'].ma_spatializer_set_max_distance
    ma_spatializer_set_max_distance.restype = None
    ma_spatializer_set_max_distance.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_max_distance = _libraries['libminiaudio.so'].ma_spatializer_get_max_distance
    ma_spatializer_get_max_distance.restype = ctypes.c_float
    ma_spatializer_get_max_distance.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_cone = _libraries['libminiaudio.so'].ma_spatializer_set_cone
    ma_spatializer_set_cone.restype = None
    ma_spatializer_set_cone.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_cone = _libraries['libminiaudio.so'].ma_spatializer_get_cone
    ma_spatializer_get_cone.restype = None
    ma_spatializer_get_cone.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_spatializer_set_doppler_factor = _libraries['libminiaudio.so'].ma_spatializer_set_doppler_factor
    ma_spatializer_set_doppler_factor.restype = None
    ma_spatializer_set_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_doppler_factor = _libraries['libminiaudio.so'].ma_spatializer_get_doppler_factor
    ma_spatializer_get_doppler_factor.restype = ctypes.c_float
    ma_spatializer_get_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_spatializer_set_directional_attenuation_factor
    ma_spatializer_set_directional_attenuation_factor.restype = None
    ma_spatializer_set_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_spatializer_get_directional_attenuation_factor
    ma_spatializer_get_directional_attenuation_factor.restype = ctypes.c_float
    ma_spatializer_get_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_position = _libraries['libminiaudio.so'].ma_spatializer_set_position
    ma_spatializer_set_position.restype = None
    ma_spatializer_set_position.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_position = _libraries['libminiaudio.so'].ma_spatializer_get_position
    ma_spatializer_get_position.restype = ma_vec3f
    ma_spatializer_get_position.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_direction = _libraries['libminiaudio.so'].ma_spatializer_set_direction
    ma_spatializer_set_direction.restype = None
    ma_spatializer_set_direction.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_direction = _libraries['libminiaudio.so'].ma_spatializer_get_direction
    ma_spatializer_get_direction.restype = ma_vec3f
    ma_spatializer_get_direction.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_set_velocity = _libraries['libminiaudio.so'].ma_spatializer_set_velocity
    ma_spatializer_set_velocity.restype = None
    ma_spatializer_set_velocity.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_spatializer_get_velocity = _libraries['libminiaudio.so'].ma_spatializer_get_velocity
    ma_spatializer_get_velocity.restype = ma_vec3f
    ma_spatializer_get_velocity.argtypes = [ctypes.POINTER(struct_ma_spatializer)]
except AttributeError:
    pass
try:
    ma_spatializer_get_relative_position_and_direction = _libraries['libminiaudio.so'].ma_spatializer_get_relative_position_and_direction
    ma_spatializer_get_relative_position_and_direction.restype = None
    ma_spatializer_get_relative_position_and_direction.argtypes = [ctypes.POINTER(struct_ma_spatializer), ctypes.POINTER(struct_ma_spatializer_listener), ctypes.POINTER(struct_ma_vec3f), ctypes.POINTER(struct_ma_vec3f)]
except AttributeError:
    pass
try:
    ma_linear_resampler_config_init = _libraries['libminiaudio.so'].ma_linear_resampler_config_init
    ma_linear_resampler_config_init.restype = ma_linear_resampler_config
    ma_linear_resampler_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_linear_resampler_get_heap_size = _libraries['libminiaudio.so'].ma_linear_resampler_get_heap_size
    ma_linear_resampler_get_heap_size.restype = ma_result
    ma_linear_resampler_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_linear_resampler_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_linear_resampler_init_preallocated = _libraries['libminiaudio.so'].ma_linear_resampler_init_preallocated
    ma_linear_resampler_init_preallocated.restype = ma_result
    ma_linear_resampler_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_linear_resampler_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_linear_resampler)]
except AttributeError:
    pass
try:
    ma_linear_resampler_init = _libraries['libminiaudio.so'].ma_linear_resampler_init
    ma_linear_resampler_init.restype = ma_result
    ma_linear_resampler_init.argtypes = [ctypes.POINTER(struct_ma_linear_resampler_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_linear_resampler)]
except AttributeError:
    pass
try:
    ma_linear_resampler_uninit = _libraries['libminiaudio.so'].ma_linear_resampler_uninit
    ma_linear_resampler_uninit.restype = None
    ma_linear_resampler_uninit.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_linear_resampler_process_pcm_frames = _libraries['libminiaudio.so'].ma_linear_resampler_process_pcm_frames
    ma_linear_resampler_process_pcm_frames.restype = ma_result
    ma_linear_resampler_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_linear_resampler_set_rate = _libraries['libminiaudio.so'].ma_linear_resampler_set_rate
    ma_linear_resampler_set_rate.restype = ma_result
    ma_linear_resampler_set_rate.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_linear_resampler_set_rate_ratio = _libraries['libminiaudio.so'].ma_linear_resampler_set_rate_ratio
    ma_linear_resampler_set_rate_ratio.restype = ma_result
    ma_linear_resampler_set_rate_ratio.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_linear_resampler_get_input_latency = _libraries['libminiaudio.so'].ma_linear_resampler_get_input_latency
    ma_linear_resampler_get_input_latency.restype = ma_uint64
    ma_linear_resampler_get_input_latency.argtypes = [ctypes.POINTER(struct_ma_linear_resampler)]
except AttributeError:
    pass
try:
    ma_linear_resampler_get_output_latency = _libraries['libminiaudio.so'].ma_linear_resampler_get_output_latency
    ma_linear_resampler_get_output_latency.restype = ma_uint64
    ma_linear_resampler_get_output_latency.argtypes = [ctypes.POINTER(struct_ma_linear_resampler)]
except AttributeError:
    pass
try:
    ma_linear_resampler_get_required_input_frame_count = _libraries['libminiaudio.so'].ma_linear_resampler_get_required_input_frame_count
    ma_linear_resampler_get_required_input_frame_count.restype = ma_result
    ma_linear_resampler_get_required_input_frame_count.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_linear_resampler_get_expected_output_frame_count = _libraries['libminiaudio.so'].ma_linear_resampler_get_expected_output_frame_count
    ma_linear_resampler_get_expected_output_frame_count.restype = ma_result
    ma_linear_resampler_get_expected_output_frame_count.argtypes = [ctypes.POINTER(struct_ma_linear_resampler), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_linear_resampler_reset = _libraries['libminiaudio.so'].ma_linear_resampler_reset
    ma_linear_resampler_reset.restype = ma_result
    ma_linear_resampler_reset.argtypes = [ctypes.POINTER(struct_ma_linear_resampler)]
except AttributeError:
    pass
class struct_ma_resampler_config(Structure):
    pass

class struct_ma_resampler_config_linear(Structure):
    pass

struct_ma_resampler_config_linear._pack_ = 1 # source:False
struct_ma_resampler_config_linear._fields_ = [
    ('lpfOrder', ctypes.c_uint32),
]

struct_ma_resampler_config._pack_ = 1 # source:False
struct_ma_resampler_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRateIn', ctypes.c_uint32),
    ('sampleRateOut', ctypes.c_uint32),
    ('algorithm', ma_resample_algorithm),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pBackendVTable', ctypes.POINTER(struct_ma_resampling_backend_vtable)),
    ('pBackendUserData', ctypes.POINTER(None)),
    ('linear', struct_ma_resampler_config_linear),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_resampler_config = struct_ma_resampler_config
ma_resampling_backend = None
struct_ma_resampling_backend_vtable._pack_ = 1 # source:False
struct_ma_resampling_backend_vtable._fields_ = [
    ('onGetHeapSize', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(struct_ma_resampler_config), ctypes.POINTER(ctypes.c_uint64))),
    ('onInit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(struct_ma_resampler_config), ctypes.POINTER(None), ctypes.POINTER(ctypes.POINTER(None)))),
    ('onUninit', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks))),
    ('onProcess', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64))),
    ('onSetRate', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32, ctypes.c_uint32)),
    ('onGetInputLatency', ctypes.CFUNCTYPE(ctypes.c_uint64, ctypes.POINTER(None), ctypes.POINTER(None))),
    ('onGetOutputLatency', ctypes.CFUNCTYPE(ctypes.c_uint64, ctypes.POINTER(None), ctypes.POINTER(None))),
    ('onGetRequiredInputFrameCount', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onGetExpectedOutputFrameCount', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onReset', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None))),
]

ma_resampling_backend_vtable = struct_ma_resampling_backend_vtable
try:
    ma_resampler_config_init = _libraries['libminiaudio.so'].ma_resampler_config_init
    ma_resampler_config_init.restype = ma_resampler_config
    ma_resampler_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ma_uint32, ma_resample_algorithm]
except AttributeError:
    pass
try:
    ma_resampler_get_heap_size = _libraries['libminiaudio.so'].ma_resampler_get_heap_size
    ma_resampler_get_heap_size.restype = ma_result
    ma_resampler_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_resampler_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resampler_init_preallocated = _libraries['libminiaudio.so'].ma_resampler_init_preallocated
    ma_resampler_init_preallocated.restype = ma_result
    ma_resampler_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_resampler_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_resampler)]
except AttributeError:
    pass
try:
    ma_resampler_init = _libraries['libminiaudio.so'].ma_resampler_init
    ma_resampler_init.restype = ma_result
    ma_resampler_init.argtypes = [ctypes.POINTER(struct_ma_resampler_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_resampler)]
except AttributeError:
    pass
try:
    ma_resampler_uninit = _libraries['libminiaudio.so'].ma_resampler_uninit
    ma_resampler_uninit.restype = None
    ma_resampler_uninit.argtypes = [ctypes.POINTER(struct_ma_resampler), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_resampler_process_pcm_frames = _libraries['libminiaudio.so'].ma_resampler_process_pcm_frames
    ma_resampler_process_pcm_frames.restype = ma_result
    ma_resampler_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resampler), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resampler_set_rate = _libraries['libminiaudio.so'].ma_resampler_set_rate
    ma_resampler_set_rate.restype = ma_result
    ma_resampler_set_rate.argtypes = [ctypes.POINTER(struct_ma_resampler), ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_resampler_set_rate_ratio = _libraries['libminiaudio.so'].ma_resampler_set_rate_ratio
    ma_resampler_set_rate_ratio.restype = ma_result
    ma_resampler_set_rate_ratio.argtypes = [ctypes.POINTER(struct_ma_resampler), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_resampler_get_input_latency = _libraries['libminiaudio.so'].ma_resampler_get_input_latency
    ma_resampler_get_input_latency.restype = ma_uint64
    ma_resampler_get_input_latency.argtypes = [ctypes.POINTER(struct_ma_resampler)]
except AttributeError:
    pass
try:
    ma_resampler_get_output_latency = _libraries['libminiaudio.so'].ma_resampler_get_output_latency
    ma_resampler_get_output_latency.restype = ma_uint64
    ma_resampler_get_output_latency.argtypes = [ctypes.POINTER(struct_ma_resampler)]
except AttributeError:
    pass
try:
    ma_resampler_get_required_input_frame_count = _libraries['libminiaudio.so'].ma_resampler_get_required_input_frame_count
    ma_resampler_get_required_input_frame_count.restype = ma_result
    ma_resampler_get_required_input_frame_count.argtypes = [ctypes.POINTER(struct_ma_resampler), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resampler_get_expected_output_frame_count = _libraries['libminiaudio.so'].ma_resampler_get_expected_output_frame_count
    ma_resampler_get_expected_output_frame_count.restype = ma_result
    ma_resampler_get_expected_output_frame_count.argtypes = [ctypes.POINTER(struct_ma_resampler), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resampler_reset = _libraries['libminiaudio.so'].ma_resampler_reset
    ma_resampler_reset.restype = ma_result
    ma_resampler_reset.argtypes = [ctypes.POINTER(struct_ma_resampler)]
except AttributeError:
    pass

# values for enumeration 'ma_mono_expansion_mode'
ma_mono_expansion_mode__enumvalues = {
    0: 'ma_mono_expansion_mode_duplicate',
    1: 'ma_mono_expansion_mode_average',
    2: 'ma_mono_expansion_mode_stereo_only',
    0: 'ma_mono_expansion_mode_default',
}
ma_mono_expansion_mode_duplicate = 0
ma_mono_expansion_mode_average = 1
ma_mono_expansion_mode_stereo_only = 2
ma_mono_expansion_mode_default = 0
ma_mono_expansion_mode = ctypes.c_uint32 # enum
class struct_ma_channel_converter_config(Structure):
    pass

struct_ma_channel_converter_config._pack_ = 1 # source:False
struct_ma_channel_converter_config._fields_ = [
    ('format', ma_format),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pChannelMapIn', ctypes.POINTER(ctypes.c_ubyte)),
    ('pChannelMapOut', ctypes.POINTER(ctypes.c_ubyte)),
    ('mixingMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('ppWeights', ctypes.POINTER(ctypes.POINTER(ctypes.c_float))),
]

ma_channel_converter_config = struct_ma_channel_converter_config
try:
    ma_channel_converter_config_init = _libraries['libminiaudio.so'].ma_channel_converter_config_init
    ma_channel_converter_config_init.restype = ma_channel_converter_config
    ma_channel_converter_config_init.argtypes = [ma_format, ma_uint32, ctypes.POINTER(ctypes.c_ubyte), ma_uint32, ctypes.POINTER(ctypes.c_ubyte), ma_channel_mix_mode]
except AttributeError:
    pass
try:
    ma_channel_converter_get_heap_size = _libraries['libminiaudio.so'].ma_channel_converter_get_heap_size
    ma_channel_converter_get_heap_size.restype = ma_result
    ma_channel_converter_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_channel_converter_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_channel_converter_init_preallocated = _libraries['libminiaudio.so'].ma_channel_converter_init_preallocated
    ma_channel_converter_init_preallocated.restype = ma_result
    ma_channel_converter_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_channel_converter_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_channel_converter)]
except AttributeError:
    pass
try:
    ma_channel_converter_init = _libraries['libminiaudio.so'].ma_channel_converter_init
    ma_channel_converter_init.restype = ma_result
    ma_channel_converter_init.argtypes = [ctypes.POINTER(struct_ma_channel_converter_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_channel_converter)]
except AttributeError:
    pass
try:
    ma_channel_converter_uninit = _libraries['libminiaudio.so'].ma_channel_converter_uninit
    ma_channel_converter_uninit.restype = None
    ma_channel_converter_uninit.argtypes = [ctypes.POINTER(struct_ma_channel_converter), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_channel_converter_process_pcm_frames = _libraries['libminiaudio.so'].ma_channel_converter_process_pcm_frames
    ma_channel_converter_process_pcm_frames.restype = ma_result
    ma_channel_converter_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_channel_converter), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
size_t = ctypes.c_uint64
try:
    ma_channel_converter_get_input_channel_map = _libraries['libminiaudio.so'].ma_channel_converter_get_input_channel_map
    ma_channel_converter_get_input_channel_map.restype = ma_result
    ma_channel_converter_get_input_channel_map.argtypes = [ctypes.POINTER(struct_ma_channel_converter), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_channel_converter_get_output_channel_map = _libraries['libminiaudio.so'].ma_channel_converter_get_output_channel_map
    ma_channel_converter_get_output_channel_map.restype = ma_result
    ma_channel_converter_get_output_channel_map.argtypes = [ctypes.POINTER(struct_ma_channel_converter), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
class struct_ma_data_converter_config(Structure):
    pass

struct_ma_data_converter_config._pack_ = 1 # source:False
struct_ma_data_converter_config._fields_ = [
    ('formatIn', ma_format),
    ('formatOut', ma_format),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('sampleRateIn', ctypes.c_uint32),
    ('sampleRateOut', ctypes.c_uint32),
    ('pChannelMapIn', ctypes.POINTER(ctypes.c_ubyte)),
    ('pChannelMapOut', ctypes.POINTER(ctypes.c_ubyte)),
    ('ditherMode', ma_dither_mode),
    ('channelMixMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('ppChannelWeights', ctypes.POINTER(ctypes.POINTER(ctypes.c_float))),
    ('allowDynamicSampleRate', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('resampling', ma_resampler_config),
]

ma_data_converter_config = struct_ma_data_converter_config
try:
    ma_data_converter_config_init_default = _libraries['libminiaudio.so'].ma_data_converter_config_init_default
    ma_data_converter_config_init_default.restype = ma_data_converter_config
    ma_data_converter_config_init_default.argtypes = []
except AttributeError:
    pass
try:
    ma_data_converter_config_init = _libraries['libminiaudio.so'].ma_data_converter_config_init
    ma_data_converter_config_init.restype = ma_data_converter_config
    ma_data_converter_config_init.argtypes = [ma_format, ma_format, ma_uint32, ma_uint32, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_data_converter_get_heap_size = _libraries['libminiaudio.so'].ma_data_converter_get_heap_size
    ma_data_converter_get_heap_size.restype = ma_result
    ma_data_converter_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_data_converter_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_converter_init_preallocated = _libraries['libminiaudio.so'].ma_data_converter_init_preallocated
    ma_data_converter_init_preallocated.restype = ma_result
    ma_data_converter_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_data_converter_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_data_converter)]
except AttributeError:
    pass
try:
    ma_data_converter_init = _libraries['libminiaudio.so'].ma_data_converter_init
    ma_data_converter_init.restype = ma_result
    ma_data_converter_init.argtypes = [ctypes.POINTER(struct_ma_data_converter_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_data_converter)]
except AttributeError:
    pass
try:
    ma_data_converter_uninit = _libraries['libminiaudio.so'].ma_data_converter_uninit
    ma_data_converter_uninit.restype = None
    ma_data_converter_uninit.argtypes = [ctypes.POINTER(struct_ma_data_converter), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_data_converter_process_pcm_frames = _libraries['libminiaudio.so'].ma_data_converter_process_pcm_frames
    ma_data_converter_process_pcm_frames.restype = ma_result
    ma_data_converter_process_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_data_converter), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_converter_set_rate = _libraries['libminiaudio.so'].ma_data_converter_set_rate
    ma_data_converter_set_rate.restype = ma_result
    ma_data_converter_set_rate.argtypes = [ctypes.POINTER(struct_ma_data_converter), ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_data_converter_set_rate_ratio = _libraries['libminiaudio.so'].ma_data_converter_set_rate_ratio
    ma_data_converter_set_rate_ratio.restype = ma_result
    ma_data_converter_set_rate_ratio.argtypes = [ctypes.POINTER(struct_ma_data_converter), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_data_converter_get_input_latency = _libraries['libminiaudio.so'].ma_data_converter_get_input_latency
    ma_data_converter_get_input_latency.restype = ma_uint64
    ma_data_converter_get_input_latency.argtypes = [ctypes.POINTER(struct_ma_data_converter)]
except AttributeError:
    pass
try:
    ma_data_converter_get_output_latency = _libraries['libminiaudio.so'].ma_data_converter_get_output_latency
    ma_data_converter_get_output_latency.restype = ma_uint64
    ma_data_converter_get_output_latency.argtypes = [ctypes.POINTER(struct_ma_data_converter)]
except AttributeError:
    pass
try:
    ma_data_converter_get_required_input_frame_count = _libraries['libminiaudio.so'].ma_data_converter_get_required_input_frame_count
    ma_data_converter_get_required_input_frame_count.restype = ma_result
    ma_data_converter_get_required_input_frame_count.argtypes = [ctypes.POINTER(struct_ma_data_converter), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_converter_get_expected_output_frame_count = _libraries['libminiaudio.so'].ma_data_converter_get_expected_output_frame_count
    ma_data_converter_get_expected_output_frame_count.restype = ma_result
    ma_data_converter_get_expected_output_frame_count.argtypes = [ctypes.POINTER(struct_ma_data_converter), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_converter_get_input_channel_map = _libraries['libminiaudio.so'].ma_data_converter_get_input_channel_map
    ma_data_converter_get_input_channel_map.restype = ma_result
    ma_data_converter_get_input_channel_map.argtypes = [ctypes.POINTER(struct_ma_data_converter), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_data_converter_get_output_channel_map = _libraries['libminiaudio.so'].ma_data_converter_get_output_channel_map
    ma_data_converter_get_output_channel_map.restype = ma_result
    ma_data_converter_get_output_channel_map.argtypes = [ctypes.POINTER(struct_ma_data_converter), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_data_converter_reset = _libraries['libminiaudio.so'].ma_data_converter_reset
    ma_data_converter_reset.restype = ma_result
    ma_data_converter_reset.argtypes = [ctypes.POINTER(struct_ma_data_converter)]
except AttributeError:
    pass
try:
    ma_pcm_u8_to_s16 = _libraries['libminiaudio.so'].ma_pcm_u8_to_s16
    ma_pcm_u8_to_s16.restype = None
    ma_pcm_u8_to_s16.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_u8_to_s24 = _libraries['libminiaudio.so'].ma_pcm_u8_to_s24
    ma_pcm_u8_to_s24.restype = None
    ma_pcm_u8_to_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_u8_to_s32 = _libraries['libminiaudio.so'].ma_pcm_u8_to_s32
    ma_pcm_u8_to_s32.restype = None
    ma_pcm_u8_to_s32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_u8_to_f32 = _libraries['libminiaudio.so'].ma_pcm_u8_to_f32
    ma_pcm_u8_to_f32.restype = None
    ma_pcm_u8_to_f32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s16_to_u8 = _libraries['libminiaudio.so'].ma_pcm_s16_to_u8
    ma_pcm_s16_to_u8.restype = None
    ma_pcm_s16_to_u8.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s16_to_s24 = _libraries['libminiaudio.so'].ma_pcm_s16_to_s24
    ma_pcm_s16_to_s24.restype = None
    ma_pcm_s16_to_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s16_to_s32 = _libraries['libminiaudio.so'].ma_pcm_s16_to_s32
    ma_pcm_s16_to_s32.restype = None
    ma_pcm_s16_to_s32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s16_to_f32 = _libraries['libminiaudio.so'].ma_pcm_s16_to_f32
    ma_pcm_s16_to_f32.restype = None
    ma_pcm_s16_to_f32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s24_to_u8 = _libraries['libminiaudio.so'].ma_pcm_s24_to_u8
    ma_pcm_s24_to_u8.restype = None
    ma_pcm_s24_to_u8.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s24_to_s16 = _libraries['libminiaudio.so'].ma_pcm_s24_to_s16
    ma_pcm_s24_to_s16.restype = None
    ma_pcm_s24_to_s16.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s24_to_s32 = _libraries['libminiaudio.so'].ma_pcm_s24_to_s32
    ma_pcm_s24_to_s32.restype = None
    ma_pcm_s24_to_s32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s24_to_f32 = _libraries['libminiaudio.so'].ma_pcm_s24_to_f32
    ma_pcm_s24_to_f32.restype = None
    ma_pcm_s24_to_f32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s32_to_u8 = _libraries['libminiaudio.so'].ma_pcm_s32_to_u8
    ma_pcm_s32_to_u8.restype = None
    ma_pcm_s32_to_u8.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s32_to_s16 = _libraries['libminiaudio.so'].ma_pcm_s32_to_s16
    ma_pcm_s32_to_s16.restype = None
    ma_pcm_s32_to_s16.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s32_to_s24 = _libraries['libminiaudio.so'].ma_pcm_s32_to_s24
    ma_pcm_s32_to_s24.restype = None
    ma_pcm_s32_to_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_s32_to_f32 = _libraries['libminiaudio.so'].ma_pcm_s32_to_f32
    ma_pcm_s32_to_f32.restype = None
    ma_pcm_s32_to_f32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_f32_to_u8 = _libraries['libminiaudio.so'].ma_pcm_f32_to_u8
    ma_pcm_f32_to_u8.restype = None
    ma_pcm_f32_to_u8.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_f32_to_s16 = _libraries['libminiaudio.so'].ma_pcm_f32_to_s16
    ma_pcm_f32_to_s16.restype = None
    ma_pcm_f32_to_s16.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_f32_to_s24 = _libraries['libminiaudio.so'].ma_pcm_f32_to_s24
    ma_pcm_f32_to_s24.restype = None
    ma_pcm_f32_to_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_f32_to_s32 = _libraries['libminiaudio.so'].ma_pcm_f32_to_s32
    ma_pcm_f32_to_s32.restype = None
    ma_pcm_f32_to_s32.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_pcm_convert = _libraries['libminiaudio.so'].ma_pcm_convert
    ma_pcm_convert.restype = None
    ma_pcm_convert.argtypes = [ctypes.POINTER(None), ma_format, ctypes.POINTER(None), ma_format, ma_uint64, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_convert_pcm_frames_format = _libraries['libminiaudio.so'].ma_convert_pcm_frames_format
    ma_convert_pcm_frames_format.restype = None
    ma_convert_pcm_frames_format.argtypes = [ctypes.POINTER(None), ma_format, ctypes.POINTER(None), ma_format, ma_uint64, ma_uint32, ma_dither_mode]
except AttributeError:
    pass
try:
    ma_deinterleave_pcm_frames = _libraries['libminiaudio.so'].ma_deinterleave_pcm_frames
    ma_deinterleave_pcm_frames.restype = None
    ma_deinterleave_pcm_frames.argtypes = [ma_format, ma_uint32, ma_uint64, ctypes.POINTER(None), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_interleave_pcm_frames = _libraries['libminiaudio.so'].ma_interleave_pcm_frames
    ma_interleave_pcm_frames.restype = None
    ma_interleave_pcm_frames.argtypes = [ma_format, ma_uint32, ma_uint64, ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_channel_map_get_channel = _libraries['libminiaudio.so'].ma_channel_map_get_channel
    ma_channel_map_get_channel.restype = ma_channel
    ma_channel_map_get_channel.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_init_blank = _libraries['libminiaudio.so'].ma_channel_map_init_blank
    ma_channel_map_init_blank.restype = None
    ma_channel_map_init_blank.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_init_standard = _libraries['libminiaudio.so'].ma_channel_map_init_standard
    ma_channel_map_init_standard.restype = None
    ma_channel_map_init_standard.argtypes = [ma_standard_channel_map, ctypes.POINTER(ctypes.c_ubyte), size_t, ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_copy = _libraries['libminiaudio.so'].ma_channel_map_copy
    ma_channel_map_copy.restype = None
    ma_channel_map_copy.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_copy_or_default = _libraries['libminiaudio.so'].ma_channel_map_copy_or_default
    ma_channel_map_copy_or_default.restype = None
    ma_channel_map_copy_or_default.argtypes = [ctypes.POINTER(ctypes.c_ubyte), size_t, ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_is_valid = _libraries['libminiaudio.so'].ma_channel_map_is_valid
    ma_channel_map_is_valid.restype = ma_bool32
    ma_channel_map_is_valid.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_is_equal = _libraries['libminiaudio.so'].ma_channel_map_is_equal
    ma_channel_map_is_equal.restype = ma_bool32
    ma_channel_map_is_equal.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_is_blank = _libraries['libminiaudio.so'].ma_channel_map_is_blank
    ma_channel_map_is_blank.restype = ma_bool32
    ma_channel_map_is_blank.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint32]
except AttributeError:
    pass
try:
    ma_channel_map_contains_channel_position = _libraries['libminiaudio.so'].ma_channel_map_contains_channel_position
    ma_channel_map_contains_channel_position.restype = ma_bool32
    ma_channel_map_contains_channel_position.argtypes = [ma_uint32, ctypes.POINTER(ctypes.c_ubyte), ma_channel]
except AttributeError:
    pass
try:
    ma_channel_map_find_channel_position = _libraries['libminiaudio.so'].ma_channel_map_find_channel_position
    ma_channel_map_find_channel_position.restype = ma_bool32
    ma_channel_map_find_channel_position.argtypes = [ma_uint32, ctypes.POINTER(ctypes.c_ubyte), ma_channel, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_channel_map_to_string = _libraries['libminiaudio.so'].ma_channel_map_to_string
    ma_channel_map_to_string.restype = size_t
    ma_channel_map_to_string.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint32, ctypes.POINTER(ctypes.c_char), size_t]
except AttributeError:
    pass
try:
    ma_channel_position_to_string = _libraries['libminiaudio.so'].ma_channel_position_to_string
    ma_channel_position_to_string.restype = ctypes.POINTER(ctypes.c_char)
    ma_channel_position_to_string.argtypes = [ma_channel]
except AttributeError:
    pass
try:
    ma_convert_frames = _libraries['libminiaudio.so'].ma_convert_frames
    ma_convert_frames.restype = ma_uint64
    ma_convert_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ma_uint32, ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_convert_frames_ex = _libraries['libminiaudio.so'].ma_convert_frames_ex
    ma_convert_frames_ex.restype = ma_uint64
    ma_convert_frames_ex.argtypes = [ctypes.POINTER(None), ma_uint64, ctypes.POINTER(None), ma_uint64, ctypes.POINTER(struct_ma_data_converter_config)]
except AttributeError:
    pass
ma_data_source = None
struct_ma_data_source_vtable._pack_ = 1 # source:False
struct_ma_data_source_vtable._fields_ = [
    ('onRead', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onSeek', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.c_uint64)),
    ('onGetDataFormat', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint64)),
    ('onGetCursor', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64))),
    ('onGetLength', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64))),
    ('onSetLooping', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.c_uint32)),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_data_source_vtable = struct_ma_data_source_vtable
ma_data_source_get_next_proc = ctypes.CFUNCTYPE(ctypes.POINTER(None), ctypes.POINTER(None))
class struct_ma_data_source_config(Structure):
    pass

struct_ma_data_source_config._pack_ = 1 # source:False
struct_ma_data_source_config._fields_ = [
    ('vtable', ctypes.POINTER(struct_ma_data_source_vtable)),
]

ma_data_source_config = struct_ma_data_source_config
try:
    ma_data_source_config_init = _libraries['libminiaudio.so'].ma_data_source_config_init
    ma_data_source_config_init.restype = ma_data_source_config
    ma_data_source_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_data_source_init = _libraries['libminiaudio.so'].ma_data_source_init
    ma_data_source_init.restype = ma_result
    ma_data_source_init.argtypes = [ctypes.POINTER(struct_ma_data_source_config), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_uninit = _libraries['libminiaudio.so'].ma_data_source_uninit
    ma_data_source_uninit.restype = None
    ma_data_source_uninit.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_read_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_read_pcm_frames
    ma_data_source_read_pcm_frames.restype = ma_result
    ma_data_source_read_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_seek_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_seek_pcm_frames
    ma_data_source_seek_pcm_frames.restype = ma_result
    ma_data_source_seek_pcm_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_data_source_seek_to_pcm_frame
    ma_data_source_seek_to_pcm_frame.restype = ma_result
    ma_data_source_seek_to_pcm_frame.argtypes = [ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_data_source_seek_seconds = _libraries['libminiaudio.so'].ma_data_source_seek_seconds
    ma_data_source_seek_seconds.restype = ma_result
    ma_data_source_seek_seconds.argtypes = [ctypes.POINTER(None), ctypes.c_float, ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_data_source_seek_to_second = _libraries['libminiaudio.so'].ma_data_source_seek_to_second
    ma_data_source_seek_to_second.restype = ma_result
    ma_data_source_seek_to_second.argtypes = [ctypes.POINTER(None), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_data_source_get_data_format = _libraries['libminiaudio.so'].ma_data_source_get_data_format
    ma_data_source_get_data_format.restype = ma_result
    ma_data_source_get_data_format.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_data_source_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_get_cursor_in_pcm_frames
    ma_data_source_get_cursor_in_pcm_frames.restype = ma_result
    ma_data_source_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_get_length_in_pcm_frames
    ma_data_source_get_length_in_pcm_frames.restype = ma_result
    ma_data_source_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_get_cursor_in_seconds = _libraries['libminiaudio.so'].ma_data_source_get_cursor_in_seconds
    ma_data_source_get_cursor_in_seconds.restype = ma_result
    ma_data_source_get_cursor_in_seconds.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_data_source_get_length_in_seconds = _libraries['libminiaudio.so'].ma_data_source_get_length_in_seconds
    ma_data_source_get_length_in_seconds.restype = ma_result
    ma_data_source_get_length_in_seconds.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_data_source_set_looping = _libraries['libminiaudio.so'].ma_data_source_set_looping
    ma_data_source_set_looping.restype = ma_result
    ma_data_source_set_looping.argtypes = [ctypes.POINTER(None), ma_bool32]
except AttributeError:
    pass
try:
    ma_data_source_is_looping = _libraries['libminiaudio.so'].ma_data_source_is_looping
    ma_data_source_is_looping.restype = ma_bool32
    ma_data_source_is_looping.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_set_range_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_set_range_in_pcm_frames
    ma_data_source_set_range_in_pcm_frames.restype = ma_result
    ma_data_source_set_range_in_pcm_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_data_source_get_range_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_get_range_in_pcm_frames
    ma_data_source_get_range_in_pcm_frames.restype = None
    ma_data_source_get_range_in_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_set_loop_point_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_set_loop_point_in_pcm_frames
    ma_data_source_set_loop_point_in_pcm_frames.restype = ma_result
    ma_data_source_set_loop_point_in_pcm_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_data_source_get_loop_point_in_pcm_frames = _libraries['libminiaudio.so'].ma_data_source_get_loop_point_in_pcm_frames
    ma_data_source_get_loop_point_in_pcm_frames.restype = None
    ma_data_source_get_loop_point_in_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_data_source_set_current = _libraries['libminiaudio.so'].ma_data_source_set_current
    ma_data_source_set_current.restype = ma_result
    ma_data_source_set_current.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_get_current = _libraries['libminiaudio.so'].ma_data_source_get_current
    ma_data_source_get_current.restype = ctypes.POINTER(None)
    ma_data_source_get_current.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_set_next = _libraries['libminiaudio.so'].ma_data_source_set_next
    ma_data_source_set_next.restype = ma_result
    ma_data_source_set_next.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_get_next = _libraries['libminiaudio.so'].ma_data_source_get_next
    ma_data_source_get_next.restype = ctypes.POINTER(None)
    ma_data_source_get_next.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_data_source_set_next_callback = _libraries['libminiaudio.so'].ma_data_source_set_next_callback
    ma_data_source_set_next_callback.restype = ma_result
    ma_data_source_set_next_callback.argtypes = [ctypes.POINTER(None), ma_data_source_get_next_proc]
except AttributeError:
    pass
try:
    ma_data_source_get_next_callback = _libraries['libminiaudio.so'].ma_data_source_get_next_callback
    ma_data_source_get_next_callback.restype = ma_data_source_get_next_proc
    ma_data_source_get_next_callback.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
class struct_ma_audio_buffer_ref(Structure):
    pass

struct_ma_audio_buffer_ref._pack_ = 1 # source:False
struct_ma_audio_buffer_ref._fields_ = [
    ('ds', ma_data_source_base),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('cursor', ctypes.c_uint64),
    ('sizeInFrames', ctypes.c_uint64),
    ('pData', ctypes.POINTER(None)),
]

ma_audio_buffer_ref = struct_ma_audio_buffer_ref
try:
    ma_audio_buffer_ref_init = _libraries['libminiaudio.so'].ma_audio_buffer_ref_init
    ma_audio_buffer_ref_init.restype = ma_result
    ma_audio_buffer_ref_init.argtypes = [ma_format, ma_uint32, ctypes.POINTER(None), ma_uint64, ctypes.POINTER(struct_ma_audio_buffer_ref)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_uninit = _libraries['libminiaudio.so'].ma_audio_buffer_ref_uninit
    ma_audio_buffer_ref_uninit.restype = None
    ma_audio_buffer_ref_uninit.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_set_data = _libraries['libminiaudio.so'].ma_audio_buffer_ref_set_data
    ma_audio_buffer_ref_set_data.restype = ma_result
    ma_audio_buffer_ref_set_data.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_read_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_ref_read_pcm_frames
    ma_audio_buffer_ref_read_pcm_frames.restype = ma_uint64
    ma_audio_buffer_ref_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(None), ma_uint64, ma_bool32]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_audio_buffer_ref_seek_to_pcm_frame
    ma_audio_buffer_ref_seek_to_pcm_frame.restype = ma_result
    ma_audio_buffer_ref_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ma_uint64]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_map = _libraries['libminiaudio.so'].ma_audio_buffer_ref_map
    ma_audio_buffer_ref_map.restype = ma_result
    ma_audio_buffer_ref_map.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_unmap = _libraries['libminiaudio.so'].ma_audio_buffer_ref_unmap
    ma_audio_buffer_ref_unmap.restype = ma_result
    ma_audio_buffer_ref_unmap.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ma_uint64]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_at_end = _libraries['libminiaudio.so'].ma_audio_buffer_ref_at_end
    ma_audio_buffer_ref_at_end.restype = ma_bool32
    ma_audio_buffer_ref_at_end.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_ref_get_cursor_in_pcm_frames
    ma_audio_buffer_ref_get_cursor_in_pcm_frames.restype = ma_result
    ma_audio_buffer_ref_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_ref_get_length_in_pcm_frames
    ma_audio_buffer_ref_get_length_in_pcm_frames.restype = ma_result
    ma_audio_buffer_ref_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_ref_get_available_frames = _libraries['libminiaudio.so'].ma_audio_buffer_ref_get_available_frames
    ma_audio_buffer_ref_get_available_frames.restype = ma_result
    ma_audio_buffer_ref_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_ref), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
class struct_ma_audio_buffer_config(Structure):
    pass

struct_ma_audio_buffer_config._pack_ = 1 # source:False
struct_ma_audio_buffer_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('sizeInFrames', ctypes.c_uint64),
    ('pData', ctypes.POINTER(None)),
    ('allocationCallbacks', ma_allocation_callbacks),
]

ma_audio_buffer_config = struct_ma_audio_buffer_config
try:
    ma_audio_buffer_config_init = _libraries['libminiaudio.so'].ma_audio_buffer_config_init
    ma_audio_buffer_config_init.restype = ma_audio_buffer_config
    ma_audio_buffer_config_init.argtypes = [ma_format, ma_uint32, ma_uint64, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_audio_buffer(Structure):
    pass

struct_ma_audio_buffer._pack_ = 1 # source:False
struct_ma_audio_buffer._fields_ = [
    ('ref', ma_audio_buffer_ref),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('ownsData', ctypes.c_uint32),
    ('_pExtraData', ctypes.c_ubyte * 1),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

ma_audio_buffer = struct_ma_audio_buffer
try:
    ma_audio_buffer_init = _libraries['libminiaudio.so'].ma_audio_buffer_init
    ma_audio_buffer_init.restype = ma_result
    ma_audio_buffer_init.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_config), ctypes.POINTER(struct_ma_audio_buffer)]
except AttributeError:
    pass
try:
    ma_audio_buffer_init_copy = _libraries['libminiaudio.so'].ma_audio_buffer_init_copy
    ma_audio_buffer_init_copy.restype = ma_result
    ma_audio_buffer_init_copy.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_config), ctypes.POINTER(struct_ma_audio_buffer)]
except AttributeError:
    pass
try:
    ma_audio_buffer_alloc_and_init = _libraries['libminiaudio.so'].ma_audio_buffer_alloc_and_init
    ma_audio_buffer_alloc_and_init.restype = ma_result
    ma_audio_buffer_alloc_and_init.argtypes = [ctypes.POINTER(struct_ma_audio_buffer_config), ctypes.POINTER(ctypes.POINTER(struct_ma_audio_buffer))]
except AttributeError:
    pass
try:
    ma_audio_buffer_uninit = _libraries['libminiaudio.so'].ma_audio_buffer_uninit
    ma_audio_buffer_uninit.restype = None
    ma_audio_buffer_uninit.argtypes = [ctypes.POINTER(struct_ma_audio_buffer)]
except AttributeError:
    pass
try:
    ma_audio_buffer_uninit_and_free = _libraries['libminiaudio.so'].ma_audio_buffer_uninit_and_free
    ma_audio_buffer_uninit_and_free.restype = None
    ma_audio_buffer_uninit_and_free.argtypes = [ctypes.POINTER(struct_ma_audio_buffer)]
except AttributeError:
    pass
try:
    ma_audio_buffer_read_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_read_pcm_frames
    ma_audio_buffer_read_pcm_frames.restype = ma_uint64
    ma_audio_buffer_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ctypes.POINTER(None), ma_uint64, ma_bool32]
except AttributeError:
    pass
try:
    ma_audio_buffer_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_audio_buffer_seek_to_pcm_frame
    ma_audio_buffer_seek_to_pcm_frame.restype = ma_result
    ma_audio_buffer_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ma_uint64]
except AttributeError:
    pass
try:
    ma_audio_buffer_map = _libraries['libminiaudio.so'].ma_audio_buffer_map
    ma_audio_buffer_map.restype = ma_result
    ma_audio_buffer_map.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_unmap = _libraries['libminiaudio.so'].ma_audio_buffer_unmap
    ma_audio_buffer_unmap.restype = ma_result
    ma_audio_buffer_unmap.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ma_uint64]
except AttributeError:
    pass
try:
    ma_audio_buffer_at_end = _libraries['libminiaudio.so'].ma_audio_buffer_at_end
    ma_audio_buffer_at_end.restype = ma_bool32
    ma_audio_buffer_at_end.argtypes = [ctypes.POINTER(struct_ma_audio_buffer)]
except AttributeError:
    pass
try:
    ma_audio_buffer_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_get_cursor_in_pcm_frames
    ma_audio_buffer_get_cursor_in_pcm_frames.restype = ma_result
    ma_audio_buffer_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_audio_buffer_get_length_in_pcm_frames
    ma_audio_buffer_get_length_in_pcm_frames.restype = ma_result
    ma_audio_buffer_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_audio_buffer_get_available_frames = _libraries['libminiaudio.so'].ma_audio_buffer_get_available_frames
    ma_audio_buffer_get_available_frames.restype = ma_result
    ma_audio_buffer_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_audio_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
class struct_ma_paged_audio_buffer_page(Structure):
    pass

struct_ma_paged_audio_buffer_page._pack_ = 1 # source:False
struct_ma_paged_audio_buffer_page._fields_ = [
    ('pNext', ctypes.POINTER(struct_ma_paged_audio_buffer_page)),
    ('sizeInFrames', ctypes.c_uint64),
    ('pAudioData', ctypes.c_ubyte * 1),
    ('PADDING_0', ctypes.c_ubyte * 7),
]

ma_paged_audio_buffer_page = struct_ma_paged_audio_buffer_page
class struct_ma_paged_audio_buffer_data(Structure):
    pass

struct_ma_paged_audio_buffer_data._pack_ = 1 # source:False
struct_ma_paged_audio_buffer_data._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('head', ma_paged_audio_buffer_page),
    ('pTail', ctypes.POINTER(struct_ma_paged_audio_buffer_page)),
]

ma_paged_audio_buffer_data = struct_ma_paged_audio_buffer_data
try:
    ma_paged_audio_buffer_data_init = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_init
    ma_paged_audio_buffer_data_init.restype = ma_result
    ma_paged_audio_buffer_data_init.argtypes = [ma_format, ma_uint32, ctypes.POINTER(struct_ma_paged_audio_buffer_data)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_uninit = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_uninit
    ma_paged_audio_buffer_data_uninit.restype = None
    ma_paged_audio_buffer_data_uninit.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_get_head = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_get_head
    ma_paged_audio_buffer_data_get_head.restype = ctypes.POINTER(struct_ma_paged_audio_buffer_page)
    ma_paged_audio_buffer_data_get_head.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_get_tail = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_get_tail
    ma_paged_audio_buffer_data_get_tail.restype = ctypes.POINTER(struct_ma_paged_audio_buffer_page)
    ma_paged_audio_buffer_data_get_tail.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_get_length_in_pcm_frames
    ma_paged_audio_buffer_data_get_length_in_pcm_frames.restype = ma_result
    ma_paged_audio_buffer_data_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_allocate_page = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_allocate_page
    ma_paged_audio_buffer_data_allocate_page.restype = ma_result
    ma_paged_audio_buffer_data_allocate_page.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ma_uint64, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(ctypes.POINTER(struct_ma_paged_audio_buffer_page))]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_free_page = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_free_page
    ma_paged_audio_buffer_data_free_page.restype = ma_result
    ma_paged_audio_buffer_data_free_page.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ctypes.POINTER(struct_ma_paged_audio_buffer_page), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_append_page = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_append_page
    ma_paged_audio_buffer_data_append_page.restype = ma_result
    ma_paged_audio_buffer_data_append_page.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ctypes.POINTER(struct_ma_paged_audio_buffer_page)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_data_allocate_and_append_page = _libraries['libminiaudio.so'].ma_paged_audio_buffer_data_allocate_and_append_page
    ma_paged_audio_buffer_data_allocate_and_append_page.restype = ma_result
    ma_paged_audio_buffer_data_allocate_and_append_page.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data), ma_uint32, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_paged_audio_buffer_config(Structure):
    pass

struct_ma_paged_audio_buffer_config._pack_ = 1 # source:False
struct_ma_paged_audio_buffer_config._fields_ = [
    ('pData', ctypes.POINTER(struct_ma_paged_audio_buffer_data)),
]

ma_paged_audio_buffer_config = struct_ma_paged_audio_buffer_config
try:
    ma_paged_audio_buffer_config_init = _libraries['libminiaudio.so'].ma_paged_audio_buffer_config_init
    ma_paged_audio_buffer_config_init.restype = ma_paged_audio_buffer_config
    ma_paged_audio_buffer_config_init.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_data)]
except AttributeError:
    pass
class struct_ma_paged_audio_buffer(Structure):
    pass

struct_ma_paged_audio_buffer._pack_ = 1 # source:False
struct_ma_paged_audio_buffer._fields_ = [
    ('ds', ma_data_source_base),
    ('pData', ctypes.POINTER(struct_ma_paged_audio_buffer_data)),
    ('pCurrent', ctypes.POINTER(struct_ma_paged_audio_buffer_page)),
    ('relativeCursor', ctypes.c_uint64),
    ('absoluteCursor', ctypes.c_uint64),
]

ma_paged_audio_buffer = struct_ma_paged_audio_buffer
try:
    ma_paged_audio_buffer_init = _libraries['libminiaudio.so'].ma_paged_audio_buffer_init
    ma_paged_audio_buffer_init.restype = ma_result
    ma_paged_audio_buffer_init.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer_config), ctypes.POINTER(struct_ma_paged_audio_buffer)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_uninit = _libraries['libminiaudio.so'].ma_paged_audio_buffer_uninit
    ma_paged_audio_buffer_uninit.restype = None
    ma_paged_audio_buffer_uninit.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_read_pcm_frames = _libraries['libminiaudio.so'].ma_paged_audio_buffer_read_pcm_frames
    ma_paged_audio_buffer_read_pcm_frames.restype = ma_result
    ma_paged_audio_buffer_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_paged_audio_buffer_seek_to_pcm_frame
    ma_paged_audio_buffer_seek_to_pcm_frame.restype = ma_result
    ma_paged_audio_buffer_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer), ma_uint64]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_paged_audio_buffer_get_cursor_in_pcm_frames
    ma_paged_audio_buffer_get_cursor_in_pcm_frames.restype = ma_result
    ma_paged_audio_buffer_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_paged_audio_buffer_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_paged_audio_buffer_get_length_in_pcm_frames
    ma_paged_audio_buffer_get_length_in_pcm_frames.restype = ma_result
    ma_paged_audio_buffer_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_paged_audio_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_rb_init_ex = _libraries['libminiaudio.so'].ma_rb_init_ex
    ma_rb_init_ex.restype = ma_result
    ma_rb_init_ex.argtypes = [size_t, size_t, size_t, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_init = _libraries['libminiaudio.so'].ma_rb_init
    ma_rb_init.restype = ma_result
    ma_rb_init.argtypes = [size_t, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_uninit = _libraries['libminiaudio.so'].ma_rb_uninit
    ma_rb_uninit.restype = None
    ma_rb_uninit.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_reset = _libraries['libminiaudio.so'].ma_rb_reset
    ma_rb_reset.restype = None
    ma_rb_reset.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_acquire_read = _libraries['libminiaudio.so'].ma_rb_acquire_read
    ma_rb_acquire_read.restype = ma_result
    ma_rb_acquire_read.argtypes = [ctypes.POINTER(struct_ma_rb), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_rb_commit_read = _libraries['libminiaudio.so'].ma_rb_commit_read
    ma_rb_commit_read.restype = ma_result
    ma_rb_commit_read.argtypes = [ctypes.POINTER(struct_ma_rb), size_t]
except AttributeError:
    pass
try:
    ma_rb_acquire_write = _libraries['libminiaudio.so'].ma_rb_acquire_write
    ma_rb_acquire_write.restype = ma_result
    ma_rb_acquire_write.argtypes = [ctypes.POINTER(struct_ma_rb), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_rb_commit_write = _libraries['libminiaudio.so'].ma_rb_commit_write
    ma_rb_commit_write.restype = ma_result
    ma_rb_commit_write.argtypes = [ctypes.POINTER(struct_ma_rb), size_t]
except AttributeError:
    pass
try:
    ma_rb_seek_read = _libraries['libminiaudio.so'].ma_rb_seek_read
    ma_rb_seek_read.restype = ma_result
    ma_rb_seek_read.argtypes = [ctypes.POINTER(struct_ma_rb), size_t]
except AttributeError:
    pass
try:
    ma_rb_seek_write = _libraries['libminiaudio.so'].ma_rb_seek_write
    ma_rb_seek_write.restype = ma_result
    ma_rb_seek_write.argtypes = [ctypes.POINTER(struct_ma_rb), size_t]
except AttributeError:
    pass
try:
    ma_rb_pointer_distance = _libraries['libminiaudio.so'].ma_rb_pointer_distance
    ma_rb_pointer_distance.restype = ma_int32
    ma_rb_pointer_distance.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_available_read = _libraries['libminiaudio.so'].ma_rb_available_read
    ma_rb_available_read.restype = ma_uint32
    ma_rb_available_read.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_available_write = _libraries['libminiaudio.so'].ma_rb_available_write
    ma_rb_available_write.restype = ma_uint32
    ma_rb_available_write.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_get_subbuffer_size = _libraries['libminiaudio.so'].ma_rb_get_subbuffer_size
    ma_rb_get_subbuffer_size.restype = size_t
    ma_rb_get_subbuffer_size.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_get_subbuffer_stride = _libraries['libminiaudio.so'].ma_rb_get_subbuffer_stride
    ma_rb_get_subbuffer_stride.restype = size_t
    ma_rb_get_subbuffer_stride.argtypes = [ctypes.POINTER(struct_ma_rb)]
except AttributeError:
    pass
try:
    ma_rb_get_subbuffer_offset = _libraries['libminiaudio.so'].ma_rb_get_subbuffer_offset
    ma_rb_get_subbuffer_offset.restype = size_t
    ma_rb_get_subbuffer_offset.argtypes = [ctypes.POINTER(struct_ma_rb), size_t]
except AttributeError:
    pass
try:
    ma_rb_get_subbuffer_ptr = _libraries['libminiaudio.so'].ma_rb_get_subbuffer_ptr
    ma_rb_get_subbuffer_ptr.restype = ctypes.POINTER(None)
    ma_rb_get_subbuffer_ptr.argtypes = [ctypes.POINTER(struct_ma_rb), size_t, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_pcm_rb_init_ex = _libraries['libminiaudio.so'].ma_pcm_rb_init_ex
    ma_pcm_rb_init_ex.restype = ma_result
    ma_pcm_rb_init_ex.argtypes = [ma_format, ma_uint32, ma_uint32, ma_uint32, ma_uint32, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_init = _libraries['libminiaudio.so'].ma_pcm_rb_init
    ma_pcm_rb_init.restype = ma_result
    ma_pcm_rb_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_uninit = _libraries['libminiaudio.so'].ma_pcm_rb_uninit
    ma_pcm_rb_uninit.restype = None
    ma_pcm_rb_uninit.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_reset = _libraries['libminiaudio.so'].ma_pcm_rb_reset
    ma_pcm_rb_reset.restype = None
    ma_pcm_rb_reset.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_acquire_read = _libraries['libminiaudio.so'].ma_pcm_rb_acquire_read
    ma_pcm_rb_acquire_read.restype = ma_result
    ma_pcm_rb_acquire_read.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_pcm_rb_commit_read = _libraries['libminiaudio.so'].ma_pcm_rb_commit_read
    ma_pcm_rb_commit_read.restype = ma_result
    ma_pcm_rb_commit_read.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_pcm_rb_acquire_write = _libraries['libminiaudio.so'].ma_pcm_rb_acquire_write
    ma_pcm_rb_acquire_write.restype = ma_result
    ma_pcm_rb_acquire_write.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_pcm_rb_commit_write = _libraries['libminiaudio.so'].ma_pcm_rb_commit_write
    ma_pcm_rb_commit_write.restype = ma_result
    ma_pcm_rb_commit_write.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_pcm_rb_seek_read = _libraries['libminiaudio.so'].ma_pcm_rb_seek_read
    ma_pcm_rb_seek_read.restype = ma_result
    ma_pcm_rb_seek_read.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_pcm_rb_seek_write = _libraries['libminiaudio.so'].ma_pcm_rb_seek_write
    ma_pcm_rb_seek_write.restype = ma_result
    ma_pcm_rb_seek_write.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_pcm_rb_pointer_distance = _libraries['libminiaudio.so'].ma_pcm_rb_pointer_distance
    ma_pcm_rb_pointer_distance.restype = ma_int32
    ma_pcm_rb_pointer_distance.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_available_read = _libraries['libminiaudio.so'].ma_pcm_rb_available_read
    ma_pcm_rb_available_read.restype = ma_uint32
    ma_pcm_rb_available_read.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_available_write = _libraries['libminiaudio.so'].ma_pcm_rb_available_write
    ma_pcm_rb_available_write.restype = ma_uint32
    ma_pcm_rb_available_write.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_subbuffer_size = _libraries['libminiaudio.so'].ma_pcm_rb_get_subbuffer_size
    ma_pcm_rb_get_subbuffer_size.restype = ma_uint32
    ma_pcm_rb_get_subbuffer_size.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_subbuffer_stride = _libraries['libminiaudio.so'].ma_pcm_rb_get_subbuffer_stride
    ma_pcm_rb_get_subbuffer_stride.restype = ma_uint32
    ma_pcm_rb_get_subbuffer_stride.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_subbuffer_offset = _libraries['libminiaudio.so'].ma_pcm_rb_get_subbuffer_offset
    ma_pcm_rb_get_subbuffer_offset.restype = ma_uint32
    ma_pcm_rb_get_subbuffer_offset.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_subbuffer_ptr = _libraries['libminiaudio.so'].ma_pcm_rb_get_subbuffer_ptr
    ma_pcm_rb_get_subbuffer_ptr.restype = ctypes.POINTER(None)
    ma_pcm_rb_get_subbuffer_ptr.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_format = _libraries['libminiaudio.so'].ma_pcm_rb_get_format
    ma_pcm_rb_get_format.restype = ma_format
    ma_pcm_rb_get_format.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_channels = _libraries['libminiaudio.so'].ma_pcm_rb_get_channels
    ma_pcm_rb_get_channels.restype = ma_uint32
    ma_pcm_rb_get_channels.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_get_sample_rate = _libraries['libminiaudio.so'].ma_pcm_rb_get_sample_rate
    ma_pcm_rb_get_sample_rate.restype = ma_uint32
    ma_pcm_rb_get_sample_rate.argtypes = [ctypes.POINTER(struct_ma_pcm_rb)]
except AttributeError:
    pass
try:
    ma_pcm_rb_set_sample_rate = _libraries['libminiaudio.so'].ma_pcm_rb_set_sample_rate
    ma_pcm_rb_set_sample_rate.restype = None
    ma_pcm_rb_set_sample_rate.argtypes = [ctypes.POINTER(struct_ma_pcm_rb), ma_uint32]
except AttributeError:
    pass
try:
    ma_duplex_rb_init = _libraries['libminiaudio.so'].ma_duplex_rb_init
    ma_duplex_rb_init.restype = ma_result
    ma_duplex_rb_init.argtypes = [ma_format, ma_uint32, ma_uint32, ma_uint32, ma_uint32, ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_duplex_rb)]
except AttributeError:
    pass
try:
    ma_duplex_rb_uninit = _libraries['libminiaudio.so'].ma_duplex_rb_uninit
    ma_duplex_rb_uninit.restype = ma_result
    ma_duplex_rb_uninit.argtypes = [ctypes.POINTER(struct_ma_duplex_rb)]
except AttributeError:
    pass
try:
    ma_result_description = _libraries['libminiaudio.so'].ma_result_description
    ma_result_description.restype = ctypes.POINTER(ctypes.c_char)
    ma_result_description.argtypes = [ma_result]
except AttributeError:
    pass
try:
    ma_malloc = _libraries['libminiaudio.so'].ma_malloc
    ma_malloc.restype = ctypes.POINTER(None)
    ma_malloc.argtypes = [size_t, ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_calloc = _libraries['libminiaudio.so'].ma_calloc
    ma_calloc.restype = ctypes.POINTER(None)
    ma_calloc.argtypes = [size_t, ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_realloc = _libraries['libminiaudio.so'].ma_realloc
    ma_realloc.restype = ctypes.POINTER(None)
    ma_realloc.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_free = _libraries['libminiaudio.so'].ma_free
    ma_free.restype = None
    ma_free.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_aligned_malloc = _libraries['libminiaudio.so'].ma_aligned_malloc
    ma_aligned_malloc.restype = ctypes.POINTER(None)
    ma_aligned_malloc.argtypes = [size_t, size_t, ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_aligned_free = _libraries['libminiaudio.so'].ma_aligned_free
    ma_aligned_free.restype = None
    ma_aligned_free.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_get_format_name = _libraries['libminiaudio.so'].ma_get_format_name
    ma_get_format_name.restype = ctypes.POINTER(ctypes.c_char)
    ma_get_format_name.argtypes = [ma_format]
except AttributeError:
    pass
try:
    ma_blend_f32 = _libraries['libminiaudio.so'].ma_blend_f32
    ma_blend_f32.restype = None
    ma_blend_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_float, ma_uint32]
except AttributeError:
    pass
try:
    ma_get_bytes_per_sample = _libraries['libminiaudio.so'].ma_get_bytes_per_sample
    ma_get_bytes_per_sample.restype = ma_uint32
    ma_get_bytes_per_sample.argtypes = [ma_format]
except AttributeError:
    pass
try:
    ma_get_bytes_per_frame = _libraries['FIXME_STUB'].ma_get_bytes_per_frame
    ma_get_bytes_per_frame.restype = ma_uint32
    ma_get_bytes_per_frame.argtypes = [ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_log_level_to_string = _libraries['libminiaudio.so'].ma_log_level_to_string
    ma_log_level_to_string.restype = ctypes.POINTER(ctypes.c_char)
    ma_log_level_to_string.argtypes = [ma_uint32]
except AttributeError:
    pass
try:
    ma_spinlock_lock = _libraries['libminiaudio.so'].ma_spinlock_lock
    ma_spinlock_lock.restype = ma_result
    ma_spinlock_lock.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_spinlock_lock_noyield = _libraries['libminiaudio.so'].ma_spinlock_lock_noyield
    ma_spinlock_lock_noyield.restype = ma_result
    ma_spinlock_lock_noyield.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_spinlock_unlock = _libraries['libminiaudio.so'].ma_spinlock_unlock
    ma_spinlock_unlock.restype = ma_result
    ma_spinlock_unlock.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_mutex_init = _libraries['libminiaudio.so'].ma_mutex_init
    ma_mutex_init.restype = ma_result
    ma_mutex_init.argtypes = [ctypes.POINTER(union_pthread_mutex_t)]
except AttributeError:
    pass
try:
    ma_mutex_uninit = _libraries['libminiaudio.so'].ma_mutex_uninit
    ma_mutex_uninit.restype = None
    ma_mutex_uninit.argtypes = [ctypes.POINTER(union_pthread_mutex_t)]
except AttributeError:
    pass
try:
    ma_mutex_lock = _libraries['libminiaudio.so'].ma_mutex_lock
    ma_mutex_lock.restype = None
    ma_mutex_lock.argtypes = [ctypes.POINTER(union_pthread_mutex_t)]
except AttributeError:
    pass
try:
    ma_mutex_unlock = _libraries['libminiaudio.so'].ma_mutex_unlock
    ma_mutex_unlock.restype = None
    ma_mutex_unlock.argtypes = [ctypes.POINTER(union_pthread_mutex_t)]
except AttributeError:
    pass
try:
    ma_event_init = _libraries['libminiaudio.so'].ma_event_init
    ma_event_init.restype = ma_result
    ma_event_init.argtypes = [ctypes.POINTER(struct_ma_event)]
except AttributeError:
    pass
try:
    ma_event_uninit = _libraries['libminiaudio.so'].ma_event_uninit
    ma_event_uninit.restype = None
    ma_event_uninit.argtypes = [ctypes.POINTER(struct_ma_event)]
except AttributeError:
    pass
try:
    ma_event_wait = _libraries['libminiaudio.so'].ma_event_wait
    ma_event_wait.restype = ma_result
    ma_event_wait.argtypes = [ctypes.POINTER(struct_ma_event)]
except AttributeError:
    pass
try:
    ma_event_signal = _libraries['libminiaudio.so'].ma_event_signal
    ma_event_signal.restype = ma_result
    ma_event_signal.argtypes = [ctypes.POINTER(struct_ma_event)]
except AttributeError:
    pass
try:
    ma_semaphore_init = _libraries['libminiaudio.so'].ma_semaphore_init
    ma_semaphore_init.restype = ma_result
    ma_semaphore_init.argtypes = [ctypes.c_int32, ctypes.POINTER(struct_ma_semaphore)]
except AttributeError:
    pass
try:
    ma_semaphore_uninit = _libraries['libminiaudio.so'].ma_semaphore_uninit
    ma_semaphore_uninit.restype = None
    ma_semaphore_uninit.argtypes = [ctypes.POINTER(struct_ma_semaphore)]
except AttributeError:
    pass
try:
    ma_semaphore_wait = _libraries['libminiaudio.so'].ma_semaphore_wait
    ma_semaphore_wait.restype = ma_result
    ma_semaphore_wait.argtypes = [ctypes.POINTER(struct_ma_semaphore)]
except AttributeError:
    pass
try:
    ma_semaphore_release = _libraries['libminiaudio.so'].ma_semaphore_release
    ma_semaphore_release.restype = ma_result
    ma_semaphore_release.argtypes = [ctypes.POINTER(struct_ma_semaphore)]
except AttributeError:
    pass
class struct_ma_fence(Structure):
    pass

struct_ma_fence._pack_ = 1 # source:False
struct_ma_fence._fields_ = [
    ('e', ma_event),
    ('counter', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_fence = struct_ma_fence
try:
    ma_fence_init = _libraries['libminiaudio.so'].ma_fence_init
    ma_fence_init.restype = ma_result
    ma_fence_init.argtypes = [ctypes.POINTER(struct_ma_fence)]
except AttributeError:
    pass
try:
    ma_fence_uninit = _libraries['libminiaudio.so'].ma_fence_uninit
    ma_fence_uninit.restype = None
    ma_fence_uninit.argtypes = [ctypes.POINTER(struct_ma_fence)]
except AttributeError:
    pass
try:
    ma_fence_acquire = _libraries['libminiaudio.so'].ma_fence_acquire
    ma_fence_acquire.restype = ma_result
    ma_fence_acquire.argtypes = [ctypes.POINTER(struct_ma_fence)]
except AttributeError:
    pass
try:
    ma_fence_release = _libraries['libminiaudio.so'].ma_fence_release
    ma_fence_release.restype = ma_result
    ma_fence_release.argtypes = [ctypes.POINTER(struct_ma_fence)]
except AttributeError:
    pass
try:
    ma_fence_wait = _libraries['libminiaudio.so'].ma_fence_wait
    ma_fence_wait.restype = ma_result
    ma_fence_wait.argtypes = [ctypes.POINTER(struct_ma_fence)]
except AttributeError:
    pass
ma_async_notification = None
class struct_ma_async_notification_callbacks(Structure):
    pass

struct_ma_async_notification_callbacks._pack_ = 1 # source:False
struct_ma_async_notification_callbacks._fields_ = [
    ('onSignal', ctypes.CFUNCTYPE(None, ctypes.POINTER(None))),
]

ma_async_notification_callbacks = struct_ma_async_notification_callbacks
try:
    ma_async_notification_signal = _libraries['libminiaudio.so'].ma_async_notification_signal
    ma_async_notification_signal.restype = ma_result
    ma_async_notification_signal.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
class struct_ma_async_notification_poll(Structure):
    pass

struct_ma_async_notification_poll._pack_ = 1 # source:False
struct_ma_async_notification_poll._fields_ = [
    ('cb', ma_async_notification_callbacks),
    ('signalled', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_async_notification_poll = struct_ma_async_notification_poll
try:
    ma_async_notification_poll_init = _libraries['libminiaudio.so'].ma_async_notification_poll_init
    ma_async_notification_poll_init.restype = ma_result
    ma_async_notification_poll_init.argtypes = [ctypes.POINTER(struct_ma_async_notification_poll)]
except AttributeError:
    pass
try:
    ma_async_notification_poll_is_signalled = _libraries['libminiaudio.so'].ma_async_notification_poll_is_signalled
    ma_async_notification_poll_is_signalled.restype = ma_bool32
    ma_async_notification_poll_is_signalled.argtypes = [ctypes.POINTER(struct_ma_async_notification_poll)]
except AttributeError:
    pass
class struct_ma_async_notification_event(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('cb', ma_async_notification_callbacks),
    ('e', ma_event),
     ]

ma_async_notification_event = struct_ma_async_notification_event
try:
    ma_async_notification_event_init = _libraries['libminiaudio.so'].ma_async_notification_event_init
    ma_async_notification_event_init.restype = ma_result
    ma_async_notification_event_init.argtypes = [ctypes.POINTER(struct_ma_async_notification_event)]
except AttributeError:
    pass
try:
    ma_async_notification_event_uninit = _libraries['libminiaudio.so'].ma_async_notification_event_uninit
    ma_async_notification_event_uninit.restype = ma_result
    ma_async_notification_event_uninit.argtypes = [ctypes.POINTER(struct_ma_async_notification_event)]
except AttributeError:
    pass
try:
    ma_async_notification_event_wait = _libraries['libminiaudio.so'].ma_async_notification_event_wait
    ma_async_notification_event_wait.restype = ma_result
    ma_async_notification_event_wait.argtypes = [ctypes.POINTER(struct_ma_async_notification_event)]
except AttributeError:
    pass
try:
    ma_async_notification_event_signal = _libraries['libminiaudio.so'].ma_async_notification_event_signal
    ma_async_notification_event_signal.restype = ma_result
    ma_async_notification_event_signal.argtypes = [ctypes.POINTER(struct_ma_async_notification_event)]
except AttributeError:
    pass
class struct_ma_slot_allocator_config(Structure):
    pass

struct_ma_slot_allocator_config._pack_ = 1 # source:False
struct_ma_slot_allocator_config._fields_ = [
    ('capacity', ctypes.c_uint32),
]

ma_slot_allocator_config = struct_ma_slot_allocator_config
try:
    ma_slot_allocator_config_init = _libraries['libminiaudio.so'].ma_slot_allocator_config_init
    ma_slot_allocator_config_init.restype = ma_slot_allocator_config
    ma_slot_allocator_config_init.argtypes = [ma_uint32]
except AttributeError:
    pass
class struct_ma_slot_allocator_group(Structure):
    pass

struct_ma_slot_allocator_group._pack_ = 1 # source:False
struct_ma_slot_allocator_group._fields_ = [
    ('bitfield', ctypes.c_uint32),
]

ma_slot_allocator_group = struct_ma_slot_allocator_group
class struct_ma_slot_allocator(Structure):
    pass

struct_ma_slot_allocator._pack_ = 1 # source:False
struct_ma_slot_allocator._fields_ = [
    ('pGroups', ctypes.POINTER(struct_ma_slot_allocator_group)),
    ('pSlots', ctypes.POINTER(ctypes.c_uint32)),
    ('count', ctypes.c_uint32),
    ('capacity', ctypes.c_uint32),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('_pHeap', ctypes.POINTER(None)),
]

ma_slot_allocator = struct_ma_slot_allocator
try:
    ma_slot_allocator_get_heap_size = _libraries['libminiaudio.so'].ma_slot_allocator_get_heap_size
    ma_slot_allocator_get_heap_size.restype = ma_result
    ma_slot_allocator_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_slot_allocator_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_slot_allocator_init_preallocated = _libraries['libminiaudio.so'].ma_slot_allocator_init_preallocated
    ma_slot_allocator_init_preallocated.restype = ma_result
    ma_slot_allocator_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_slot_allocator_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_slot_allocator)]
except AttributeError:
    pass
try:
    ma_slot_allocator_init = _libraries['libminiaudio.so'].ma_slot_allocator_init
    ma_slot_allocator_init.restype = ma_result
    ma_slot_allocator_init.argtypes = [ctypes.POINTER(struct_ma_slot_allocator_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_slot_allocator)]
except AttributeError:
    pass
try:
    ma_slot_allocator_uninit = _libraries['libminiaudio.so'].ma_slot_allocator_uninit
    ma_slot_allocator_uninit.restype = None
    ma_slot_allocator_uninit.argtypes = [ctypes.POINTER(struct_ma_slot_allocator), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_slot_allocator_alloc = _libraries['libminiaudio.so'].ma_slot_allocator_alloc
    ma_slot_allocator_alloc.restype = ma_result
    ma_slot_allocator_alloc.argtypes = [ctypes.POINTER(struct_ma_slot_allocator), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_slot_allocator_free = _libraries['libminiaudio.so'].ma_slot_allocator_free
    ma_slot_allocator_free.restype = ma_result
    ma_slot_allocator_free.argtypes = [ctypes.POINTER(struct_ma_slot_allocator), ma_uint64]
except AttributeError:
    pass
class struct_ma_job(Structure):
    pass

class union_ma_job_toc(Union):
    pass

class struct_ma_job_0_breakup(Structure):
    pass

struct_ma_job_0_breakup._pack_ = 1 # source:False
struct_ma_job_0_breakup._fields_ = [
    ('code', ctypes.c_uint16),
    ('slot', ctypes.c_uint16),
    ('refcount', ctypes.c_uint32),
]

union_ma_job_toc._pack_ = 1 # source:False
union_ma_job_toc._fields_ = [
    ('breakup', struct_ma_job_0_breakup),
    ('allocation', ctypes.c_uint64),
]

class union_ma_job_data(Union):
    pass

class struct_ma_job_1_custom(Structure):
    pass

struct_ma_job_1_custom._pack_ = 1 # source:False
struct_ma_job_1_custom._fields_ = [
    ('proc', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_job))),
    ('data0', ctypes.c_uint64),
    ('data1', ctypes.c_uint64),
]

class union_ma_job_1_resourceManager(Union):
    pass

class struct_ma_job_1_1_loadDataBufferNode(Structure):
    pass

struct_ma_job_1_1_loadDataBufferNode._pack_ = 1 # source:False
struct_ma_job_1_1_loadDataBufferNode._fields_ = [
    ('pResourceManager', ctypes.POINTER(None)),
    ('pDataBufferNode', ctypes.POINTER(None)),
    ('pFilePath', ctypes.POINTER(ctypes.c_char)),
    ('pFilePathW', ctypes.POINTER(ctypes.c_int32)),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pInitNotification', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pInitFence', ctypes.POINTER(struct_ma_fence)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_freeDataBufferNode(Structure):
    pass

struct_ma_job_1_1_freeDataBufferNode._pack_ = 1 # source:False
struct_ma_job_1_1_freeDataBufferNode._fields_ = [
    ('pResourceManager', ctypes.POINTER(None)),
    ('pDataBufferNode', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_pageDataBufferNode(Structure):
    pass

struct_ma_job_1_1_pageDataBufferNode._pack_ = 1 # source:False
struct_ma_job_1_1_pageDataBufferNode._fields_ = [
    ('pResourceManager', ctypes.POINTER(None)),
    ('pDataBufferNode', ctypes.POINTER(None)),
    ('pDecoder', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_loadDataBuffer(Structure):
    pass

struct_ma_job_1_1_loadDataBuffer._pack_ = 1 # source:False
struct_ma_job_1_1_loadDataBuffer._fields_ = [
    ('pDataBuffer', ctypes.POINTER(None)),
    ('pInitNotification', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pInitFence', ctypes.POINTER(struct_ma_fence)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
    ('rangeBegInPCMFrames', ctypes.c_uint64),
    ('rangeEndInPCMFrames', ctypes.c_uint64),
    ('loopPointBegInPCMFrames', ctypes.c_uint64),
    ('loopPointEndInPCMFrames', ctypes.c_uint64),
    ('isLooping', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_job_1_1_freeDataBuffer(Structure):
    pass

struct_ma_job_1_1_freeDataBuffer._pack_ = 1 # source:False
struct_ma_job_1_1_freeDataBuffer._fields_ = [
    ('pDataBuffer', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_loadDataStream(Structure):
    pass

struct_ma_job_1_1_loadDataStream._pack_ = 1 # source:False
struct_ma_job_1_1_loadDataStream._fields_ = [
    ('pDataStream', ctypes.POINTER(None)),
    ('pFilePath', ctypes.POINTER(ctypes.c_char)),
    ('pFilePathW', ctypes.POINTER(ctypes.c_int32)),
    ('initialSeekPoint', ctypes.c_uint64),
    ('pInitNotification', ctypes.POINTER(None)),
    ('pInitFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_freeDataStream(Structure):
    pass

struct_ma_job_1_1_freeDataStream._pack_ = 1 # source:False
struct_ma_job_1_1_freeDataStream._fields_ = [
    ('pDataStream', ctypes.POINTER(None)),
    ('pDoneNotification', ctypes.POINTER(None)),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
]

class struct_ma_job_1_1_pageDataStream(Structure):
    pass

struct_ma_job_1_1_pageDataStream._pack_ = 1 # source:False
struct_ma_job_1_1_pageDataStream._fields_ = [
    ('pDataStream', ctypes.POINTER(None)),
    ('pageIndex', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_job_1_1_seekDataStream(Structure):
    pass

struct_ma_job_1_1_seekDataStream._pack_ = 1 # source:False
struct_ma_job_1_1_seekDataStream._fields_ = [
    ('pDataStream', ctypes.POINTER(None)),
    ('frameIndex', ctypes.c_uint64),
]

union_ma_job_1_resourceManager._pack_ = 1 # source:False
union_ma_job_1_resourceManager._fields_ = [
    ('loadDataBufferNode', struct_ma_job_1_1_loadDataBufferNode),
    ('freeDataBufferNode', struct_ma_job_1_1_freeDataBufferNode),
    ('pageDataBufferNode', struct_ma_job_1_1_pageDataBufferNode),
    ('loadDataBuffer', struct_ma_job_1_1_loadDataBuffer),
    ('freeDataBuffer', struct_ma_job_1_1_freeDataBuffer),
    ('loadDataStream', struct_ma_job_1_1_loadDataStream),
    ('freeDataStream', struct_ma_job_1_1_freeDataStream),
    ('pageDataStream', struct_ma_job_1_1_pageDataStream),
    ('seekDataStream', struct_ma_job_1_1_seekDataStream),
    ('PADDING_0', ctypes.c_ubyte * 64),
]

class union_ma_job_1_device(Union):
    pass

class union_ma_job_1_2_aaudio(Union):
    pass

class struct_ma_job_1_2_0_reroute(Structure):
    pass

struct_ma_job_1_2_0_reroute._pack_ = 1 # source:False
struct_ma_job_1_2_0_reroute._fields_ = [
    ('pDevice', ctypes.POINTER(None)),
    ('deviceType', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

union_ma_job_1_2_aaudio._pack_ = 1 # source:False
union_ma_job_1_2_aaudio._fields_ = [
    ('reroute', struct_ma_job_1_2_0_reroute),
]

union_ma_job_1_device._pack_ = 1 # source:False
union_ma_job_1_device._fields_ = [
    ('aaudio', union_ma_job_1_2_aaudio),
]

union_ma_job_data._pack_ = 1 # source:False
union_ma_job_data._fields_ = [
    ('custom', struct_ma_job_1_custom),
    ('resourceManager', union_ma_job_1_resourceManager),
    ('device', union_ma_job_1_device),
    ('PADDING_0', ctypes.c_ubyte * 64),
]

struct_ma_job._pack_ = 1 # source:False
struct_ma_job._fields_ = [
    ('toc', union_ma_job_toc),
    ('next', ctypes.c_uint64),
    ('order', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('data', union_ma_job_data),
]

ma_job = struct_ma_job
ma_job_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_job))

# values for enumeration 'ma_job_type'
ma_job_type__enumvalues = {
    0: 'MA_JOB_TYPE_QUIT',
    1: 'MA_JOB_TYPE_CUSTOM',
    2: 'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER_NODE',
    3: 'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER_NODE',
    4: 'MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_BUFFER_NODE',
    5: 'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER',
    6: 'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER',
    7: 'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_STREAM',
    8: 'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_STREAM',
    9: 'MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_STREAM',
    10: 'MA_JOB_TYPE_RESOURCE_MANAGER_SEEK_DATA_STREAM',
    11: 'MA_JOB_TYPE_DEVICE_AAUDIO_REROUTE',
    12: 'MA_JOB_TYPE_COUNT',
}
MA_JOB_TYPE_QUIT = 0
MA_JOB_TYPE_CUSTOM = 1
MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER_NODE = 2
MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER_NODE = 3
MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_BUFFER_NODE = 4
MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER = 5
MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER = 6
MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_STREAM = 7
MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_STREAM = 8
MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_STREAM = 9
MA_JOB_TYPE_RESOURCE_MANAGER_SEEK_DATA_STREAM = 10
MA_JOB_TYPE_DEVICE_AAUDIO_REROUTE = 11
MA_JOB_TYPE_COUNT = 12
ma_job_type = ctypes.c_uint32 # enum
try:
    ma_job_init = _libraries['libminiaudio.so'].ma_job_init
    ma_job_init.restype = ma_job
    ma_job_init.argtypes = [ma_uint16]
except AttributeError:
    pass
try:
    ma_job_process = _libraries['libminiaudio.so'].ma_job_process
    ma_job_process.restype = ma_result
    ma_job_process.argtypes = [ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass

# values for enumeration 'ma_job_queue_flags'
ma_job_queue_flags__enumvalues = {
    1: 'MA_JOB_QUEUE_FLAG_NON_BLOCKING',
}
MA_JOB_QUEUE_FLAG_NON_BLOCKING = 1
ma_job_queue_flags = ctypes.c_uint32 # enum
class struct_ma_job_queue_config(Structure):
    pass

struct_ma_job_queue_config._pack_ = 1 # source:False
struct_ma_job_queue_config._fields_ = [
    ('flags', ctypes.c_uint32),
    ('capacity', ctypes.c_uint32),
]

ma_job_queue_config = struct_ma_job_queue_config
try:
    ma_job_queue_config_init = _libraries['libminiaudio.so'].ma_job_queue_config_init
    ma_job_queue_config_init.restype = ma_job_queue_config
    ma_job_queue_config_init.argtypes = [ma_uint32, ma_uint32]
except AttributeError:
    pass
class struct_ma_job_queue(Structure):
    pass

struct_ma_job_queue._pack_ = 1 # source:False
struct_ma_job_queue._fields_ = [
    ('flags', ctypes.c_uint32),
    ('capacity', ctypes.c_uint32),
    ('head', ctypes.c_uint64),
    ('tail', ctypes.c_uint64),
    ('sem', ma_semaphore),
    ('allocator', ma_slot_allocator),
    ('pJobs', ctypes.POINTER(struct_ma_job)),
    ('lock', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_job_queue = struct_ma_job_queue
try:
    ma_job_queue_get_heap_size = _libraries['libminiaudio.so'].ma_job_queue_get_heap_size
    ma_job_queue_get_heap_size.restype = ma_result
    ma_job_queue_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_job_queue_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_job_queue_init_preallocated = _libraries['libminiaudio.so'].ma_job_queue_init_preallocated
    ma_job_queue_init_preallocated.restype = ma_result
    ma_job_queue_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_job_queue_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_job_queue)]
except AttributeError:
    pass
try:
    ma_job_queue_init = _libraries['libminiaudio.so'].ma_job_queue_init
    ma_job_queue_init.restype = ma_result
    ma_job_queue_init.argtypes = [ctypes.POINTER(struct_ma_job_queue_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_job_queue)]
except AttributeError:
    pass
try:
    ma_job_queue_uninit = _libraries['libminiaudio.so'].ma_job_queue_uninit
    ma_job_queue_uninit.restype = None
    ma_job_queue_uninit.argtypes = [ctypes.POINTER(struct_ma_job_queue), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_job_queue_post = _libraries['libminiaudio.so'].ma_job_queue_post
    ma_job_queue_post.restype = ma_result
    ma_job_queue_post.argtypes = [ctypes.POINTER(struct_ma_job_queue), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
try:
    ma_job_queue_next = _libraries['libminiaudio.so'].ma_job_queue_next
    ma_job_queue_next.restype = ma_result
    ma_job_queue_next.argtypes = [ctypes.POINTER(struct_ma_job_queue), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
class struct_ma_device_job_thread_config(Structure):
    pass

struct_ma_device_job_thread_config._pack_ = 1 # source:False
struct_ma_device_job_thread_config._fields_ = [
    ('noThread', ctypes.c_uint32),
    ('jobQueueCapacity', ctypes.c_uint32),
    ('jobQueueFlags', ctypes.c_uint32),
]

ma_device_job_thread_config = struct_ma_device_job_thread_config
try:
    ma_device_job_thread_config_init = _libraries['libminiaudio.so'].ma_device_job_thread_config_init
    ma_device_job_thread_config_init.restype = ma_device_job_thread_config
    ma_device_job_thread_config_init.argtypes = []
except AttributeError:
    pass
class struct_ma_device_job_thread(Structure):
    pass

struct_ma_device_job_thread._pack_ = 1 # source:False
struct_ma_device_job_thread._fields_ = [
    ('thread', ctypes.c_uint64),
    ('jobQueue', ma_job_queue),
    ('_hasThread', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_device_job_thread = struct_ma_device_job_thread
try:
    ma_device_job_thread_init = _libraries['libminiaudio.so'].ma_device_job_thread_init
    ma_device_job_thread_init.restype = ma_result
    ma_device_job_thread_init.argtypes = [ctypes.POINTER(struct_ma_device_job_thread_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_device_job_thread)]
except AttributeError:
    pass
try:
    ma_device_job_thread_uninit = _libraries['libminiaudio.so'].ma_device_job_thread_uninit
    ma_device_job_thread_uninit.restype = None
    ma_device_job_thread_uninit.argtypes = [ctypes.POINTER(struct_ma_device_job_thread), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_device_job_thread_post = _libraries['libminiaudio.so'].ma_device_job_thread_post
    ma_device_job_thread_post.restype = ma_result
    ma_device_job_thread_post.argtypes = [ctypes.POINTER(struct_ma_device_job_thread), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
try:
    ma_device_job_thread_next = _libraries['libminiaudio.so'].ma_device_job_thread_next
    ma_device_job_thread_next.restype = ma_result
    ma_device_job_thread_next.argtypes = [ctypes.POINTER(struct_ma_device_job_thread), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass

# values for enumeration 'ma_device_notification_type'
ma_device_notification_type__enumvalues = {
    0: 'ma_device_notification_type_started',
    1: 'ma_device_notification_type_stopped',
    2: 'ma_device_notification_type_rerouted',
    3: 'ma_device_notification_type_interruption_began',
    4: 'ma_device_notification_type_interruption_ended',
    5: 'ma_device_notification_type_unlocked',
}
ma_device_notification_type_started = 0
ma_device_notification_type_stopped = 1
ma_device_notification_type_rerouted = 2
ma_device_notification_type_interruption_began = 3
ma_device_notification_type_interruption_ended = 4
ma_device_notification_type_unlocked = 5
ma_device_notification_type = ctypes.c_uint32 # enum
class union_ma_device_notification_data(Union):
    pass

class struct_ma_device_notification_0_started(Structure):
    pass

struct_ma_device_notification_0_started._pack_ = 1 # source:False
struct_ma_device_notification_0_started._fields_ = [
    ('_unused', ctypes.c_int32),
]

class struct_ma_device_notification_0_stopped(Structure):
    pass

struct_ma_device_notification_0_stopped._pack_ = 1 # source:False
struct_ma_device_notification_0_stopped._fields_ = [
    ('_unused', ctypes.c_int32),
]

class struct_ma_device_notification_0_rerouted(Structure):
    pass

struct_ma_device_notification_0_rerouted._pack_ = 1 # source:False
struct_ma_device_notification_0_rerouted._fields_ = [
    ('_unused', ctypes.c_int32),
]

class struct_ma_device_notification_0_interruption(Structure):
    pass

struct_ma_device_notification_0_interruption._pack_ = 1 # source:False
struct_ma_device_notification_0_interruption._fields_ = [
    ('_unused', ctypes.c_int32),
]

union_ma_device_notification_data._pack_ = 1 # source:False
union_ma_device_notification_data._fields_ = [
    ('started', struct_ma_device_notification_0_started),
    ('stopped', struct_ma_device_notification_0_stopped),
    ('rerouted', struct_ma_device_notification_0_rerouted),
    ('interruption', struct_ma_device_notification_0_interruption),
]

struct_ma_device_notification._pack_ = 1 # source:False
struct_ma_device_notification._fields_ = [
    ('pDevice', ctypes.POINTER(struct_ma_device)),
    ('type', ma_device_notification_type),
    ('data', union_ma_device_notification_data),
]

ma_device_notification = struct_ma_device_notification
ma_device_notification_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device_notification))
ma_device_data_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)
ma_stop_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device))

# values for enumeration 'ma_ios_session_category'
ma_ios_session_category__enumvalues = {
    0: 'ma_ios_session_category_default',
    1: 'ma_ios_session_category_none',
    2: 'ma_ios_session_category_ambient',
    3: 'ma_ios_session_category_solo_ambient',
    4: 'ma_ios_session_category_playback',
    5: 'ma_ios_session_category_record',
    6: 'ma_ios_session_category_play_and_record',
    7: 'ma_ios_session_category_multi_route',
}
ma_ios_session_category_default = 0
ma_ios_session_category_none = 1
ma_ios_session_category_ambient = 2
ma_ios_session_category_solo_ambient = 3
ma_ios_session_category_playback = 4
ma_ios_session_category_record = 5
ma_ios_session_category_play_and_record = 6
ma_ios_session_category_multi_route = 7
ma_ios_session_category = ctypes.c_uint32 # enum

# values for enumeration 'ma_ios_session_category_option'
ma_ios_session_category_option__enumvalues = {
    1: 'ma_ios_session_category_option_mix_with_others',
    2: 'ma_ios_session_category_option_duck_others',
    4: 'ma_ios_session_category_option_allow_bluetooth',
    8: 'ma_ios_session_category_option_default_to_speaker',
    17: 'ma_ios_session_category_option_interrupt_spoken_audio_and_mix_with_others',
    32: 'ma_ios_session_category_option_allow_bluetooth_a2dp',
    64: 'ma_ios_session_category_option_allow_air_play',
}
ma_ios_session_category_option_mix_with_others = 1
ma_ios_session_category_option_duck_others = 2
ma_ios_session_category_option_allow_bluetooth = 4
ma_ios_session_category_option_default_to_speaker = 8
ma_ios_session_category_option_interrupt_spoken_audio_and_mix_with_others = 17
ma_ios_session_category_option_allow_bluetooth_a2dp = 32
ma_ios_session_category_option_allow_air_play = 64
ma_ios_session_category_option = ctypes.c_uint32 # enum

# values for enumeration 'ma_opensl_stream_type'
ma_opensl_stream_type__enumvalues = {
    0: 'ma_opensl_stream_type_default',
    1: 'ma_opensl_stream_type_voice',
    2: 'ma_opensl_stream_type_system',
    3: 'ma_opensl_stream_type_ring',
    4: 'ma_opensl_stream_type_media',
    5: 'ma_opensl_stream_type_alarm',
    6: 'ma_opensl_stream_type_notification',
}
ma_opensl_stream_type_default = 0
ma_opensl_stream_type_voice = 1
ma_opensl_stream_type_system = 2
ma_opensl_stream_type_ring = 3
ma_opensl_stream_type_media = 4
ma_opensl_stream_type_alarm = 5
ma_opensl_stream_type_notification = 6
ma_opensl_stream_type = ctypes.c_uint32 # enum

# values for enumeration 'ma_opensl_recording_preset'
ma_opensl_recording_preset__enumvalues = {
    0: 'ma_opensl_recording_preset_default',
    1: 'ma_opensl_recording_preset_generic',
    2: 'ma_opensl_recording_preset_camcorder',
    3: 'ma_opensl_recording_preset_voice_recognition',
    4: 'ma_opensl_recording_preset_voice_communication',
    5: 'ma_opensl_recording_preset_voice_unprocessed',
}
ma_opensl_recording_preset_default = 0
ma_opensl_recording_preset_generic = 1
ma_opensl_recording_preset_camcorder = 2
ma_opensl_recording_preset_voice_recognition = 3
ma_opensl_recording_preset_voice_communication = 4
ma_opensl_recording_preset_voice_unprocessed = 5
ma_opensl_recording_preset = ctypes.c_uint32 # enum

# values for enumeration 'ma_wasapi_usage'
ma_wasapi_usage__enumvalues = {
    0: 'ma_wasapi_usage_default',
    1: 'ma_wasapi_usage_games',
    2: 'ma_wasapi_usage_pro_audio',
}
ma_wasapi_usage_default = 0
ma_wasapi_usage_games = 1
ma_wasapi_usage_pro_audio = 2
ma_wasapi_usage = ctypes.c_uint32 # enum

# values for enumeration 'ma_aaudio_usage'
ma_aaudio_usage__enumvalues = {
    0: 'ma_aaudio_usage_default',
    1: 'ma_aaudio_usage_media',
    2: 'ma_aaudio_usage_voice_communication',
    3: 'ma_aaudio_usage_voice_communication_signalling',
    4: 'ma_aaudio_usage_alarm',
    5: 'ma_aaudio_usage_notification',
    6: 'ma_aaudio_usage_notification_ringtone',
    7: 'ma_aaudio_usage_notification_event',
    8: 'ma_aaudio_usage_assistance_accessibility',
    9: 'ma_aaudio_usage_assistance_navigation_guidance',
    10: 'ma_aaudio_usage_assistance_sonification',
    11: 'ma_aaudio_usage_game',
    12: 'ma_aaudio_usage_assitant',
    13: 'ma_aaudio_usage_emergency',
    14: 'ma_aaudio_usage_safety',
    15: 'ma_aaudio_usage_vehicle_status',
    16: 'ma_aaudio_usage_announcement',
}
ma_aaudio_usage_default = 0
ma_aaudio_usage_media = 1
ma_aaudio_usage_voice_communication = 2
ma_aaudio_usage_voice_communication_signalling = 3
ma_aaudio_usage_alarm = 4
ma_aaudio_usage_notification = 5
ma_aaudio_usage_notification_ringtone = 6
ma_aaudio_usage_notification_event = 7
ma_aaudio_usage_assistance_accessibility = 8
ma_aaudio_usage_assistance_navigation_guidance = 9
ma_aaudio_usage_assistance_sonification = 10
ma_aaudio_usage_game = 11
ma_aaudio_usage_assitant = 12
ma_aaudio_usage_emergency = 13
ma_aaudio_usage_safety = 14
ma_aaudio_usage_vehicle_status = 15
ma_aaudio_usage_announcement = 16
ma_aaudio_usage = ctypes.c_uint32 # enum

# values for enumeration 'ma_aaudio_content_type'
ma_aaudio_content_type__enumvalues = {
    0: 'ma_aaudio_content_type_default',
    1: 'ma_aaudio_content_type_speech',
    2: 'ma_aaudio_content_type_music',
    3: 'ma_aaudio_content_type_movie',
    4: 'ma_aaudio_content_type_sonification',
}
ma_aaudio_content_type_default = 0
ma_aaudio_content_type_speech = 1
ma_aaudio_content_type_music = 2
ma_aaudio_content_type_movie = 3
ma_aaudio_content_type_sonification = 4
ma_aaudio_content_type = ctypes.c_uint32 # enum

# values for enumeration 'ma_aaudio_input_preset'
ma_aaudio_input_preset__enumvalues = {
    0: 'ma_aaudio_input_preset_default',
    1: 'ma_aaudio_input_preset_generic',
    2: 'ma_aaudio_input_preset_camcorder',
    3: 'ma_aaudio_input_preset_voice_recognition',
    4: 'ma_aaudio_input_preset_voice_communication',
    5: 'ma_aaudio_input_preset_unprocessed',
    6: 'ma_aaudio_input_preset_voice_performance',
}
ma_aaudio_input_preset_default = 0
ma_aaudio_input_preset_generic = 1
ma_aaudio_input_preset_camcorder = 2
ma_aaudio_input_preset_voice_recognition = 3
ma_aaudio_input_preset_voice_communication = 4
ma_aaudio_input_preset_unprocessed = 5
ma_aaudio_input_preset_voice_performance = 6
ma_aaudio_input_preset = ctypes.c_uint32 # enum

# values for enumeration 'ma_aaudio_allowed_capture_policy'
ma_aaudio_allowed_capture_policy__enumvalues = {
    0: 'ma_aaudio_allow_capture_default',
    1: 'ma_aaudio_allow_capture_by_all',
    2: 'ma_aaudio_allow_capture_by_system',
    3: 'ma_aaudio_allow_capture_by_none',
}
ma_aaudio_allow_capture_default = 0
ma_aaudio_allow_capture_by_all = 1
ma_aaudio_allow_capture_by_system = 2
ma_aaudio_allow_capture_by_none = 3
ma_aaudio_allowed_capture_policy = ctypes.c_uint32 # enum
try:
    ma_device_id_equal = _libraries['libminiaudio.so'].ma_device_id_equal
    ma_device_id_equal.restype = ma_bool32
    ma_device_id_equal.argtypes = [ctypes.POINTER(union_ma_device_id), ctypes.POINTER(union_ma_device_id)]
except AttributeError:
    pass
class struct_ma_context_config_dsound(Structure):
    pass

struct_ma_context_config_dsound._pack_ = 1 # source:False
struct_ma_context_config_dsound._fields_ = [
    ('hWnd', ctypes.POINTER(None)),
]

class struct_ma_context_config_alsa(Structure):
    pass

struct_ma_context_config_alsa._pack_ = 1 # source:False
struct_ma_context_config_alsa._fields_ = [
    ('useVerboseDeviceEnumeration', ctypes.c_uint32),
]

class struct_ma_context_config_pulse(Structure):
    pass

struct_ma_context_config_pulse._pack_ = 1 # source:False
struct_ma_context_config_pulse._fields_ = [
    ('pApplicationName', ctypes.POINTER(ctypes.c_char)),
    ('pServerName', ctypes.POINTER(ctypes.c_char)),
    ('tryAutoSpawn', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_context_config_coreaudio(Structure):
    pass

struct_ma_context_config_coreaudio._pack_ = 1 # source:False
struct_ma_context_config_coreaudio._fields_ = [
    ('sessionCategory', ma_ios_session_category),
    ('sessionCategoryOptions', ctypes.c_uint32),
    ('noAudioSessionActivate', ctypes.c_uint32),
    ('noAudioSessionDeactivate', ctypes.c_uint32),
]

class struct_ma_context_config_jack(Structure):
    pass

struct_ma_context_config_jack._pack_ = 1 # source:False
struct_ma_context_config_jack._fields_ = [
    ('pClientName', ctypes.POINTER(ctypes.c_char)),
    ('tryStartServer', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

struct_ma_context_config._pack_ = 1 # source:False
struct_ma_context_config._fields_ = [
    ('pLog', ctypes.POINTER(struct_ma_log)),
    ('threadPriority', ma_thread_priority),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('threadStackSize', ctypes.c_uint64),
    ('pUserData', ctypes.POINTER(None)),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('dsound', struct_ma_context_config_dsound),
    ('alsa', struct_ma_context_config_alsa),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('pulse', struct_ma_context_config_pulse),
    ('coreaudio', struct_ma_context_config_coreaudio),
    ('jack', struct_ma_context_config_jack),
    ('custom', ma_backend_callbacks),
]

ma_context_config = struct_ma_context_config
class struct_ma_device_config_playback(Structure):
    pass

struct_ma_device_config_playback._pack_ = 1 # source:False
struct_ma_device_config_playback._fields_ = [
    ('pDeviceID', ctypes.POINTER(union_ma_device_id)),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('pChannelMap', ctypes.POINTER(ctypes.c_ubyte)),
    ('channelMixMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('shareMode', ma_share_mode),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_device_config_capture(Structure):
    pass

struct_ma_device_config_capture._pack_ = 1 # source:False
struct_ma_device_config_capture._fields_ = [
    ('pDeviceID', ctypes.POINTER(union_ma_device_id)),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('pChannelMap', ctypes.POINTER(ctypes.c_ubyte)),
    ('channelMixMode', ma_channel_mix_mode),
    ('calculateLFEFromSpatialChannels', ctypes.c_uint32),
    ('shareMode', ma_share_mode),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_device_config_wasapi(Structure):
    pass

struct_ma_device_config_wasapi._pack_ = 1 # source:False
struct_ma_device_config_wasapi._fields_ = [
    ('usage', ma_wasapi_usage),
    ('noAutoConvertSRC', ctypes.c_ubyte),
    ('noDefaultQualitySRC', ctypes.c_ubyte),
    ('noAutoStreamRouting', ctypes.c_ubyte),
    ('noHardwareOffloading', ctypes.c_ubyte),
    ('loopbackProcessID', ctypes.c_uint32),
    ('loopbackProcessExclude', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
]

class struct_ma_device_config_alsa(Structure):
    pass

struct_ma_device_config_alsa._pack_ = 1 # source:False
struct_ma_device_config_alsa._fields_ = [
    ('noMMap', ctypes.c_uint32),
    ('noAutoFormat', ctypes.c_uint32),
    ('noAutoChannels', ctypes.c_uint32),
    ('noAutoResample', ctypes.c_uint32),
]

class struct_ma_device_config_pulse(Structure):
    pass

struct_ma_device_config_pulse._pack_ = 1 # source:False
struct_ma_device_config_pulse._fields_ = [
    ('pStreamNamePlayback', ctypes.POINTER(ctypes.c_char)),
    ('pStreamNameCapture', ctypes.POINTER(ctypes.c_char)),
    ('channelMap', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_device_config_coreaudio(Structure):
    pass

struct_ma_device_config_coreaudio._pack_ = 1 # source:False
struct_ma_device_config_coreaudio._fields_ = [
    ('allowNominalSampleRateChange', ctypes.c_uint32),
]

class struct_ma_device_config_opensl(Structure):
    pass

struct_ma_device_config_opensl._pack_ = 1 # source:False
struct_ma_device_config_opensl._fields_ = [
    ('streamType', ma_opensl_stream_type),
    ('recordingPreset', ma_opensl_recording_preset),
    ('enableCompatibilityWorkarounds', ctypes.c_uint32),
]

class struct_ma_device_config_aaudio(Structure):
    pass

struct_ma_device_config_aaudio._pack_ = 1 # source:False
struct_ma_device_config_aaudio._fields_ = [
    ('usage', ma_aaudio_usage),
    ('contentType', ma_aaudio_content_type),
    ('inputPreset', ma_aaudio_input_preset),
    ('allowedCapturePolicy', ma_aaudio_allowed_capture_policy),
    ('noAutoStartAfterReroute', ctypes.c_uint32),
    ('enableCompatibilityWorkarounds', ctypes.c_uint32),
    ('allowSetBufferCapacity', ctypes.c_uint32),
]

struct_ma_device_config._pack_ = 1 # source:False
struct_ma_device_config._fields_ = [
    ('deviceType', ma_device_type),
    ('sampleRate', ctypes.c_uint32),
    ('periodSizeInFrames', ctypes.c_uint32),
    ('periodSizeInMilliseconds', ctypes.c_uint32),
    ('periods', ctypes.c_uint32),
    ('performanceProfile', ma_performance_profile),
    ('noPreSilencedOutputBuffer', ctypes.c_ubyte),
    ('noClip', ctypes.c_ubyte),
    ('noDisableDenormals', ctypes.c_ubyte),
    ('noFixedSizedCallback', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('dataCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)),
    ('notificationCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device_notification))),
    ('stopCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device))),
    ('pUserData', ctypes.POINTER(None)),
    ('resampling', ma_resampler_config),
    ('playback', struct_ma_device_config_playback),
    ('capture', struct_ma_device_config_capture),
    ('wasapi', struct_ma_device_config_wasapi),
    ('alsa', struct_ma_device_config_alsa),
    ('pulse', struct_ma_device_config_pulse),
    ('coreaudio', struct_ma_device_config_coreaudio),
    ('opensl', struct_ma_device_config_opensl),
    ('aaudio', struct_ma_device_config_aaudio),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_device_config = struct_ma_device_config
class struct_ma_device_info_0(Structure):
    pass

struct_ma_device_info_0._pack_ = 1 # source:False
struct_ma_device_info_0._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

struct_ma_device_info._pack_ = 1 # source:False
struct_ma_device_info._fields_ = [
    ('id', ma_device_id),
    ('name', ctypes.c_char * 256),
    ('isDefault', ctypes.c_uint32),
    ('nativeDataFormatCount', ctypes.c_uint32),
    ('nativeDataFormats', struct_ma_device_info_0 * 64),
]

ma_device_info = struct_ma_device_info
ma_enum_devices_callback_proc = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(struct_ma_context), ma_device_type, ctypes.POINTER(struct_ma_device_info), ctypes.POINTER(None))
struct_ma_device_descriptor._pack_ = 1 # source:False
struct_ma_device_descriptor._fields_ = [
    ('pDeviceID', ctypes.POINTER(union_ma_device_id)),
    ('shareMode', ma_share_mode),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('channelMap', ctypes.c_ubyte * 254),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('periodSizeInFrames', ctypes.c_uint32),
    ('periodSizeInMilliseconds', ctypes.c_uint32),
    ('periodCount', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_device_descriptor = struct_ma_device_descriptor
class struct_ma_context_command__wasapi(Structure):
    pass

class union_ma_context_command__wasapi_data(Union):
    pass

class struct_ma_context_command__wasapi_0_quit(Structure):
    pass

struct_ma_context_command__wasapi_0_quit._pack_ = 1 # source:False
struct_ma_context_command__wasapi_0_quit._fields_ = [
    ('_unused', ctypes.c_int32),
]

class struct_ma_context_command__wasapi_0_createAudioClient(Structure):
    pass

struct_ma_context_command__wasapi_0_createAudioClient._pack_ = 1 # source:False
struct_ma_context_command__wasapi_0_createAudioClient._fields_ = [
    ('deviceType', ma_device_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pAudioClient', ctypes.POINTER(None)),
    ('ppAudioClientService', ctypes.POINTER(ctypes.POINTER(None))),
    ('pResult', ctypes.POINTER(ma_result)),
]

class struct_ma_context_command__wasapi_0_releaseAudioClient(Structure):
    pass

struct_ma_context_command__wasapi_0_releaseAudioClient._pack_ = 1 # source:False
struct_ma_context_command__wasapi_0_releaseAudioClient._fields_ = [
    ('pDevice', ctypes.POINTER(struct_ma_device)),
    ('deviceType', ma_device_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

union_ma_context_command__wasapi_data._pack_ = 1 # source:False
union_ma_context_command__wasapi_data._fields_ = [
    ('quit', struct_ma_context_command__wasapi_0_quit),
    ('createAudioClient', struct_ma_context_command__wasapi_0_createAudioClient),
    ('releaseAudioClient', struct_ma_context_command__wasapi_0_releaseAudioClient),
    ('PADDING_0', ctypes.c_ubyte * 16),
]

struct_ma_context_command__wasapi._pack_ = 1 # source:False
struct_ma_context_command__wasapi._fields_ = [
    ('code', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pEvent', ctypes.POINTER(struct_ma_event)),
    ('data', union_ma_context_command__wasapi_data),
]

ma_context_command__wasapi = struct_ma_context_command__wasapi
try:
    ma_context_config_init = _libraries['libminiaudio.so'].ma_context_config_init
    ma_context_config_init.restype = ma_context_config
    ma_context_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_context_init = _libraries['libminiaudio.so'].ma_context_init
    ma_context_init.restype = ma_result
    ma_context_init.argtypes = [ma_backend * 0, ma_uint32, ctypes.POINTER(struct_ma_context_config), ctypes.POINTER(struct_ma_context)]
except AttributeError:
    pass
try:
    ma_context_uninit = _libraries['libminiaudio.so'].ma_context_uninit
    ma_context_uninit.restype = ma_result
    ma_context_uninit.argtypes = [ctypes.POINTER(struct_ma_context)]
except AttributeError:
    pass
try:
    ma_context_sizeof = _libraries['libminiaudio.so'].ma_context_sizeof
    ma_context_sizeof.restype = size_t
    ma_context_sizeof.argtypes = []
except AttributeError:
    pass
try:
    ma_context_get_log = _libraries['libminiaudio.so'].ma_context_get_log
    ma_context_get_log.restype = ctypes.POINTER(struct_ma_log)
    ma_context_get_log.argtypes = [ctypes.POINTER(struct_ma_context)]
except AttributeError:
    pass
try:
    ma_context_enumerate_devices = _libraries['libminiaudio.so'].ma_context_enumerate_devices
    ma_context_enumerate_devices.restype = ma_result
    ma_context_enumerate_devices.argtypes = [ctypes.POINTER(struct_ma_context), ma_enum_devices_callback_proc, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_context_get_devices = _libraries['libminiaudio.so'].ma_context_get_devices
    ma_context_get_devices.restype = ma_result
    ma_context_get_devices.argtypes = [ctypes.POINTER(struct_ma_context), ctypes.POINTER(ctypes.POINTER(struct_ma_device_info)), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(struct_ma_device_info)), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    ma_context_get_device_info = _libraries['libminiaudio.so'].ma_context_get_device_info
    ma_context_get_device_info.restype = ma_result
    ma_context_get_device_info.argtypes = [ctypes.POINTER(struct_ma_context), ma_device_type, ctypes.POINTER(union_ma_device_id), ctypes.POINTER(struct_ma_device_info)]
except AttributeError:
    pass
try:
    ma_context_is_loopback_supported = _libraries['libminiaudio.so'].ma_context_is_loopback_supported
    ma_context_is_loopback_supported.restype = ma_bool32
    ma_context_is_loopback_supported.argtypes = [ctypes.POINTER(struct_ma_context)]
except AttributeError:
    pass
try:
    ma_device_config_init = _libraries['libminiaudio.so'].ma_device_config_init
    ma_device_config_init.restype = ma_device_config
    ma_device_config_init.argtypes = [ma_device_type]
except AttributeError:
    pass
try:
    ma_device_init = _libraries['libminiaudio.so'].ma_device_init
    ma_device_init.restype = ma_result
    ma_device_init.argtypes = [ctypes.POINTER(struct_ma_context), ctypes.POINTER(struct_ma_device_config), ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_init_ex = _libraries['libminiaudio.so'].ma_device_init_ex
    ma_device_init_ex.restype = ma_result
    ma_device_init_ex.argtypes = [ma_backend * 0, ma_uint32, ctypes.POINTER(struct_ma_context_config), ctypes.POINTER(struct_ma_device_config), ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_uninit = _libraries['libminiaudio.so'].ma_device_uninit
    ma_device_uninit.restype = None
    ma_device_uninit.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_get_context = _libraries['libminiaudio.so'].ma_device_get_context
    ma_device_get_context.restype = ctypes.POINTER(struct_ma_context)
    ma_device_get_context.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_get_log = _libraries['libminiaudio.so'].ma_device_get_log
    ma_device_get_log.restype = ctypes.POINTER(struct_ma_log)
    ma_device_get_log.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_get_info = _libraries['libminiaudio.so'].ma_device_get_info
    ma_device_get_info.restype = ma_result
    ma_device_get_info.argtypes = [ctypes.POINTER(struct_ma_device), ma_device_type, ctypes.POINTER(struct_ma_device_info)]
except AttributeError:
    pass
try:
    ma_device_get_name = _libraries['libminiaudio.so'].ma_device_get_name
    ma_device_get_name.restype = ma_result
    ma_device_get_name.argtypes = [ctypes.POINTER(struct_ma_device), ma_device_type, ctypes.POINTER(ctypes.c_char), size_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_device_start = _libraries['libminiaudio.so'].ma_device_start
    ma_device_start.restype = ma_result
    ma_device_start.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_stop = _libraries['libminiaudio.so'].ma_device_stop
    ma_device_stop.restype = ma_result
    ma_device_stop.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_is_started = _libraries['libminiaudio.so'].ma_device_is_started
    ma_device_is_started.restype = ma_bool32
    ma_device_is_started.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_get_state = _libraries['libminiaudio.so'].ma_device_get_state
    ma_device_get_state.restype = ma_device_state
    ma_device_get_state.argtypes = [ctypes.POINTER(struct_ma_device)]
except AttributeError:
    pass
try:
    ma_device_post_init = _libraries['libminiaudio.so'].ma_device_post_init
    ma_device_post_init.restype = ma_result
    ma_device_post_init.argtypes = [ctypes.POINTER(struct_ma_device), ma_device_type, ctypes.POINTER(struct_ma_device_descriptor), ctypes.POINTER(struct_ma_device_descriptor)]
except AttributeError:
    pass
try:
    ma_device_set_master_volume = _libraries['libminiaudio.so'].ma_device_set_master_volume
    ma_device_set_master_volume.restype = ma_result
    ma_device_set_master_volume.argtypes = [ctypes.POINTER(struct_ma_device), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_device_get_master_volume = _libraries['libminiaudio.so'].ma_device_get_master_volume
    ma_device_get_master_volume.restype = ma_result
    ma_device_get_master_volume.argtypes = [ctypes.POINTER(struct_ma_device), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_device_set_master_volume_db = _libraries['libminiaudio.so'].ma_device_set_master_volume_db
    ma_device_set_master_volume_db.restype = ma_result
    ma_device_set_master_volume_db.argtypes = [ctypes.POINTER(struct_ma_device), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_device_get_master_volume_db = _libraries['libminiaudio.so'].ma_device_get_master_volume_db
    ma_device_get_master_volume_db.restype = ma_result
    ma_device_get_master_volume_db.argtypes = [ctypes.POINTER(struct_ma_device), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_device_handle_backend_data_callback = _libraries['libminiaudio.so'].ma_device_handle_backend_data_callback
    ma_device_handle_backend_data_callback.restype = ma_result
    ma_device_handle_backend_data_callback.argtypes = [ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_calculate_buffer_size_in_frames_from_descriptor = _libraries['libminiaudio.so'].ma_calculate_buffer_size_in_frames_from_descriptor
    ma_calculate_buffer_size_in_frames_from_descriptor.restype = ma_uint32
    ma_calculate_buffer_size_in_frames_from_descriptor.argtypes = [ctypes.POINTER(struct_ma_device_descriptor), ma_uint32, ma_performance_profile]
except AttributeError:
    pass
try:
    ma_get_backend_name = _libraries['libminiaudio.so'].ma_get_backend_name
    ma_get_backend_name.restype = ctypes.POINTER(ctypes.c_char)
    ma_get_backend_name.argtypes = [ma_backend]
except AttributeError:
    pass
try:
    ma_get_backend_from_name = _libraries['libminiaudio.so'].ma_get_backend_from_name
    ma_get_backend_from_name.restype = ma_result
    ma_get_backend_from_name.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ma_backend)]
except AttributeError:
    pass
try:
    ma_is_backend_enabled = _libraries['libminiaudio.so'].ma_is_backend_enabled
    ma_is_backend_enabled.restype = ma_bool32
    ma_is_backend_enabled.argtypes = [ma_backend]
except AttributeError:
    pass
try:
    ma_get_enabled_backends = _libraries['libminiaudio.so'].ma_get_enabled_backends
    ma_get_enabled_backends.restype = ma_result
    ma_get_enabled_backends.argtypes = [ctypes.POINTER(ma_backend), size_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_is_loopback_supported = _libraries['libminiaudio.so'].ma_is_loopback_supported
    ma_is_loopback_supported.restype = ma_bool32
    ma_is_loopback_supported.argtypes = [ma_backend]
except AttributeError:
    pass
try:
    ma_calculate_buffer_size_in_milliseconds_from_frames = _libraries['libminiaudio.so'].ma_calculate_buffer_size_in_milliseconds_from_frames
    ma_calculate_buffer_size_in_milliseconds_from_frames.restype = ma_uint32
    ma_calculate_buffer_size_in_milliseconds_from_frames.argtypes = [ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_calculate_buffer_size_in_frames_from_milliseconds = _libraries['libminiaudio.so'].ma_calculate_buffer_size_in_frames_from_milliseconds
    ma_calculate_buffer_size_in_frames_from_milliseconds.restype = ma_uint32
    ma_calculate_buffer_size_in_frames_from_milliseconds.argtypes = [ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_copy_pcm_frames = _libraries['libminiaudio.so'].ma_copy_pcm_frames
    ma_copy_pcm_frames.restype = None
    ma_copy_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_silence_pcm_frames = _libraries['libminiaudio.so'].ma_silence_pcm_frames
    ma_silence_pcm_frames.restype = None
    ma_silence_pcm_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_offset_pcm_frames_ptr = _libraries['libminiaudio.so'].ma_offset_pcm_frames_ptr
    ma_offset_pcm_frames_ptr.restype = ctypes.POINTER(None)
    ma_offset_pcm_frames_ptr.argtypes = [ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_offset_pcm_frames_const_ptr = _libraries['libminiaudio.so'].ma_offset_pcm_frames_const_ptr
    ma_offset_pcm_frames_const_ptr.restype = ctypes.POINTER(None)
    ma_offset_pcm_frames_const_ptr.argtypes = [ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_offset_pcm_frames_ptr_f32 = _libraries['FIXME_STUB'].ma_offset_pcm_frames_ptr_f32
    ma_offset_pcm_frames_ptr_f32.restype = ctypes.POINTER(ctypes.c_float)
    ma_offset_pcm_frames_ptr_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32]
except AttributeError:
    pass
try:
    ma_offset_pcm_frames_const_ptr_f32 = _libraries['FIXME_STUB'].ma_offset_pcm_frames_const_ptr_f32
    ma_offset_pcm_frames_const_ptr_f32.restype = ctypes.POINTER(ctypes.c_float)
    ma_offset_pcm_frames_const_ptr_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32]
except AttributeError:
    pass
try:
    ma_clip_samples_u8 = _libraries['libminiaudio.so'].ma_clip_samples_u8
    ma_clip_samples_u8.restype = None
    ma_clip_samples_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int16), ma_uint64]
except AttributeError:
    pass
try:
    ma_clip_samples_s16 = _libraries['libminiaudio.so'].ma_clip_samples_s16
    ma_clip_samples_s16.restype = None
    ma_clip_samples_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int32), ma_uint64]
except AttributeError:
    pass
try:
    ma_clip_samples_s24 = _libraries['libminiaudio.so'].ma_clip_samples_s24
    ma_clip_samples_s24.restype = None
    ma_clip_samples_s24.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int64), ma_uint64]
except AttributeError:
    pass
try:
    ma_clip_samples_s32 = _libraries['libminiaudio.so'].ma_clip_samples_s32
    ma_clip_samples_s32.restype = None
    ma_clip_samples_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int64), ma_uint64]
except AttributeError:
    pass
try:
    ma_clip_samples_f32 = _libraries['libminiaudio.so'].ma_clip_samples_f32
    ma_clip_samples_f32.restype = None
    ma_clip_samples_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64]
except AttributeError:
    pass
try:
    ma_clip_pcm_frames = _libraries['libminiaudio.so'].ma_clip_pcm_frames
    ma_clip_pcm_frames.restype = None
    ma_clip_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_u8 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_u8
    ma_copy_and_apply_volume_factor_u8.restype = None
    ma_copy_and_apply_volume_factor_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_s16 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_s16
    ma_copy_and_apply_volume_factor_s16.restype = None
    ma_copy_and_apply_volume_factor_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int16), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_s24 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_s24
    ma_copy_and_apply_volume_factor_s24.restype = None
    ma_copy_and_apply_volume_factor_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_s32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_s32
    ma_copy_and_apply_volume_factor_s32.restype = None
    ma_copy_and_apply_volume_factor_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_f32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_f32
    ma_copy_and_apply_volume_factor_f32.restype = None
    ma_copy_and_apply_volume_factor_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_u8 = _libraries['libminiaudio.so'].ma_apply_volume_factor_u8
    ma_apply_volume_factor_u8.restype = None
    ma_apply_volume_factor_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_s16 = _libraries['libminiaudio.so'].ma_apply_volume_factor_s16
    ma_apply_volume_factor_s16.restype = None
    ma_apply_volume_factor_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_s24 = _libraries['libminiaudio.so'].ma_apply_volume_factor_s24
    ma_apply_volume_factor_s24.restype = None
    ma_apply_volume_factor_s24.argtypes = [ctypes.POINTER(None), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_s32 = _libraries['libminiaudio.so'].ma_apply_volume_factor_s32
    ma_apply_volume_factor_s32.restype = None
    ma_apply_volume_factor_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_f32 = _libraries['libminiaudio.so'].ma_apply_volume_factor_f32
    ma_apply_volume_factor_f32.restype = None
    ma_apply_volume_factor_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames_u8 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames_u8
    ma_copy_and_apply_volume_factor_pcm_frames_u8.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames_s16 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames_s16
    ma_copy_and_apply_volume_factor_pcm_frames_s16.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int16), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames_s24 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames_s24
    ma_copy_and_apply_volume_factor_pcm_frames_s24.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames_s24.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames_s32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames_s32
    ma_copy_and_apply_volume_factor_pcm_frames_s32.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames_f32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames_f32
    ma_copy_and_apply_volume_factor_pcm_frames_f32.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_pcm_frames = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_pcm_frames
    ma_copy_and_apply_volume_factor_pcm_frames.restype = None
    ma_copy_and_apply_volume_factor_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames_u8 = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames_u8
    ma_apply_volume_factor_pcm_frames_u8.restype = None
    ma_apply_volume_factor_pcm_frames_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames_s16 = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames_s16
    ma_apply_volume_factor_pcm_frames_s16.restype = None
    ma_apply_volume_factor_pcm_frames_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames_s24 = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames_s24
    ma_apply_volume_factor_pcm_frames_s24.restype = None
    ma_apply_volume_factor_pcm_frames_s24.argtypes = [ctypes.POINTER(None), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames_s32 = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames_s32
    ma_apply_volume_factor_pcm_frames_s32.restype = None
    ma_apply_volume_factor_pcm_frames_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames_f32 = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames_f32
    ma_apply_volume_factor_pcm_frames_f32.restype = None
    ma_apply_volume_factor_pcm_frames_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_apply_volume_factor_pcm_frames = _libraries['libminiaudio.so'].ma_apply_volume_factor_pcm_frames
    ma_apply_volume_factor_pcm_frames.restype = None
    ma_apply_volume_factor_pcm_frames.argtypes = [ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_factor_per_channel_f32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_factor_per_channel_f32
    ma_copy_and_apply_volume_factor_per_channel_f32.restype = None
    ma_copy_and_apply_volume_factor_per_channel_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32, ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_samples_u8 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_samples_u8
    ma_copy_and_apply_volume_and_clip_samples_u8.restype = None
    ma_copy_and_apply_volume_and_clip_samples_u8.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int16), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_samples_s16 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_samples_s16
    ma_copy_and_apply_volume_and_clip_samples_s16.restype = None
    ma_copy_and_apply_volume_and_clip_samples_s16.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_int32), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_samples_s24 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_samples_s24
    ma_copy_and_apply_volume_and_clip_samples_s24.restype = None
    ma_copy_and_apply_volume_and_clip_samples_s24.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_int64), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_samples_s32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_samples_s32
    ma_copy_and_apply_volume_and_clip_samples_s32.restype = None
    ma_copy_and_apply_volume_and_clip_samples_s32.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int64), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_samples_f32 = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_samples_f32
    ma_copy_and_apply_volume_and_clip_samples_f32.restype = None
    ma_copy_and_apply_volume_and_clip_samples_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_copy_and_apply_volume_and_clip_pcm_frames = _libraries['libminiaudio.so'].ma_copy_and_apply_volume_and_clip_pcm_frames
    ma_copy_and_apply_volume_and_clip_pcm_frames.restype = None
    ma_copy_and_apply_volume_and_clip_pcm_frames.argtypes = [ctypes.POINTER(None), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_volume_linear_to_db = _libraries['libminiaudio.so'].ma_volume_linear_to_db
    ma_volume_linear_to_db.restype = ctypes.c_float
    ma_volume_linear_to_db.argtypes = [ctypes.c_float]
except AttributeError:
    pass
try:
    ma_volume_db_to_linear = _libraries['libminiaudio.so'].ma_volume_db_to_linear
    ma_volume_db_to_linear.restype = ctypes.c_float
    ma_volume_db_to_linear.argtypes = [ctypes.c_float]
except AttributeError:
    pass
try:
    ma_mix_pcm_frames_f32 = _libraries['libminiaudio.so'].ma_mix_pcm_frames_f32
    ma_mix_pcm_frames_f32.restype = ma_result
    ma_mix_pcm_frames_f32.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ma_uint64, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
ma_vfs = None
ma_vfs_file = ctypes.POINTER(None)

# values for enumeration 'ma_open_mode_flags'
ma_open_mode_flags__enumvalues = {
    1: 'MA_OPEN_MODE_READ',
    2: 'MA_OPEN_MODE_WRITE',
}
MA_OPEN_MODE_READ = 1
MA_OPEN_MODE_WRITE = 2
ma_open_mode_flags = ctypes.c_uint32 # enum

# values for enumeration 'ma_seek_origin'
ma_seek_origin__enumvalues = {
    0: 'ma_seek_origin_start',
    1: 'ma_seek_origin_current',
    2: 'ma_seek_origin_end',
}
ma_seek_origin_start = 0
ma_seek_origin_current = 1
ma_seek_origin_end = 2
ma_seek_origin = ctypes.c_uint32 # enum
class struct_ma_file_info(Structure):
    pass

struct_ma_file_info._pack_ = 1 # source:False
struct_ma_file_info._fields_ = [
    ('sizeInBytes', ctypes.c_uint64),
]

ma_file_info = struct_ma_file_info
class struct_ma_vfs_callbacks(Structure):
    pass

struct_ma_vfs_callbacks._pack_ = 1 # source:False
struct_ma_vfs_callbacks._fields_ = [
    ('onOpen', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(None)))),
    ('onOpenW', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32), ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(None)))),
    ('onClose', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None))),
    ('onRead', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onWrite', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onSeek', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_int64, ma_seek_origin)),
    ('onTell', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int64))),
    ('onInfo', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(struct_ma_file_info))),
]

ma_vfs_callbacks = struct_ma_vfs_callbacks
try:
    ma_vfs_open = _libraries['libminiaudio.so'].ma_vfs_open
    ma_vfs_open.restype = ma_result
    ma_vfs_open.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ma_uint32, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_vfs_open_w = _libraries['libminiaudio.so'].ma_vfs_open_w
    ma_vfs_open_w.restype = ma_result
    ma_vfs_open_w.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32), ma_uint32, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_vfs_close = _libraries['libminiaudio.so'].ma_vfs_close
    ma_vfs_close.restype = ma_result
    ma_vfs_close.argtypes = [ctypes.POINTER(None), ma_vfs_file]
except AttributeError:
    pass
try:
    ma_vfs_read = _libraries['libminiaudio.so'].ma_vfs_read
    ma_vfs_read.restype = ma_result
    ma_vfs_read.argtypes = [ctypes.POINTER(None), ma_vfs_file, ctypes.POINTER(None), size_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_vfs_write = _libraries['libminiaudio.so'].ma_vfs_write
    ma_vfs_write.restype = ma_result
    ma_vfs_write.argtypes = [ctypes.POINTER(None), ma_vfs_file, ctypes.POINTER(None), size_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_vfs_seek = _libraries['libminiaudio.so'].ma_vfs_seek
    ma_vfs_seek.restype = ma_result
    ma_vfs_seek.argtypes = [ctypes.POINTER(None), ma_vfs_file, ma_int64, ma_seek_origin]
except AttributeError:
    pass
try:
    ma_vfs_tell = _libraries['libminiaudio.so'].ma_vfs_tell
    ma_vfs_tell.restype = ma_result
    ma_vfs_tell.argtypes = [ctypes.POINTER(None), ma_vfs_file, ctypes.POINTER(ctypes.c_int64)]
except AttributeError:
    pass
try:
    ma_vfs_info = _libraries['libminiaudio.so'].ma_vfs_info
    ma_vfs_info.restype = ma_result
    ma_vfs_info.argtypes = [ctypes.POINTER(None), ma_vfs_file, ctypes.POINTER(struct_ma_file_info)]
except AttributeError:
    pass
try:
    ma_vfs_open_and_read_file = _libraries['libminiaudio.so'].ma_vfs_open_and_read_file
    ma_vfs_open_and_read_file.restype = ma_result
    ma_vfs_open_and_read_file.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_default_vfs(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('cb', ma_vfs_callbacks),
    ('allocationCallbacks', ma_allocation_callbacks),
     ]

ma_default_vfs = struct_ma_default_vfs
try:
    ma_default_vfs_init = _libraries['libminiaudio.so'].ma_default_vfs_init
    ma_default_vfs_init.restype = ma_result
    ma_default_vfs_init.argtypes = [ctypes.POINTER(struct_ma_default_vfs), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
ma_read_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))
ma_seek_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.c_int64, ma_seek_origin)
ma_tell_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int64))

# values for enumeration 'ma_encoding_format'
ma_encoding_format__enumvalues = {
    0: 'ma_encoding_format_unknown',
    1: 'ma_encoding_format_wav',
    2: 'ma_encoding_format_flac',
    3: 'ma_encoding_format_mp3',
    4: 'ma_encoding_format_vorbis',
}
ma_encoding_format_unknown = 0
ma_encoding_format_wav = 1
ma_encoding_format_flac = 2
ma_encoding_format_mp3 = 3
ma_encoding_format_vorbis = 4
ma_encoding_format = ctypes.c_uint32 # enum
class struct_ma_decoder(Structure):
    pass

class struct_ma_decoding_backend_vtable(Structure):
    pass

class union_ma_decoder_data(Union):
    pass

class struct_ma_decoder_0_vfs(Structure):
    pass

struct_ma_decoder_0_vfs._pack_ = 1 # source:False
struct_ma_decoder_0_vfs._fields_ = [
    ('pVFS', ctypes.POINTER(None)),
    ('file', ctypes.POINTER(None)),
]

class struct_ma_decoder_0_memory(Structure):
    pass

struct_ma_decoder_0_memory._pack_ = 1 # source:False
struct_ma_decoder_0_memory._fields_ = [
    ('pData', ctypes.POINTER(ctypes.c_ubyte)),
    ('dataSize', ctypes.c_uint64),
    ('currentReadPos', ctypes.c_uint64),
]

union_ma_decoder_data._pack_ = 1 # source:False
union_ma_decoder_data._fields_ = [
    ('vfs', struct_ma_decoder_0_vfs),
    ('memory', struct_ma_decoder_0_memory),
]

struct_ma_decoder._pack_ = 1 # source:False
struct_ma_decoder._fields_ = [
    ('ds', ma_data_source_base),
    ('pBackend', ctypes.POINTER(None)),
    ('pBackendVTable', ctypes.POINTER(struct_ma_decoding_backend_vtable)),
    ('pBackendUserData', ctypes.POINTER(None)),
    ('onRead', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onSeek', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.c_int64, ma_seek_origin)),
    ('onTell', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ctypes.c_int64))),
    ('pUserData', ctypes.POINTER(None)),
    ('readPointerInPCMFrames', ctypes.c_uint64),
    ('outputFormat', ma_format),
    ('outputChannels', ctypes.c_uint32),
    ('outputSampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('converter', ma_data_converter),
    ('pInputCache', ctypes.POINTER(None)),
    ('inputCacheCap', ctypes.c_uint64),
    ('inputCacheConsumed', ctypes.c_uint64),
    ('inputCacheRemaining', ctypes.c_uint64),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('data', union_ma_decoder_data),
]

ma_decoder = struct_ma_decoder
class struct_ma_decoding_backend_config(Structure):
    pass

struct_ma_decoding_backend_config._pack_ = 1 # source:False
struct_ma_decoding_backend_config._fields_ = [
    ('preferredFormat', ma_format),
    ('seekPointCount', ctypes.c_uint32),
]

ma_decoding_backend_config = struct_ma_decoding_backend_config
try:
    ma_decoding_backend_config_init = _libraries['libminiaudio.so'].ma_decoding_backend_config_init
    ma_decoding_backend_config_init.restype = ma_decoding_backend_config
    ma_decoding_backend_config_init.argtypes = [ma_format, ma_uint32]
except AttributeError:
    pass
struct_ma_decoding_backend_vtable._pack_ = 1 # source:False
struct_ma_decoding_backend_vtable._fields_ = [
    ('onInit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)), ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.c_int64, ma_seek_origin), ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int64)), ctypes.POINTER(None), ctypes.POINTER(struct_ma_decoding_backend_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(ctypes.POINTER(None)))),
    ('onInitFile', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_decoding_backend_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(ctypes.POINTER(None)))),
    ('onInitFileW', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_ma_decoding_backend_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(ctypes.POINTER(None)))),
    ('onInitMemory', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(struct_ma_decoding_backend_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(ctypes.POINTER(None)))),
    ('onUninit', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks))),
]

ma_decoding_backend_vtable = struct_ma_decoding_backend_vtable
ma_decoder_read_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))
ma_decoder_seek_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.c_int64, ma_seek_origin)
ma_decoder_tell_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ctypes.c_int64))
class struct_ma_decoder_config(Structure):
    pass

struct_ma_decoder_config._pack_ = 1 # source:False
struct_ma_decoder_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pChannelMap', ctypes.POINTER(ctypes.c_ubyte)),
    ('channelMixMode', ma_channel_mix_mode),
    ('ditherMode', ma_dither_mode),
    ('resampling', ma_resampler_config),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('encodingFormat', ma_encoding_format),
    ('seekPointCount', ctypes.c_uint32),
    ('ppCustomBackendVTables', ctypes.POINTER(ctypes.POINTER(struct_ma_decoding_backend_vtable))),
    ('customBackendCount', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('pCustomBackendUserData', ctypes.POINTER(None)),
]

ma_decoder_config = struct_ma_decoder_config
try:
    ma_decoder_config_init = _libraries['libminiaudio.so'].ma_decoder_config_init
    ma_decoder_config_init.restype = ma_decoder_config
    ma_decoder_config_init.argtypes = [ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_decoder_config_init_default = _libraries['libminiaudio.so'].ma_decoder_config_init_default
    ma_decoder_config_init_default.restype = ma_decoder_config
    ma_decoder_config_init_default.argtypes = []
except AttributeError:
    pass
try:
    ma_decoder_init = _libraries['libminiaudio.so'].ma_decoder_init
    ma_decoder_init.restype = ma_result
    ma_decoder_init.argtypes = [ma_decoder_read_proc, ma_decoder_seek_proc, ctypes.POINTER(None), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_init_memory = _libraries['libminiaudio.so'].ma_decoder_init_memory
    ma_decoder_init_memory.restype = ma_result
    ma_decoder_init_memory.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_init_vfs = _libraries['libminiaudio.so'].ma_decoder_init_vfs
    ma_decoder_init_vfs.restype = ma_result
    ma_decoder_init_vfs.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_init_vfs_w = _libraries['libminiaudio.so'].ma_decoder_init_vfs_w
    ma_decoder_init_vfs_w.restype = ma_result
    ma_decoder_init_vfs_w.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_init_file = _libraries['libminiaudio.so'].ma_decoder_init_file
    ma_decoder_init_file.restype = ma_result
    ma_decoder_init_file.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_init_file_w = _libraries['libminiaudio.so'].ma_decoder_init_file_w
    ma_decoder_init_file_w.restype = ma_result
    ma_decoder_init_file_w.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_uninit = _libraries['libminiaudio.so'].ma_decoder_uninit
    ma_decoder_uninit.restype = ma_result
    ma_decoder_uninit.argtypes = [ctypes.POINTER(struct_ma_decoder)]
except AttributeError:
    pass
try:
    ma_decoder_read_pcm_frames = _libraries['libminiaudio.so'].ma_decoder_read_pcm_frames
    ma_decoder_read_pcm_frames.restype = ma_result
    ma_decoder_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_decoder_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_decoder_seek_to_pcm_frame
    ma_decoder_seek_to_pcm_frame.restype = ma_result
    ma_decoder_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_decoder), ma_uint64]
except AttributeError:
    pass
try:
    ma_decoder_get_data_format = _libraries['libminiaudio.so'].ma_decoder_get_data_format
    ma_decoder_get_data_format.restype = ma_result
    ma_decoder_get_data_format.argtypes = [ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_decoder_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_decoder_get_cursor_in_pcm_frames
    ma_decoder_get_cursor_in_pcm_frames.restype = ma_result
    ma_decoder_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_decoder_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_decoder_get_length_in_pcm_frames
    ma_decoder_get_length_in_pcm_frames.restype = ma_result
    ma_decoder_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_decoder_get_available_frames = _libraries['libminiaudio.so'].ma_decoder_get_available_frames
    ma_decoder_get_available_frames.restype = ma_result
    ma_decoder_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_decoder), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_decode_from_vfs = _libraries['libminiaudio.so'].ma_decode_from_vfs
    ma_decode_from_vfs.restype = ma_result
    ma_decode_from_vfs.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_decode_file = _libraries['libminiaudio.so'].ma_decode_file
    ma_decode_file.restype = ma_result
    ma_decode_file.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    ma_decode_memory = _libraries['libminiaudio.so'].ma_decode_memory
    ma_decode_memory.restype = ma_result
    ma_decode_memory.argtypes = [ctypes.POINTER(None), size_t, ctypes.POINTER(struct_ma_decoder_config), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
class struct_ma_encoder(Structure):
    pass

class struct_ma_encoder_config(Structure):
    pass

struct_ma_encoder_config._pack_ = 1 # source:False
struct_ma_encoder_config._fields_ = [
    ('encodingFormat', ma_encoding_format),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('allocationCallbacks', ma_allocation_callbacks),
]

ma_encoder_config = struct_ma_encoder_config
class union_ma_encoder_data(Union):
    pass

class struct_ma_encoder_0_vfs(Structure):
    pass

struct_ma_encoder_0_vfs._pack_ = 1 # source:False
struct_ma_encoder_0_vfs._fields_ = [
    ('pVFS', ctypes.POINTER(None)),
    ('file', ctypes.POINTER(None)),
]

union_ma_encoder_data._pack_ = 1 # source:False
union_ma_encoder_data._fields_ = [
    ('vfs', struct_ma_encoder_0_vfs),
]

struct_ma_encoder._pack_ = 1 # source:False
struct_ma_encoder._fields_ = [
    ('config', ma_encoder_config),
    ('onWrite', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('onSeek', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.c_int64, ma_seek_origin)),
    ('onInit', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder))),
    ('onUninit', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_encoder))),
    ('onWritePCMFrames', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))),
    ('pUserData', ctypes.POINTER(None)),
    ('pInternalEncoder', ctypes.POINTER(None)),
    ('data', union_ma_encoder_data),
]

ma_encoder = struct_ma_encoder
ma_encoder_write_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))
ma_encoder_seek_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.c_int64, ma_seek_origin)
ma_encoder_init_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder))
ma_encoder_uninit_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_encoder))
ma_encoder_write_pcm_frames_proc = ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(struct_ma_encoder), ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64))
try:
    ma_encoder_config_init = _libraries['libminiaudio.so'].ma_encoder_config_init
    ma_encoder_config_init.restype = ma_encoder_config
    ma_encoder_config_init.argtypes = [ma_encoding_format, ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_encoder_init = _libraries['libminiaudio.so'].ma_encoder_init
    ma_encoder_init.restype = ma_result
    ma_encoder_init.argtypes = [ma_encoder_write_proc, ma_encoder_seek_proc, ctypes.POINTER(None), ctypes.POINTER(struct_ma_encoder_config), ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_init_vfs = _libraries['libminiaudio.so'].ma_encoder_init_vfs
    ma_encoder_init_vfs.restype = ma_result
    ma_encoder_init_vfs.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_encoder_config), ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_init_vfs_w = _libraries['libminiaudio.so'].ma_encoder_init_vfs_w
    ma_encoder_init_vfs_w.restype = ma_result
    ma_encoder_init_vfs_w.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_ma_encoder_config), ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_init_file = _libraries['libminiaudio.so'].ma_encoder_init_file
    ma_encoder_init_file.restype = ma_result
    ma_encoder_init_file.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_encoder_config), ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_init_file_w = _libraries['libminiaudio.so'].ma_encoder_init_file_w
    ma_encoder_init_file_w.restype = ma_result
    ma_encoder_init_file_w.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(struct_ma_encoder_config), ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_uninit = _libraries['libminiaudio.so'].ma_encoder_uninit
    ma_encoder_uninit.restype = None
    ma_encoder_uninit.argtypes = [ctypes.POINTER(struct_ma_encoder)]
except AttributeError:
    pass
try:
    ma_encoder_write_pcm_frames = _libraries['libminiaudio.so'].ma_encoder_write_pcm_frames
    ma_encoder_write_pcm_frames.restype = ma_result
    ma_encoder_write_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_encoder), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass

# values for enumeration 'ma_waveform_type'
ma_waveform_type__enumvalues = {
    0: 'ma_waveform_type_sine',
    1: 'ma_waveform_type_square',
    2: 'ma_waveform_type_triangle',
    3: 'ma_waveform_type_sawtooth',
}
ma_waveform_type_sine = 0
ma_waveform_type_square = 1
ma_waveform_type_triangle = 2
ma_waveform_type_sawtooth = 3
ma_waveform_type = ctypes.c_uint32 # enum
class struct_ma_waveform_config(Structure):
    pass

struct_ma_waveform_config._pack_ = 1 # source:False
struct_ma_waveform_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('type', ma_waveform_type),
    ('amplitude', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_waveform_config = struct_ma_waveform_config
try:
    ma_waveform_config_init = _libraries['libminiaudio.so'].ma_waveform_config_init
    ma_waveform_config_init.restype = ma_waveform_config
    ma_waveform_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ma_waveform_type, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_waveform(Structure):
    pass

struct_ma_waveform._pack_ = 1 # source:False
struct_ma_waveform._fields_ = [
    ('ds', ma_data_source_base),
    ('config', ma_waveform_config),
    ('advance', ctypes.c_double),
    ('time', ctypes.c_double),
]

ma_waveform = struct_ma_waveform
try:
    ma_waveform_init = _libraries['libminiaudio.so'].ma_waveform_init
    ma_waveform_init.restype = ma_result
    ma_waveform_init.argtypes = [ctypes.POINTER(struct_ma_waveform_config), ctypes.POINTER(struct_ma_waveform)]
except AttributeError:
    pass
try:
    ma_waveform_uninit = _libraries['libminiaudio.so'].ma_waveform_uninit
    ma_waveform_uninit.restype = None
    ma_waveform_uninit.argtypes = [ctypes.POINTER(struct_ma_waveform)]
except AttributeError:
    pass
try:
    ma_waveform_read_pcm_frames = _libraries['libminiaudio.so'].ma_waveform_read_pcm_frames
    ma_waveform_read_pcm_frames.restype = ma_result
    ma_waveform_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_waveform), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_waveform_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_waveform_seek_to_pcm_frame
    ma_waveform_seek_to_pcm_frame.restype = ma_result
    ma_waveform_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_waveform), ma_uint64]
except AttributeError:
    pass
try:
    ma_waveform_set_amplitude = _libraries['libminiaudio.so'].ma_waveform_set_amplitude
    ma_waveform_set_amplitude.restype = ma_result
    ma_waveform_set_amplitude.argtypes = [ctypes.POINTER(struct_ma_waveform), ctypes.c_double]
except AttributeError:
    pass
try:
    ma_waveform_set_frequency = _libraries['libminiaudio.so'].ma_waveform_set_frequency
    ma_waveform_set_frequency.restype = ma_result
    ma_waveform_set_frequency.argtypes = [ctypes.POINTER(struct_ma_waveform), ctypes.c_double]
except AttributeError:
    pass
try:
    ma_waveform_set_type = _libraries['libminiaudio.so'].ma_waveform_set_type
    ma_waveform_set_type.restype = ma_result
    ma_waveform_set_type.argtypes = [ctypes.POINTER(struct_ma_waveform), ma_waveform_type]
except AttributeError:
    pass
try:
    ma_waveform_set_sample_rate = _libraries['libminiaudio.so'].ma_waveform_set_sample_rate
    ma_waveform_set_sample_rate.restype = ma_result
    ma_waveform_set_sample_rate.argtypes = [ctypes.POINTER(struct_ma_waveform), ma_uint32]
except AttributeError:
    pass
class struct_ma_pulsewave_config(Structure):
    pass

struct_ma_pulsewave_config._pack_ = 1 # source:False
struct_ma_pulsewave_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('dutyCycle', ctypes.c_double),
    ('amplitude', ctypes.c_double),
    ('frequency', ctypes.c_double),
]

ma_pulsewave_config = struct_ma_pulsewave_config
try:
    ma_pulsewave_config_init = _libraries['libminiaudio.so'].ma_pulsewave_config_init
    ma_pulsewave_config_init.restype = ma_pulsewave_config
    ma_pulsewave_config_init.argtypes = [ma_format, ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_pulsewave(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('waveform', ma_waveform),
    ('config', ma_pulsewave_config),
     ]

ma_pulsewave = struct_ma_pulsewave
try:
    ma_pulsewave_init = _libraries['libminiaudio.so'].ma_pulsewave_init
    ma_pulsewave_init.restype = ma_result
    ma_pulsewave_init.argtypes = [ctypes.POINTER(struct_ma_pulsewave_config), ctypes.POINTER(struct_ma_pulsewave)]
except AttributeError:
    pass
try:
    ma_pulsewave_uninit = _libraries['libminiaudio.so'].ma_pulsewave_uninit
    ma_pulsewave_uninit.restype = None
    ma_pulsewave_uninit.argtypes = [ctypes.POINTER(struct_ma_pulsewave)]
except AttributeError:
    pass
try:
    ma_pulsewave_read_pcm_frames = _libraries['libminiaudio.so'].ma_pulsewave_read_pcm_frames
    ma_pulsewave_read_pcm_frames.restype = ma_result
    ma_pulsewave_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_pulsewave_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_pulsewave_seek_to_pcm_frame
    ma_pulsewave_seek_to_pcm_frame.restype = ma_result
    ma_pulsewave_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ma_uint64]
except AttributeError:
    pass
try:
    ma_pulsewave_set_amplitude = _libraries['libminiaudio.so'].ma_pulsewave_set_amplitude
    ma_pulsewave_set_amplitude.restype = ma_result
    ma_pulsewave_set_amplitude.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ctypes.c_double]
except AttributeError:
    pass
try:
    ma_pulsewave_set_frequency = _libraries['libminiaudio.so'].ma_pulsewave_set_frequency
    ma_pulsewave_set_frequency.restype = ma_result
    ma_pulsewave_set_frequency.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ctypes.c_double]
except AttributeError:
    pass
try:
    ma_pulsewave_set_sample_rate = _libraries['libminiaudio.so'].ma_pulsewave_set_sample_rate
    ma_pulsewave_set_sample_rate.restype = ma_result
    ma_pulsewave_set_sample_rate.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ma_uint32]
except AttributeError:
    pass
try:
    ma_pulsewave_set_duty_cycle = _libraries['libminiaudio.so'].ma_pulsewave_set_duty_cycle
    ma_pulsewave_set_duty_cycle.restype = ma_result
    ma_pulsewave_set_duty_cycle.argtypes = [ctypes.POINTER(struct_ma_pulsewave), ctypes.c_double]
except AttributeError:
    pass

# values for enumeration 'ma_noise_type'
ma_noise_type__enumvalues = {
    0: 'ma_noise_type_white',
    1: 'ma_noise_type_pink',
    2: 'ma_noise_type_brownian',
}
ma_noise_type_white = 0
ma_noise_type_pink = 1
ma_noise_type_brownian = 2
ma_noise_type = ctypes.c_uint32 # enum
class struct_ma_noise_config(Structure):
    pass

struct_ma_noise_config._pack_ = 1 # source:False
struct_ma_noise_config._fields_ = [
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('type', ma_noise_type),
    ('seed', ctypes.c_int32),
    ('amplitude', ctypes.c_double),
    ('duplicateChannels', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_noise_config = struct_ma_noise_config
try:
    ma_noise_config_init = _libraries['libminiaudio.so'].ma_noise_config_init
    ma_noise_config_init.restype = ma_noise_config
    ma_noise_config_init.argtypes = [ma_format, ma_uint32, ma_noise_type, ma_int32, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_noise(Structure):
    pass

class union_ma_noise_state(Union):
    pass

class struct_ma_noise_0_pink(Structure):
    pass

struct_ma_noise_0_pink._pack_ = 1 # source:False
struct_ma_noise_0_pink._fields_ = [
    ('bin', ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
    ('accumulation', ctypes.POINTER(ctypes.c_double)),
    ('counter', ctypes.POINTER(ctypes.c_uint32)),
]

class struct_ma_noise_0_brownian(Structure):
    pass

struct_ma_noise_0_brownian._pack_ = 1 # source:False
struct_ma_noise_0_brownian._fields_ = [
    ('accumulation', ctypes.POINTER(ctypes.c_double)),
]

union_ma_noise_state._pack_ = 1 # source:False
union_ma_noise_state._fields_ = [
    ('pink', struct_ma_noise_0_pink),
    ('brownian', struct_ma_noise_0_brownian),
    ('PADDING_0', ctypes.c_ubyte * 16),
]

struct_ma_noise._pack_ = 1 # source:False
struct_ma_noise._fields_ = [
    ('ds', ma_data_source_base),
    ('config', ma_noise_config),
    ('lcg', ma_lcg),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('state', union_ma_noise_state),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_noise = struct_ma_noise
try:
    ma_noise_get_heap_size = _libraries['libminiaudio.so'].ma_noise_get_heap_size
    ma_noise_get_heap_size.restype = ma_result
    ma_noise_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_noise_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_noise_init_preallocated = _libraries['libminiaudio.so'].ma_noise_init_preallocated
    ma_noise_init_preallocated.restype = ma_result
    ma_noise_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_noise_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_noise)]
except AttributeError:
    pass
try:
    ma_noise_init = _libraries['libminiaudio.so'].ma_noise_init
    ma_noise_init.restype = ma_result
    ma_noise_init.argtypes = [ctypes.POINTER(struct_ma_noise_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_noise)]
except AttributeError:
    pass
try:
    ma_noise_uninit = _libraries['libminiaudio.so'].ma_noise_uninit
    ma_noise_uninit.restype = None
    ma_noise_uninit.argtypes = [ctypes.POINTER(struct_ma_noise), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_noise_read_pcm_frames = _libraries['libminiaudio.so'].ma_noise_read_pcm_frames
    ma_noise_read_pcm_frames.restype = ma_result
    ma_noise_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_noise), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_noise_set_amplitude = _libraries['libminiaudio.so'].ma_noise_set_amplitude
    ma_noise_set_amplitude.restype = ma_result
    ma_noise_set_amplitude.argtypes = [ctypes.POINTER(struct_ma_noise), ctypes.c_double]
except AttributeError:
    pass
try:
    ma_noise_set_seed = _libraries['libminiaudio.so'].ma_noise_set_seed
    ma_noise_set_seed.restype = ma_result
    ma_noise_set_seed.argtypes = [ctypes.POINTER(struct_ma_noise), ma_int32]
except AttributeError:
    pass
try:
    ma_noise_set_type = _libraries['libminiaudio.so'].ma_noise_set_type
    ma_noise_set_type.restype = ma_result
    ma_noise_set_type.argtypes = [ctypes.POINTER(struct_ma_noise), ma_noise_type]
except AttributeError:
    pass
class struct_ma_resource_manager(Structure):
    pass

class struct_ma_resource_manager_data_buffer_node(Structure):
    pass

class struct_ma_resource_manager_config(Structure):
    pass

struct_ma_resource_manager_config._pack_ = 1 # source:False
struct_ma_resource_manager_config._fields_ = [
    ('allocationCallbacks', ma_allocation_callbacks),
    ('pLog', ctypes.POINTER(struct_ma_log)),
    ('decodedFormat', ma_format),
    ('decodedChannels', ctypes.c_uint32),
    ('decodedSampleRate', ctypes.c_uint32),
    ('jobThreadCount', ctypes.c_uint32),
    ('jobThreadStackSize', ctypes.c_uint64),
    ('jobQueueCapacity', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('pVFS', ctypes.POINTER(None)),
    ('ppCustomDecodingBackendVTables', ctypes.POINTER(ctypes.POINTER(struct_ma_decoding_backend_vtable))),
    ('customDecodingBackendCount', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pCustomDecodingBackendUserData', ctypes.POINTER(None)),
]

ma_resource_manager_config = struct_ma_resource_manager_config
struct_ma_resource_manager._pack_ = 1 # source:False
struct_ma_resource_manager._fields_ = [
    ('config', ma_resource_manager_config),
    ('pRootDataBufferNode', ctypes.POINTER(struct_ma_resource_manager_data_buffer_node)),
    ('dataBufferBSTLock', ma_mutex),
    ('jobThreads', ctypes.c_uint64 * 64),
    ('jobQueue', ma_job_queue),
    ('defaultVFS', ma_default_vfs),
    ('log', ma_log),
]

ma_resource_manager = struct_ma_resource_manager
class struct_ma_resource_manager_data_supply(Structure):
    pass


# values for enumeration 'ma_resource_manager_data_supply_type'
ma_resource_manager_data_supply_type__enumvalues = {
    0: 'ma_resource_manager_data_supply_type_unknown',
    1: 'ma_resource_manager_data_supply_type_encoded',
    2: 'ma_resource_manager_data_supply_type_decoded',
    3: 'ma_resource_manager_data_supply_type_decoded_paged',
}
ma_resource_manager_data_supply_type_unknown = 0
ma_resource_manager_data_supply_type_encoded = 1
ma_resource_manager_data_supply_type_decoded = 2
ma_resource_manager_data_supply_type_decoded_paged = 3
ma_resource_manager_data_supply_type = ctypes.c_uint32 # enum
class union_ma_resource_manager_data_supply_backend(Union):
    pass

class struct_ma_resource_manager_data_supply_0_encoded(Structure):
    pass

struct_ma_resource_manager_data_supply_0_encoded._pack_ = 1 # source:False
struct_ma_resource_manager_data_supply_0_encoded._fields_ = [
    ('pData', ctypes.POINTER(None)),
    ('sizeInBytes', ctypes.c_uint64),
]

class struct_ma_resource_manager_data_supply_0_decoded(Structure):
    pass

struct_ma_resource_manager_data_supply_0_decoded._pack_ = 1 # source:False
struct_ma_resource_manager_data_supply_0_decoded._fields_ = [
    ('pData', ctypes.POINTER(None)),
    ('totalFrameCount', ctypes.c_uint64),
    ('decodedFrameCount', ctypes.c_uint64),
    ('format', ma_format),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_ma_resource_manager_data_supply_0_decodedPaged(Structure):
    pass

struct_ma_resource_manager_data_supply_0_decodedPaged._pack_ = 1 # source:False
struct_ma_resource_manager_data_supply_0_decodedPaged._fields_ = [
    ('data', ma_paged_audio_buffer_data),
    ('decodedFrameCount', ctypes.c_uint64),
    ('sampleRate', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

union_ma_resource_manager_data_supply_backend._pack_ = 1 # source:False
union_ma_resource_manager_data_supply_backend._fields_ = [
    ('encoded', struct_ma_resource_manager_data_supply_0_encoded),
    ('decoded', struct_ma_resource_manager_data_supply_0_decoded),
    ('decodedPaged', struct_ma_resource_manager_data_supply_0_decodedPaged),
]

struct_ma_resource_manager_data_supply._pack_ = 1 # source:False
struct_ma_resource_manager_data_supply._fields_ = [
    ('type', ma_resource_manager_data_supply_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('backend', union_ma_resource_manager_data_supply_backend),
]

ma_resource_manager_data_supply = struct_ma_resource_manager_data_supply
struct_ma_resource_manager_data_buffer_node._pack_ = 1 # source:False
struct_ma_resource_manager_data_buffer_node._fields_ = [
    ('hashedName32', ctypes.c_uint32),
    ('refCount', ctypes.c_uint32),
    ('result', ma_result),
    ('executionCounter', ctypes.c_uint32),
    ('executionPointer', ctypes.c_uint32),
    ('isDataOwnedByResourceManager', ctypes.c_uint32),
    ('data', ma_resource_manager_data_supply),
    ('pParent', ctypes.POINTER(struct_ma_resource_manager_data_buffer_node)),
    ('pChildLo', ctypes.POINTER(struct_ma_resource_manager_data_buffer_node)),
    ('pChildHi', ctypes.POINTER(struct_ma_resource_manager_data_buffer_node)),
]

ma_resource_manager_data_buffer_node = struct_ma_resource_manager_data_buffer_node
class struct_ma_resource_manager_data_buffer(Structure):
    pass

class union_ma_resource_manager_data_buffer_connector(Union):
    pass

union_ma_resource_manager_data_buffer_connector._pack_ = 1 # source:False
union_ma_resource_manager_data_buffer_connector._fields_ = [
    ('decoder', ma_decoder),
    ('buffer', ma_audio_buffer),
    ('pagedBuffer', ma_paged_audio_buffer),
    ('PADDING_0', ctypes.c_ubyte * 448),
]

struct_ma_resource_manager_data_buffer._pack_ = 1 # source:False
struct_ma_resource_manager_data_buffer._fields_ = [
    ('ds', ma_data_source_base),
    ('pResourceManager', ctypes.POINTER(struct_ma_resource_manager)),
    ('pNode', ctypes.POINTER(struct_ma_resource_manager_data_buffer_node)),
    ('flags', ctypes.c_uint32),
    ('executionCounter', ctypes.c_uint32),
    ('executionPointer', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('seekTargetInPCMFrames', ctypes.c_uint64),
    ('seekToCursorOnNextRead', ctypes.c_uint32),
    ('result', ma_result),
    ('isLooping', ctypes.c_uint32),
    ('isConnectorInitialized', ma_atomic_bool32),
    ('connector', union_ma_resource_manager_data_buffer_connector),
]

ma_resource_manager_data_buffer = struct_ma_resource_manager_data_buffer
class struct_ma_resource_manager_data_stream(Structure):
    pass

struct_ma_resource_manager_data_stream._pack_ = 1 # source:False
struct_ma_resource_manager_data_stream._fields_ = [
    ('ds', ma_data_source_base),
    ('pResourceManager', ctypes.POINTER(struct_ma_resource_manager)),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('decoder', ma_decoder),
    ('isDecoderInitialized', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('totalLengthInPCMFrames', ctypes.c_uint64),
    ('relativeCursor', ctypes.c_uint32),
    ('PADDING_2', ctypes.c_ubyte * 4),
    ('absoluteCursor', ctypes.c_uint64),
    ('currentPageIndex', ctypes.c_uint32),
    ('executionCounter', ctypes.c_uint32),
    ('executionPointer', ctypes.c_uint32),
    ('isLooping', ctypes.c_uint32),
    ('pPageData', ctypes.POINTER(None)),
    ('pageFrameCount', ctypes.c_uint32 * 2),
    ('result', ma_result),
    ('isDecoderAtEnd', ctypes.c_uint32),
    ('isPageValid', ctypes.c_uint32 * 2),
    ('seekCounter', ctypes.c_uint32),
    ('PADDING_3', ctypes.c_ubyte * 4),
]

ma_resource_manager_data_stream = struct_ma_resource_manager_data_stream
class struct_ma_resource_manager_data_source(Structure):
    pass

class union_ma_resource_manager_data_source_backend(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('buffer', ma_resource_manager_data_buffer),
    ('stream', ma_resource_manager_data_stream),
     ]

struct_ma_resource_manager_data_source._pack_ = 1 # source:False
struct_ma_resource_manager_data_source._fields_ = [
    ('backend', union_ma_resource_manager_data_source_backend),
    ('flags', ctypes.c_uint32),
    ('executionCounter', ctypes.c_uint32),
    ('executionPointer', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_resource_manager_data_source = struct_ma_resource_manager_data_source

# values for enumeration 'ma_resource_manager_data_source_flags'
ma_resource_manager_data_source_flags__enumvalues = {
    1: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_STREAM',
    2: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_DECODE',
    4: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_ASYNC',
    8: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT',
    16: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_UNKNOWN_LENGTH',
    32: 'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_LOOPING',
}
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_STREAM = 1
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_DECODE = 2
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_ASYNC = 4
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT = 8
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_UNKNOWN_LENGTH = 16
MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_LOOPING = 32
ma_resource_manager_data_source_flags = ctypes.c_uint32 # enum
class struct_ma_resource_manager_pipeline_stage_notification(Structure):
    pass

struct_ma_resource_manager_pipeline_stage_notification._pack_ = 1 # source:False
struct_ma_resource_manager_pipeline_stage_notification._fields_ = [
    ('pNotification', ctypes.POINTER(None)),
    ('pFence', ctypes.POINTER(struct_ma_fence)),
]

ma_resource_manager_pipeline_stage_notification = struct_ma_resource_manager_pipeline_stage_notification
class struct_ma_resource_manager_pipeline_notifications(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('init', ma_resource_manager_pipeline_stage_notification),
    ('done', ma_resource_manager_pipeline_stage_notification),
     ]

ma_resource_manager_pipeline_notifications = struct_ma_resource_manager_pipeline_notifications
try:
    ma_resource_manager_pipeline_notifications_init = _libraries['libminiaudio.so'].ma_resource_manager_pipeline_notifications_init
    ma_resource_manager_pipeline_notifications_init.restype = ma_resource_manager_pipeline_notifications
    ma_resource_manager_pipeline_notifications_init.argtypes = []
except AttributeError:
    pass

# values for enumeration 'ma_resource_manager_flags'
ma_resource_manager_flags__enumvalues = {
    1: 'MA_RESOURCE_MANAGER_FLAG_NON_BLOCKING',
    2: 'MA_RESOURCE_MANAGER_FLAG_NO_THREADING',
}
MA_RESOURCE_MANAGER_FLAG_NON_BLOCKING = 1
MA_RESOURCE_MANAGER_FLAG_NO_THREADING = 2
ma_resource_manager_flags = ctypes.c_uint32 # enum
class struct_ma_resource_manager_data_source_config(Structure):
    pass

struct_ma_resource_manager_data_source_config._pack_ = 1 # source:False
struct_ma_resource_manager_data_source_config._fields_ = [
    ('pFilePath', ctypes.POINTER(ctypes.c_char)),
    ('pFilePathW', ctypes.POINTER(ctypes.c_int32)),
    ('pNotifications', ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications)),
    ('initialSeekPointInPCMFrames', ctypes.c_uint64),
    ('rangeBegInPCMFrames', ctypes.c_uint64),
    ('rangeEndInPCMFrames', ctypes.c_uint64),
    ('loopPointBegInPCMFrames', ctypes.c_uint64),
    ('loopPointEndInPCMFrames', ctypes.c_uint64),
    ('flags', ctypes.c_uint32),
    ('isLooping', ctypes.c_uint32),
]

ma_resource_manager_data_source_config = struct_ma_resource_manager_data_source_config
try:
    ma_resource_manager_data_source_config_init = _libraries['libminiaudio.so'].ma_resource_manager_data_source_config_init
    ma_resource_manager_data_source_config_init.restype = ma_resource_manager_data_source_config
    ma_resource_manager_data_source_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_resource_manager_config_init = _libraries['libminiaudio.so'].ma_resource_manager_config_init
    ma_resource_manager_config_init.restype = ma_resource_manager_config
    ma_resource_manager_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_resource_manager_init = _libraries['libminiaudio.so'].ma_resource_manager_init
    ma_resource_manager_init.restype = ma_result
    ma_resource_manager_init.argtypes = [ctypes.POINTER(struct_ma_resource_manager_config), ctypes.POINTER(struct_ma_resource_manager)]
except AttributeError:
    pass
try:
    ma_resource_manager_uninit = _libraries['libminiaudio.so'].ma_resource_manager_uninit
    ma_resource_manager_uninit.restype = None
    ma_resource_manager_uninit.argtypes = [ctypes.POINTER(struct_ma_resource_manager)]
except AttributeError:
    pass
try:
    ma_resource_manager_get_log = _libraries['libminiaudio.so'].ma_resource_manager_get_log
    ma_resource_manager_get_log.restype = ctypes.POINTER(struct_ma_log)
    ma_resource_manager_get_log.argtypes = [ctypes.POINTER(struct_ma_resource_manager)]
except AttributeError:
    pass
try:
    ma_resource_manager_register_file = _libraries['libminiaudio.so'].ma_resource_manager_register_file
    ma_resource_manager_register_file.restype = ma_result
    ma_resource_manager_register_file.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ma_uint32]
except AttributeError:
    pass
try:
    ma_resource_manager_register_file_w = _libraries['libminiaudio.so'].ma_resource_manager_register_file_w
    ma_resource_manager_register_file_w.restype = ma_result
    ma_resource_manager_register_file_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ma_uint32]
except AttributeError:
    pass
try:
    ma_resource_manager_register_decoded_data = _libraries['libminiaudio.so'].ma_resource_manager_register_decoded_data
    ma_resource_manager_register_decoded_data.restype = ma_result
    ma_resource_manager_register_decoded_data.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_resource_manager_register_decoded_data_w = _libraries['libminiaudio.so'].ma_resource_manager_register_decoded_data_w
    ma_resource_manager_register_decoded_data_w.restype = ma_result
    ma_resource_manager_register_decoded_data_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(None), ma_uint64, ma_format, ma_uint32, ma_uint32]
except AttributeError:
    pass
try:
    ma_resource_manager_register_encoded_data = _libraries['libminiaudio.so'].ma_resource_manager_register_encoded_data
    ma_resource_manager_register_encoded_data.restype = ma_result
    ma_resource_manager_register_encoded_data.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    ma_resource_manager_register_encoded_data_w = _libraries['libminiaudio.so'].ma_resource_manager_register_encoded_data_w
    ma_resource_manager_register_encoded_data_w.restype = ma_result
    ma_resource_manager_register_encoded_data_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(None), size_t]
except AttributeError:
    pass
try:
    ma_resource_manager_unregister_file = _libraries['libminiaudio.so'].ma_resource_manager_unregister_file
    ma_resource_manager_unregister_file.restype = ma_result
    ma_resource_manager_unregister_file.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    ma_resource_manager_unregister_file_w = _libraries['libminiaudio.so'].ma_resource_manager_unregister_file_w
    ma_resource_manager_unregister_file_w.restype = ma_result
    ma_resource_manager_unregister_file_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    ma_resource_manager_unregister_data = _libraries['libminiaudio.so'].ma_resource_manager_unregister_data
    ma_resource_manager_unregister_data.restype = ma_result
    ma_resource_manager_unregister_data.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    ma_resource_manager_unregister_data_w = _libraries['libminiaudio.so'].ma_resource_manager_unregister_data_w
    ma_resource_manager_unregister_data_w.restype = ma_result
    ma_resource_manager_unregister_data_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_init_ex = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_init_ex
    ma_resource_manager_data_buffer_init_ex.restype = ma_result
    ma_resource_manager_data_buffer_init_ex.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_resource_manager_data_source_config), ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_init = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_init
    ma_resource_manager_data_buffer_init.restype = ma_result
    ma_resource_manager_data_buffer_init.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_init_w = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_init_w
    ma_resource_manager_data_buffer_init_w.restype = ma_result
    ma_resource_manager_data_buffer_init_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_init_copy = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_init_copy
    ma_resource_manager_data_buffer_init_copy.restype = ma_result
    ma_resource_manager_data_buffer_init_copy.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_uninit = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_uninit
    ma_resource_manager_data_buffer_uninit.restype = ma_result
    ma_resource_manager_data_buffer_uninit.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_read_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_read_pcm_frames
    ma_resource_manager_data_buffer_read_pcm_frames.restype = ma_result
    ma_resource_manager_data_buffer_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_seek_to_pcm_frame
    ma_resource_manager_data_buffer_seek_to_pcm_frame.restype = ma_result
    ma_resource_manager_data_buffer_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ma_uint64]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_get_data_format = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_get_data_format
    ma_resource_manager_data_buffer_get_data_format.restype = ma_result
    ma_resource_manager_data_buffer_get_data_format.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_get_cursor_in_pcm_frames
    ma_resource_manager_data_buffer_get_cursor_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_buffer_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_get_length_in_pcm_frames
    ma_resource_manager_data_buffer_get_length_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_buffer_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_result = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_result
    ma_resource_manager_data_buffer_result.restype = ma_result
    ma_resource_manager_data_buffer_result.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_set_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_set_looping
    ma_resource_manager_data_buffer_set_looping.restype = ma_result
    ma_resource_manager_data_buffer_set_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ma_bool32]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_is_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_is_looping
    ma_resource_manager_data_buffer_is_looping.restype = ma_bool32
    ma_resource_manager_data_buffer_is_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_buffer_get_available_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_buffer_get_available_frames
    ma_resource_manager_data_buffer_get_available_frames.restype = ma_result
    ma_resource_manager_data_buffer_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_buffer), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_init_ex = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_init_ex
    ma_resource_manager_data_stream_init_ex.restype = ma_result
    ma_resource_manager_data_stream_init_ex.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_resource_manager_data_source_config), ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_init = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_init
    ma_resource_manager_data_stream_init.restype = ma_result
    ma_resource_manager_data_stream_init.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_init_w = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_init_w
    ma_resource_manager_data_stream_init_w.restype = ma_result
    ma_resource_manager_data_stream_init_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_uninit = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_uninit
    ma_resource_manager_data_stream_uninit.restype = ma_result
    ma_resource_manager_data_stream_uninit.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_read_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_read_pcm_frames
    ma_resource_manager_data_stream_read_pcm_frames.restype = ma_result
    ma_resource_manager_data_stream_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_seek_to_pcm_frame
    ma_resource_manager_data_stream_seek_to_pcm_frame.restype = ma_result
    ma_resource_manager_data_stream_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ma_uint64]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_get_data_format = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_get_data_format
    ma_resource_manager_data_stream_get_data_format.restype = ma_result
    ma_resource_manager_data_stream_get_data_format.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_get_cursor_in_pcm_frames
    ma_resource_manager_data_stream_get_cursor_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_stream_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_get_length_in_pcm_frames
    ma_resource_manager_data_stream_get_length_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_stream_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_result = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_result
    ma_resource_manager_data_stream_result.restype = ma_result
    ma_resource_manager_data_stream_result.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_set_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_set_looping
    ma_resource_manager_data_stream_set_looping.restype = ma_result
    ma_resource_manager_data_stream_set_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ma_bool32]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_is_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_is_looping
    ma_resource_manager_data_stream_is_looping.restype = ma_bool32
    ma_resource_manager_data_stream_is_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_stream_get_available_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_stream_get_available_frames
    ma_resource_manager_data_stream_get_available_frames.restype = ma_result
    ma_resource_manager_data_stream_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_stream), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_init_ex = _libraries['libminiaudio.so'].ma_resource_manager_data_source_init_ex
    ma_resource_manager_data_source_init_ex.restype = ma_result
    ma_resource_manager_data_source_init_ex.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_resource_manager_data_source_config), ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_init = _libraries['libminiaudio.so'].ma_resource_manager_data_source_init
    ma_resource_manager_data_source_init.restype = ma_result
    ma_resource_manager_data_source_init.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_char), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_init_w = _libraries['libminiaudio.so'].ma_resource_manager_data_source_init_w
    ma_resource_manager_data_source_init_w.restype = ma_result
    ma_resource_manager_data_source_init_w.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(ctypes.c_int32), ma_uint32, ctypes.POINTER(struct_ma_resource_manager_pipeline_notifications), ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_init_copy = _libraries['libminiaudio.so'].ma_resource_manager_data_source_init_copy
    ma_resource_manager_data_source_init_copy.restype = ma_result
    ma_resource_manager_data_source_init_copy.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_uninit = _libraries['libminiaudio.so'].ma_resource_manager_data_source_uninit
    ma_resource_manager_data_source_uninit.restype = ma_result
    ma_resource_manager_data_source_uninit.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_read_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_source_read_pcm_frames
    ma_resource_manager_data_source_read_pcm_frames.restype = ma_result
    ma_resource_manager_data_source_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_resource_manager_data_source_seek_to_pcm_frame
    ma_resource_manager_data_source_seek_to_pcm_frame.restype = ma_result
    ma_resource_manager_data_source_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ma_uint64]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_get_data_format = _libraries['libminiaudio.so'].ma_resource_manager_data_source_get_data_format
    ma_resource_manager_data_source_get_data_format.restype = ma_result
    ma_resource_manager_data_source_get_data_format.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_source_get_cursor_in_pcm_frames
    ma_resource_manager_data_source_get_cursor_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_source_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_source_get_length_in_pcm_frames
    ma_resource_manager_data_source_get_length_in_pcm_frames.restype = ma_result
    ma_resource_manager_data_source_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_result = _libraries['libminiaudio.so'].ma_resource_manager_data_source_result
    ma_resource_manager_data_source_result.restype = ma_result
    ma_resource_manager_data_source_result.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_set_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_source_set_looping
    ma_resource_manager_data_source_set_looping.restype = ma_result
    ma_resource_manager_data_source_set_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ma_bool32]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_is_looping = _libraries['libminiaudio.so'].ma_resource_manager_data_source_is_looping
    ma_resource_manager_data_source_is_looping.restype = ma_bool32
    ma_resource_manager_data_source_is_looping.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source)]
except AttributeError:
    pass
try:
    ma_resource_manager_data_source_get_available_frames = _libraries['libminiaudio.so'].ma_resource_manager_data_source_get_available_frames
    ma_resource_manager_data_source_get_available_frames.restype = ma_result
    ma_resource_manager_data_source_get_available_frames.argtypes = [ctypes.POINTER(struct_ma_resource_manager_data_source), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_resource_manager_post_job = _libraries['libminiaudio.so'].ma_resource_manager_post_job
    ma_resource_manager_post_job.restype = ma_result
    ma_resource_manager_post_job.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
try:
    ma_resource_manager_post_job_quit = _libraries['libminiaudio.so'].ma_resource_manager_post_job_quit
    ma_resource_manager_post_job_quit.restype = ma_result
    ma_resource_manager_post_job_quit.argtypes = [ctypes.POINTER(struct_ma_resource_manager)]
except AttributeError:
    pass
try:
    ma_resource_manager_next_job = _libraries['libminiaudio.so'].ma_resource_manager_next_job
    ma_resource_manager_next_job.restype = ma_result
    ma_resource_manager_next_job.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
try:
    ma_resource_manager_process_job = _libraries['libminiaudio.so'].ma_resource_manager_process_job
    ma_resource_manager_process_job.restype = ma_result
    ma_resource_manager_process_job.argtypes = [ctypes.POINTER(struct_ma_resource_manager), ctypes.POINTER(struct_ma_job)]
except AttributeError:
    pass
try:
    ma_resource_manager_process_next_job = _libraries['libminiaudio.so'].ma_resource_manager_process_next_job
    ma_resource_manager_process_next_job.restype = ma_result
    ma_resource_manager_process_next_job.argtypes = [ctypes.POINTER(struct_ma_resource_manager)]
except AttributeError:
    pass
class struct_ma_stack(Structure):
    pass

struct_ma_stack._pack_ = 1 # source:False
struct_ma_stack._fields_ = [
    ('offset', ctypes.c_uint64),
    ('sizeInBytes', ctypes.c_uint64),
    ('_data', ctypes.c_ubyte * 1),
    ('PADDING_0', ctypes.c_ubyte * 7),
]

ma_stack = struct_ma_stack
class struct_ma_node_graph(Structure):
    pass

class struct_ma_node_base(Structure):
    pass

class struct_ma_node_vtable(Structure):
    pass

class struct_ma_node_input_bus(Structure):
    pass

class struct_ma_node_output_bus(Structure):
    pass


# values for enumeration 'ma_node_state'
ma_node_state__enumvalues = {
    0: 'ma_node_state_started',
    1: 'ma_node_state_stopped',
}
ma_node_state_started = 0
ma_node_state_stopped = 1
ma_node_state = ctypes.c_uint32 # enum
struct_ma_node_output_bus._pack_ = 1 # source:False
struct_ma_node_output_bus._fields_ = [
    ('pNode', ctypes.POINTER(None)),
    ('outputBusIndex', ctypes.c_ubyte),
    ('channels', ctypes.c_ubyte),
    ('inputNodeInputBusIndex', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
    ('flags', ctypes.c_uint32),
    ('refCount', ctypes.c_uint32),
    ('isAttached', ctypes.c_uint32),
    ('lock', ctypes.c_uint32),
    ('volume', ctypes.c_float),
    ('pNext', ctypes.POINTER(struct_ma_node_output_bus)),
    ('pPrev', ctypes.POINTER(struct_ma_node_output_bus)),
    ('pInputNode', ctypes.POINTER(None)),
]

ma_node_output_bus = struct_ma_node_output_bus
struct_ma_node_input_bus._pack_ = 1 # source:False
struct_ma_node_input_bus._fields_ = [
    ('head', ma_node_output_bus),
    ('nextCounter', ctypes.c_uint32),
    ('lock', ctypes.c_uint32),
    ('channels', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 7),
]

struct_ma_node_base._pack_ = 1 # source:False
struct_ma_node_base._fields_ = [
    ('pNodeGraph', ctypes.POINTER(struct_ma_node_graph)),
    ('vtable', ctypes.POINTER(struct_ma_node_vtable)),
    ('inputBusCount', ctypes.c_uint32),
    ('outputBusCount', ctypes.c_uint32),
    ('pInputBuses', ctypes.POINTER(struct_ma_node_input_bus)),
    ('pOutputBuses', ctypes.POINTER(struct_ma_node_output_bus)),
    ('pCachedData', ctypes.POINTER(ctypes.c_float)),
    ('cachedDataCapInFramesPerBus', ctypes.c_uint16),
    ('cachedFrameCountOut', ctypes.c_uint16),
    ('cachedFrameCountIn', ctypes.c_uint16),
    ('consumedFrameCountIn', ctypes.c_uint16),
    ('state', ma_node_state),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('stateTimes', ctypes.c_uint64 * 2),
    ('localTime', ctypes.c_uint64),
    ('_inputBuses', struct_ma_node_input_bus * 2),
    ('_outputBuses', struct_ma_node_output_bus * 2),
    ('_pHeap', ctypes.POINTER(None)),
    ('_ownsHeap', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

ma_node_base = struct_ma_node_base
struct_ma_node_graph._pack_ = 1 # source:False
struct_ma_node_graph._fields_ = [
    ('base', ma_node_base),
    ('endpoint', ma_node_base),
    ('pProcessingCache', ctypes.POINTER(ctypes.c_float)),
    ('processingCacheFramesRemaining', ctypes.c_uint32),
    ('processingSizeInFrames', ctypes.c_uint32),
    ('isReading', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pPreMixStack', ctypes.POINTER(struct_ma_stack)),
]

ma_node_graph = struct_ma_node_graph
ma_node = None

# values for enumeration 'ma_node_flags'
ma_node_flags__enumvalues = {
    1: 'MA_NODE_FLAG_PASSTHROUGH',
    2: 'MA_NODE_FLAG_CONTINUOUS_PROCESSING',
    4: 'MA_NODE_FLAG_ALLOW_NULL_INPUT',
    8: 'MA_NODE_FLAG_DIFFERENT_PROCESSING_RATES',
    16: 'MA_NODE_FLAG_SILENT_OUTPUT',
}
MA_NODE_FLAG_PASSTHROUGH = 1
MA_NODE_FLAG_CONTINUOUS_PROCESSING = 2
MA_NODE_FLAG_ALLOW_NULL_INPUT = 4
MA_NODE_FLAG_DIFFERENT_PROCESSING_RATES = 8
MA_NODE_FLAG_SILENT_OUTPUT = 16
ma_node_flags = ctypes.c_uint32 # enum
struct_ma_node_vtable._pack_ = 1 # source:False
struct_ma_node_vtable._fields_ = [
    ('onProcess', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.POINTER(ctypes.c_uint32))),
    ('onGetRequiredInputFrameCount', ctypes.CFUNCTYPE(ma_result, ctypes.POINTER(None), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32))),
    ('inputBusCount', ctypes.c_ubyte),
    ('outputBusCount', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('flags', ctypes.c_uint32),
]

ma_node_vtable = struct_ma_node_vtable
class struct_ma_node_config(Structure):
    pass

struct_ma_node_config._pack_ = 1 # source:False
struct_ma_node_config._fields_ = [
    ('vtable', ctypes.POINTER(struct_ma_node_vtable)),
    ('initialState', ma_node_state),
    ('inputBusCount', ctypes.c_uint32),
    ('outputBusCount', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('pInputChannels', ctypes.POINTER(ctypes.c_uint32)),
    ('pOutputChannels', ctypes.POINTER(ctypes.c_uint32)),
]

ma_node_config = struct_ma_node_config
try:
    ma_node_config_init = _libraries['libminiaudio.so'].ma_node_config_init
    ma_node_config_init.restype = ma_node_config
    ma_node_config_init.argtypes = []
except AttributeError:
    pass
ma_node_input_bus = struct_ma_node_input_bus
try:
    ma_node_get_heap_size = _libraries['libminiaudio.so'].ma_node_get_heap_size
    ma_node_get_heap_size.restype = ma_result
    ma_node_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_node_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_node_init_preallocated = _libraries['libminiaudio.so'].ma_node_init_preallocated
    ma_node_init_preallocated.restype = ma_result
    ma_node_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_node_config), ctypes.POINTER(None), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_init = _libraries['libminiaudio.so'].ma_node_init
    ma_node_init.restype = ma_result
    ma_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_uninit = _libraries['libminiaudio.so'].ma_node_uninit
    ma_node_uninit.restype = None
    ma_node_uninit.argtypes = [ctypes.POINTER(None), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_node_get_node_graph = _libraries['libminiaudio.so'].ma_node_get_node_graph
    ma_node_get_node_graph.restype = ctypes.POINTER(struct_ma_node_graph)
    ma_node_get_node_graph.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_get_input_bus_count = _libraries['libminiaudio.so'].ma_node_get_input_bus_count
    ma_node_get_input_bus_count.restype = ma_uint32
    ma_node_get_input_bus_count.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_get_output_bus_count = _libraries['libminiaudio.so'].ma_node_get_output_bus_count
    ma_node_get_output_bus_count.restype = ma_uint32
    ma_node_get_output_bus_count.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_get_input_channels = _libraries['libminiaudio.so'].ma_node_get_input_channels
    ma_node_get_input_channels.restype = ma_uint32
    ma_node_get_input_channels.argtypes = [ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_node_get_output_channels = _libraries['libminiaudio.so'].ma_node_get_output_channels
    ma_node_get_output_channels.restype = ma_uint32
    ma_node_get_output_channels.argtypes = [ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_node_attach_output_bus = _libraries['libminiaudio.so'].ma_node_attach_output_bus
    ma_node_attach_output_bus.restype = ma_result
    ma_node_attach_output_bus.argtypes = [ctypes.POINTER(None), ma_uint32, ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_node_detach_output_bus = _libraries['libminiaudio.so'].ma_node_detach_output_bus
    ma_node_detach_output_bus.restype = ma_result
    ma_node_detach_output_bus.argtypes = [ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_node_detach_all_output_buses = _libraries['libminiaudio.so'].ma_node_detach_all_output_buses
    ma_node_detach_all_output_buses.restype = ma_result
    ma_node_detach_all_output_buses.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_set_output_bus_volume = _libraries['libminiaudio.so'].ma_node_set_output_bus_volume
    ma_node_set_output_bus_volume.restype = ma_result
    ma_node_set_output_bus_volume.argtypes = [ctypes.POINTER(None), ma_uint32, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_node_get_output_bus_volume = _libraries['libminiaudio.so'].ma_node_get_output_bus_volume
    ma_node_get_output_bus_volume.restype = ctypes.c_float
    ma_node_get_output_bus_volume.argtypes = [ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_node_set_state = _libraries['libminiaudio.so'].ma_node_set_state
    ma_node_set_state.restype = ma_result
    ma_node_set_state.argtypes = [ctypes.POINTER(None), ma_node_state]
except AttributeError:
    pass
try:
    ma_node_get_state = _libraries['libminiaudio.so'].ma_node_get_state
    ma_node_get_state.restype = ma_node_state
    ma_node_get_state.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_set_state_time = _libraries['libminiaudio.so'].ma_node_set_state_time
    ma_node_set_state_time.restype = ma_result
    ma_node_set_state_time.argtypes = [ctypes.POINTER(None), ma_node_state, ma_uint64]
except AttributeError:
    pass
try:
    ma_node_get_state_time = _libraries['libminiaudio.so'].ma_node_get_state_time
    ma_node_get_state_time.restype = ma_uint64
    ma_node_get_state_time.argtypes = [ctypes.POINTER(None), ma_node_state]
except AttributeError:
    pass
try:
    ma_node_get_state_by_time = _libraries['libminiaudio.so'].ma_node_get_state_by_time
    ma_node_get_state_by_time.restype = ma_node_state
    ma_node_get_state_by_time.argtypes = [ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
try:
    ma_node_get_state_by_time_range = _libraries['libminiaudio.so'].ma_node_get_state_by_time_range
    ma_node_get_state_by_time_range.restype = ma_node_state
    ma_node_get_state_by_time_range.argtypes = [ctypes.POINTER(None), ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_node_get_time = _libraries['libminiaudio.so'].ma_node_get_time
    ma_node_get_time.restype = ma_uint64
    ma_node_get_time.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_node_set_time = _libraries['libminiaudio.so'].ma_node_set_time
    ma_node_set_time.restype = ma_result
    ma_node_set_time.argtypes = [ctypes.POINTER(None), ma_uint64]
except AttributeError:
    pass
class struct_ma_node_graph_config(Structure):
    pass

struct_ma_node_graph_config._pack_ = 1 # source:False
struct_ma_node_graph_config._fields_ = [
    ('channels', ctypes.c_uint32),
    ('processingSizeInFrames', ctypes.c_uint32),
    ('preMixStackSizeInBytes', ctypes.c_uint64),
]

ma_node_graph_config = struct_ma_node_graph_config
try:
    ma_node_graph_config_init = _libraries['libminiaudio.so'].ma_node_graph_config_init
    ma_node_graph_config_init.restype = ma_node_graph_config
    ma_node_graph_config_init.argtypes = [ma_uint32]
except AttributeError:
    pass
try:
    ma_node_graph_init = _libraries['libminiaudio.so'].ma_node_graph_init
    ma_node_graph_init.restype = ma_result
    ma_node_graph_init.argtypes = [ctypes.POINTER(struct_ma_node_graph_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_node_graph)]
except AttributeError:
    pass
try:
    ma_node_graph_uninit = _libraries['libminiaudio.so'].ma_node_graph_uninit
    ma_node_graph_uninit.restype = None
    ma_node_graph_uninit.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_node_graph_get_endpoint = _libraries['libminiaudio.so'].ma_node_graph_get_endpoint
    ma_node_graph_get_endpoint.restype = ctypes.POINTER(None)
    ma_node_graph_get_endpoint.argtypes = [ctypes.POINTER(struct_ma_node_graph)]
except AttributeError:
    pass
try:
    ma_node_graph_read_pcm_frames = _libraries['libminiaudio.so'].ma_node_graph_read_pcm_frames
    ma_node_graph_read_pcm_frames.restype = ma_result
    ma_node_graph_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_node_graph_get_channels = _libraries['libminiaudio.so'].ma_node_graph_get_channels
    ma_node_graph_get_channels.restype = ma_uint32
    ma_node_graph_get_channels.argtypes = [ctypes.POINTER(struct_ma_node_graph)]
except AttributeError:
    pass
try:
    ma_node_graph_get_time = _libraries['libminiaudio.so'].ma_node_graph_get_time
    ma_node_graph_get_time.restype = ma_uint64
    ma_node_graph_get_time.argtypes = [ctypes.POINTER(struct_ma_node_graph)]
except AttributeError:
    pass
try:
    ma_node_graph_set_time = _libraries['libminiaudio.so'].ma_node_graph_set_time
    ma_node_graph_set_time.restype = ma_result
    ma_node_graph_set_time.argtypes = [ctypes.POINTER(struct_ma_node_graph), ma_uint64]
except AttributeError:
    pass
class struct_ma_data_source_node_config(Structure):
    pass

struct_ma_data_source_node_config._pack_ = 1 # source:False
struct_ma_data_source_node_config._fields_ = [
    ('nodeConfig', ma_node_config),
    ('pDataSource', ctypes.POINTER(None)),
]

ma_data_source_node_config = struct_ma_data_source_node_config
try:
    ma_data_source_node_config_init = _libraries['libminiaudio.so'].ma_data_source_node_config_init
    ma_data_source_node_config_init.restype = ma_data_source_node_config
    ma_data_source_node_config_init.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
class struct_ma_data_source_node(Structure):
    pass

struct_ma_data_source_node._pack_ = 1 # source:False
struct_ma_data_source_node._fields_ = [
    ('base', ma_node_base),
    ('pDataSource', ctypes.POINTER(None)),
]

ma_data_source_node = struct_ma_data_source_node
try:
    ma_data_source_node_init = _libraries['libminiaudio.so'].ma_data_source_node_init
    ma_data_source_node_init.restype = ma_result
    ma_data_source_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_data_source_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_data_source_node)]
except AttributeError:
    pass
try:
    ma_data_source_node_uninit = _libraries['libminiaudio.so'].ma_data_source_node_uninit
    ma_data_source_node_uninit.restype = None
    ma_data_source_node_uninit.argtypes = [ctypes.POINTER(struct_ma_data_source_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_data_source_node_set_looping = _libraries['libminiaudio.so'].ma_data_source_node_set_looping
    ma_data_source_node_set_looping.restype = ma_result
    ma_data_source_node_set_looping.argtypes = [ctypes.POINTER(struct_ma_data_source_node), ma_bool32]
except AttributeError:
    pass
try:
    ma_data_source_node_is_looping = _libraries['libminiaudio.so'].ma_data_source_node_is_looping
    ma_data_source_node_is_looping.restype = ma_bool32
    ma_data_source_node_is_looping.argtypes = [ctypes.POINTER(struct_ma_data_source_node)]
except AttributeError:
    pass
class struct_ma_splitter_node_config(Structure):
    pass

struct_ma_splitter_node_config._pack_ = 1 # source:False
struct_ma_splitter_node_config._fields_ = [
    ('nodeConfig', ma_node_config),
    ('channels', ctypes.c_uint32),
    ('outputBusCount', ctypes.c_uint32),
]

ma_splitter_node_config = struct_ma_splitter_node_config
try:
    ma_splitter_node_config_init = _libraries['libminiaudio.so'].ma_splitter_node_config_init
    ma_splitter_node_config_init.restype = ma_splitter_node_config
    ma_splitter_node_config_init.argtypes = [ma_uint32]
except AttributeError:
    pass
class struct_ma_splitter_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('base', ma_node_base),
     ]

ma_splitter_node = struct_ma_splitter_node
try:
    ma_splitter_node_init = _libraries['libminiaudio.so'].ma_splitter_node_init
    ma_splitter_node_init.restype = ma_result
    ma_splitter_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_splitter_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_splitter_node)]
except AttributeError:
    pass
try:
    ma_splitter_node_uninit = _libraries['libminiaudio.so'].ma_splitter_node_uninit
    ma_splitter_node_uninit.restype = None
    ma_splitter_node_uninit.argtypes = [ctypes.POINTER(struct_ma_splitter_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_biquad_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('biquad', ma_biquad_config),
     ]

ma_biquad_node_config = struct_ma_biquad_node_config
try:
    ma_biquad_node_config_init = _libraries['libminiaudio.so'].ma_biquad_node_config_init
    ma_biquad_node_config_init.restype = ma_biquad_node_config
    ma_biquad_node_config_init.argtypes = [ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
class struct_ma_biquad_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('biquad', ma_biquad),
     ]

ma_biquad_node = struct_ma_biquad_node
try:
    ma_biquad_node_init = _libraries['libminiaudio.so'].ma_biquad_node_init
    ma_biquad_node_init.restype = ma_result
    ma_biquad_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_biquad_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_biquad_node)]
except AttributeError:
    pass
try:
    ma_biquad_node_reinit = _libraries['libminiaudio.so'].ma_biquad_node_reinit
    ma_biquad_node_reinit.restype = ma_result
    ma_biquad_node_reinit.argtypes = [ctypes.POINTER(struct_ma_biquad_config), ctypes.POINTER(struct_ma_biquad_node)]
except AttributeError:
    pass
try:
    ma_biquad_node_uninit = _libraries['libminiaudio.so'].ma_biquad_node_uninit
    ma_biquad_node_uninit.restype = None
    ma_biquad_node_uninit.argtypes = [ctypes.POINTER(struct_ma_biquad_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_lpf_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('lpf', ma_lpf_config),
     ]

ma_lpf_node_config = struct_ma_lpf_node_config
try:
    ma_lpf_node_config_init = _libraries['libminiaudio.so'].ma_lpf_node_config_init
    ma_lpf_node_config_init.restype = ma_lpf_node_config
    ma_lpf_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
class struct_ma_lpf_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('lpf', ma_lpf),
     ]

ma_lpf_node = struct_ma_lpf_node
try:
    ma_lpf_node_init = _libraries['libminiaudio.so'].ma_lpf_node_init
    ma_lpf_node_init.restype = ma_result
    ma_lpf_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_lpf_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_lpf_node)]
except AttributeError:
    pass
try:
    ma_lpf_node_reinit = _libraries['libminiaudio.so'].ma_lpf_node_reinit
    ma_lpf_node_reinit.restype = ma_result
    ma_lpf_node_reinit.argtypes = [ctypes.POINTER(struct_ma_lpf_config), ctypes.POINTER(struct_ma_lpf_node)]
except AttributeError:
    pass
try:
    ma_lpf_node_uninit = _libraries['libminiaudio.so'].ma_lpf_node_uninit
    ma_lpf_node_uninit.restype = None
    ma_lpf_node_uninit.argtypes = [ctypes.POINTER(struct_ma_lpf_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_hpf_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('hpf', ma_hpf_config),
     ]

ma_hpf_node_config = struct_ma_hpf_node_config
try:
    ma_hpf_node_config_init = _libraries['libminiaudio.so'].ma_hpf_node_config_init
    ma_hpf_node_config_init.restype = ma_hpf_node_config
    ma_hpf_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
class struct_ma_hpf_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('hpf', ma_hpf),
     ]

ma_hpf_node = struct_ma_hpf_node
try:
    ma_hpf_node_init = _libraries['libminiaudio.so'].ma_hpf_node_init
    ma_hpf_node_init.restype = ma_result
    ma_hpf_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_hpf_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hpf_node)]
except AttributeError:
    pass
try:
    ma_hpf_node_reinit = _libraries['libminiaudio.so'].ma_hpf_node_reinit
    ma_hpf_node_reinit.restype = ma_result
    ma_hpf_node_reinit.argtypes = [ctypes.POINTER(struct_ma_hpf_config), ctypes.POINTER(struct_ma_hpf_node)]
except AttributeError:
    pass
try:
    ma_hpf_node_uninit = _libraries['libminiaudio.so'].ma_hpf_node_uninit
    ma_hpf_node_uninit.restype = None
    ma_hpf_node_uninit.argtypes = [ctypes.POINTER(struct_ma_hpf_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_bpf_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('bpf', ma_bpf_config),
     ]

ma_bpf_node_config = struct_ma_bpf_node_config
try:
    ma_bpf_node_config_init = _libraries['libminiaudio.so'].ma_bpf_node_config_init
    ma_bpf_node_config_init.restype = ma_bpf_node_config
    ma_bpf_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ma_uint32]
except AttributeError:
    pass
class struct_ma_bpf_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('bpf', ma_bpf),
     ]

ma_bpf_node = struct_ma_bpf_node
try:
    ma_bpf_node_init = _libraries['libminiaudio.so'].ma_bpf_node_init
    ma_bpf_node_init.restype = ma_result
    ma_bpf_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_bpf_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_bpf_node)]
except AttributeError:
    pass
try:
    ma_bpf_node_reinit = _libraries['libminiaudio.so'].ma_bpf_node_reinit
    ma_bpf_node_reinit.restype = ma_result
    ma_bpf_node_reinit.argtypes = [ctypes.POINTER(struct_ma_bpf_config), ctypes.POINTER(struct_ma_bpf_node)]
except AttributeError:
    pass
try:
    ma_bpf_node_uninit = _libraries['libminiaudio.so'].ma_bpf_node_uninit
    ma_bpf_node_uninit.restype = None
    ma_bpf_node_uninit.argtypes = [ctypes.POINTER(struct_ma_bpf_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_notch_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('notch', ma_notch_config),
     ]

ma_notch_node_config = struct_ma_notch_node_config
try:
    ma_notch_node_config_init = _libraries['libminiaudio.so'].ma_notch_node_config_init
    ma_notch_node_config_init.restype = ma_notch_node_config
    ma_notch_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_notch_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('notch', ma_notch2),
     ]

ma_notch_node = struct_ma_notch_node
try:
    ma_notch_node_init = _libraries['libminiaudio.so'].ma_notch_node_init
    ma_notch_node_init.restype = ma_result
    ma_notch_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_notch_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_notch_node)]
except AttributeError:
    pass
try:
    ma_notch_node_reinit = _libraries['libminiaudio.so'].ma_notch_node_reinit
    ma_notch_node_reinit.restype = ma_result
    ma_notch_node_reinit.argtypes = [ctypes.POINTER(struct_ma_notch2_config), ctypes.POINTER(struct_ma_notch_node)]
except AttributeError:
    pass
try:
    ma_notch_node_uninit = _libraries['libminiaudio.so'].ma_notch_node_uninit
    ma_notch_node_uninit.restype = None
    ma_notch_node_uninit.argtypes = [ctypes.POINTER(struct_ma_notch_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_peak_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('peak', ma_peak_config),
     ]

ma_peak_node_config = struct_ma_peak_node_config
try:
    ma_peak_node_config_init = _libraries['libminiaudio.so'].ma_peak_node_config_init
    ma_peak_node_config_init.restype = ma_peak_node_config
    ma_peak_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_peak_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('peak', ma_peak2),
     ]

ma_peak_node = struct_ma_peak_node
try:
    ma_peak_node_init = _libraries['libminiaudio.so'].ma_peak_node_init
    ma_peak_node_init.restype = ma_result
    ma_peak_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_peak_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_peak_node)]
except AttributeError:
    pass
try:
    ma_peak_node_reinit = _libraries['libminiaudio.so'].ma_peak_node_reinit
    ma_peak_node_reinit.restype = ma_result
    ma_peak_node_reinit.argtypes = [ctypes.POINTER(struct_ma_peak2_config), ctypes.POINTER(struct_ma_peak_node)]
except AttributeError:
    pass
try:
    ma_peak_node_uninit = _libraries['libminiaudio.so'].ma_peak_node_uninit
    ma_peak_node_uninit.restype = None
    ma_peak_node_uninit.argtypes = [ctypes.POINTER(struct_ma_peak_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_loshelf_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('loshelf', ma_loshelf_config),
     ]

ma_loshelf_node_config = struct_ma_loshelf_node_config
try:
    ma_loshelf_node_config_init = _libraries['libminiaudio.so'].ma_loshelf_node_config_init
    ma_loshelf_node_config_init.restype = ma_loshelf_node_config
    ma_loshelf_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_loshelf_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('loshelf', ma_loshelf2),
     ]

ma_loshelf_node = struct_ma_loshelf_node
try:
    ma_loshelf_node_init = _libraries['libminiaudio.so'].ma_loshelf_node_init
    ma_loshelf_node_init.restype = ma_result
    ma_loshelf_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_loshelf_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_loshelf_node)]
except AttributeError:
    pass
try:
    ma_loshelf_node_reinit = _libraries['libminiaudio.so'].ma_loshelf_node_reinit
    ma_loshelf_node_reinit.restype = ma_result
    ma_loshelf_node_reinit.argtypes = [ctypes.POINTER(struct_ma_loshelf2_config), ctypes.POINTER(struct_ma_loshelf_node)]
except AttributeError:
    pass
try:
    ma_loshelf_node_uninit = _libraries['libminiaudio.so'].ma_loshelf_node_uninit
    ma_loshelf_node_uninit.restype = None
    ma_loshelf_node_uninit.argtypes = [ctypes.POINTER(struct_ma_loshelf_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_hishelf_node_config(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('nodeConfig', ma_node_config),
    ('hishelf', ma_hishelf_config),
     ]

ma_hishelf_node_config = struct_ma_hishelf_node_config
try:
    ma_hishelf_node_config_init = _libraries['libminiaudio.so'].ma_hishelf_node_config_init
    ma_hishelf_node_config_init.restype = ma_hishelf_node_config
    ma_hishelf_node_config_init.argtypes = [ma_uint32, ma_uint32, ctypes.c_double, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
class struct_ma_hishelf_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('hishelf', ma_hishelf2),
     ]

ma_hishelf_node = struct_ma_hishelf_node
try:
    ma_hishelf_node_init = _libraries['libminiaudio.so'].ma_hishelf_node_init
    ma_hishelf_node_init.restype = ma_result
    ma_hishelf_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_hishelf_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_hishelf_node)]
except AttributeError:
    pass
try:
    ma_hishelf_node_reinit = _libraries['libminiaudio.so'].ma_hishelf_node_reinit
    ma_hishelf_node_reinit.restype = ma_result
    ma_hishelf_node_reinit.argtypes = [ctypes.POINTER(struct_ma_hishelf2_config), ctypes.POINTER(struct_ma_hishelf_node)]
except AttributeError:
    pass
try:
    ma_hishelf_node_uninit = _libraries['libminiaudio.so'].ma_hishelf_node_uninit
    ma_hishelf_node_uninit.restype = None
    ma_hishelf_node_uninit.argtypes = [ctypes.POINTER(struct_ma_hishelf_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
class struct_ma_delay_node_config(Structure):
    pass

struct_ma_delay_node_config._pack_ = 1 # source:False
struct_ma_delay_node_config._fields_ = [
    ('nodeConfig', ma_node_config),
    ('delay', ma_delay_config),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_delay_node_config = struct_ma_delay_node_config
try:
    ma_delay_node_config_init = _libraries['libminiaudio.so'].ma_delay_node_config_init
    ma_delay_node_config_init.restype = ma_delay_node_config
    ma_delay_node_config_init.argtypes = [ma_uint32, ma_uint32, ma_uint32, ctypes.c_float]
except AttributeError:
    pass
class struct_ma_delay_node(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('baseNode', ma_node_base),
    ('delay', ma_delay),
     ]

ma_delay_node = struct_ma_delay_node
try:
    ma_delay_node_init = _libraries['libminiaudio.so'].ma_delay_node_init
    ma_delay_node_init.restype = ma_result
    ma_delay_node_init.argtypes = [ctypes.POINTER(struct_ma_node_graph), ctypes.POINTER(struct_ma_delay_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_delay_node)]
except AttributeError:
    pass
try:
    ma_delay_node_uninit = _libraries['libminiaudio.so'].ma_delay_node_uninit
    ma_delay_node_uninit.restype = None
    ma_delay_node_uninit.argtypes = [ctypes.POINTER(struct_ma_delay_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
try:
    ma_delay_node_set_wet = _libraries['libminiaudio.so'].ma_delay_node_set_wet
    ma_delay_node_set_wet.restype = None
    ma_delay_node_set_wet.argtypes = [ctypes.POINTER(struct_ma_delay_node), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_node_get_wet = _libraries['libminiaudio.so'].ma_delay_node_get_wet
    ma_delay_node_get_wet.restype = ctypes.c_float
    ma_delay_node_get_wet.argtypes = [ctypes.POINTER(struct_ma_delay_node)]
except AttributeError:
    pass
try:
    ma_delay_node_set_dry = _libraries['libminiaudio.so'].ma_delay_node_set_dry
    ma_delay_node_set_dry.restype = None
    ma_delay_node_set_dry.argtypes = [ctypes.POINTER(struct_ma_delay_node), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_node_get_dry = _libraries['libminiaudio.so'].ma_delay_node_get_dry
    ma_delay_node_get_dry.restype = ctypes.c_float
    ma_delay_node_get_dry.argtypes = [ctypes.POINTER(struct_ma_delay_node)]
except AttributeError:
    pass
try:
    ma_delay_node_set_decay = _libraries['libminiaudio.so'].ma_delay_node_set_decay
    ma_delay_node_set_decay.restype = None
    ma_delay_node_set_decay.argtypes = [ctypes.POINTER(struct_ma_delay_node), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_delay_node_get_decay = _libraries['libminiaudio.so'].ma_delay_node_get_decay
    ma_delay_node_get_decay.restype = ctypes.c_float
    ma_delay_node_get_decay.argtypes = [ctypes.POINTER(struct_ma_delay_node)]
except AttributeError:
    pass
class struct_ma_engine(Structure):
    pass

class struct_ma_sound_inlined(Structure):
    pass

struct_ma_engine._pack_ = 1 # source:False
struct_ma_engine._fields_ = [
    ('nodeGraph', ma_node_graph),
    ('pResourceManager', ctypes.POINTER(struct_ma_resource_manager)),
    ('pDevice', ctypes.POINTER(struct_ma_device)),
    ('pLog', ctypes.POINTER(struct_ma_log)),
    ('sampleRate', ctypes.c_uint32),
    ('listenerCount', ctypes.c_uint32),
    ('listeners', struct_ma_spatializer_listener * 4),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('ownsResourceManager', ctypes.c_ubyte),
    ('ownsDevice', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('inlinedSoundLock', ctypes.c_uint32),
    ('pInlinedSoundHead', ctypes.POINTER(struct_ma_sound_inlined)),
    ('inlinedSoundCount', ctypes.c_uint32),
    ('gainSmoothTimeInFrames', ctypes.c_uint32),
    ('defaultVolumeSmoothTimeInPCMFrames', ctypes.c_uint32),
    ('monoExpansionMode', ma_mono_expansion_mode),
    ('onProcess', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_float), ctypes.c_uint64)),
    ('pProcessUserData', ctypes.POINTER(None)),
]

ma_engine = struct_ma_engine
class struct_ma_sound(Structure):
    pass

class struct_ma_engine_node(Structure):
    pass

class struct_ma_engine_node_fadeSettings(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('volumeBeg', ma_atomic_float),
    ('volumeEnd', ma_atomic_float),
    ('fadeLengthInFrames', ma_atomic_uint64),
    ('absoluteGlobalTimeInFrames', ma_atomic_uint64),
     ]

struct_ma_engine_node._pack_ = 1 # source:False
struct_ma_engine_node._fields_ = [
    ('baseNode', ma_node_base),
    ('pEngine', ctypes.POINTER(struct_ma_engine)),
    ('sampleRate', ctypes.c_uint32),
    ('volumeSmoothTimeInPCMFrames', ctypes.c_uint32),
    ('monoExpansionMode', ma_mono_expansion_mode),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('fader', ma_fader),
    ('resampler', ma_linear_resampler),
    ('spatializer', ma_spatializer),
    ('panner', ma_panner),
    ('volumeGainer', ma_gainer),
    ('volume', ma_atomic_float),
    ('pitch', ctypes.c_float),
    ('oldPitch', ctypes.c_float),
    ('oldDopplerPitch', ctypes.c_float),
    ('isPitchDisabled', ctypes.c_uint32),
    ('isSpatializationDisabled', ctypes.c_uint32),
    ('pinnedListenerIndex', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('fadeSettings', struct_ma_engine_node_fadeSettings),
    ('_ownsHeap', ctypes.c_ubyte),
    ('PADDING_2', ctypes.c_ubyte * 7),
    ('_pHeap', ctypes.POINTER(None)),
]

ma_engine_node = struct_ma_engine_node
struct_ma_sound._pack_ = 1 # source:False
struct_ma_sound._fields_ = [
    ('engineNode', ma_engine_node),
    ('pDataSource', ctypes.POINTER(None)),
    ('seekTarget', ctypes.c_uint64),
    ('atEnd', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('endCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(struct_ma_sound))),
    ('pEndCallbackUserData', ctypes.POINTER(None)),
    ('ownsDataSource', ctypes.c_ubyte),
    ('PADDING_1', ctypes.c_ubyte * 7),
    ('pResourceManagerDataSource', ctypes.POINTER(struct_ma_resource_manager_data_source)),
]

ma_sound = struct_ma_sound

# values for enumeration 'ma_sound_flags'
ma_sound_flags__enumvalues = {
    1: 'MA_SOUND_FLAG_STREAM',
    2: 'MA_SOUND_FLAG_DECODE',
    4: 'MA_SOUND_FLAG_ASYNC',
    8: 'MA_SOUND_FLAG_WAIT_INIT',
    16: 'MA_SOUND_FLAG_UNKNOWN_LENGTH',
    32: 'MA_SOUND_FLAG_LOOPING',
    4096: 'MA_SOUND_FLAG_NO_DEFAULT_ATTACHMENT',
    8192: 'MA_SOUND_FLAG_NO_PITCH',
    16384: 'MA_SOUND_FLAG_NO_SPATIALIZATION',
}
MA_SOUND_FLAG_STREAM = 1
MA_SOUND_FLAG_DECODE = 2
MA_SOUND_FLAG_ASYNC = 4
MA_SOUND_FLAG_WAIT_INIT = 8
MA_SOUND_FLAG_UNKNOWN_LENGTH = 16
MA_SOUND_FLAG_LOOPING = 32
MA_SOUND_FLAG_NO_DEFAULT_ATTACHMENT = 4096
MA_SOUND_FLAG_NO_PITCH = 8192
MA_SOUND_FLAG_NO_SPATIALIZATION = 16384
ma_sound_flags = ctypes.c_uint32 # enum

# values for enumeration 'ma_engine_node_type'
ma_engine_node_type__enumvalues = {
    0: 'ma_engine_node_type_sound',
    1: 'ma_engine_node_type_group',
}
ma_engine_node_type_sound = 0
ma_engine_node_type_group = 1
ma_engine_node_type = ctypes.c_uint32 # enum
class struct_ma_engine_node_config(Structure):
    pass

struct_ma_engine_node_config._pack_ = 1 # source:False
struct_ma_engine_node_config._fields_ = [
    ('pEngine', ctypes.POINTER(struct_ma_engine)),
    ('type', ma_engine_node_type),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('volumeSmoothTimeInPCMFrames', ctypes.c_uint32),
    ('monoExpansionMode', ma_mono_expansion_mode),
    ('isPitchDisabled', ctypes.c_ubyte),
    ('isSpatializationDisabled', ctypes.c_ubyte),
    ('pinnedListenerIndex', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 5),
]

ma_engine_node_config = struct_ma_engine_node_config
try:
    ma_engine_node_config_init = _libraries['libminiaudio.so'].ma_engine_node_config_init
    ma_engine_node_config_init.restype = ma_engine_node_config
    ma_engine_node_config_init.argtypes = [ctypes.POINTER(struct_ma_engine), ma_engine_node_type, ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_node_get_heap_size = _libraries['libminiaudio.so'].ma_engine_node_get_heap_size
    ma_engine_node_get_heap_size.restype = ma_result
    ma_engine_node_get_heap_size.argtypes = [ctypes.POINTER(struct_ma_engine_node_config), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_engine_node_init_preallocated = _libraries['libminiaudio.so'].ma_engine_node_init_preallocated
    ma_engine_node_init_preallocated.restype = ma_result
    ma_engine_node_init_preallocated.argtypes = [ctypes.POINTER(struct_ma_engine_node_config), ctypes.POINTER(None), ctypes.POINTER(struct_ma_engine_node)]
except AttributeError:
    pass
try:
    ma_engine_node_init = _libraries['libminiaudio.so'].ma_engine_node_init
    ma_engine_node_init.restype = ma_result
    ma_engine_node_init.argtypes = [ctypes.POINTER(struct_ma_engine_node_config), ctypes.POINTER(struct_ma_allocation_callbacks), ctypes.POINTER(struct_ma_engine_node)]
except AttributeError:
    pass
try:
    ma_engine_node_uninit = _libraries['libminiaudio.so'].ma_engine_node_uninit
    ma_engine_node_uninit.restype = None
    ma_engine_node_uninit.argtypes = [ctypes.POINTER(struct_ma_engine_node), ctypes.POINTER(struct_ma_allocation_callbacks)]
except AttributeError:
    pass
ma_sound_end_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(struct_ma_sound))
class struct_ma_sound_config(Structure):
    pass

struct_ma_sound_config._pack_ = 1 # source:False
struct_ma_sound_config._fields_ = [
    ('pFilePath', ctypes.POINTER(ctypes.c_char)),
    ('pFilePathW', ctypes.POINTER(ctypes.c_int32)),
    ('pDataSource', ctypes.POINTER(None)),
    ('pInitialAttachment', ctypes.POINTER(None)),
    ('initialAttachmentInputBusIndex', ctypes.c_uint32),
    ('channelsIn', ctypes.c_uint32),
    ('channelsOut', ctypes.c_uint32),
    ('monoExpansionMode', ma_mono_expansion_mode),
    ('flags', ctypes.c_uint32),
    ('volumeSmoothTimeInPCMFrames', ctypes.c_uint32),
    ('initialSeekPointInPCMFrames', ctypes.c_uint64),
    ('rangeBegInPCMFrames', ctypes.c_uint64),
    ('rangeEndInPCMFrames', ctypes.c_uint64),
    ('loopPointBegInPCMFrames', ctypes.c_uint64),
    ('loopPointEndInPCMFrames', ctypes.c_uint64),
    ('endCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(struct_ma_sound))),
    ('pEndCallbackUserData', ctypes.POINTER(None)),
    ('initNotifications', ma_resource_manager_pipeline_notifications),
    ('pDoneFence', ctypes.POINTER(struct_ma_fence)),
    ('isLooping', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

ma_sound_config = struct_ma_sound_config
try:
    ma_sound_config_init = _libraries['libminiaudio.so'].ma_sound_config_init
    ma_sound_config_init.restype = ma_sound_config
    ma_sound_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_sound_config_init_2 = _libraries['libminiaudio.so'].ma_sound_config_init_2
    ma_sound_config_init_2.restype = ma_sound_config
    ma_sound_config_init_2.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
struct_ma_sound_inlined._pack_ = 1 # source:False
struct_ma_sound_inlined._fields_ = [
    ('sound', ma_sound),
    ('pNext', ctypes.POINTER(struct_ma_sound_inlined)),
    ('pPrev', ctypes.POINTER(struct_ma_sound_inlined)),
]

ma_sound_inlined = struct_ma_sound_inlined
ma_sound_group_config = struct_ma_sound_config
ma_sound_group = struct_ma_sound
try:
    ma_sound_group_config_init = _libraries['libminiaudio.so'].ma_sound_group_config_init
    ma_sound_group_config_init.restype = ma_sound_group_config
    ma_sound_group_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_sound_group_config_init_2 = _libraries['libminiaudio.so'].ma_sound_group_config_init_2
    ma_sound_group_config_init_2.restype = ma_sound_group_config
    ma_sound_group_config_init_2.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
ma_engine_process_proc = ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_float), ctypes.c_uint64)
class struct_ma_engine_config(Structure):
    pass

struct_ma_engine_config._pack_ = 1 # source:False
struct_ma_engine_config._fields_ = [
    ('pResourceManager', ctypes.POINTER(struct_ma_resource_manager)),
    ('pContext', ctypes.POINTER(struct_ma_context)),
    ('pDevice', ctypes.POINTER(struct_ma_device)),
    ('pPlaybackDeviceID', ctypes.POINTER(union_ma_device_id)),
    ('dataCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)),
    ('notificationCallback', ctypes.CFUNCTYPE(None, ctypes.POINTER(struct_ma_device_notification))),
    ('pLog', ctypes.POINTER(struct_ma_log)),
    ('listenerCount', ctypes.c_uint32),
    ('channels', ctypes.c_uint32),
    ('sampleRate', ctypes.c_uint32),
    ('periodSizeInFrames', ctypes.c_uint32),
    ('periodSizeInMilliseconds', ctypes.c_uint32),
    ('gainSmoothTimeInFrames', ctypes.c_uint32),
    ('gainSmoothTimeInMilliseconds', ctypes.c_uint32),
    ('defaultVolumeSmoothTimeInPCMFrames', ctypes.c_uint32),
    ('preMixStackSizeInBytes', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('allocationCallbacks', ma_allocation_callbacks),
    ('noAutoStart', ctypes.c_uint32),
    ('noDevice', ctypes.c_uint32),
    ('monoExpansionMode', ma_mono_expansion_mode),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('pResourceManagerVFS', ctypes.POINTER(None)),
    ('onProcess', ctypes.CFUNCTYPE(None, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_float), ctypes.c_uint64)),
    ('pProcessUserData', ctypes.POINTER(None)),
]

ma_engine_config = struct_ma_engine_config
try:
    ma_engine_config_init = _libraries['libminiaudio.so'].ma_engine_config_init
    ma_engine_config_init.restype = ma_engine_config
    ma_engine_config_init.argtypes = []
except AttributeError:
    pass
try:
    ma_engine_init = _libraries['libminiaudio.so'].ma_engine_init
    ma_engine_init.restype = ma_result
    ma_engine_init.argtypes = [ctypes.POINTER(struct_ma_engine_config), ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_uninit = _libraries['libminiaudio.so'].ma_engine_uninit
    ma_engine_uninit.restype = None
    ma_engine_uninit.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_read_pcm_frames = _libraries['libminiaudio.so'].ma_engine_read_pcm_frames
    ma_engine_read_pcm_frames.restype = ma_result
    ma_engine_read_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(None), ma_uint64, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_engine_get_node_graph = _libraries['libminiaudio.so'].ma_engine_get_node_graph
    ma_engine_get_node_graph.restype = ctypes.POINTER(struct_ma_node_graph)
    ma_engine_get_node_graph.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_resource_manager = _libraries['libminiaudio.so'].ma_engine_get_resource_manager
    ma_engine_get_resource_manager.restype = ctypes.POINTER(struct_ma_resource_manager)
    ma_engine_get_resource_manager.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_device = _libraries['libminiaudio.so'].ma_engine_get_device
    ma_engine_get_device.restype = ctypes.POINTER(struct_ma_device)
    ma_engine_get_device.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_log = _libraries['libminiaudio.so'].ma_engine_get_log
    ma_engine_get_log.restype = ctypes.POINTER(struct_ma_log)
    ma_engine_get_log.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_endpoint = _libraries['libminiaudio.so'].ma_engine_get_endpoint
    ma_engine_get_endpoint.restype = ctypes.POINTER(None)
    ma_engine_get_endpoint.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_engine_get_time_in_pcm_frames
    ma_engine_get_time_in_pcm_frames.restype = ma_uint64
    ma_engine_get_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_time_in_milliseconds = _libraries['libminiaudio.so'].ma_engine_get_time_in_milliseconds
    ma_engine_get_time_in_milliseconds.restype = ma_uint64
    ma_engine_get_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_set_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_engine_set_time_in_pcm_frames
    ma_engine_set_time_in_pcm_frames.restype = ma_result
    ma_engine_set_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint64]
except AttributeError:
    pass
try:
    ma_engine_set_time_in_milliseconds = _libraries['libminiaudio.so'].ma_engine_set_time_in_milliseconds
    ma_engine_set_time_in_milliseconds.restype = ma_result
    ma_engine_set_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint64]
except AttributeError:
    pass
try:
    ma_engine_get_time = _libraries['libminiaudio.so'].ma_engine_get_time
    ma_engine_get_time.restype = ma_uint64
    ma_engine_get_time.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_set_time = _libraries['libminiaudio.so'].ma_engine_set_time
    ma_engine_set_time.restype = ma_result
    ma_engine_set_time.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint64]
except AttributeError:
    pass
try:
    ma_engine_get_channels = _libraries['libminiaudio.so'].ma_engine_get_channels
    ma_engine_get_channels.restype = ma_uint32
    ma_engine_get_channels.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_sample_rate = _libraries['libminiaudio.so'].ma_engine_get_sample_rate
    ma_engine_get_sample_rate.restype = ma_uint32
    ma_engine_get_sample_rate.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_start = _libraries['libminiaudio.so'].ma_engine_start
    ma_engine_start.restype = ma_result
    ma_engine_start.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_stop = _libraries['libminiaudio.so'].ma_engine_stop
    ma_engine_stop.restype = ma_result
    ma_engine_stop.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_set_volume = _libraries['libminiaudio.so'].ma_engine_set_volume
    ma_engine_set_volume.restype = ma_result
    ma_engine_set_volume.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_get_volume = _libraries['libminiaudio.so'].ma_engine_get_volume
    ma_engine_get_volume.restype = ctypes.c_float
    ma_engine_get_volume.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_set_gain_db = _libraries['libminiaudio.so'].ma_engine_set_gain_db
    ma_engine_set_gain_db.restype = ma_result
    ma_engine_set_gain_db.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_get_gain_db = _libraries['libminiaudio.so'].ma_engine_get_gain_db
    ma_engine_get_gain_db.restype = ctypes.c_float
    ma_engine_get_gain_db.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_get_listener_count = _libraries['libminiaudio.so'].ma_engine_get_listener_count
    ma_engine_get_listener_count.restype = ma_uint32
    ma_engine_get_listener_count.argtypes = [ctypes.POINTER(struct_ma_engine)]
except AttributeError:
    pass
try:
    ma_engine_find_closest_listener = _libraries['libminiaudio.so'].ma_engine_find_closest_listener
    ma_engine_find_closest_listener.restype = ma_uint32
    ma_engine_find_closest_listener.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_set_position = _libraries['libminiaudio.so'].ma_engine_listener_set_position
    ma_engine_listener_set_position.restype = None
    ma_engine_listener_set_position.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_get_position = _libraries['libminiaudio.so'].ma_engine_listener_get_position
    ma_engine_listener_get_position.restype = ma_vec3f
    ma_engine_listener_get_position.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_listener_set_direction = _libraries['libminiaudio.so'].ma_engine_listener_set_direction
    ma_engine_listener_set_direction.restype = None
    ma_engine_listener_set_direction.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_get_direction = _libraries['libminiaudio.so'].ma_engine_listener_get_direction
    ma_engine_listener_get_direction.restype = ma_vec3f
    ma_engine_listener_get_direction.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_listener_set_velocity = _libraries['libminiaudio.so'].ma_engine_listener_set_velocity
    ma_engine_listener_set_velocity.restype = None
    ma_engine_listener_set_velocity.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_get_velocity = _libraries['libminiaudio.so'].ma_engine_listener_get_velocity
    ma_engine_listener_get_velocity.restype = ma_vec3f
    ma_engine_listener_get_velocity.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_listener_set_cone = _libraries['libminiaudio.so'].ma_engine_listener_set_cone
    ma_engine_listener_set_cone.restype = None
    ma_engine_listener_set_cone.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_get_cone = _libraries['libminiaudio.so'].ma_engine_listener_get_cone
    ma_engine_listener_get_cone.restype = None
    ma_engine_listener_get_cone.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_engine_listener_set_world_up = _libraries['libminiaudio.so'].ma_engine_listener_set_world_up
    ma_engine_listener_set_world_up.restype = None
    ma_engine_listener_set_world_up.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_engine_listener_get_world_up = _libraries['libminiaudio.so'].ma_engine_listener_get_world_up
    ma_engine_listener_get_world_up.restype = ma_vec3f
    ma_engine_listener_get_world_up.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_listener_set_enabled = _libraries['libminiaudio.so'].ma_engine_listener_set_enabled
    ma_engine_listener_set_enabled.restype = None
    ma_engine_listener_set_enabled.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ma_bool32]
except AttributeError:
    pass
try:
    ma_engine_listener_is_enabled = _libraries['libminiaudio.so'].ma_engine_listener_is_enabled
    ma_engine_listener_is_enabled.restype = ma_bool32
    ma_engine_listener_is_enabled.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_play_sound_ex = _libraries['libminiaudio.so'].ma_engine_play_sound_ex
    ma_engine_play_sound_ex.restype = ma_result
    ma_engine_play_sound_ex.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(None), ma_uint32]
except AttributeError:
    pass
try:
    ma_engine_play_sound = _libraries['libminiaudio.so'].ma_engine_play_sound
    ma_engine_play_sound.restype = ma_result
    ma_engine_play_sound.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_init_from_file = _libraries['libminiaudio.so'].ma_sound_init_from_file
    ma_sound_init_from_file.restype = ma_result
    ma_sound_init_from_file.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(ctypes.c_char), ma_uint32, ctypes.POINTER(struct_ma_sound), ctypes.POINTER(struct_ma_fence), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_init_from_file_w = _libraries['libminiaudio.so'].ma_sound_init_from_file_w
    ma_sound_init_from_file_w.restype = ma_result
    ma_sound_init_from_file_w.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(ctypes.c_int32), ma_uint32, ctypes.POINTER(struct_ma_sound), ctypes.POINTER(struct_ma_fence), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_init_copy = _libraries['libminiaudio.so'].ma_sound_init_copy
    ma_sound_init_copy.restype = ma_result
    ma_sound_init_copy.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(struct_ma_sound), ma_uint32, ctypes.POINTER(struct_ma_sound), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_init_from_data_source = _libraries['libminiaudio.so'].ma_sound_init_from_data_source
    ma_sound_init_from_data_source.restype = ma_result
    ma_sound_init_from_data_source.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(None), ma_uint32, ctypes.POINTER(struct_ma_sound), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_init_ex = _libraries['libminiaudio.so'].ma_sound_init_ex
    ma_sound_init_ex.restype = ma_result
    ma_sound_init_ex.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(struct_ma_sound_config), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_uninit = _libraries['libminiaudio.so'].ma_sound_uninit
    ma_sound_uninit.restype = None
    ma_sound_uninit.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_engine = _libraries['libminiaudio.so'].ma_sound_get_engine
    ma_sound_get_engine.restype = ctypes.POINTER(struct_ma_engine)
    ma_sound_get_engine.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_data_source = _libraries['libminiaudio.so'].ma_sound_get_data_source
    ma_sound_get_data_source.restype = ctypes.POINTER(None)
    ma_sound_get_data_source.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_start = _libraries['libminiaudio.so'].ma_sound_start
    ma_sound_start.restype = ma_result
    ma_sound_start.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_stop = _libraries['libminiaudio.so'].ma_sound_stop
    ma_sound_stop.restype = ma_result
    ma_sound_stop.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_stop_with_fade_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_stop_with_fade_in_pcm_frames
    ma_sound_stop_with_fade_in_pcm_frames.restype = ma_result
    ma_sound_stop_with_fade_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_stop_with_fade_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_stop_with_fade_in_milliseconds
    ma_sound_stop_with_fade_in_milliseconds.restype = ma_result
    ma_sound_stop_with_fade_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_volume = _libraries['libminiaudio.so'].ma_sound_set_volume
    ma_sound_set_volume.restype = None
    ma_sound_set_volume.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_volume = _libraries['libminiaudio.so'].ma_sound_get_volume
    ma_sound_get_volume.restype = ctypes.c_float
    ma_sound_get_volume.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_pan = _libraries['libminiaudio.so'].ma_sound_set_pan
    ma_sound_set_pan.restype = None
    ma_sound_set_pan.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_pan = _libraries['libminiaudio.so'].ma_sound_get_pan
    ma_sound_get_pan.restype = ctypes.c_float
    ma_sound_get_pan.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_pan_mode = _libraries['libminiaudio.so'].ma_sound_set_pan_mode
    ma_sound_set_pan_mode.restype = None
    ma_sound_set_pan_mode.argtypes = [ctypes.POINTER(struct_ma_sound), ma_pan_mode]
except AttributeError:
    pass
try:
    ma_sound_get_pan_mode = _libraries['libminiaudio.so'].ma_sound_get_pan_mode
    ma_sound_get_pan_mode.restype = ma_pan_mode
    ma_sound_get_pan_mode.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_pitch = _libraries['libminiaudio.so'].ma_sound_set_pitch
    ma_sound_set_pitch.restype = None
    ma_sound_set_pitch.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_pitch = _libraries['libminiaudio.so'].ma_sound_get_pitch
    ma_sound_get_pitch.restype = ctypes.c_float
    ma_sound_get_pitch.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_spatialization_enabled = _libraries['libminiaudio.so'].ma_sound_set_spatialization_enabled
    ma_sound_set_spatialization_enabled.restype = None
    ma_sound_set_spatialization_enabled.argtypes = [ctypes.POINTER(struct_ma_sound), ma_bool32]
except AttributeError:
    pass
try:
    ma_sound_is_spatialization_enabled = _libraries['libminiaudio.so'].ma_sound_is_spatialization_enabled
    ma_sound_is_spatialization_enabled.restype = ma_bool32
    ma_sound_is_spatialization_enabled.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_pinned_listener_index = _libraries['libminiaudio.so'].ma_sound_set_pinned_listener_index
    ma_sound_set_pinned_listener_index.restype = None
    ma_sound_set_pinned_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint32]
except AttributeError:
    pass
try:
    ma_sound_get_pinned_listener_index = _libraries['libminiaudio.so'].ma_sound_get_pinned_listener_index
    ma_sound_get_pinned_listener_index.restype = ma_uint32
    ma_sound_get_pinned_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_listener_index = _libraries['libminiaudio.so'].ma_sound_get_listener_index
    ma_sound_get_listener_index.restype = ma_uint32
    ma_sound_get_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_direction_to_listener = _libraries['libminiaudio.so'].ma_sound_get_direction_to_listener
    ma_sound_get_direction_to_listener.restype = ma_vec3f
    ma_sound_get_direction_to_listener.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_position = _libraries['libminiaudio.so'].ma_sound_set_position
    ma_sound_set_position.restype = None
    ma_sound_set_position.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_position = _libraries['libminiaudio.so'].ma_sound_get_position
    ma_sound_get_position.restype = ma_vec3f
    ma_sound_get_position.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_direction = _libraries['libminiaudio.so'].ma_sound_set_direction
    ma_sound_set_direction.restype = None
    ma_sound_set_direction.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_direction = _libraries['libminiaudio.so'].ma_sound_get_direction
    ma_sound_get_direction.restype = ma_vec3f
    ma_sound_get_direction.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_velocity = _libraries['libminiaudio.so'].ma_sound_set_velocity
    ma_sound_set_velocity.restype = None
    ma_sound_set_velocity.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_velocity = _libraries['libminiaudio.so'].ma_sound_get_velocity
    ma_sound_get_velocity.restype = ma_vec3f
    ma_sound_get_velocity.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_attenuation_model = _libraries['libminiaudio.so'].ma_sound_set_attenuation_model
    ma_sound_set_attenuation_model.restype = None
    ma_sound_set_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_sound), ma_attenuation_model]
except AttributeError:
    pass
try:
    ma_sound_get_attenuation_model = _libraries['libminiaudio.so'].ma_sound_get_attenuation_model
    ma_sound_get_attenuation_model.restype = ma_attenuation_model
    ma_sound_get_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_positioning = _libraries['libminiaudio.so'].ma_sound_set_positioning
    ma_sound_set_positioning.restype = None
    ma_sound_set_positioning.argtypes = [ctypes.POINTER(struct_ma_sound), ma_positioning]
except AttributeError:
    pass
try:
    ma_sound_get_positioning = _libraries['libminiaudio.so'].ma_sound_get_positioning
    ma_sound_get_positioning.restype = ma_positioning
    ma_sound_get_positioning.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_rolloff = _libraries['libminiaudio.so'].ma_sound_set_rolloff
    ma_sound_set_rolloff.restype = None
    ma_sound_set_rolloff.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_rolloff = _libraries['libminiaudio.so'].ma_sound_get_rolloff
    ma_sound_get_rolloff.restype = ctypes.c_float
    ma_sound_get_rolloff.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_min_gain = _libraries['libminiaudio.so'].ma_sound_set_min_gain
    ma_sound_set_min_gain.restype = None
    ma_sound_set_min_gain.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_min_gain = _libraries['libminiaudio.so'].ma_sound_get_min_gain
    ma_sound_get_min_gain.restype = ctypes.c_float
    ma_sound_get_min_gain.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_max_gain = _libraries['libminiaudio.so'].ma_sound_set_max_gain
    ma_sound_set_max_gain.restype = None
    ma_sound_set_max_gain.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_max_gain = _libraries['libminiaudio.so'].ma_sound_get_max_gain
    ma_sound_get_max_gain.restype = ctypes.c_float
    ma_sound_get_max_gain.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_min_distance = _libraries['libminiaudio.so'].ma_sound_set_min_distance
    ma_sound_set_min_distance.restype = None
    ma_sound_set_min_distance.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_min_distance = _libraries['libminiaudio.so'].ma_sound_get_min_distance
    ma_sound_get_min_distance.restype = ctypes.c_float
    ma_sound_get_min_distance.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_max_distance = _libraries['libminiaudio.so'].ma_sound_set_max_distance
    ma_sound_set_max_distance.restype = None
    ma_sound_set_max_distance.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_max_distance = _libraries['libminiaudio.so'].ma_sound_get_max_distance
    ma_sound_get_max_distance.restype = ctypes.c_float
    ma_sound_get_max_distance.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_cone = _libraries['libminiaudio.so'].ma_sound_set_cone
    ma_sound_set_cone.restype = None
    ma_sound_set_cone.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_cone = _libraries['libminiaudio.so'].ma_sound_get_cone
    ma_sound_get_cone.restype = None
    ma_sound_get_cone.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_sound_set_doppler_factor = _libraries['libminiaudio.so'].ma_sound_set_doppler_factor
    ma_sound_set_doppler_factor.restype = None
    ma_sound_set_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_doppler_factor = _libraries['libminiaudio.so'].ma_sound_get_doppler_factor
    ma_sound_get_doppler_factor.restype = ctypes.c_float
    ma_sound_get_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_sound_set_directional_attenuation_factor
    ma_sound_set_directional_attenuation_factor.restype = None
    ma_sound_set_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_sound_get_directional_attenuation_factor
    ma_sound_get_directional_attenuation_factor.restype = ctypes.c_float
    ma_sound_get_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_fade_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_set_fade_in_pcm_frames
    ma_sound_set_fade_in_pcm_frames.restype = None
    ma_sound_set_fade_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_fade_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_set_fade_in_milliseconds
    ma_sound_set_fade_in_milliseconds.restype = None
    ma_sound_set_fade_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_fade_start_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_set_fade_start_in_pcm_frames
    ma_sound_set_fade_start_in_pcm_frames.restype = None
    ma_sound_set_fade_start_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_fade_start_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_set_fade_start_in_milliseconds
    ma_sound_set_fade_start_in_milliseconds.restype = None
    ma_sound_set_fade_start_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_get_current_fade_volume = _libraries['libminiaudio.so'].ma_sound_get_current_fade_volume
    ma_sound_get_current_fade_volume.restype = ctypes.c_float
    ma_sound_get_current_fade_volume.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_start_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_set_start_time_in_pcm_frames
    ma_sound_set_start_time_in_pcm_frames.restype = None
    ma_sound_set_start_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_start_time_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_set_start_time_in_milliseconds
    ma_sound_set_start_time_in_milliseconds.restype = None
    ma_sound_set_start_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_stop_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_set_stop_time_in_pcm_frames
    ma_sound_set_stop_time_in_pcm_frames.restype = None
    ma_sound_set_stop_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_stop_time_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_set_stop_time_in_milliseconds
    ma_sound_set_stop_time_in_milliseconds.restype = None
    ma_sound_set_stop_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_stop_time_with_fade_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_set_stop_time_with_fade_in_pcm_frames
    ma_sound_set_stop_time_with_fade_in_pcm_frames.restype = None
    ma_sound_set_stop_time_with_fade_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_set_stop_time_with_fade_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_set_stop_time_with_fade_in_milliseconds
    ma_sound_set_stop_time_with_fade_in_milliseconds.restype = None
    ma_sound_set_stop_time_with_fade_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_is_playing = _libraries['libminiaudio.so'].ma_sound_is_playing
    ma_sound_is_playing.restype = ma_bool32
    ma_sound_is_playing.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_get_time_in_pcm_frames
    ma_sound_get_time_in_pcm_frames.restype = ma_uint64
    ma_sound_get_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_get_time_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_get_time_in_milliseconds
    ma_sound_get_time_in_milliseconds.restype = ma_uint64
    ma_sound_get_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_set_looping = _libraries['libminiaudio.so'].ma_sound_set_looping
    ma_sound_set_looping.restype = None
    ma_sound_set_looping.argtypes = [ctypes.POINTER(struct_ma_sound), ma_bool32]
except AttributeError:
    pass
try:
    ma_sound_is_looping = _libraries['libminiaudio.so'].ma_sound_is_looping
    ma_sound_is_looping.restype = ma_bool32
    ma_sound_is_looping.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_at_end = _libraries['libminiaudio.so'].ma_sound_at_end
    ma_sound_at_end.restype = ma_bool32
    ma_sound_at_end.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_seek_to_pcm_frame = _libraries['libminiaudio.so'].ma_sound_seek_to_pcm_frame
    ma_sound_seek_to_pcm_frame.restype = ma_result
    ma_sound_seek_to_pcm_frame.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_seek_to_second = _libraries['libminiaudio.so'].ma_sound_seek_to_second
    ma_sound_seek_to_second.restype = ma_result
    ma_sound_seek_to_second.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_get_data_format = _libraries['libminiaudio.so'].ma_sound_get_data_format
    ma_sound_get_data_format.restype = ma_result
    ma_sound_get_data_format.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ma_format), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_ubyte), size_t]
except AttributeError:
    pass
try:
    ma_sound_get_cursor_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_get_cursor_in_pcm_frames
    ma_sound_get_cursor_in_pcm_frames.restype = ma_result
    ma_sound_get_cursor_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_sound_get_length_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_get_length_in_pcm_frames
    ma_sound_get_length_in_pcm_frames.restype = ma_result
    ma_sound_get_length_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    ma_sound_get_cursor_in_seconds = _libraries['libminiaudio.so'].ma_sound_get_cursor_in_seconds
    ma_sound_get_cursor_in_seconds.restype = ma_result
    ma_sound_get_cursor_in_seconds.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_sound_get_length_in_seconds = _libraries['libminiaudio.so'].ma_sound_get_length_in_seconds
    ma_sound_get_length_in_seconds.restype = ma_result
    ma_sound_get_length_in_seconds.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_sound_set_end_callback = _libraries['libminiaudio.so'].ma_sound_set_end_callback
    ma_sound_set_end_callback.restype = ma_result
    ma_sound_set_end_callback.argtypes = [ctypes.POINTER(struct_ma_sound), ma_sound_end_proc, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    ma_sound_group_init = _libraries['libminiaudio.so'].ma_sound_group_init
    ma_sound_group_init.restype = ma_result
    ma_sound_group_init.argtypes = [ctypes.POINTER(struct_ma_engine), ma_uint32, ctypes.POINTER(struct_ma_sound), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_init_ex = _libraries['libminiaudio.so'].ma_sound_group_init_ex
    ma_sound_group_init_ex.restype = ma_result
    ma_sound_group_init_ex.argtypes = [ctypes.POINTER(struct_ma_engine), ctypes.POINTER(struct_ma_sound_config), ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_uninit = _libraries['libminiaudio.so'].ma_sound_group_uninit
    ma_sound_group_uninit.restype = None
    ma_sound_group_uninit.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_get_engine = _libraries['libminiaudio.so'].ma_sound_group_get_engine
    ma_sound_group_get_engine.restype = ctypes.POINTER(struct_ma_engine)
    ma_sound_group_get_engine.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_start = _libraries['libminiaudio.so'].ma_sound_group_start
    ma_sound_group_start.restype = ma_result
    ma_sound_group_start.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_stop = _libraries['libminiaudio.so'].ma_sound_group_stop
    ma_sound_group_stop.restype = ma_result
    ma_sound_group_stop.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_volume = _libraries['libminiaudio.so'].ma_sound_group_set_volume
    ma_sound_group_set_volume.restype = None
    ma_sound_group_set_volume.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_volume = _libraries['libminiaudio.so'].ma_sound_group_get_volume
    ma_sound_group_get_volume.restype = ctypes.c_float
    ma_sound_group_get_volume.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_pan = _libraries['libminiaudio.so'].ma_sound_group_set_pan
    ma_sound_group_set_pan.restype = None
    ma_sound_group_set_pan.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_pan = _libraries['libminiaudio.so'].ma_sound_group_get_pan
    ma_sound_group_get_pan.restype = ctypes.c_float
    ma_sound_group_get_pan.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_pan_mode = _libraries['libminiaudio.so'].ma_sound_group_set_pan_mode
    ma_sound_group_set_pan_mode.restype = None
    ma_sound_group_set_pan_mode.argtypes = [ctypes.POINTER(struct_ma_sound), ma_pan_mode]
except AttributeError:
    pass
try:
    ma_sound_group_get_pan_mode = _libraries['libminiaudio.so'].ma_sound_group_get_pan_mode
    ma_sound_group_get_pan_mode.restype = ma_pan_mode
    ma_sound_group_get_pan_mode.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_pitch = _libraries['libminiaudio.so'].ma_sound_group_set_pitch
    ma_sound_group_set_pitch.restype = None
    ma_sound_group_set_pitch.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_pitch = _libraries['libminiaudio.so'].ma_sound_group_get_pitch
    ma_sound_group_get_pitch.restype = ctypes.c_float
    ma_sound_group_get_pitch.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_spatialization_enabled = _libraries['libminiaudio.so'].ma_sound_group_set_spatialization_enabled
    ma_sound_group_set_spatialization_enabled.restype = None
    ma_sound_group_set_spatialization_enabled.argtypes = [ctypes.POINTER(struct_ma_sound), ma_bool32]
except AttributeError:
    pass
try:
    ma_sound_group_is_spatialization_enabled = _libraries['libminiaudio.so'].ma_sound_group_is_spatialization_enabled
    ma_sound_group_is_spatialization_enabled.restype = ma_bool32
    ma_sound_group_is_spatialization_enabled.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_pinned_listener_index = _libraries['libminiaudio.so'].ma_sound_group_set_pinned_listener_index
    ma_sound_group_set_pinned_listener_index.restype = None
    ma_sound_group_set_pinned_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint32]
except AttributeError:
    pass
try:
    ma_sound_group_get_pinned_listener_index = _libraries['libminiaudio.so'].ma_sound_group_get_pinned_listener_index
    ma_sound_group_get_pinned_listener_index.restype = ma_uint32
    ma_sound_group_get_pinned_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_get_listener_index = _libraries['libminiaudio.so'].ma_sound_group_get_listener_index
    ma_sound_group_get_listener_index.restype = ma_uint32
    ma_sound_group_get_listener_index.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_get_direction_to_listener = _libraries['libminiaudio.so'].ma_sound_group_get_direction_to_listener
    ma_sound_group_get_direction_to_listener.restype = ma_vec3f
    ma_sound_group_get_direction_to_listener.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_position = _libraries['libminiaudio.so'].ma_sound_group_set_position
    ma_sound_group_set_position.restype = None
    ma_sound_group_set_position.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_position = _libraries['libminiaudio.so'].ma_sound_group_get_position
    ma_sound_group_get_position.restype = ma_vec3f
    ma_sound_group_get_position.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_direction = _libraries['libminiaudio.so'].ma_sound_group_set_direction
    ma_sound_group_set_direction.restype = None
    ma_sound_group_set_direction.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_direction = _libraries['libminiaudio.so'].ma_sound_group_get_direction
    ma_sound_group_get_direction.restype = ma_vec3f
    ma_sound_group_get_direction.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_velocity = _libraries['libminiaudio.so'].ma_sound_group_set_velocity
    ma_sound_group_set_velocity.restype = None
    ma_sound_group_set_velocity.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_velocity = _libraries['libminiaudio.so'].ma_sound_group_get_velocity
    ma_sound_group_get_velocity.restype = ma_vec3f
    ma_sound_group_get_velocity.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_attenuation_model = _libraries['libminiaudio.so'].ma_sound_group_set_attenuation_model
    ma_sound_group_set_attenuation_model.restype = None
    ma_sound_group_set_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_sound), ma_attenuation_model]
except AttributeError:
    pass
try:
    ma_sound_group_get_attenuation_model = _libraries['libminiaudio.so'].ma_sound_group_get_attenuation_model
    ma_sound_group_get_attenuation_model.restype = ma_attenuation_model
    ma_sound_group_get_attenuation_model.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_positioning = _libraries['libminiaudio.so'].ma_sound_group_set_positioning
    ma_sound_group_set_positioning.restype = None
    ma_sound_group_set_positioning.argtypes = [ctypes.POINTER(struct_ma_sound), ma_positioning]
except AttributeError:
    pass
try:
    ma_sound_group_get_positioning = _libraries['libminiaudio.so'].ma_sound_group_get_positioning
    ma_sound_group_get_positioning.restype = ma_positioning
    ma_sound_group_get_positioning.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_rolloff = _libraries['libminiaudio.so'].ma_sound_group_set_rolloff
    ma_sound_group_set_rolloff.restype = None
    ma_sound_group_set_rolloff.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_rolloff = _libraries['libminiaudio.so'].ma_sound_group_get_rolloff
    ma_sound_group_get_rolloff.restype = ctypes.c_float
    ma_sound_group_get_rolloff.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_min_gain = _libraries['libminiaudio.so'].ma_sound_group_set_min_gain
    ma_sound_group_set_min_gain.restype = None
    ma_sound_group_set_min_gain.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_min_gain = _libraries['libminiaudio.so'].ma_sound_group_get_min_gain
    ma_sound_group_get_min_gain.restype = ctypes.c_float
    ma_sound_group_get_min_gain.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_max_gain = _libraries['libminiaudio.so'].ma_sound_group_set_max_gain
    ma_sound_group_set_max_gain.restype = None
    ma_sound_group_set_max_gain.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_max_gain = _libraries['libminiaudio.so'].ma_sound_group_get_max_gain
    ma_sound_group_get_max_gain.restype = ctypes.c_float
    ma_sound_group_get_max_gain.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_min_distance = _libraries['libminiaudio.so'].ma_sound_group_set_min_distance
    ma_sound_group_set_min_distance.restype = None
    ma_sound_group_set_min_distance.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_min_distance = _libraries['libminiaudio.so'].ma_sound_group_get_min_distance
    ma_sound_group_get_min_distance.restype = ctypes.c_float
    ma_sound_group_get_min_distance.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_max_distance = _libraries['libminiaudio.so'].ma_sound_group_set_max_distance
    ma_sound_group_set_max_distance.restype = None
    ma_sound_group_set_max_distance.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_max_distance = _libraries['libminiaudio.so'].ma_sound_group_get_max_distance
    ma_sound_group_get_max_distance.restype = ctypes.c_float
    ma_sound_group_get_max_distance.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_cone = _libraries['libminiaudio.so'].ma_sound_group_set_cone
    ma_sound_group_set_cone.restype = None
    ma_sound_group_set_cone.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_cone = _libraries['libminiaudio.so'].ma_sound_group_get_cone
    ma_sound_group_get_cone.restype = None
    ma_sound_group_get_cone.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
except AttributeError:
    pass
try:
    ma_sound_group_set_doppler_factor = _libraries['libminiaudio.so'].ma_sound_group_set_doppler_factor
    ma_sound_group_set_doppler_factor.restype = None
    ma_sound_group_set_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_doppler_factor = _libraries['libminiaudio.so'].ma_sound_group_get_doppler_factor
    ma_sound_group_get_doppler_factor.restype = ctypes.c_float
    ma_sound_group_get_doppler_factor.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_sound_group_set_directional_attenuation_factor
    ma_sound_group_set_directional_attenuation_factor.restype = None
    ma_sound_group_set_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float]
except AttributeError:
    pass
try:
    ma_sound_group_get_directional_attenuation_factor = _libraries['libminiaudio.so'].ma_sound_group_get_directional_attenuation_factor
    ma_sound_group_get_directional_attenuation_factor.restype = ctypes.c_float
    ma_sound_group_get_directional_attenuation_factor.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_fade_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_group_set_fade_in_pcm_frames
    ma_sound_group_set_fade_in_pcm_frames.restype = None
    ma_sound_group_set_fade_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_set_fade_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_group_set_fade_in_milliseconds
    ma_sound_group_set_fade_in_milliseconds.restype = None
    ma_sound_group_set_fade_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ctypes.c_float, ctypes.c_float, ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_get_current_fade_volume = _libraries['libminiaudio.so'].ma_sound_group_get_current_fade_volume
    ma_sound_group_get_current_fade_volume.restype = ctypes.c_float
    ma_sound_group_get_current_fade_volume.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_set_start_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_group_set_start_time_in_pcm_frames
    ma_sound_group_set_start_time_in_pcm_frames.restype = None
    ma_sound_group_set_start_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_set_start_time_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_group_set_start_time_in_milliseconds
    ma_sound_group_set_start_time_in_milliseconds.restype = None
    ma_sound_group_set_start_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_set_stop_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_group_set_stop_time_in_pcm_frames
    ma_sound_group_set_stop_time_in_pcm_frames.restype = None
    ma_sound_group_set_stop_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_set_stop_time_in_milliseconds = _libraries['libminiaudio.so'].ma_sound_group_set_stop_time_in_milliseconds
    ma_sound_group_set_stop_time_in_milliseconds.restype = None
    ma_sound_group_set_stop_time_in_milliseconds.argtypes = [ctypes.POINTER(struct_ma_sound), ma_uint64]
except AttributeError:
    pass
try:
    ma_sound_group_is_playing = _libraries['libminiaudio.so'].ma_sound_group_is_playing
    ma_sound_group_is_playing.restype = ma_bool32
    ma_sound_group_is_playing.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
try:
    ma_sound_group_get_time_in_pcm_frames = _libraries['libminiaudio.so'].ma_sound_group_get_time_in_pcm_frames
    ma_sound_group_get_time_in_pcm_frames.restype = ma_uint64
    ma_sound_group_get_time_in_pcm_frames.argtypes = [ctypes.POINTER(struct_ma_sound)]
except AttributeError:
    pass
__all__ = \
    ['MA_ACCESS_DENIED', 'MA_ADDRESS_FAMILY_NOT_SUPPORTED',
    'MA_ALREADY_CONNECTED', 'MA_ALREADY_EXISTS', 'MA_ALREADY_IN_USE',
    'MA_API_NOT_FOUND', 'MA_AT_END', 'MA_BACKEND_NOT_ENABLED',
    'MA_BAD_ADDRESS', 'MA_BAD_MESSAGE', 'MA_BAD_PIPE',
    'MA_BAD_PROTOCOL', 'MA_BAD_SEEK', 'MA_BUSY', 'MA_CANCELLED',
    'MA_CHANNEL_AUX_0', 'MA_CHANNEL_AUX_1', 'MA_CHANNEL_AUX_10',
    'MA_CHANNEL_AUX_11', 'MA_CHANNEL_AUX_12', 'MA_CHANNEL_AUX_13',
    'MA_CHANNEL_AUX_14', 'MA_CHANNEL_AUX_15', 'MA_CHANNEL_AUX_16',
    'MA_CHANNEL_AUX_17', 'MA_CHANNEL_AUX_18', 'MA_CHANNEL_AUX_19',
    'MA_CHANNEL_AUX_2', 'MA_CHANNEL_AUX_20', 'MA_CHANNEL_AUX_21',
    'MA_CHANNEL_AUX_22', 'MA_CHANNEL_AUX_23', 'MA_CHANNEL_AUX_24',
    'MA_CHANNEL_AUX_25', 'MA_CHANNEL_AUX_26', 'MA_CHANNEL_AUX_27',
    'MA_CHANNEL_AUX_28', 'MA_CHANNEL_AUX_29', 'MA_CHANNEL_AUX_3',
    'MA_CHANNEL_AUX_30', 'MA_CHANNEL_AUX_31', 'MA_CHANNEL_AUX_4',
    'MA_CHANNEL_AUX_5', 'MA_CHANNEL_AUX_6', 'MA_CHANNEL_AUX_7',
    'MA_CHANNEL_AUX_8', 'MA_CHANNEL_AUX_9', 'MA_CHANNEL_BACK_CENTER',
    'MA_CHANNEL_BACK_LEFT', 'MA_CHANNEL_BACK_RIGHT',
    'MA_CHANNEL_FRONT_CENTER', 'MA_CHANNEL_FRONT_LEFT',
    'MA_CHANNEL_FRONT_LEFT_CENTER', 'MA_CHANNEL_FRONT_RIGHT',
    'MA_CHANNEL_FRONT_RIGHT_CENTER', 'MA_CHANNEL_LEFT',
    'MA_CHANNEL_LFE', 'MA_CHANNEL_MONO', 'MA_CHANNEL_NONE',
    'MA_CHANNEL_POSITION_COUNT', 'MA_CHANNEL_RIGHT',
    'MA_CHANNEL_SIDE_LEFT', 'MA_CHANNEL_SIDE_RIGHT',
    'MA_CHANNEL_TOP_BACK_CENTER', 'MA_CHANNEL_TOP_BACK_LEFT',
    'MA_CHANNEL_TOP_BACK_RIGHT', 'MA_CHANNEL_TOP_CENTER',
    'MA_CHANNEL_TOP_FRONT_CENTER', 'MA_CHANNEL_TOP_FRONT_LEFT',
    'MA_CHANNEL_TOP_FRONT_RIGHT', 'MA_CONNECTION_REFUSED',
    'MA_CONNECTION_RESET', 'MA_CRC_MISMATCH', 'MA_DEADLOCK',
    'MA_DEVICE_ALREADY_INITIALIZED', 'MA_DEVICE_NOT_INITIALIZED',
    'MA_DEVICE_NOT_STARTED', 'MA_DEVICE_NOT_STOPPED',
    'MA_DEVICE_TYPE_NOT_SUPPORTED', 'MA_DIRECTORY_NOT_EMPTY',
    'MA_DOES_NOT_EXIST', 'MA_ERROR', 'MA_FAILED_TO_INIT_BACKEND',
    'MA_FAILED_TO_OPEN_BACKEND_DEVICE',
    'MA_FAILED_TO_START_BACKEND_DEVICE',
    'MA_FAILED_TO_STOP_BACKEND_DEVICE', 'MA_FORMAT_NOT_SUPPORTED',
    'MA_INTERRUPT', 'MA_INVALID_ARGS', 'MA_INVALID_DATA',
    'MA_INVALID_DEVICE_CONFIG', 'MA_INVALID_FILE',
    'MA_INVALID_OPERATION', 'MA_IN_PROGRESS', 'MA_IO_ERROR',
    'MA_IS_DIRECTORY', 'MA_JOB_QUEUE_FLAG_NON_BLOCKING',
    'MA_JOB_TYPE_COUNT', 'MA_JOB_TYPE_CUSTOM',
    'MA_JOB_TYPE_DEVICE_AAUDIO_REROUTE', 'MA_JOB_TYPE_QUIT',
    'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER',
    'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_BUFFER_NODE',
    'MA_JOB_TYPE_RESOURCE_MANAGER_FREE_DATA_STREAM',
    'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER',
    'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_BUFFER_NODE',
    'MA_JOB_TYPE_RESOURCE_MANAGER_LOAD_DATA_STREAM',
    'MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_BUFFER_NODE',
    'MA_JOB_TYPE_RESOURCE_MANAGER_PAGE_DATA_STREAM',
    'MA_JOB_TYPE_RESOURCE_MANAGER_SEEK_DATA_STREAM',
    'MA_LOG_LEVEL_DEBUG', 'MA_LOG_LEVEL_ERROR', 'MA_LOG_LEVEL_INFO',
    'MA_LOG_LEVEL_WARNING', 'MA_LOOP', 'MA_MEMORY_ALREADY_MAPPED',
    'MA_NAME_TOO_LONG', 'MA_NODE_FLAG_ALLOW_NULL_INPUT',
    'MA_NODE_FLAG_CONTINUOUS_PROCESSING',
    'MA_NODE_FLAG_DIFFERENT_PROCESSING_RATES',
    'MA_NODE_FLAG_PASSTHROUGH', 'MA_NODE_FLAG_SILENT_OUTPUT',
    'MA_NOT_CONNECTED', 'MA_NOT_DIRECTORY', 'MA_NOT_IMPLEMENTED',
    'MA_NOT_SOCKET', 'MA_NOT_UNIQUE', 'MA_NO_ADDRESS',
    'MA_NO_BACKEND', 'MA_NO_DATA_AVAILABLE', 'MA_NO_DEVICE',
    'MA_NO_HOST', 'MA_NO_MESSAGE', 'MA_NO_NETWORK', 'MA_NO_SPACE',
    'MA_OPEN_MODE_READ', 'MA_OPEN_MODE_WRITE', 'MA_OUT_OF_MEMORY',
    'MA_OUT_OF_RANGE', 'MA_PATH_TOO_LONG',
    'MA_PROTOCOL_FAMILY_NOT_SUPPORTED', 'MA_PROTOCOL_NOT_SUPPORTED',
    'MA_PROTOCOL_UNAVAILABLE',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_ASYNC',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_DECODE',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_LOOPING',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_STREAM',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_UNKNOWN_LENGTH',
    'MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT',
    'MA_RESOURCE_MANAGER_FLAG_NON_BLOCKING',
    'MA_RESOURCE_MANAGER_FLAG_NO_THREADING',
    'MA_SHARE_MODE_NOT_SUPPORTED', 'MA_SOCKET_NOT_SUPPORTED',
    'MA_SOUND_FLAG_ASYNC', 'MA_SOUND_FLAG_DECODE',
    'MA_SOUND_FLAG_LOOPING', 'MA_SOUND_FLAG_NO_DEFAULT_ATTACHMENT',
    'MA_SOUND_FLAG_NO_PITCH', 'MA_SOUND_FLAG_NO_SPATIALIZATION',
    'MA_SOUND_FLAG_STREAM', 'MA_SOUND_FLAG_UNKNOWN_LENGTH',
    'MA_SOUND_FLAG_WAIT_INIT', 'MA_SUCCESS', 'MA_TIMEOUT',
    'MA_TOO_BIG', 'MA_TOO_MANY_LINKS', 'MA_TOO_MANY_OPEN_FILES',
    'MA_UNAVAILABLE', '_ma_channel_position',
    'ma_aaudio_allow_capture_by_all',
    'ma_aaudio_allow_capture_by_none',
    'ma_aaudio_allow_capture_by_system',
    'ma_aaudio_allow_capture_default',
    'ma_aaudio_allowed_capture_policy', 'ma_aaudio_content_type',
    'ma_aaudio_content_type_default', 'ma_aaudio_content_type_movie',
    'ma_aaudio_content_type_music',
    'ma_aaudio_content_type_sonification',
    'ma_aaudio_content_type_speech', 'ma_aaudio_input_preset',
    'ma_aaudio_input_preset_camcorder',
    'ma_aaudio_input_preset_default',
    'ma_aaudio_input_preset_generic',
    'ma_aaudio_input_preset_unprocessed',
    'ma_aaudio_input_preset_voice_communication',
    'ma_aaudio_input_preset_voice_performance',
    'ma_aaudio_input_preset_voice_recognition', 'ma_aaudio_usage',
    'ma_aaudio_usage_alarm', 'ma_aaudio_usage_announcement',
    'ma_aaudio_usage_assistance_accessibility',
    'ma_aaudio_usage_assistance_navigation_guidance',
    'ma_aaudio_usage_assistance_sonification',
    'ma_aaudio_usage_assitant', 'ma_aaudio_usage_default',
    'ma_aaudio_usage_emergency', 'ma_aaudio_usage_game',
    'ma_aaudio_usage_media', 'ma_aaudio_usage_notification',
    'ma_aaudio_usage_notification_event',
    'ma_aaudio_usage_notification_ringtone', 'ma_aaudio_usage_safety',
    'ma_aaudio_usage_vehicle_status',
    'ma_aaudio_usage_voice_communication',
    'ma_aaudio_usage_voice_communication_signalling',
    'ma_aligned_free', 'ma_aligned_malloc', 'ma_allocation_callbacks',
    'ma_apply_volume_factor_f32', 'ma_apply_volume_factor_pcm_frames',
    'ma_apply_volume_factor_pcm_frames_f32',
    'ma_apply_volume_factor_pcm_frames_s16',
    'ma_apply_volume_factor_pcm_frames_s24',
    'ma_apply_volume_factor_pcm_frames_s32',
    'ma_apply_volume_factor_pcm_frames_u8',
    'ma_apply_volume_factor_s16', 'ma_apply_volume_factor_s24',
    'ma_apply_volume_factor_s32', 'ma_apply_volume_factor_u8',
    'ma_async_notification', 'ma_async_notification_callbacks',
    'ma_async_notification_event', 'ma_async_notification_event_init',
    'ma_async_notification_event_signal',
    'ma_async_notification_event_uninit',
    'ma_async_notification_event_wait', 'ma_async_notification_poll',
    'ma_async_notification_poll_init',
    'ma_async_notification_poll_is_signalled',
    'ma_async_notification_signal', 'ma_atomic_bool32',
    'ma_atomic_device_state', 'ma_atomic_float', 'ma_atomic_int32',
    'ma_atomic_uint32', 'ma_atomic_uint64', 'ma_atomic_vec3f',
    'ma_attenuation_model', 'ma_attenuation_model_exponential',
    'ma_attenuation_model_inverse', 'ma_attenuation_model_linear',
    'ma_attenuation_model_none', 'ma_audio_buffer',
    'ma_audio_buffer_alloc_and_init', 'ma_audio_buffer_at_end',
    'ma_audio_buffer_config', 'ma_audio_buffer_config_init',
    'ma_audio_buffer_get_available_frames',
    'ma_audio_buffer_get_cursor_in_pcm_frames',
    'ma_audio_buffer_get_length_in_pcm_frames',
    'ma_audio_buffer_init', 'ma_audio_buffer_init_copy',
    'ma_audio_buffer_map', 'ma_audio_buffer_read_pcm_frames',
    'ma_audio_buffer_ref', 'ma_audio_buffer_ref_at_end',
    'ma_audio_buffer_ref_get_available_frames',
    'ma_audio_buffer_ref_get_cursor_in_pcm_frames',
    'ma_audio_buffer_ref_get_length_in_pcm_frames',
    'ma_audio_buffer_ref_init', 'ma_audio_buffer_ref_map',
    'ma_audio_buffer_ref_read_pcm_frames',
    'ma_audio_buffer_ref_seek_to_pcm_frame',
    'ma_audio_buffer_ref_set_data', 'ma_audio_buffer_ref_uninit',
    'ma_audio_buffer_ref_unmap', 'ma_audio_buffer_seek_to_pcm_frame',
    'ma_audio_buffer_uninit', 'ma_audio_buffer_uninit_and_free',
    'ma_audio_buffer_unmap', 'ma_backend', 'ma_backend_aaudio',
    'ma_backend_alsa', 'ma_backend_audio4', 'ma_backend_callbacks',
    'ma_backend_coreaudio', 'ma_backend_custom', 'ma_backend_dsound',
    'ma_backend_jack', 'ma_backend_null', 'ma_backend_opensl',
    'ma_backend_oss', 'ma_backend_pulseaudio', 'ma_backend_sndio',
    'ma_backend_wasapi', 'ma_backend_webaudio', 'ma_backend_winmm',
    'ma_biquad', 'ma_biquad_clear_cache', 'ma_biquad_coefficient',
    'ma_biquad_config', 'ma_biquad_config_init',
    'ma_biquad_get_heap_size', 'ma_biquad_get_latency',
    'ma_biquad_init', 'ma_biquad_init_preallocated', 'ma_biquad_node',
    'ma_biquad_node_config', 'ma_biquad_node_config_init',
    'ma_biquad_node_init', 'ma_biquad_node_reinit',
    'ma_biquad_node_uninit', 'ma_biquad_process_pcm_frames',
    'ma_biquad_reinit', 'ma_biquad_uninit', 'ma_blend_f32',
    'ma_bool32', 'ma_bool8', 'ma_bpf', 'ma_bpf2', 'ma_bpf2_config',
    'ma_bpf2_config_init', 'ma_bpf2_get_heap_size',
    'ma_bpf2_get_latency', 'ma_bpf2_init',
    'ma_bpf2_init_preallocated', 'ma_bpf2_process_pcm_frames',
    'ma_bpf2_reinit', 'ma_bpf2_uninit', 'ma_bpf_config',
    'ma_bpf_config_init', 'ma_bpf_get_heap_size',
    'ma_bpf_get_latency', 'ma_bpf_init', 'ma_bpf_init_preallocated',
    'ma_bpf_node', 'ma_bpf_node_config', 'ma_bpf_node_config_init',
    'ma_bpf_node_init', 'ma_bpf_node_reinit', 'ma_bpf_node_uninit',
    'ma_bpf_process_pcm_frames', 'ma_bpf_reinit', 'ma_bpf_uninit',
    'ma_calculate_buffer_size_in_frames_from_descriptor',
    'ma_calculate_buffer_size_in_frames_from_milliseconds',
    'ma_calculate_buffer_size_in_milliseconds_from_frames',
    'ma_calloc', 'ma_channel', 'ma_channel_conversion_path',
    'ma_channel_conversion_path_mono_in',
    'ma_channel_conversion_path_mono_out',
    'ma_channel_conversion_path_passthrough',
    'ma_channel_conversion_path_shuffle',
    'ma_channel_conversion_path_unknown',
    'ma_channel_conversion_path_weights', 'ma_channel_converter',
    'ma_channel_converter_config', 'ma_channel_converter_config_init',
    'ma_channel_converter_get_heap_size',
    'ma_channel_converter_get_input_channel_map',
    'ma_channel_converter_get_output_channel_map',
    'ma_channel_converter_init',
    'ma_channel_converter_init_preallocated',
    'ma_channel_converter_process_pcm_frames',
    'ma_channel_converter_uninit',
    'ma_channel_map_contains_channel_position', 'ma_channel_map_copy',
    'ma_channel_map_copy_or_default',
    'ma_channel_map_find_channel_position',
    'ma_channel_map_get_channel', 'ma_channel_map_init_blank',
    'ma_channel_map_init_standard', 'ma_channel_map_is_blank',
    'ma_channel_map_is_equal', 'ma_channel_map_is_valid',
    'ma_channel_map_to_string', 'ma_channel_mix_mode',
    'ma_channel_mix_mode_custom_weights',
    'ma_channel_mix_mode_default', 'ma_channel_mix_mode_rectangular',
    'ma_channel_mix_mode_simple', 'ma_channel_position_to_string',
    'ma_clip_pcm_frames', 'ma_clip_samples_f32',
    'ma_clip_samples_s16', 'ma_clip_samples_s24',
    'ma_clip_samples_s32', 'ma_clip_samples_u8', 'ma_context',
    'ma_context_command__wasapi', 'ma_context_config',
    'ma_context_config_init', 'ma_context_enumerate_devices',
    'ma_context_get_device_info', 'ma_context_get_devices',
    'ma_context_get_log', 'ma_context_init',
    'ma_context_is_loopback_supported', 'ma_context_sizeof',
    'ma_context_uninit', 'ma_convert_frames', 'ma_convert_frames_ex',
    'ma_convert_pcm_frames_format',
    'ma_copy_and_apply_volume_and_clip_pcm_frames',
    'ma_copy_and_apply_volume_and_clip_samples_f32',
    'ma_copy_and_apply_volume_and_clip_samples_s16',
    'ma_copy_and_apply_volume_and_clip_samples_s24',
    'ma_copy_and_apply_volume_and_clip_samples_s32',
    'ma_copy_and_apply_volume_and_clip_samples_u8',
    'ma_copy_and_apply_volume_factor_f32',
    'ma_copy_and_apply_volume_factor_pcm_frames',
    'ma_copy_and_apply_volume_factor_pcm_frames_f32',
    'ma_copy_and_apply_volume_factor_pcm_frames_s16',
    'ma_copy_and_apply_volume_factor_pcm_frames_s24',
    'ma_copy_and_apply_volume_factor_pcm_frames_s32',
    'ma_copy_and_apply_volume_factor_pcm_frames_u8',
    'ma_copy_and_apply_volume_factor_per_channel_f32',
    'ma_copy_and_apply_volume_factor_s16',
    'ma_copy_and_apply_volume_factor_s24',
    'ma_copy_and_apply_volume_factor_s32',
    'ma_copy_and_apply_volume_factor_u8', 'ma_copy_pcm_frames',
    'ma_data_converter', 'ma_data_converter_config',
    'ma_data_converter_config_init',
    'ma_data_converter_config_init_default',
    'ma_data_converter_execution_path',
    'ma_data_converter_execution_path_channels_first',
    'ma_data_converter_execution_path_channels_only',
    'ma_data_converter_execution_path_format_only',
    'ma_data_converter_execution_path_passthrough',
    'ma_data_converter_execution_path_resample_first',
    'ma_data_converter_execution_path_resample_only',
    'ma_data_converter_get_expected_output_frame_count',
    'ma_data_converter_get_heap_size',
    'ma_data_converter_get_input_channel_map',
    'ma_data_converter_get_input_latency',
    'ma_data_converter_get_output_channel_map',
    'ma_data_converter_get_output_latency',
    'ma_data_converter_get_required_input_frame_count',
    'ma_data_converter_init', 'ma_data_converter_init_preallocated',
    'ma_data_converter_process_pcm_frames', 'ma_data_converter_reset',
    'ma_data_converter_set_rate', 'ma_data_converter_set_rate_ratio',
    'ma_data_converter_uninit', 'ma_data_source',
    'ma_data_source_base', 'ma_data_source_config',
    'ma_data_source_config_init', 'ma_data_source_get_current',
    'ma_data_source_get_cursor_in_pcm_frames',
    'ma_data_source_get_cursor_in_seconds',
    'ma_data_source_get_data_format',
    'ma_data_source_get_length_in_pcm_frames',
    'ma_data_source_get_length_in_seconds',
    'ma_data_source_get_loop_point_in_pcm_frames',
    'ma_data_source_get_next', 'ma_data_source_get_next_callback',
    'ma_data_source_get_next_proc',
    'ma_data_source_get_range_in_pcm_frames', 'ma_data_source_init',
    'ma_data_source_is_looping', 'ma_data_source_node',
    'ma_data_source_node_config', 'ma_data_source_node_config_init',
    'ma_data_source_node_init', 'ma_data_source_node_is_looping',
    'ma_data_source_node_set_looping', 'ma_data_source_node_uninit',
    'ma_data_source_read_pcm_frames',
    'ma_data_source_seek_pcm_frames', 'ma_data_source_seek_seconds',
    'ma_data_source_seek_to_pcm_frame',
    'ma_data_source_seek_to_second', 'ma_data_source_set_current',
    'ma_data_source_set_loop_point_in_pcm_frames',
    'ma_data_source_set_looping', 'ma_data_source_set_next',
    'ma_data_source_set_next_callback',
    'ma_data_source_set_range_in_pcm_frames', 'ma_data_source_uninit',
    'ma_data_source_vtable', 'ma_decode_file', 'ma_decode_from_vfs',
    'ma_decode_memory', 'ma_decoder', 'ma_decoder_config',
    'ma_decoder_config_init', 'ma_decoder_config_init_default',
    'ma_decoder_get_available_frames',
    'ma_decoder_get_cursor_in_pcm_frames',
    'ma_decoder_get_data_format',
    'ma_decoder_get_length_in_pcm_frames', 'ma_decoder_init',
    'ma_decoder_init_file', 'ma_decoder_init_file_w',
    'ma_decoder_init_memory', 'ma_decoder_init_vfs',
    'ma_decoder_init_vfs_w', 'ma_decoder_read_pcm_frames',
    'ma_decoder_read_proc', 'ma_decoder_seek_proc',
    'ma_decoder_seek_to_pcm_frame', 'ma_decoder_tell_proc',
    'ma_decoder_uninit', 'ma_decoding_backend_config',
    'ma_decoding_backend_config_init', 'ma_decoding_backend_vtable',
    'ma_default_vfs', 'ma_default_vfs_init',
    'ma_deinterleave_pcm_frames', 'ma_delay', 'ma_delay_config',
    'ma_delay_config_init', 'ma_delay_get_decay', 'ma_delay_get_dry',
    'ma_delay_get_wet', 'ma_delay_init', 'ma_delay_node',
    'ma_delay_node_config', 'ma_delay_node_config_init',
    'ma_delay_node_get_decay', 'ma_delay_node_get_dry',
    'ma_delay_node_get_wet', 'ma_delay_node_init',
    'ma_delay_node_set_decay', 'ma_delay_node_set_dry',
    'ma_delay_node_set_wet', 'ma_delay_node_uninit',
    'ma_delay_process_pcm_frames', 'ma_delay_set_decay',
    'ma_delay_set_dry', 'ma_delay_set_wet', 'ma_delay_uninit',
    'ma_device', 'ma_device_config', 'ma_device_config_init',
    'ma_device_data_proc', 'ma_device_descriptor',
    'ma_device_get_context', 'ma_device_get_info',
    'ma_device_get_log', 'ma_device_get_master_volume',
    'ma_device_get_master_volume_db', 'ma_device_get_name',
    'ma_device_get_state', 'ma_device_handle_backend_data_callback',
    'ma_device_id', 'ma_device_id_equal', 'ma_device_info',
    'ma_device_init', 'ma_device_init_ex', 'ma_device_is_started',
    'ma_device_job_thread', 'ma_device_job_thread_config',
    'ma_device_job_thread_config_init', 'ma_device_job_thread_init',
    'ma_device_job_thread_next', 'ma_device_job_thread_post',
    'ma_device_job_thread_uninit', 'ma_device_notification',
    'ma_device_notification_proc', 'ma_device_notification_type',
    'ma_device_notification_type_interruption_began',
    'ma_device_notification_type_interruption_ended',
    'ma_device_notification_type_rerouted',
    'ma_device_notification_type_started',
    'ma_device_notification_type_stopped',
    'ma_device_notification_type_unlocked', 'ma_device_post_init',
    'ma_device_set_master_volume', 'ma_device_set_master_volume_db',
    'ma_device_start', 'ma_device_state', 'ma_device_state_started',
    'ma_device_state_starting', 'ma_device_state_stopped',
    'ma_device_state_stopping', 'ma_device_state_uninitialized',
    'ma_device_stop', 'ma_device_type', 'ma_device_type_capture',
    'ma_device_type_duplex', 'ma_device_type_loopback',
    'ma_device_type_playback', 'ma_device_uninit', 'ma_dither_mode',
    'ma_dither_mode_none', 'ma_dither_mode_rectangle',
    'ma_dither_mode_triangle', 'ma_double', 'ma_duplex_rb',
    'ma_duplex_rb_init', 'ma_duplex_rb_uninit', 'ma_encoder',
    'ma_encoder_config', 'ma_encoder_config_init', 'ma_encoder_init',
    'ma_encoder_init_file', 'ma_encoder_init_file_w',
    'ma_encoder_init_proc', 'ma_encoder_init_vfs',
    'ma_encoder_init_vfs_w', 'ma_encoder_seek_proc',
    'ma_encoder_uninit', 'ma_encoder_uninit_proc',
    'ma_encoder_write_pcm_frames', 'ma_encoder_write_pcm_frames_proc',
    'ma_encoder_write_proc', 'ma_encoding_format',
    'ma_encoding_format_flac', 'ma_encoding_format_mp3',
    'ma_encoding_format_unknown', 'ma_encoding_format_vorbis',
    'ma_encoding_format_wav', 'ma_engine', 'ma_engine_config',
    'ma_engine_config_init', 'ma_engine_find_closest_listener',
    'ma_engine_get_channels', 'ma_engine_get_device',
    'ma_engine_get_endpoint', 'ma_engine_get_gain_db',
    'ma_engine_get_listener_count', 'ma_engine_get_log',
    'ma_engine_get_node_graph', 'ma_engine_get_resource_manager',
    'ma_engine_get_sample_rate', 'ma_engine_get_time',
    'ma_engine_get_time_in_milliseconds',
    'ma_engine_get_time_in_pcm_frames', 'ma_engine_get_volume',
    'ma_engine_init', 'ma_engine_listener_get_cone',
    'ma_engine_listener_get_direction',
    'ma_engine_listener_get_position',
    'ma_engine_listener_get_velocity',
    'ma_engine_listener_get_world_up',
    'ma_engine_listener_is_enabled', 'ma_engine_listener_set_cone',
    'ma_engine_listener_set_direction',
    'ma_engine_listener_set_enabled',
    'ma_engine_listener_set_position',
    'ma_engine_listener_set_velocity',
    'ma_engine_listener_set_world_up', 'ma_engine_node',
    'ma_engine_node_config', 'ma_engine_node_config_init',
    'ma_engine_node_get_heap_size', 'ma_engine_node_init',
    'ma_engine_node_init_preallocated', 'ma_engine_node_type',
    'ma_engine_node_type_group', 'ma_engine_node_type_sound',
    'ma_engine_node_uninit', 'ma_engine_play_sound',
    'ma_engine_play_sound_ex', 'ma_engine_process_proc',
    'ma_engine_read_pcm_frames', 'ma_engine_set_gain_db',
    'ma_engine_set_time', 'ma_engine_set_time_in_milliseconds',
    'ma_engine_set_time_in_pcm_frames', 'ma_engine_set_volume',
    'ma_engine_start', 'ma_engine_stop', 'ma_engine_uninit',
    'ma_enum_devices_callback_proc', 'ma_event', 'ma_event_init',
    'ma_event_signal', 'ma_event_uninit', 'ma_event_wait', 'ma_fader',
    'ma_fader_config', 'ma_fader_config_init',
    'ma_fader_get_current_volume', 'ma_fader_get_data_format',
    'ma_fader_init', 'ma_fader_process_pcm_frames',
    'ma_fader_set_fade', 'ma_fader_set_fade_ex', 'ma_fence',
    'ma_fence_acquire', 'ma_fence_init', 'ma_fence_release',
    'ma_fence_uninit', 'ma_fence_wait', 'ma_file_info', 'ma_float',
    'ma_format', 'ma_format_count', 'ma_format_f32', 'ma_format_s16',
    'ma_format_s24', 'ma_format_s32', 'ma_format_u8',
    'ma_format_unknown', 'ma_free', 'ma_gainer', 'ma_gainer_config',
    'ma_gainer_config_init', 'ma_gainer_get_heap_size',
    'ma_gainer_get_master_volume', 'ma_gainer_init',
    'ma_gainer_init_preallocated', 'ma_gainer_process_pcm_frames',
    'ma_gainer_set_gain', 'ma_gainer_set_gains',
    'ma_gainer_set_master_volume', 'ma_gainer_uninit',
    'ma_get_backend_from_name', 'ma_get_backend_name',
    'ma_get_bytes_per_frame', 'ma_get_bytes_per_sample',
    'ma_get_enabled_backends', 'ma_get_format_name', 'ma_handedness',
    'ma_handedness_left', 'ma_handedness_right', 'ma_handle',
    'ma_hishelf2', 'ma_hishelf2_config', 'ma_hishelf2_config_init',
    'ma_hishelf2_get_heap_size', 'ma_hishelf2_get_latency',
    'ma_hishelf2_init', 'ma_hishelf2_init_preallocated',
    'ma_hishelf2_process_pcm_frames', 'ma_hishelf2_reinit',
    'ma_hishelf2_uninit', 'ma_hishelf_config', 'ma_hishelf_node',
    'ma_hishelf_node_config', 'ma_hishelf_node_config_init',
    'ma_hishelf_node_init', 'ma_hishelf_node_reinit',
    'ma_hishelf_node_uninit', 'ma_hpf', 'ma_hpf1', 'ma_hpf1_config',
    'ma_hpf1_config_init', 'ma_hpf1_get_heap_size',
    'ma_hpf1_get_latency', 'ma_hpf1_init',
    'ma_hpf1_init_preallocated', 'ma_hpf1_process_pcm_frames',
    'ma_hpf1_reinit', 'ma_hpf1_uninit', 'ma_hpf2', 'ma_hpf2_config',
    'ma_hpf2_config_init', 'ma_hpf2_get_heap_size',
    'ma_hpf2_get_latency', 'ma_hpf2_init',
    'ma_hpf2_init_preallocated', 'ma_hpf2_process_pcm_frames',
    'ma_hpf2_reinit', 'ma_hpf2_uninit', 'ma_hpf_config',
    'ma_hpf_config_init', 'ma_hpf_get_heap_size',
    'ma_hpf_get_latency', 'ma_hpf_init', 'ma_hpf_init_preallocated',
    'ma_hpf_node', 'ma_hpf_node_config', 'ma_hpf_node_config_init',
    'ma_hpf_node_init', 'ma_hpf_node_reinit', 'ma_hpf_node_uninit',
    'ma_hpf_process_pcm_frames', 'ma_hpf_reinit', 'ma_hpf_uninit',
    'ma_int16', 'ma_int32', 'ma_int64', 'ma_int8',
    'ma_interleave_pcm_frames', 'ma_ios_session_category',
    'ma_ios_session_category_ambient',
    'ma_ios_session_category_default',
    'ma_ios_session_category_multi_route',
    'ma_ios_session_category_none', 'ma_ios_session_category_option',
    'ma_ios_session_category_option_allow_air_play',
    'ma_ios_session_category_option_allow_bluetooth',
    'ma_ios_session_category_option_allow_bluetooth_a2dp',
    'ma_ios_session_category_option_default_to_speaker',
    'ma_ios_session_category_option_duck_others',
    'ma_ios_session_category_option_interrupt_spoken_audio_and_mix_with_others',
    'ma_ios_session_category_option_mix_with_others',
    'ma_ios_session_category_play_and_record',
    'ma_ios_session_category_playback',
    'ma_ios_session_category_record',
    'ma_ios_session_category_solo_ambient', 'ma_is_backend_enabled',
    'ma_is_loopback_supported', 'ma_job', 'ma_job_init',
    'ma_job_proc', 'ma_job_process', 'ma_job_queue',
    'ma_job_queue_config', 'ma_job_queue_config_init',
    'ma_job_queue_flags', 'ma_job_queue_get_heap_size',
    'ma_job_queue_init', 'ma_job_queue_init_preallocated',
    'ma_job_queue_next', 'ma_job_queue_post', 'ma_job_queue_uninit',
    'ma_job_type', 'ma_lcg', 'ma_linear_resampler',
    'ma_linear_resampler_config', 'ma_linear_resampler_config_init',
    'ma_linear_resampler_get_expected_output_frame_count',
    'ma_linear_resampler_get_heap_size',
    'ma_linear_resampler_get_input_latency',
    'ma_linear_resampler_get_output_latency',
    'ma_linear_resampler_get_required_input_frame_count',
    'ma_linear_resampler_init',
    'ma_linear_resampler_init_preallocated',
    'ma_linear_resampler_process_pcm_frames',
    'ma_linear_resampler_reset', 'ma_linear_resampler_set_rate',
    'ma_linear_resampler_set_rate_ratio',
    'ma_linear_resampler_uninit', 'ma_log', 'ma_log_callback',
    'ma_log_callback_init', 'ma_log_callback_proc', 'ma_log_init',
    'ma_log_level', 'ma_log_level_to_string', 'ma_log_post',
    'ma_log_postf', 'ma_log_postv', 'ma_log_register_callback',
    'ma_log_uninit', 'ma_log_unregister_callback', 'ma_loshelf2',
    'ma_loshelf2_config', 'ma_loshelf2_config_init',
    'ma_loshelf2_get_heap_size', 'ma_loshelf2_get_latency',
    'ma_loshelf2_init', 'ma_loshelf2_init_preallocated',
    'ma_loshelf2_process_pcm_frames', 'ma_loshelf2_reinit',
    'ma_loshelf2_uninit', 'ma_loshelf_config', 'ma_loshelf_node',
    'ma_loshelf_node_config', 'ma_loshelf_node_config_init',
    'ma_loshelf_node_init', 'ma_loshelf_node_reinit',
    'ma_loshelf_node_uninit', 'ma_lpf', 'ma_lpf1',
    'ma_lpf1_clear_cache', 'ma_lpf1_config', 'ma_lpf1_config_init',
    'ma_lpf1_get_heap_size', 'ma_lpf1_get_latency', 'ma_lpf1_init',
    'ma_lpf1_init_preallocated', 'ma_lpf1_process_pcm_frames',
    'ma_lpf1_reinit', 'ma_lpf1_uninit', 'ma_lpf2',
    'ma_lpf2_clear_cache', 'ma_lpf2_config', 'ma_lpf2_config_init',
    'ma_lpf2_get_heap_size', 'ma_lpf2_get_latency', 'ma_lpf2_init',
    'ma_lpf2_init_preallocated', 'ma_lpf2_process_pcm_frames',
    'ma_lpf2_reinit', 'ma_lpf2_uninit', 'ma_lpf_clear_cache',
    'ma_lpf_config', 'ma_lpf_config_init', 'ma_lpf_get_heap_size',
    'ma_lpf_get_latency', 'ma_lpf_init', 'ma_lpf_init_preallocated',
    'ma_lpf_node', 'ma_lpf_node_config', 'ma_lpf_node_config_init',
    'ma_lpf_node_init', 'ma_lpf_node_reinit', 'ma_lpf_node_uninit',
    'ma_lpf_process_pcm_frames', 'ma_lpf_reinit', 'ma_lpf_uninit',
    'ma_malloc', 'ma_mix_pcm_frames_f32', 'ma_mono_expansion_mode',
    'ma_mono_expansion_mode_average',
    'ma_mono_expansion_mode_default',
    'ma_mono_expansion_mode_duplicate',
    'ma_mono_expansion_mode_stereo_only', 'ma_mutex', 'ma_mutex_init',
    'ma_mutex_lock', 'ma_mutex_uninit', 'ma_mutex_unlock', 'ma_node',
    'ma_node_attach_output_bus', 'ma_node_base', 'ma_node_config',
    'ma_node_config_init', 'ma_node_detach_all_output_buses',
    'ma_node_detach_output_bus', 'ma_node_flags',
    'ma_node_get_heap_size', 'ma_node_get_input_bus_count',
    'ma_node_get_input_channels', 'ma_node_get_node_graph',
    'ma_node_get_output_bus_count', 'ma_node_get_output_bus_volume',
    'ma_node_get_output_channels', 'ma_node_get_state',
    'ma_node_get_state_by_time', 'ma_node_get_state_by_time_range',
    'ma_node_get_state_time', 'ma_node_get_time', 'ma_node_graph',
    'ma_node_graph_config', 'ma_node_graph_config_init',
    'ma_node_graph_get_channels', 'ma_node_graph_get_endpoint',
    'ma_node_graph_get_time', 'ma_node_graph_init',
    'ma_node_graph_read_pcm_frames', 'ma_node_graph_set_time',
    'ma_node_graph_uninit', 'ma_node_init',
    'ma_node_init_preallocated', 'ma_node_input_bus',
    'ma_node_output_bus', 'ma_node_set_output_bus_volume',
    'ma_node_set_state', 'ma_node_set_state_time', 'ma_node_set_time',
    'ma_node_state', 'ma_node_state_started', 'ma_node_state_stopped',
    'ma_node_uninit', 'ma_node_vtable', 'ma_noise', 'ma_noise_config',
    'ma_noise_config_init', 'ma_noise_get_heap_size', 'ma_noise_init',
    'ma_noise_init_preallocated', 'ma_noise_read_pcm_frames',
    'ma_noise_set_amplitude', 'ma_noise_set_seed',
    'ma_noise_set_type', 'ma_noise_type', 'ma_noise_type_brownian',
    'ma_noise_type_pink', 'ma_noise_type_white', 'ma_noise_uninit',
    'ma_notch2', 'ma_notch2_config', 'ma_notch2_config_init',
    'ma_notch2_get_heap_size', 'ma_notch2_get_latency',
    'ma_notch2_init', 'ma_notch2_init_preallocated',
    'ma_notch2_process_pcm_frames', 'ma_notch2_reinit',
    'ma_notch2_uninit', 'ma_notch_config', 'ma_notch_node',
    'ma_notch_node_config', 'ma_notch_node_config_init',
    'ma_notch_node_init', 'ma_notch_node_reinit',
    'ma_notch_node_uninit', 'ma_offset_pcm_frames_const_ptr',
    'ma_offset_pcm_frames_const_ptr_f32', 'ma_offset_pcm_frames_ptr',
    'ma_offset_pcm_frames_ptr_f32', 'ma_open_mode_flags',
    'ma_opensl_recording_preset',
    'ma_opensl_recording_preset_camcorder',
    'ma_opensl_recording_preset_default',
    'ma_opensl_recording_preset_generic',
    'ma_opensl_recording_preset_voice_communication',
    'ma_opensl_recording_preset_voice_recognition',
    'ma_opensl_recording_preset_voice_unprocessed',
    'ma_opensl_stream_type', 'ma_opensl_stream_type_alarm',
    'ma_opensl_stream_type_default', 'ma_opensl_stream_type_media',
    'ma_opensl_stream_type_notification',
    'ma_opensl_stream_type_ring', 'ma_opensl_stream_type_system',
    'ma_opensl_stream_type_voice', 'ma_paged_audio_buffer',
    'ma_paged_audio_buffer_config',
    'ma_paged_audio_buffer_config_init', 'ma_paged_audio_buffer_data',
    'ma_paged_audio_buffer_data_allocate_and_append_page',
    'ma_paged_audio_buffer_data_allocate_page',
    'ma_paged_audio_buffer_data_append_page',
    'ma_paged_audio_buffer_data_free_page',
    'ma_paged_audio_buffer_data_get_head',
    'ma_paged_audio_buffer_data_get_length_in_pcm_frames',
    'ma_paged_audio_buffer_data_get_tail',
    'ma_paged_audio_buffer_data_init',
    'ma_paged_audio_buffer_data_uninit',
    'ma_paged_audio_buffer_get_cursor_in_pcm_frames',
    'ma_paged_audio_buffer_get_length_in_pcm_frames',
    'ma_paged_audio_buffer_init', 'ma_paged_audio_buffer_page',
    'ma_paged_audio_buffer_read_pcm_frames',
    'ma_paged_audio_buffer_seek_to_pcm_frame',
    'ma_paged_audio_buffer_uninit', 'ma_pan_mode',
    'ma_pan_mode_balance', 'ma_pan_mode_pan', 'ma_panner',
    'ma_panner_config', 'ma_panner_config_init', 'ma_panner_get_mode',
    'ma_panner_get_pan', 'ma_panner_init',
    'ma_panner_process_pcm_frames', 'ma_panner_set_mode',
    'ma_panner_set_pan', 'ma_pcm_convert', 'ma_pcm_f32_to_s16',
    'ma_pcm_f32_to_s24', 'ma_pcm_f32_to_s32', 'ma_pcm_f32_to_u8',
    'ma_pcm_rb', 'ma_pcm_rb_acquire_read', 'ma_pcm_rb_acquire_write',
    'ma_pcm_rb_available_read', 'ma_pcm_rb_available_write',
    'ma_pcm_rb_commit_read', 'ma_pcm_rb_commit_write',
    'ma_pcm_rb_get_channels', 'ma_pcm_rb_get_format',
    'ma_pcm_rb_get_sample_rate', 'ma_pcm_rb_get_subbuffer_offset',
    'ma_pcm_rb_get_subbuffer_ptr', 'ma_pcm_rb_get_subbuffer_size',
    'ma_pcm_rb_get_subbuffer_stride', 'ma_pcm_rb_init',
    'ma_pcm_rb_init_ex', 'ma_pcm_rb_pointer_distance',
    'ma_pcm_rb_reset', 'ma_pcm_rb_seek_read', 'ma_pcm_rb_seek_write',
    'ma_pcm_rb_set_sample_rate', 'ma_pcm_rb_uninit',
    'ma_pcm_s16_to_f32', 'ma_pcm_s16_to_s24', 'ma_pcm_s16_to_s32',
    'ma_pcm_s16_to_u8', 'ma_pcm_s24_to_f32', 'ma_pcm_s24_to_s16',
    'ma_pcm_s24_to_s32', 'ma_pcm_s24_to_u8', 'ma_pcm_s32_to_f32',
    'ma_pcm_s32_to_s16', 'ma_pcm_s32_to_s24', 'ma_pcm_s32_to_u8',
    'ma_pcm_u8_to_f32', 'ma_pcm_u8_to_s16', 'ma_pcm_u8_to_s24',
    'ma_pcm_u8_to_s32', 'ma_peak2', 'ma_peak2_config',
    'ma_peak2_config_init', 'ma_peak2_get_heap_size',
    'ma_peak2_get_latency', 'ma_peak2_init',
    'ma_peak2_init_preallocated', 'ma_peak2_process_pcm_frames',
    'ma_peak2_reinit', 'ma_peak2_uninit', 'ma_peak_config',
    'ma_peak_node', 'ma_peak_node_config', 'ma_peak_node_config_init',
    'ma_peak_node_init', 'ma_peak_node_reinit', 'ma_peak_node_uninit',
    'ma_performance_profile', 'ma_performance_profile_conservative',
    'ma_performance_profile_low_latency', 'ma_positioning',
    'ma_positioning_absolute', 'ma_positioning_relative', 'ma_proc',
    'ma_pthread_cond_t', 'ma_pthread_mutex_t', 'ma_pthread_t',
    'ma_ptr', 'ma_pulsewave', 'ma_pulsewave_config',
    'ma_pulsewave_config_init', 'ma_pulsewave_init',
    'ma_pulsewave_read_pcm_frames', 'ma_pulsewave_seek_to_pcm_frame',
    'ma_pulsewave_set_amplitude', 'ma_pulsewave_set_duty_cycle',
    'ma_pulsewave_set_frequency', 'ma_pulsewave_set_sample_rate',
    'ma_pulsewave_uninit', 'ma_rb', 'ma_rb_acquire_read',
    'ma_rb_acquire_write', 'ma_rb_available_read',
    'ma_rb_available_write', 'ma_rb_commit_read',
    'ma_rb_commit_write', 'ma_rb_get_subbuffer_offset',
    'ma_rb_get_subbuffer_ptr', 'ma_rb_get_subbuffer_size',
    'ma_rb_get_subbuffer_stride', 'ma_rb_init', 'ma_rb_init_ex',
    'ma_rb_pointer_distance', 'ma_rb_reset', 'ma_rb_seek_read',
    'ma_rb_seek_write', 'ma_rb_uninit', 'ma_read_proc', 'ma_realloc',
    'ma_resample_algorithm', 'ma_resample_algorithm_custom',
    'ma_resample_algorithm_linear', 'ma_resampler',
    'ma_resampler_config', 'ma_resampler_config_init',
    'ma_resampler_get_expected_output_frame_count',
    'ma_resampler_get_heap_size', 'ma_resampler_get_input_latency',
    'ma_resampler_get_output_latency',
    'ma_resampler_get_required_input_frame_count',
    'ma_resampler_init', 'ma_resampler_init_preallocated',
    'ma_resampler_process_pcm_frames', 'ma_resampler_reset',
    'ma_resampler_set_rate', 'ma_resampler_set_rate_ratio',
    'ma_resampler_uninit', 'ma_resampling_backend',
    'ma_resampling_backend_vtable', 'ma_resource_manager',
    'ma_resource_manager_config', 'ma_resource_manager_config_init',
    'ma_resource_manager_data_buffer',
    'ma_resource_manager_data_buffer_get_available_frames',
    'ma_resource_manager_data_buffer_get_cursor_in_pcm_frames',
    'ma_resource_manager_data_buffer_get_data_format',
    'ma_resource_manager_data_buffer_get_length_in_pcm_frames',
    'ma_resource_manager_data_buffer_init',
    'ma_resource_manager_data_buffer_init_copy',
    'ma_resource_manager_data_buffer_init_ex',
    'ma_resource_manager_data_buffer_init_w',
    'ma_resource_manager_data_buffer_is_looping',
    'ma_resource_manager_data_buffer_node',
    'ma_resource_manager_data_buffer_read_pcm_frames',
    'ma_resource_manager_data_buffer_result',
    'ma_resource_manager_data_buffer_seek_to_pcm_frame',
    'ma_resource_manager_data_buffer_set_looping',
    'ma_resource_manager_data_buffer_uninit',
    'ma_resource_manager_data_source',
    'ma_resource_manager_data_source_config',
    'ma_resource_manager_data_source_config_init',
    'ma_resource_manager_data_source_flags',
    'ma_resource_manager_data_source_get_available_frames',
    'ma_resource_manager_data_source_get_cursor_in_pcm_frames',
    'ma_resource_manager_data_source_get_data_format',
    'ma_resource_manager_data_source_get_length_in_pcm_frames',
    'ma_resource_manager_data_source_init',
    'ma_resource_manager_data_source_init_copy',
    'ma_resource_manager_data_source_init_ex',
    'ma_resource_manager_data_source_init_w',
    'ma_resource_manager_data_source_is_looping',
    'ma_resource_manager_data_source_read_pcm_frames',
    'ma_resource_manager_data_source_result',
    'ma_resource_manager_data_source_seek_to_pcm_frame',
    'ma_resource_manager_data_source_set_looping',
    'ma_resource_manager_data_source_uninit',
    'ma_resource_manager_data_stream',
    'ma_resource_manager_data_stream_get_available_frames',
    'ma_resource_manager_data_stream_get_cursor_in_pcm_frames',
    'ma_resource_manager_data_stream_get_data_format',
    'ma_resource_manager_data_stream_get_length_in_pcm_frames',
    'ma_resource_manager_data_stream_init',
    'ma_resource_manager_data_stream_init_ex',
    'ma_resource_manager_data_stream_init_w',
    'ma_resource_manager_data_stream_is_looping',
    'ma_resource_manager_data_stream_read_pcm_frames',
    'ma_resource_manager_data_stream_result',
    'ma_resource_manager_data_stream_seek_to_pcm_frame',
    'ma_resource_manager_data_stream_set_looping',
    'ma_resource_manager_data_stream_uninit',
    'ma_resource_manager_data_supply',
    'ma_resource_manager_data_supply_type',
    'ma_resource_manager_data_supply_type_decoded',
    'ma_resource_manager_data_supply_type_decoded_paged',
    'ma_resource_manager_data_supply_type_encoded',
    'ma_resource_manager_data_supply_type_unknown',
    'ma_resource_manager_flags', 'ma_resource_manager_get_log',
    'ma_resource_manager_init', 'ma_resource_manager_next_job',
    'ma_resource_manager_pipeline_notifications',
    'ma_resource_manager_pipeline_notifications_init',
    'ma_resource_manager_pipeline_stage_notification',
    'ma_resource_manager_post_job',
    'ma_resource_manager_post_job_quit',
    'ma_resource_manager_process_job',
    'ma_resource_manager_process_next_job',
    'ma_resource_manager_register_decoded_data',
    'ma_resource_manager_register_decoded_data_w',
    'ma_resource_manager_register_encoded_data',
    'ma_resource_manager_register_encoded_data_w',
    'ma_resource_manager_register_file',
    'ma_resource_manager_register_file_w',
    'ma_resource_manager_uninit',
    'ma_resource_manager_unregister_data',
    'ma_resource_manager_unregister_data_w',
    'ma_resource_manager_unregister_file',
    'ma_resource_manager_unregister_file_w', 'ma_result',
    'ma_result_description', 'ma_seek_origin',
    'ma_seek_origin_current', 'ma_seek_origin_end',
    'ma_seek_origin_start', 'ma_seek_proc', 'ma_semaphore',
    'ma_semaphore_init', 'ma_semaphore_release',
    'ma_semaphore_uninit', 'ma_semaphore_wait', 'ma_share_mode',
    'ma_share_mode_exclusive', 'ma_share_mode_shared',
    'ma_silence_pcm_frames', 'ma_slot_allocator',
    'ma_slot_allocator_alloc', 'ma_slot_allocator_config',
    'ma_slot_allocator_config_init', 'ma_slot_allocator_free',
    'ma_slot_allocator_get_heap_size', 'ma_slot_allocator_group',
    'ma_slot_allocator_init', 'ma_slot_allocator_init_preallocated',
    'ma_slot_allocator_uninit', 'ma_sound', 'ma_sound_at_end',
    'ma_sound_config', 'ma_sound_config_init',
    'ma_sound_config_init_2', 'ma_sound_end_proc', 'ma_sound_flags',
    'ma_sound_get_attenuation_model', 'ma_sound_get_cone',
    'ma_sound_get_current_fade_volume',
    'ma_sound_get_cursor_in_pcm_frames',
    'ma_sound_get_cursor_in_seconds', 'ma_sound_get_data_format',
    'ma_sound_get_data_source', 'ma_sound_get_direction',
    'ma_sound_get_direction_to_listener',
    'ma_sound_get_directional_attenuation_factor',
    'ma_sound_get_doppler_factor', 'ma_sound_get_engine',
    'ma_sound_get_length_in_pcm_frames',
    'ma_sound_get_length_in_seconds', 'ma_sound_get_listener_index',
    'ma_sound_get_max_distance', 'ma_sound_get_max_gain',
    'ma_sound_get_min_distance', 'ma_sound_get_min_gain',
    'ma_sound_get_pan', 'ma_sound_get_pan_mode',
    'ma_sound_get_pinned_listener_index', 'ma_sound_get_pitch',
    'ma_sound_get_position', 'ma_sound_get_positioning',
    'ma_sound_get_rolloff', 'ma_sound_get_time_in_milliseconds',
    'ma_sound_get_time_in_pcm_frames', 'ma_sound_get_velocity',
    'ma_sound_get_volume', 'ma_sound_group', 'ma_sound_group_config',
    'ma_sound_group_config_init', 'ma_sound_group_config_init_2',
    'ma_sound_group_get_attenuation_model', 'ma_sound_group_get_cone',
    'ma_sound_group_get_current_fade_volume',
    'ma_sound_group_get_direction',
    'ma_sound_group_get_direction_to_listener',
    'ma_sound_group_get_directional_attenuation_factor',
    'ma_sound_group_get_doppler_factor', 'ma_sound_group_get_engine',
    'ma_sound_group_get_listener_index',
    'ma_sound_group_get_max_distance', 'ma_sound_group_get_max_gain',
    'ma_sound_group_get_min_distance', 'ma_sound_group_get_min_gain',
    'ma_sound_group_get_pan', 'ma_sound_group_get_pan_mode',
    'ma_sound_group_get_pinned_listener_index',
    'ma_sound_group_get_pitch', 'ma_sound_group_get_position',
    'ma_sound_group_get_positioning', 'ma_sound_group_get_rolloff',
    'ma_sound_group_get_time_in_pcm_frames',
    'ma_sound_group_get_velocity', 'ma_sound_group_get_volume',
    'ma_sound_group_init', 'ma_sound_group_init_ex',
    'ma_sound_group_is_playing',
    'ma_sound_group_is_spatialization_enabled',
    'ma_sound_group_set_attenuation_model', 'ma_sound_group_set_cone',
    'ma_sound_group_set_direction',
    'ma_sound_group_set_directional_attenuation_factor',
    'ma_sound_group_set_doppler_factor',
    'ma_sound_group_set_fade_in_milliseconds',
    'ma_sound_group_set_fade_in_pcm_frames',
    'ma_sound_group_set_max_distance', 'ma_sound_group_set_max_gain',
    'ma_sound_group_set_min_distance', 'ma_sound_group_set_min_gain',
    'ma_sound_group_set_pan', 'ma_sound_group_set_pan_mode',
    'ma_sound_group_set_pinned_listener_index',
    'ma_sound_group_set_pitch', 'ma_sound_group_set_position',
    'ma_sound_group_set_positioning', 'ma_sound_group_set_rolloff',
    'ma_sound_group_set_spatialization_enabled',
    'ma_sound_group_set_start_time_in_milliseconds',
    'ma_sound_group_set_start_time_in_pcm_frames',
    'ma_sound_group_set_stop_time_in_milliseconds',
    'ma_sound_group_set_stop_time_in_pcm_frames',
    'ma_sound_group_set_velocity', 'ma_sound_group_set_volume',
    'ma_sound_group_start', 'ma_sound_group_stop',
    'ma_sound_group_uninit', 'ma_sound_init_copy', 'ma_sound_init_ex',
    'ma_sound_init_from_data_source', 'ma_sound_init_from_file',
    'ma_sound_init_from_file_w', 'ma_sound_inlined',
    'ma_sound_is_looping', 'ma_sound_is_playing',
    'ma_sound_is_spatialization_enabled',
    'ma_sound_seek_to_pcm_frame', 'ma_sound_seek_to_second',
    'ma_sound_set_attenuation_model', 'ma_sound_set_cone',
    'ma_sound_set_direction',
    'ma_sound_set_directional_attenuation_factor',
    'ma_sound_set_doppler_factor', 'ma_sound_set_end_callback',
    'ma_sound_set_fade_in_milliseconds',
    'ma_sound_set_fade_in_pcm_frames',
    'ma_sound_set_fade_start_in_milliseconds',
    'ma_sound_set_fade_start_in_pcm_frames', 'ma_sound_set_looping',
    'ma_sound_set_max_distance', 'ma_sound_set_max_gain',
    'ma_sound_set_min_distance', 'ma_sound_set_min_gain',
    'ma_sound_set_pan', 'ma_sound_set_pan_mode',
    'ma_sound_set_pinned_listener_index', 'ma_sound_set_pitch',
    'ma_sound_set_position', 'ma_sound_set_positioning',
    'ma_sound_set_rolloff', 'ma_sound_set_spatialization_enabled',
    'ma_sound_set_start_time_in_milliseconds',
    'ma_sound_set_start_time_in_pcm_frames',
    'ma_sound_set_stop_time_in_milliseconds',
    'ma_sound_set_stop_time_in_pcm_frames',
    'ma_sound_set_stop_time_with_fade_in_milliseconds',
    'ma_sound_set_stop_time_with_fade_in_pcm_frames',
    'ma_sound_set_velocity', 'ma_sound_set_volume', 'ma_sound_start',
    'ma_sound_stop', 'ma_sound_stop_with_fade_in_milliseconds',
    'ma_sound_stop_with_fade_in_pcm_frames', 'ma_sound_uninit',
    'ma_spatializer', 'ma_spatializer_config',
    'ma_spatializer_config_init',
    'ma_spatializer_get_attenuation_model', 'ma_spatializer_get_cone',
    'ma_spatializer_get_direction',
    'ma_spatializer_get_directional_attenuation_factor',
    'ma_spatializer_get_doppler_factor',
    'ma_spatializer_get_heap_size',
    'ma_spatializer_get_input_channels',
    'ma_spatializer_get_master_volume',
    'ma_spatializer_get_max_distance', 'ma_spatializer_get_max_gain',
    'ma_spatializer_get_min_distance', 'ma_spatializer_get_min_gain',
    'ma_spatializer_get_output_channels',
    'ma_spatializer_get_position', 'ma_spatializer_get_positioning',
    'ma_spatializer_get_relative_position_and_direction',
    'ma_spatializer_get_rolloff', 'ma_spatializer_get_velocity',
    'ma_spatializer_init', 'ma_spatializer_init_preallocated',
    'ma_spatializer_listener', 'ma_spatializer_listener_config',
    'ma_spatializer_listener_config_init',
    'ma_spatializer_listener_get_channel_map',
    'ma_spatializer_listener_get_cone',
    'ma_spatializer_listener_get_direction',
    'ma_spatializer_listener_get_heap_size',
    'ma_spatializer_listener_get_position',
    'ma_spatializer_listener_get_speed_of_sound',
    'ma_spatializer_listener_get_velocity',
    'ma_spatializer_listener_get_world_up',
    'ma_spatializer_listener_init',
    'ma_spatializer_listener_init_preallocated',
    'ma_spatializer_listener_is_enabled',
    'ma_spatializer_listener_set_cone',
    'ma_spatializer_listener_set_direction',
    'ma_spatializer_listener_set_enabled',
    'ma_spatializer_listener_set_position',
    'ma_spatializer_listener_set_speed_of_sound',
    'ma_spatializer_listener_set_velocity',
    'ma_spatializer_listener_set_world_up',
    'ma_spatializer_listener_uninit',
    'ma_spatializer_process_pcm_frames',
    'ma_spatializer_set_attenuation_model', 'ma_spatializer_set_cone',
    'ma_spatializer_set_direction',
    'ma_spatializer_set_directional_attenuation_factor',
    'ma_spatializer_set_doppler_factor',
    'ma_spatializer_set_master_volume',
    'ma_spatializer_set_max_distance', 'ma_spatializer_set_max_gain',
    'ma_spatializer_set_min_distance', 'ma_spatializer_set_min_gain',
    'ma_spatializer_set_position', 'ma_spatializer_set_positioning',
    'ma_spatializer_set_rolloff', 'ma_spatializer_set_velocity',
    'ma_spatializer_uninit', 'ma_spinlock', 'ma_spinlock_lock',
    'ma_spinlock_lock_noyield', 'ma_spinlock_unlock',
    'ma_splitter_node', 'ma_splitter_node_config',
    'ma_splitter_node_config_init', 'ma_splitter_node_init',
    'ma_splitter_node_uninit', 'ma_stack', 'ma_standard_channel_map',
    'ma_standard_channel_map_alsa', 'ma_standard_channel_map_default',
    'ma_standard_channel_map_flac',
    'ma_standard_channel_map_microsoft',
    'ma_standard_channel_map_rfc3551',
    'ma_standard_channel_map_sndio', 'ma_standard_channel_map_sound4',
    'ma_standard_channel_map_vorbis',
    'ma_standard_channel_map_webaudio', 'ma_standard_sample_rate',
    'ma_standard_sample_rate_11025', 'ma_standard_sample_rate_16000',
    'ma_standard_sample_rate_176400',
    'ma_standard_sample_rate_192000', 'ma_standard_sample_rate_22050',
    'ma_standard_sample_rate_24000', 'ma_standard_sample_rate_32000',
    'ma_standard_sample_rate_352800',
    'ma_standard_sample_rate_384000', 'ma_standard_sample_rate_44100',
    'ma_standard_sample_rate_48000', 'ma_standard_sample_rate_8000',
    'ma_standard_sample_rate_88200', 'ma_standard_sample_rate_96000',
    'ma_standard_sample_rate_count', 'ma_standard_sample_rate_max',
    'ma_standard_sample_rate_min', 'ma_stop_proc', 'ma_stream_format',
    'ma_stream_format_pcm', 'ma_stream_layout',
    'ma_stream_layout_deinterleaved', 'ma_stream_layout_interleaved',
    'ma_tell_proc', 'ma_thread', 'ma_thread_priority',
    'ma_thread_priority_default', 'ma_thread_priority_high',
    'ma_thread_priority_highest', 'ma_thread_priority_idle',
    'ma_thread_priority_low', 'ma_thread_priority_lowest',
    'ma_thread_priority_normal', 'ma_thread_priority_realtime',
    'ma_timer', 'ma_uint16', 'ma_uint32', 'ma_uint64', 'ma_uint8',
    'ma_uintptr', 'ma_vec3f', 'ma_version', 'ma_version_string',
    'ma_vfs', 'ma_vfs_callbacks', 'ma_vfs_close', 'ma_vfs_file',
    'ma_vfs_info', 'ma_vfs_open', 'ma_vfs_open_and_read_file',
    'ma_vfs_open_w', 'ma_vfs_read', 'ma_vfs_seek', 'ma_vfs_tell',
    'ma_vfs_write', 'ma_volume_db_to_linear',
    'ma_volume_linear_to_db', 'ma_wasapi_usage',
    'ma_wasapi_usage_default', 'ma_wasapi_usage_games',
    'ma_wasapi_usage_pro_audio', 'ma_waveform', 'ma_waveform_config',
    'ma_waveform_config_init', 'ma_waveform_init',
    'ma_waveform_read_pcm_frames', 'ma_waveform_seek_to_pcm_frame',
    'ma_waveform_set_amplitude', 'ma_waveform_set_frequency',
    'ma_waveform_set_sample_rate', 'ma_waveform_set_type',
    'ma_waveform_type', 'ma_waveform_type_sawtooth',
    'ma_waveform_type_sine', 'ma_waveform_type_square',
    'ma_waveform_type_triangle', 'ma_waveform_uninit',
    'ma_wchar_win32', 'size_t',
    'struct___atomic_wide_counter___value32',
    'struct___pthread_cond_s', 'struct___pthread_internal_list',
    'struct___pthread_mutex_s', 'struct___va_list_tag',
    'struct_ma_allocation_callbacks',
    'struct_ma_async_notification_callbacks',
    'struct_ma_async_notification_event',
    'struct_ma_async_notification_poll', 'struct_ma_atomic_bool32',
    'struct_ma_atomic_device_state', 'struct_ma_atomic_float',
    'struct_ma_atomic_int32', 'struct_ma_atomic_uint32',
    'struct_ma_atomic_uint64', 'struct_ma_atomic_vec3f',
    'struct_ma_audio_buffer', 'struct_ma_audio_buffer_config',
    'struct_ma_audio_buffer_ref', 'struct_ma_backend_callbacks',
    'struct_ma_biquad', 'struct_ma_biquad_config',
    'struct_ma_biquad_node', 'struct_ma_biquad_node_config',
    'struct_ma_bpf', 'struct_ma_bpf2', 'struct_ma_bpf2_config',
    'struct_ma_bpf_config', 'struct_ma_bpf_node',
    'struct_ma_bpf_node_config', 'struct_ma_channel_converter',
    'struct_ma_channel_converter_config', 'struct_ma_context',
    'struct_ma_context_0_alsa', 'struct_ma_context_0_jack',
    'struct_ma_context_0_null_backend', 'struct_ma_context_0_pulse',
    'struct_ma_context_1_posix', 'struct_ma_context_command__wasapi',
    'struct_ma_context_command__wasapi_0_createAudioClient',
    'struct_ma_context_command__wasapi_0_quit',
    'struct_ma_context_command__wasapi_0_releaseAudioClient',
    'struct_ma_context_config', 'struct_ma_context_config_alsa',
    'struct_ma_context_config_coreaudio',
    'struct_ma_context_config_dsound',
    'struct_ma_context_config_jack', 'struct_ma_context_config_pulse',
    'struct_ma_data_converter', 'struct_ma_data_converter_config',
    'struct_ma_data_source_base', 'struct_ma_data_source_config',
    'struct_ma_data_source_node', 'struct_ma_data_source_node_config',
    'struct_ma_data_source_vtable', 'struct_ma_decoder',
    'struct_ma_decoder_0_memory', 'struct_ma_decoder_0_vfs',
    'struct_ma_decoder_config', 'struct_ma_decoding_backend_config',
    'struct_ma_decoding_backend_vtable', 'struct_ma_default_vfs',
    'struct_ma_delay', 'struct_ma_delay_config',
    'struct_ma_delay_node', 'struct_ma_delay_node_config',
    'struct_ma_device', 'struct_ma_device_0_linear',
    'struct_ma_device_3_alsa', 'struct_ma_device_3_jack',
    'struct_ma_device_3_null_device', 'struct_ma_device_3_pulse',
    'struct_ma_device_capture', 'struct_ma_device_config',
    'struct_ma_device_config_aaudio', 'struct_ma_device_config_alsa',
    'struct_ma_device_config_capture',
    'struct_ma_device_config_coreaudio',
    'struct_ma_device_config_opensl',
    'struct_ma_device_config_playback',
    'struct_ma_device_config_pulse', 'struct_ma_device_config_wasapi',
    'struct_ma_device_descriptor', 'struct_ma_device_info',
    'struct_ma_device_info_0', 'struct_ma_device_job_thread',
    'struct_ma_device_job_thread_config',
    'struct_ma_device_notification',
    'struct_ma_device_notification_0_interruption',
    'struct_ma_device_notification_0_rerouted',
    'struct_ma_device_notification_0_started',
    'struct_ma_device_notification_0_stopped',
    'struct_ma_device_playback', 'struct_ma_device_resampling',
    'struct_ma_duplex_rb', 'struct_ma_encoder',
    'struct_ma_encoder_0_vfs', 'struct_ma_encoder_config',
    'struct_ma_engine', 'struct_ma_engine_config',
    'struct_ma_engine_node', 'struct_ma_engine_node_config',
    'struct_ma_engine_node_fadeSettings', 'struct_ma_event',
    'struct_ma_fader', 'struct_ma_fader_config', 'struct_ma_fence',
    'struct_ma_file_info', 'struct_ma_gainer',
    'struct_ma_gainer_config', 'struct_ma_hishelf2',
    'struct_ma_hishelf2_config', 'struct_ma_hishelf_node',
    'struct_ma_hishelf_node_config', 'struct_ma_hpf',
    'struct_ma_hpf1', 'struct_ma_hpf1_config', 'struct_ma_hpf2',
    'struct_ma_hpf_config', 'struct_ma_hpf_node',
    'struct_ma_hpf_node_config', 'struct_ma_job',
    'struct_ma_job_0_breakup', 'struct_ma_job_1_1_freeDataBuffer',
    'struct_ma_job_1_1_freeDataBufferNode',
    'struct_ma_job_1_1_freeDataStream',
    'struct_ma_job_1_1_loadDataBuffer',
    'struct_ma_job_1_1_loadDataBufferNode',
    'struct_ma_job_1_1_loadDataStream',
    'struct_ma_job_1_1_pageDataBufferNode',
    'struct_ma_job_1_1_pageDataStream',
    'struct_ma_job_1_1_seekDataStream', 'struct_ma_job_1_2_0_reroute',
    'struct_ma_job_1_custom', 'struct_ma_job_queue',
    'struct_ma_job_queue_config', 'struct_ma_lcg',
    'struct_ma_linear_resampler', 'struct_ma_linear_resampler_config',
    'struct_ma_log', 'struct_ma_log_callback', 'struct_ma_loshelf2',
    'struct_ma_loshelf2_config', 'struct_ma_loshelf_node',
    'struct_ma_loshelf_node_config', 'struct_ma_lpf',
    'struct_ma_lpf1', 'struct_ma_lpf1_config', 'struct_ma_lpf2',
    'struct_ma_lpf_config', 'struct_ma_lpf_node',
    'struct_ma_lpf_node_config', 'struct_ma_node_base',
    'struct_ma_node_config', 'struct_ma_node_graph',
    'struct_ma_node_graph_config', 'struct_ma_node_input_bus',
    'struct_ma_node_output_bus', 'struct_ma_node_vtable',
    'struct_ma_noise', 'struct_ma_noise_0_brownian',
    'struct_ma_noise_0_pink', 'struct_ma_noise_config',
    'struct_ma_notch2', 'struct_ma_notch2_config',
    'struct_ma_notch_node', 'struct_ma_notch_node_config',
    'struct_ma_paged_audio_buffer',
    'struct_ma_paged_audio_buffer_config',
    'struct_ma_paged_audio_buffer_data',
    'struct_ma_paged_audio_buffer_page', 'struct_ma_panner',
    'struct_ma_panner_config', 'struct_ma_pcm_rb', 'struct_ma_peak2',
    'struct_ma_peak2_config', 'struct_ma_peak_node',
    'struct_ma_peak_node_config', 'struct_ma_pulsewave',
    'struct_ma_pulsewave_config', 'struct_ma_rb',
    'struct_ma_resampler', 'struct_ma_resampler_config',
    'struct_ma_resampler_config_linear',
    'struct_ma_resampling_backend_vtable',
    'struct_ma_resource_manager', 'struct_ma_resource_manager_config',
    'struct_ma_resource_manager_data_buffer',
    'struct_ma_resource_manager_data_buffer_node',
    'struct_ma_resource_manager_data_source',
    'struct_ma_resource_manager_data_source_config',
    'struct_ma_resource_manager_data_stream',
    'struct_ma_resource_manager_data_supply',
    'struct_ma_resource_manager_data_supply_0_decoded',
    'struct_ma_resource_manager_data_supply_0_decodedPaged',
    'struct_ma_resource_manager_data_supply_0_encoded',
    'struct_ma_resource_manager_pipeline_notifications',
    'struct_ma_resource_manager_pipeline_stage_notification',
    'struct_ma_semaphore', 'struct_ma_slot_allocator',
    'struct_ma_slot_allocator_config',
    'struct_ma_slot_allocator_group', 'struct_ma_sound',
    'struct_ma_sound_config', 'struct_ma_sound_inlined',
    'struct_ma_spatializer', 'struct_ma_spatializer_config',
    'struct_ma_spatializer_listener',
    'struct_ma_spatializer_listener_config',
    'struct_ma_splitter_node', 'struct_ma_splitter_node_config',
    'struct_ma_stack', 'struct_ma_vec3f', 'struct_ma_vfs_callbacks',
    'struct_ma_waveform', 'struct_ma_waveform_config',
    'union___atomic_wide_counter', 'union_ma_biquad_coefficient',
    'union_ma_channel_converter_weights', 'union_ma_context_0',
    'union_ma_context_1', 'union_ma_context_command__wasapi_data',
    'union_ma_decoder_data', 'union_ma_device_3',
    'union_ma_device_id', 'union_ma_device_id_custom',
    'union_ma_device_notification_data', 'union_ma_encoder_data',
    'union_ma_job_1_2_aaudio', 'union_ma_job_1_device',
    'union_ma_job_1_resourceManager', 'union_ma_job_data',
    'union_ma_job_toc', 'union_ma_linear_resampler_x0',
    'union_ma_linear_resampler_x1', 'union_ma_noise_state',
    'union_ma_resampler_state',
    'union_ma_resource_manager_data_buffer_connector',
    'union_ma_resource_manager_data_source_backend',
    'union_ma_resource_manager_data_supply_backend', 'union_ma_timer',
    'union_pthread_cond_t', 'union_pthread_mutex_t', 'va_list']
