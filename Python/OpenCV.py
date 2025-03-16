import cv2 # CV
import numpy as np # CV
import requests # HTTP
import time # TIMING

# ESP32 URL
URL = "http://10.0.0.15"
AWB = True

# Test connection to ESP32 first
try:
    response = requests.get(URL, timeout=5)
    print(f"Connection test: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Failed to connect to ESP32: {e}")
    exit(1)

# Face recognition and opencv setup
try:
    cap = cv2.VideoCapture(URL + ":81/stream")
    # may be reduant but im pre sure it does increase the res 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set to your desired width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Set to your desired height
    if not cap.isOpened():
        print("Failed to open video stream")
        exit(1)
    
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if face_classifier.empty():
        print("Failed to load face classifier")
        exit(1)
except Exception as e:
    print(f"Setup error: {e}")
    exit(1)

def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))
        
        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            resolutions_Array = ['0: QQVGA(160x120)', '', '', '3: HQVGA(240x176)', '4: QVGA(320x240)', '5: CIF(400x296)', '6: VGA(640x480)', '7: SVGA(800x600)', '8: XGA(1024x768)', '9: SXGA(1280x1024)', '10: UXGA(1600x1200)']
            response = requests.get(url + "/control?var=framesize&val={}".format(index), timeout=5)
            print(f"Resolution set response: {response.status_code}")
            print(f"Resolution set to {resolutions_Array[index]}")
            return True
        else:
            print("Wrong index")
            return False
    except Exception as e:
        print(f"SET_RESOLUTION error: {e}")
        return False



def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if 10 <= value <= 63:
            response = requests.get(url + "/control?var=quality&val={}".format(value), timeout=5)
            print(f"Quality set response: {response.status_code}")
            return True
        else:
            print("Quality value must be between 10 and 63")
            return False
    except Exception as e:
        print(f"SET_QUALITY error: {e}")
        return False

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        response = requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0), timeout=5)
        print(f"AWB set response: {response.status_code}")
        return awb
    except Exception as e:
        print(f"SET_AWB error: {e}")
        return awb

# Camera reconnection upon failure
def get_frame(cap, url):
    if not cap.isOpened() or not cap.grab():
        print("Reconnecting to camera...")
        cap.release()
        cap = cv2.VideoCapture(url + ":81/stream", cv2.CAP_FFMPEG)
        time.sleep(1)  # Give it time to connect
        return cap, None
    
    ret, frame = cap.retrieve()
    if not ret:
        return cap, None
    return cap, frame

#reconnect runs everytime camera settings are modified
def reconnect_camera(url):
    try:
        print("Reconnecting camera...")
        time.sleep(2)  # Wait for camera to adjust
        new_cap = cv2.VideoCapture(url + ":81/stream", cv2.CAP_FFMPEG)
        if not new_cap.isOpened():
            print("Failed to reconnect camera")
            return None
        return new_cap
    except Exception as e:
        print(f"Reconnection error: {e}")
        return None
    
def change_resolution(URL, idx):
    set_resolution(URL, index=idx, verbose=True)
    cap.release()
    cap = reconnect_camera(URL)

def run_camera():
    try:
        # Initialize video capture
        cap = cv2.VideoCapture(URL + ":81/stream")
        if not cap.isOpened():
            print("Failed to open video stream")
            return
            
        # Set initial resolution
        set_resolution(URL, index=8)
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            if cap.isOpened():
                try:
                    ret, frame = cap.read()
                    
                    if not ret:
                        print("Failed to read frame")
                        time.sleep(1)
                        continue
                    
                    frame_count += 1
                    if frame_count % 30 == 0:
                        fps = frame_count / (time.time() - start_time)
                        print(f"FPS: {fps:.2f}")
                        frame_count = 0
                        start_time = time.time()
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.equalizeHist(gray)
                    
                    faces = face_classifier.detectMultiScale(gray)
                    for (x, y, w, h) in faces:
                        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 4)
                
                    cv2.imshow("ESP32 Camera Feed", frame)
                
                except cv2.error as e:
                    print(f"OpenCV error: {e}")
                    cap.release()
                    cap = reconnect_camera(URL)
                    continue
                    
                key = cv2.waitKey(1)
                
                if key == ord('r'):
                    idx = int(input("Select resolution index: "))
                    if set_resolution(URL, index=idx, verbose=True):
                        cap.release()
                        cap = reconnect_camera(URL)
                elif key == ord('q'):
                    val = int(input("Set quality (10 - 63): "))
                    if set_quality(URL, value=val):
                        cap.release()
                        cap = reconnect_camera(URL)
                elif key == ord('a'):
                    AWB = set_awb(URL, AWB)
                elif key == 27:  # ESC key
                    break
            else:
                print("Video capture is not open. Trying to reopen...")
                cap = reconnect_camera(URL)
                if cap is None:
                    print("Failed to reconnect. Waiting before retry...")
                    time.sleep(5)
                    cap = cv2.VideoCapture(URL + ":81/stream")
                
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cv2.destroyAllWindows()
        if 'cap' in locals() and cap is not None:
            cap.release()
        print("Resources released")

# Keep original functionality when run directly
if __name__ == '__main__':
    run_camera()