Module for recording the videos using OpenCV

Requirements: 
1. Need to install ffmpeg in the directory of your project. ( Very Importatnt)
2. To install, simply add the path of ffmpeg.exe ("C:\....\CameraModule\ffmpeg\bin") in system environment's path variable.
3. ffmpeg is included with this module so you don't need to download it manually.

Intstructions to use the module :

1. Simple import the camera_module in your module/ python file.

2.Get the instance of the VideoRecorder and AudioRecorder class and pass the following args to "get_instance" function:
	a. device_index [optional, default: 0] -- To use other camera devices pass 1,2...like this
    b. filename -- base filename for both video and audio [default: temp]
    c. frameSize [optional, Default: 640 X 480]
	d. show_screen [optional, Default: True] -- Enable or disable the Frame Screen
	e. frame_per_second [optional, Default: 24] -- Set the frame per second
	
	***First Video object is returned and then audio object.... Pass the objects as argument in other funtions in same order.
	
3. Pass the objects recieved in (2) and pass it to the "start_av_recording" function.
	This function starts separate thread for the audio and video stream.
	
4. When the Frame or Camera Feed is being shown -- Press 'q' to stop or else wait for the process to finish

5. Call the stop_av_recording() fucntion and pass the objects recieved in (2).
	This will stop the audio and video thread and merge two to create a single file in .mp4 format
	
6. Refer "test.py" for reference.