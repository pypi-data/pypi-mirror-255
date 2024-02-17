"""
Created By: Jitendra Saxena
Created Date:
Python Version: 2.7

Purpose: An audio-video recording module. Records the video in "XVID" format and device resolution can be passed as 
         parameters
"""

try:
    import cv2
    import wave
    import pyaudio
except ImportError as import_error:
    print ('Cannot run camera module -- Error in importing all/one of the following: [ cv2, wave, pyaudio ].' \
          ' Following exception was thrown: ', import_error)
    pass
import threading
import time
import datetime
import os
import subprocess


class VideoRecorder:
    # Video class based on openCV
    def __init__(self, device_index=0, video_filename='temp', fps=30, frameSize=(1024, 720), show_screen=False):
        self.open = True
        self.close = False
        self.device_index = device_index
        self.fps = fps  # fps should be the minimum constant rate at which the camera can
        self.fourcc = "MJPG"  # capture images (with no decrease in speed over time; testing is required)
        self.filename = video_filename
        self.video_filename = ''

        # Setting the frame size of the video to be recorded
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, frameSize[0])
        self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frameSize[1])

        self.frameSize = (int(self.video_cap.get(3)), int(
            self.video_cap.get(4)))  # video formats and sizes also depend and vary according to the camera used
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = ''
        self.frame_counts = 1
        self.record_thread = ''  # Instance variable for storing the name of thread
        self.show_screen = show_screen

    def filemanager(self, filename):
        """
        Function for creating appropriate folders and setting the video file name.

        Return: Name of the video_file
        """

        local_path = os.path.join(os.getcwd(), 'camera_files', 'videos_only')
        current_date = datetime.datetime.now().strftime("%m") + "_" + \
                       datetime.datetime.now().strftime("%d") + "_" + \
                       datetime.datetime.now().strftime("%Y") + "_" + str(time.time())

        folder_name = filename
        folder_path = os.path.join(local_path, folder_name)

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, (filename + "_" + current_date + ".avi"))
        return filename

    # Function for start recording the video stream
    def record(self):
        """
        Starts recording the video and saving it in appropriate directory ( specified in self.video_filename )
        """
        self.open = True
        self.close = False
        self.video_filename = self.filemanager(self.filename)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        while (self.open == True):
            ret, video_frame = self.video_cap.read()
            if ret:

                # getting the system time and inserting it in the captured frame before writing it to a file
                time_stamp = str(datetime.datetime.now())
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.line(video_frame, (20, 15), (261, 15), (0, 0, 0), 25, lineType=cv2.LINE_AA)
                cv2.putText(video_frame, time_stamp, (30, 20), font, 0.9, (255, 255, 255), 1, cv2.LINE_AA)

                # cv2.line(video_frame, (5, 5), (250, 5), (0, 255, 0), 30, lineType=cv2.LINE_4)
                # cv2.putText(video_frame, time_stamp, (10, 16), font, 0.9, (255, 0, 0), 1, cv2.LINE_AA)

                # video_frame = cv2.flip(video_frame, 1)

                try:
                    # Save the video
                    self.video_out.write(video_frame)
                except Exception as e:
                    print ("Error Occurred:")
                    print ("**************")
                    print (str(e))

                else:
                    # displayed to screen while recording
                    if self.show_screen:
                        try:
                            cv2.imshow(self.video_filename, video_frame)
                        except Exception as err:
                            print ('Exception in showing frames:', err)
                        else:
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                            # Wait for the keyboard key to be pressed for terminating
                            # Press ' q ' to stop recording or wait for the thread to finish
                            # if cv2.waitKey(2) & 0xFF == ord('q'):
                            #     break
                if not self.open:
                    break
            else:
                break
        # Check whether video has been saved or not
        print ('Video saved\n')
        self.close = True

    # Starts the video recording by creating a new thread
    def start(self):
        self.record_thread = threading.Thread(target=self.record, name='Video thread')
        self.record_thread.start()
        print ('\n**** Video Capture is Running ****')

    # Stops the video recording thread
    def stop(self):
        """
        Finishes the video recording therefore the thread too
        """
        if self.open:
            self.open = False

            while not self.close:
                pass

            print ('Video stop', self.close)
            if self.close:
                if self.show_screen:
                    # destroy window if being shown
                    print ('Destroying Window --', self.video_filename)
                    cv2.destroyWindow(self.video_filename)

                self.video_out.release()
                print ('Closing Video Capture')
                # self.video_cap.release()

        # Wait for the video thread to complete
        # print 'Video thread', self.record_thread.get
        while self.record_thread.isAlive():
            time.sleep(1)


