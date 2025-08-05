import sys
import ctypes

import miniaudio as M


data_callback = ctypes.CFUNCTYPE(None, ctypes.POINTER(M.struct_ma_device), ctypes.POINTER(None), ctypes.POINTER(None), ctypes.c_uint32)


class PlayHandle:

    def __init__(self, device):
        self._device = device

    def destroy(self):
        self._device.destroy()
        # M.ma_device_uninit(ctypes.byref(self._device))
        # M.ma_decoder_uninit(ctypes.byref(self._decoder))


class Device:

    def __init__(self):
        self.decoder = M.ma_decoder()
        self.device = M.ma_device()
        self.device_config = M.ma_device_config_init(M.ma_device_type_playback)

    def destroy(self):
        M.ma_device_uninit(ctypes.byref(self.device))
        M.ma_decoder_uninit(ctypes.byref(self.decoder))
        

    def playfile(self, path: str) -> PlayHandle:
        def on_data(device, out, inp, frame_count):
            device = device.contents
            decoder = ctypes.cast(device.pUserData, ctypes.POINTER(M.ma_decoder))
            if not decoder:
                return
            M.ma_decoder_read_pcm_frames(decoder, out, frame_count, None)

        decoder = self.decoder

        result = M.ma_decoder_init_file(path.encode("utf-8"), None, ctypes.byref(decoder))
        if result != M.MA_SUCCESS:
            # TODO: proper exception
            raise Exception(f"failed: {result}")

        device = self.device
        device_config = self.device_config
    
        device_config.playback.format   = decoder.outputFormat
        device_config.playback.channels = decoder.outputChannels
        device_config.sampleRate        = decoder.outputSampleRate
        device_config.dataCallback      = data_callback(on_data)
        device_config.pUserData = ctypes.addressof(decoder)
    
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

        return PlayHandle(self)


if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} FILE.wav")
    sys.exit(1)

path = sys.argv[1]
device = Device()
handle = device.playfile(path)
input("Press Enter to quit...")
handle.destroy()
