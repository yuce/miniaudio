import sys
import ctypes

import miniaudio as M


data_callback = ctypes.CFUNCTYPE(None, ctypes.POINTER(M.struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)


class PlayHandle:

    def __init__(self, device, decoder, cb):
        self._device = device
        self._decoder = decoder
        self._cb = cb

    def destroy(self):
        M.ma_device_uninit(ctypes.byref(self._device))
        M.ma_decoder_uninit(ctypes.byref(self._decoder))


decoder = M.ma_decoder()
device = M.ma_device()

def playfile(path: str) -> PlayHandle:
    def on_data(pDevice, out, inp, frame_count):
        M.ma_decoder_read_pcm_frames(decoder, out, frame_count, None)

    result = M.ma_decoder_init_file(path.encode("utf-8"), None, ctypes.byref(decoder))
    if result != M.MA_SUCCESS:
        # TODO: proper exception
        raise Exception(f"failed: {result}")
    
    device_config = M.ma_device_config_init(M.ma_device_type_playback)
    device_config.playback.format   = decoder.outputFormat
    device_config.playback.channels = decoder.outputChannels
    device_config.sampleRate        = decoder.outputSampleRate
    device_config.dataCallback      = data_callback(on_data)
    res = M.ma_device_init(None, ctypes.byref(device_config), ctypes.byref(device))
    if res != M.MA_SUCCESS:
        M.ma_device_uninit(ctypes.byref(device))
        M.ma_decoder_uninit(ctypes.byref(decoder))
        # TODO: proper exception
        raise Exception(f"failed device init: {result}")
    res = M.ma_device_start(ctypes.byref(device))
    if res != M.MA_SUCCESS:
        M.ma_device_uninit(ctypes.byref(device))
        M.ma_decoder_uninit(ctypes.byref(decoder))
        # TODO: proper exception
        raise Exception(f"failed device start: {result}")

    input("www")
    return PlayHandle(device, decoder, on_data)


if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} FILE.wav")
    sys.exit(1)

path = sys.argv[1]
handle = playfile(path)
input("Press Enter to quit...")
#handle.destroy()
