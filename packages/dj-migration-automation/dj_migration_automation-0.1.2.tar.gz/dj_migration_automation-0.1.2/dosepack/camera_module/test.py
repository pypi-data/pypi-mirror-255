import camera_module
import time

if __name__ == "__main__":
    video, audio = camera_module.get_instances(device_index=1, filename='test_4', frameSize=(1024, 720),
                                               show_screen=True, frame_per_second=29)

    camera_module.start_av_recording(video, audio,1)
    time.sleep(5)
    camera_module.stop_av_recording(video, audio,1)
    camera_module.release_instance(video, audio)