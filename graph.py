from operator import concat
import cv2
import numpy as np
import argparse
import sys
import math
import pytesseract
import os
import json

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def preprocess(img):
    #img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray=img
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_canny = cv2.Canny(img_blur, 50, 50)
    kernel = np.ones((3, 3))
    img_dilate = cv2.dilate(img_canny, kernel, iterations=2)
    img_erode = cv2.erode(img_dilate, kernel, iterations=1)
    #cv2.imshow("Image", img_erode)
    #cv2.waitKey(0)
    return img_erode
    #return img_gray

def find_tip(points, convex_hull, output):
    length = len(points)
    biggest = 0
    for i in range(length):
        for j in range(length):
            if i!=j and distance(tuple(points[i]),tuple(points[j])) > biggest :
                biggest = distance(points[i],points[j])
                point1 = points[i]
                point2 = points[j]
                index1=i
                index2=j
    smallest1=99999
    smallest2=99999
    for i in range(length):
        if i!=index1 and i!=index2:
            if distance(tuple(points[i]),tuple(point1)) < smallest1:
                smallest1 = distance(tuple(points[i]),tuple(point1))
            if distance(tuple(points[i]),tuple(point2)) < smallest2:
                smallest2 = distance(tuple(points[i]),tuple(point2))
    if smallest1<smallest2:
        point1=point2
        point2=points[index1]
    tup=[0,0]
    tup[0]=tuple(point1)
    tup[1]=tuple(point2)
    return tup
    cv2.circle(output, point1, 5, (0, 255, 0), cv2.FILLED)
    cv2.circle(output, point2, 5, (0, 255, 0), cv2.FILLED)
    cv2.imshow("Image", output)
    cv2.waitKey(0)

def find_tips(points):
    length = len(points)
    biggest = 0
    for i in range(length):
        for j in range(length):
            if distance(tuple(points[i]),tuple(points[j])) > biggest :
                biggest = distance(points[i],points[j])
                point1 = points[i]
                point2 = points[j]
                index1=i
                index2=j
    biggest2=0
    for i in range(length):
        for j in range(length):
            if i!=index1 and i!=index2 and j!=index1 and j!=index2 and biggest2 < distance(tuple(points[i]),tuple(points[j])):
                if distance(tuple(points[i]),tuple(point1)) > 60 and distance(tuple(points[i]),tuple(point2)) > 60 and distance(tuple(points[j]),tuple(point1)) > 60 and distance(tuple(points[j]),tuple(point2)) > 60:
                    biggest2 = distance(points[i],points[j])
                    point3 = points[i]
                    point4 = points[j]
                    index3 = i
                    index4 = j
    smallest1=99999
    for i in range(length):
        if i!=index1 and i!=index2 and i!=index3 and i!=index4 and distance(points[i],point1) < smallest1 :
            smallest1 = distance(points[i],point1)
    smallest2=99999
    for i in range(length):
        if i!=index1 and i!=index2 and i!=index3 and i!=index4 and distance(points[i],point2) < smallest2 :
            smallest2 = distance(points[i],point2)
    if smallest1 < smallest2:
        point5=point1
        point1=point2
        point2=point5
    smallest1=99999
    for i in range(length):
        if i!=index1 and i!=index2 and i!=index3 and i!=index4 and distance(points[i],point3) < smallest1 :
            smallest1 = distance(points[i],point3)
    smallest2=99999
    for i in range(length):
        if i!=index1 and i!=index2 and i!=index3 and i!=index4 and distance(points[i],point4) < smallest2 :
            smallest2 = distance(points[i],point4)
    if smallest1 < smallest2:
        point5=point3
        point3=point4
        point4=point5
    tup=[0,0,0,0]
    tup[0]=tuple(point1)
    tup[1]=tuple(point2)
    tup[2]=tuple(point3)        
    tup[3]=tuple(point4)
    return tup

def analyzetxt(txt):
    print(len(txt))
    for i in range(len(txt)):
        print('index '+str(i)+' is '+txt[i]+' with ASCII value ' + str(ord(txt[i])))

def processtxt(txt):
    txt2=''
    for i in range(len(txt)):
        if ord(txt[i]) > 47 and ord(txt[i]) < 123:
            txt2=txt2+txt[i]
    if len(txt2)==2 and txt2[0].isupper() and txt2[1]==txt[0].lower() :
            txt2=txt2[0:1]
    return txt2

def preprocesscrop(img):
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img

class edge:
    def __init__(self,countour,beg_point,edge_tip):
        self.cnt = countour
        self.beg = beg_point
        self.arr = edge_tip
    def highlight(self,img):
        cv2.drawContours(img, self.cnt, -1, (255, 0, 0), 2)
        cv2.circle(img, self.arr, 5, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, self.beg, 5, (0, 0, 255), cv2.FILLED)
    def getBeg(self):
        tup=[0,0]
        tup[0] = int(self.beg[0])
        tup[1] = int(self.beg[1])
        return tup
    def getArr(self):
        tup=[0,0]
        tup[0] = int(self.arr[0])
        tup[1] = int(self.arr[1])
        return tup

