import cv, imutils, base64, socket, sys, detect
import numpy as np

from os.path import isfile
MOVE_DETECTION = 'MOVDET'
FACE_DETECTION = 'FACDET'
FACE_RECOGNIZE = 'FACREC'


if __name__ == '__main__':
    if len(sys.argv) == 2:
        TCP_IP = '127.0.0.1'
        TCP_PORT = int(sys.argv[1])
        video = cv.CreateCameraCapture(0) #cv2.VideoCapture(0)

        width = 320 #leave None for auto-detection
        height = 240 #leave None for auto-detection

        cv.SetCaptureProperty(video,cv.CV_CAP_PROP_FRAME_WIDTH,width)
        cv.SetCaptureProperty(video,cv.CV_CAP_PROP_FRAME_HEIGHT,height)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)

        while 1:
            conn, addr = s.accept()
            data = conn.recv(16)
            try:
                if data == 'STOP':
                    break
                if data.startswith(FACE_RECOGNIZE):
                    buffer = int(data[6:])
                    conn.send('BUFFER OK')

                    data = conn.recv(buffer)
                    print data
                    flux = data.split(' ')

                    while True:
                        frame = cv.QueryFrame(video)
                        faces = detect.FaceDetection.findFrame(frame, flux[0], flux[1], float(flux[2]), int(flux[3]))
                        #todo - add face recognizer
                        if (faces):
                            finds = '{"faces": ['
                            index = 0
                            for data in faces:
                                index += 1
                                finds += '%s' % data
                                if index < len(faces):
                                    finds += ','
                            finds += ']}'
                            conn.sendall('%s' % finds)

                        #if cv.WaitKey(10) >= 0:
                        #        break
                if data.startswith(FACE_DETECTION):
                    buffer = int(data[6:])
                    conn.send('BUFFER OK')

                    data = conn.recv(buffer)
                    print data
                    flux = data.split(' ')

                    while True:
                        image = cv.QueryFrame(video)
                        faces = detect.FaceDetection.findFrame(image, flux[0], float(flux[1]), int(flux[2]))

                        if (faces):
                            finds = '{"faces": ['
                            index = 0
                            for ((x, y, w, h), n) in faces:
                                index += 1
                                finds += '{"x": "%s", "y": "%s", "w": "%s", "h": "%s"}' % (x, y, w, h)
                                if index < len(faces):
                                    finds += ','
                            finds += ']}'
                            conn.sendall('%s' % finds)
                        #if cv.WaitKey(10) >= 0:
                        #        break
            except:
                message = '%s' % sys.exc_value
                message = message.replace('\\', '/').replace('\n', '').replace('\r', '')
                conn.send('{"error": "%s"}' % message)
                conn.close()
                s.close()
                video.release()
                cv.destroyAllWindows()
