import cv2
import os
import numpy as np
import pytesseract

#   pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def get_contours(img, cThr = [115, 120], showCanny = False, minArea = 20000, filter = 4, draw = True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    canny = cv2.Canny(blur, cThr[0], cThr[1])
    dilatation = cv2.dilate(canny, np.ones((5, 5)), iterations=3)
    erosion = cv2.erode(dilatation, np.ones((5, 5)), iterations=2)
    tmp = cv2.resize(erosion, (640, 480))
    if showCanny: cv2.imshow("Canny", tmp)

    contours, hierarchy = cv2.findContours(erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    finalContours = []

    for i in contours:
        area = cv2.contourArea(i)
        if area > minArea:
            peri = cv2.arcLength(i, True) # obvod
            approx = cv2.approxPolyDP(i, 0.02*peri, closed=True) # edges position
            bbox = cv2.boundingRect(approx)
            if filter != 0:
                if len(approx) == filter:
                    finalContours.append([len(approx), area, approx, bbox, i])
            else:
                finalContours.append([len(approx), area, approx, bbox, i])

    finalContours = sorted(finalContours, key = lambda x: x[1], reverse=True) # sort based on area
    print(len(finalContours))

    if draw:
        for contour in finalContours:
            cv2.drawContours(img, contour[4], -1, (0, 0, 255), 10)
    return img, finalContours

def reorder(points):
    points_new = np.zeros_like(points)
    points = points.reshape((4,2))
    add = points.sum(1)
    points_new[0] = points[np.argmin(add)]
    points_new[3] = points[np.argmax(add)]

    diff = np.diff(points, axis=1)
    points_new[1] = points[np.argmin(diff)]
    points_new[2] = points[np.argmax(diff)]
    return points_new

def warp_image(img, points, w, h, pad = 1):
    points = reorder(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0,0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    img_warp = cv2.warpPerspective(img, matrix, (w, h))
    img_warp = img_warp[pad:img_warp.shape[0]-pad, pad:img_warp.shape[1]-pad]
    return img_warp


for f in os.listdir("karty"):
    if os.path.splitext(f)[1].lower() in ('.jpg', '.jpeg'):
        img = cv2.imread(os.path.join("karty", f))
        img, conts = get_contours(img, cThr = [90, 100])
        if len(conts) != 0:
            img_warp = warp_image(img, conts[0][2], 800, 1250)
            cv2.imwrite(f"karty/cropped/{f}", img_warp)
            os.remove(f"karty/{f}")
        cv2.waitKey(1)