class AudioRecorder:
    """
    Class for recording the audio
    """

    # Audio class based on pyAudio and Wave
    def __init__(self, audio_filename='tmp'):

        self.open = True
        self.close = False
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_file = audio_filename
        self.audio_filename = ''
        self.audio = pyaudio.PyAudio()
        self.stream = ''
        self.audio_frames = list()
        self.audio_thread = ''  # variable for storing thread

    def filemanager(self, filename):
        """
        Function for creating appropriate folders and setting the audio file name.

        Return: Name of the video_file
        """

        local_path = os.path.join(os.getcwd(), 'camera_files', 'audio_only')
        current_date = datetime.datetime.now().strftime("%m") + "_" + \
                       datetime.datetime.now().strftime("%d") + "_" + \
                       datetime.datetime.now().strftime("%Y") + "_" + str(time.time())

        folder_name = filename
        folder_path = os.path.join(local_path, folder_name)

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, (filename + "_" + current_date + ".wav"))
        return filename

    # Audio starts being recorded
    def record(self):
        self.open = True
        self.close = False
        self.audio_frames = []
        self.audio_filename = self.filemanager(self.audio_file)
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.stream.start_stream()
        print ('\n**** Audio Capture is Running ****')
        while self.open:
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if not self.open:
                break
        # set stop to true
        self.close = True

    # Finishes the audio recording therefore the thread too
    def stop(self):

        if self.open:
            self.open = False
            print ('Audio stop', self.close)
            while not self.close:
                pass
            print ('Audio stop', self.close)
            if self.close:
                self.stream.stop_stream()
                self.stream.close()
                print ('\nClosing Audio capture')
                # self.audio.terminate()
                print (len(self.audio_frames))
                print (self.audio_filename)
                wave_file = wave.open(self.audio_filename, 'wb')
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.audio.get_sample_size(self.format))
                wave_file.setframerate(self.rate)
                wave_file.writeframes(b''.join(self.audio_frames))
                wave_file.close()

            # Wait for the audio thread to complete
            while self.audio_thread.isAlive():
                time.sleep(1)

    # Launches the audio recording function using a thread
    def start(self):
        self.audio_thread = threading.Thread(target=self.record)
        self.audio_thread.start()


def get_instances(device_index=0, filename='tmp', frameSize=(500, 500),
                  show_screen=False, frame_per_second=30):
    """
    Returns video and audio object of VideoRecorder and AudioRecorder class.
    :param device_index: index of the device to use [0,1,2]
    :param filename: name of the file
    :param frameSize: frame size to be set
    :param show_screen: whether camera feed or screen needs to be shown
    :param frame_per_second: frame per second to be set
    :return: video and audio object [return video, audio]
    """
    video_object = VideoRecorder(device_index, filename, frame_per_second, frameSize, show_screen)
    audio_object = AudioRecorder(filename)
    return video_object, audio_object


def release_instance(video_recorder_object, audio_recorder_object):
    """
    Release the resources that are in use.
    :param video_recorder_object: Object of VideoRecorder class.
    :param audio_recorder_object: Object of AudioRecorder class.
    :return: Nothing
    """
    video_recorder_object.video_cap.release()
    audio_recorder_object.audio.terminate()


def start_av_recording(video_recorder_object, audio_recorder_object,flag=0):
    """
    Starts audio and video thread separately.
    :param video_recorder_object: object of the VideoRecorder class.
    :param audio_recorder_object: object of the AudioRecorder class.
    :param flag: This flag defines type of recording , 0:both,1: only video , 2:only audio.
    :return: None
    """

    # if os.path.exists(video_file):
    #     os.remove(video_file)
    # if os.path.exists(audio_file):
    #     os.remove(audio_file)
    if flag == 1:
        video_recorder_object.start()
    elif flag == 2:
        audio_recorder_object.start()
    else:
        video_recorder_object.start()
        audio_recorder_object.start()


def stop_av_recording(video_recorder_object, audio_recorder_object,flag=0):
    """
    Stops the audio and video thread and merge the two.
    param video_recorder_object: object of the VideoRecorder class.
    :param audio_recorder_object: object of the AudioRecorder class.
    :param flag: This flag defines type of recording , 0:both,1: only video , 2:only audio.
    :return: None
    """
    if flag == 1:
        video_recorder_object.stop()
    elif flag == 2:
        audio_recorder_object.stop()
    else:
        video_recorder_object.stop()
        audio_recorder_object.stop()

        # Makes sure the threads have finished
        # while threading.active_count() > 1:
        #     time.sleep(1)
        # Create a file in the videos folder
        filename = video_recorder_object.filename
        filename = filemanager(filename)
        print('\n**** File Name: ', filename)
        # Merging audio and video signal

        # if abs(recorded_fps - 6) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected
        #
        #     print "Re-encoding"
        #     cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        #     subprocess.call(cmd, shell=True)
        #
        #     print "Muxing"
        #     cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
        #     subprocess.call(cmd, shell=True)
        #
        # else:
        audio_file = audio_recorder_object.audio_filename
        video_file = video_recorder_object.video_filename

        print ('\n Video file: ', video_file)
        print ('\n Audio file: ', audio_file)

        print ("Normal recording\nMuxing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i " + audio_file + " -i " + video_file \
              + " -pix_fmt yuv420p " + filename
        subprocess.call(cmd, shell=True)

        # Remove the video and audio files
        # os.remove(audio_file)
        # os.remove(video_file)

        print ("Encoding Done....Video saved")
        return filename


def filemanager(filename):
    """
    Function for creating appropriate folders and setting the video file name.

    Return: Name of the video_file
    """

    local_path = os.path.join(os.getcwd(), 'camera_files', 'videos')
    current_date = datetime.datetime.now().strftime("%m") + "_" + \
                   datetime.datetime.now().strftime("%d") + "_" + \
                   datetime.datetime.now().strftime("%Y") + "_" + \
                   str(time.time())

    folder_name = filename
    folder_path = os.path.join(local_path, folder_name)

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = os.path.join(folder_path, (filename + "_" + current_date + ".mp4"))
    return filename
