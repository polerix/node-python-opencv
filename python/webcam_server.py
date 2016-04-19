import cv2, imutils, base64, socket, sys, recognizer, detector
import numpy as np

from os.path import isfile
MOVE_DETECTION = 'MOVDET'
FACE_DETECTION = 'FACDET'
FACE_RECOGNIZE = 'FACREC'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        TCP_IP = '127.0.0.1'
        TCP_PORT = int(sys.argv[1])
        video = cv2.VideoCapture(0)
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
                        if video.isOpened():
                            success, frame = video.read()
                        else:
                            frame = np.zeros((300, 300), dtype=np.uint8)
                            cv2.putText(frame, 'Camera(s) OFF', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                        frame = imutils.resize(frame, width = 300)
                        #cv2.imshow('image',frame)
                        #if cv2.waitKey(1) & 0xFF == ord('q'):
                        #    break
                        t = cv2.getTickCount()
                        faces = recognizer.Face.findFrame(frame, flux[0], flux[1], float(flux[2]), int(flux[3]))
                        t = cv2.getTickCount() - t
                        print "detection time = %gms" % (t/(cv2.getTickFrequency()*1000.))

                        t = cv2.getTickCount()
                        finds = '{"faces": ['
                        index = 0
                        for data in faces:
                            index += 1
                            finds += '%s' % data
                            if index < len(faces):
                                finds += ','
                        finds += ']}'
                        conn.sendall('%s' % finds)
                        t = cv2.getTickCount() - t
                        print "send time = %gms" % (t/(cv2.getTickFrequency()*1000.))

                if data.startswith(FACE_DETECTION):
                    buffer = int(data[6:])
                    conn.send('BUFFER OK')

                    data = conn.recv(buffer)
                    print data
                    flux = data.split(' ')

                    while True:
                        if video.isOpened():
                            success, frame = video.read()
                        else:
                            frame = np.zeros((300, 300), dtype=np.uint8)
                            cv2.putText(frame, 'Camera(s) OFF', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                        frame = imutils.resize(frame, width = 300)
                        #cv2.imshow('image',frame)
                        #if cv2.waitKey(1) & 0xFF == ord('q'):
                        #    break
                        t = cv2.getTickCount()
                        faces = detector.FaceDetection.findFrame(frame, flux[0], float(flux[1]), int(flux[2]))
                        t = cv2.getTickCount() - t
                        print "detection time = %gms" % (t/(cv2.getTickFrequency()*1000.))

                        t = cv2.getTickCount()
                        finds = '{"faces": ['
                        index = 0
                        for (x, y, w, h) in faces:
                            index += 1
                            finds += '{"x": "%s", "y": "%s", "w": "%s", "h": "%s"}' % (x, y, w, h)
                            if index < len(faces):
                                finds += ','
                        finds += ']}'
                        conn.sendall('%s' % finds)
                        t = cv2.getTickCount() - t
                        print "send time = %gms" % (t/(cv2.getTickFrequency()*1000.))
                        
            except:
                message = '%s' % sys.exc_value
                message = message.replace('\\', '/').replace('\n', '').replace('\r', '')
                conn.send('{"error": "%s"}' % message)
            conn.close()
        s.close()
        video.release()
        cv2.destroyAllWindows()
