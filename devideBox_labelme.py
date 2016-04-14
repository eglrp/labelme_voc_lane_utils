from xml.dom.minidom import parse
import xml.dom.minidom
import string
import math
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import gc
import os

dy = 30

single_line_dataset = "E:/dataset/extra_diversity_lane/All_annotation_labelme"
des_dir = "E:/dataset/extra_diversity_lane/All_annotation_labelme_" + str(dy)


def trans_multi_box(xmlName):
    print xmlName
    DOMTree = xml.dom.minidom.parse(single_line_dataset + '/' + xmlName)
    Data = DOMTree.documentElement
    objects = Data.getElementsByTagName("object")
    for object in objects:
        # skip deleted lines
        if object.getElementsByTagName("deleted")[0].childNodes[0].data == '1':
            continue
        # skip line of no name
        if len(object.getElementsByTagName("name")) == 0:
            continue
        if len(object.getElementsByTagName("name")[0].childNodes) == 0:
            continue
        # incorrect anotation:single point
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')

        if len(pts) <= 1: # incorrect anotation
            continue

        # polygon to line
        line_list = list()
        pt_list = [pt for pt in pts]
        for i in range(0, len(pt_list)-1, 1):
            line_list.append((string.atoi(pt_list[i].getElementsByTagName("x")[0].childNodes[0].data),\
                            string.atoi(pt_list[i].getElementsByTagName("y")[0].childNodes[0].data),\
                            string.atoi(pt_list[i+1].getElementsByTagName("x")[0].childNodes[0].data),\
                            string.atoi(pt_list[i+1].getElementsByTagName("y")[0].childNodes[0].data)))

        for line in line_list:
            x1 = line[0]
            y1 = line[1]
            x2 = line[2]
            y2 = line[3]
            # generate new point
            num_points = int(math.fabs(y1-y2)/dy)
            # k!==0
            k = (y1-y2)/(x1-x2 + 0.0000001)

            # start point (x1,y1), end point (x2,y2)
            for i_new in range(0, num_points):
                new_object = object.cloneNode('deep')
                new_object.getElementsByTagName("name")[0].childNodes[0].data = '1'
                new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                # new_bndbox = new_object.getElementsByTagName('bndbox')
                # pts[0].getElementsByTagName("x")[0].childNodes[0].data =
                if y1 <= y2:
                    new_x1 = int(x1 + i_new*dy/k)
                    new_y1 = int(y1 + i_new*dy)
                    new_x2 = int(x1 + (i_new+1)*dy/k)
                    new_y2 = int(y1 + (i_new+1)*dy)

                    new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                    new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                    new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                    new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
                else:
                    new_x1 = int(x1 - i_new*dy/k)
                    new_y1 = int(y1 - i_new*dy)
                    new_x2 = int(x1 - (i_new+1)*dy/k)
                    new_y2 = int(y1 - (i_new+1)*dy)

                    new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                    new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                    new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                    new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
                # print new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')[0].getElementsByTagName("x")[0].childNodes[0].data
                Data.appendChild(new_object)
                del new_object

            # the last line: >20
            if abs(y1-y2) - num_points*dy >= 20:
                new_object = object.cloneNode('deep')
                new_object.getElementsByTagName("name")[0].childNodes[0].data = '1'
                new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                # new_bndbox = new_object.getElementsByTagName('bndbox')
                # pts[0].getElementsByTagName("x")[0].childNodes[0].data =
                if y1 <= y2:
                    new_x1 = int(x1 + num_points*dy/k)
                    new_y1 = int(y1 + num_points*dy)
                    new_x2 = x2
                    new_y2 = y2

                    new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                    new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                    new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                    new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
                else:
                    new_x1 = int(x1 - num_points*dy/k)
                    new_y1 = int(y1 - num_points*dy)
                    new_x2 = x2
                    new_y2 = y2

                    new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                    new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                    new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                    new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
                # print new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')[0].getElementsByTagName("x")[0].childNodes[0].data
                Data.appendChild(new_object)
                del new_object

        # deleted long lines
        #if abs(string.atoi(pt_list[0].getElementsByTagName("y")[0].childNodes[0].data) - \
        #               string.atoi(pt_list[len(pt_list - 1)].getElementsByTagName("y")[0].childNodes[0].data)) > 30:
        Data.removeChild(object)

    f = open((des_dir + '/' + xmlName),  'w')
    Data.writexml(f)

#trans_multi_box('com01/com01_0810.xml')



if not os.path.exists(des_dir):
    os.mkdir(des_dir)


test = os.walk(single_line_dataset)
xml_list = [(root,dirs,files) for root,dirs,files in os.walk(single_line_dataset)]

for root, dirs, files in os.walk(single_line_dataset):
    if dirs:
        subfolders = dirs
        for subfolder in dirs:
            if not os.path.exists(des_dir + '/' + subfolder):
                os.mkdir(des_dir + '/' + subfolder)
    else:
        for fileName in files:
            subfolder = fileName.split('_')[0]
            trans_multi_box(subfolder + '/' + fileName)

