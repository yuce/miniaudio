import ctypes

# lib = ctypes.CDLL("../miniaudio.so")
# print(lib)

import miniaudio as ma
# for item in dir(ma):
#     print(item)



decoder = ma.ma_decoder()


@ctypes.CFUNCTYPE(None, ctypes.POINTER(ma.struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)
def data_callback(pDevice, pOutput, pInput, frameCount):
    pDecoder = decoder
    ma.ma_decoder_read_pcm_frames(pDecoder, pOutput, frameCount, None)


result = ma.ma_decoder_init_file("/dev/shm/output.wav".encode("utf-8"), None, ctypes.byref(decoder))
if result != ma.MA_SUCCESS:
    raise Exception(f"failed: {result}")

device_config = ma.ma_device_config_init(ma.ma_device_type_playback)
device_config.playback.format   = decoder.outputFormat
device_config.playback.channels = decoder.outputChannels
device_config.sampleRate        = decoder.outputSampleRate
device_config.dataCallback      = data_callback

device = ma.ma_device()

res = ma.ma_device_init(None, ctypes.byref(device_config), ctypes.byref(device))
if res != ma.MA_SUCCESS:
    ma.ma_device_uninit(ctypes.byref(device))
    ma.ma_decoder_uninit(ctypes.byref(decoder))
    raise Exception(f"failed device init: {result}")

res = ma.ma_device_start(ctypes.byref(device))
if res != ma.MA_SUCCESS:
    ma.ma_device_uninit(ctypes.byref(device))
    ma.ma_decoder_uninit(ctypes.byref(decoder))
    raise Exception(f"failed device start: {result}")

input("Enter to quit")
ma.ma_device_uninit(ctypes.byref(device))
ma.ma_decoder_uninit(ctypes.byref(decoder))