class node:
    def __init__(self,countour,name):
        self.cnt = countour
        self.name = name
        
    def highlight(self,img):
        cv2.drawContours(img, self.cnt, -1, (216,191,216), 5)
        print('Highlighting node '+ self.name)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image file")
args = vars(ap.parse_args())
im_in = cv2.imread(args["image"],cv2.IMREAD_GRAYSCALE) #plain image
output = im_in
th, im_th = cv2.threshold(im_in, 220, 255, cv2.THRESH_BINARY_INV) #plain invert
im_floodfill = im_th.copy() #get rid of arrows, fill nodes with black
h, w = im_th.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)
cv2.floodFill(im_floodfill, mask, (0,0), 255)
im_floodfill_inv = cv2.bitwise_not(im_floodfill)
im_out = im_th | im_floodfill_inv

kernelSize = [9,9]
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
opening = cv2.morphologyEx(im_out, cv2.MORPH_OPEN, kernel)
sub = cv2.subtract(im_out,opening)
exar = cv2.bitwise_not(sub)
exno = cv2.add(im_in,sub)

listEdges=[]
listNodes=[]
listNodesNames=[]
"""
cv2.imshow("Arrows", exar)
cv2.waitKey(0)
cv2.imshow("Nodes", exno)
cv2.waitKey(0)
"""
contours, hierarchy = cv2.findContours(preprocess(exar), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
for cnt in contours:
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.025 * peri, True)
    hull = cv2.convexHull(approx, returnPoints=False)
    sides = len(hull)
    if 6 > sides > 3 and (len(approx)!=8):
        tips = find_tip(approx[:,0,:], hull.squeeze(), output)
        listEdges.append(edge(cnt,tips[0],tips[1]))
    elif sides == 4 and len(approx) == 8:
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True)
        tips = find_tips(approx[:,0,:])
        listEdges.append(edge(cnt,tips[0],tips[1]))
        listEdges.append(edge(cnt,tips[2],tips[3]))

contours, hierarchy = cv2.findContours(preprocess(exno), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    x=x-10
    y=y-10
    w=w+20
    h=h+20
    cropped = exno[y:y + h, x:x + w]
    gray = cropped
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 0.9, 20, param1 = 50, param2 = 30, minRadius = 30, maxRadius = 155)
    if circles is not None:
        height = gray.shape[0]
        width = gray.shape[1]
        x=0; y=0
        x=x+int((width/4))
        y=y+int((height/4))
        w=int((width/2))
        h=int((width/2))
        cropped = gray[y:y + h, x:x + w]
        cropped = preprocesscrop(cropped)
        
        #cv2.imshow("Image", cropped)
        #cv2.waitKey(0)
        
        txt = pytesseract.image_to_string(cropped,config='--psm 9')
        #analyzetxt(txt)
        txt=processtxt(txt)
        listNodes.append(node(cnt,txt))
        listNodesNames.append(txt)
        print('Found node ' + txt)
output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
matrix = [[0 for i in range(len(listNodes))] for j in range(len(listNodes))]
print('Found '+str(len(listEdges))+' arrows')
for obj in listEdges:
    obj.highlight(output)
    nearest_beg=99999
    nearest_tip=99999
    for node_ in listNodes:
        dist = cv2.pointPolygonTest(node_.cnt,obj.getBeg(),True) * -1
        if dist<nearest_beg:
            nearest_beg = dist
            beg_node=node_
       #print('Distance from beg to '+ node_.name + ' is ' + str(dist))
        dist2 = cv2.pointPolygonTest(node_.cnt,obj.getArr(),True) * -1
        if dist2 < nearest_tip:
            nearest_tip = dist2
            tip_node=node_
        #print('Distance from arr to '+ node_.name + ' is ' + str(dist2))
    if len(listNodes)>0 :
        print('Found edge connecting '+ beg_node.name + ' to ' + tip_node.name)
        matrix[listNodesNames.index(beg_node.name)][listNodesNames.index(tip_node.name)] = 1
    #cv2.imshow("Image", output)
    #cv2.waitKey(0)


for obj in listNodes:
    obj.highlight(output)
    #cv2.imshow("Image", output)
    #cv2.waitKey(0)

dictout={
        "num_nodes": len(listNodes),
        "node_names": listNodesNames,
        "matrix": matrix
    }

path = r'outputs'
isExist = os.path.exists(path)
if not isExist:
  os.makedirs(path)
  print("outputs directory created")
directory = r'outputs'
os.chdir(directory)
path_to_image = args["image"]
index1 = path_to_image.find('/')
imgName=path_to_image[index1+1:]
index1 = imgName.find('/')
imgName=imgName[index1+1:]
cv2.imwrite(imgName,output)
jsonName=imgName[0:len(imgName)-3]+"json"
with open(jsonName, "w") as outfile:
    json.dump(dictout, outfile)
print("Writing file "+imgName)
os.chdir('../')

sys.exit()




