
Computer Vision Part :-
=========================================================

This Part demonstrates real-time face recognition using OpenCV (`cv2`) and the `face_recognition` library in Python. The script captures video from the webcam, processes each frame to detect and recognize faces, and then displays the video with rectangles drawn around the recognized faces.

Requirements
------------

To install the required packages, run:

    cd /Computervision
    pip install -r requirements.txt

How to Use
----------

1.  **Place a Known Face Image:**
    *   Place an image file of the person you want to recognize (e.g., `amir.png`) in the same directory as the script.
2.  **Run the Script:**
    *   Use the following command to run the script:
    ````
        python face_recognition.py
    ````
3.  **How It Works:**
    *   The script will:
        *   Capture video from the default webcam.
        *   Load a known face from the provided image (`amir.png`).
        *   Detect faces in each video frame.
        *   Compare detected faces with the known face encoding.
        *   Draw a rectangle around recognized faces and display the name.
        *   Print a `Face Detected` flag to the console (`1` if a face is recognized, `0` otherwise).
4.  **Stop the Script:**
    *   Press the `q` key to stop the video capture and close all windows.

