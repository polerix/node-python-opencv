import cv2, os, csv
import numpy as np

from os.path import isfile
lastCSVFile = ''
trained = False
recognizer = None
faceCascade = None
names = None

class Face:
    @staticmethod
    def find(csvFile, image, haarcascade, scaleFactor = 1.2, minNeighbors = 8):
        global lastCSVFile, trained, recognizer, faceCascade, names
        frame = image.decode('base64', 'strict')
        frame = cv2.imdecode(np.fromstring(frame, dtype=np.uint8), -1)
        return findFrame(frame, csvFile, haarcascade, scaleFactor, minNeighbors)

    @staticmethod
    def findFrame(frame, csvFile, haarcascade, scaleFactor = 1.2, minNeighbors = 8):
        global lastCSVFile, trained, recognizer, faceCascade, names
   
        if (trained == True and lastCSVFile <> csvFile):
            trained = False

        if (trained == False):
            trained = True
            lastCSVFile = csvFile
            file = open(csvFile)
            faceCascade = cv2.CascadeClassifier(haarcascade)
            images = []
            names = []
            labels = []
            rownum = 0
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if rownum == 0:
                    header = row
                else:
                    idx = row[0]
                    name = row[1]
                    path = row[2]
                    if isfile(path) and path.endswith('.jpg'):
                        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                        img_to_save = cv2.resize(img, (100, 100))
                        images.append(img_to_save)
                        names.append(name)
                        labels.append(int(idx))
                rownum += 1
            file.close()
            print "starting recognizer"
            #recognizer = cv2.face.createLBPHFaceRecognizer()
            #recognizer = cv2.face.createEigenFaceRecognizer(10, 10.0)
            recognizer = cv2.createEigenFaceRecognizer()
            recognizer.train(images, np.array(labels))
            print "done recognizer"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = faceCascade.detectMultiScale(gray, scaleFactor, minNeighbors)

        finds = []
        for (x, y, w, h) in faces:
            img_to_check = cv2.resize(gray[y: y + h, x: x + w], (100, 100))
            nbr_predicted, conf = recognizer.predict(img_to_check)
            if nbr_predicted > 0 and conf < 4000:
                finds.append('{"name": "%s", "x": "%s", "y": "%s", "w": "%s", "h": "%s"}' % (names[nbr_predicted], x, y, w, h))
        return finds
