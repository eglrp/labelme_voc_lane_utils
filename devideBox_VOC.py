from xml.dom.minidom import parse
import xml.dom.minidom
import string
import math
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import gc
import os

dy = 30

single_line_dataset = "E:\VOC2007_lanedata\VOC2007\Annotations"
des_dir = "E:\VOC2007_lanedata\VOC2007\Annotations_80"

def trans_multi_box(xmlName):
    print xmlName
    DOMTree = xml.dom.minidom.parse(single_line_dataset + '/' + xmlName)
    Data = DOMTree.documentElement
    objects = Data.getElementsByTagName("object")
    for object in objects:
    # xxx=cmp(object.getElementsByTagName("name")[0].childNodes[0].data, u'1')
    # if object.getElementsByTagName("name")[0].childNodes[0].data == '1':
        # get two points
        # object.getElementsByTagName("polygon")[0].getElementsByTagName('username')[0].childNodes[0].data = 'gjy'
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
        y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
        x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
        y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)

        # generate new point
        num_points = int(math.fabs(y1-y2)/dy)
        # k!==0
        k = (y1-y2)/(x1-x2 + 0.00001)
        for i_new in range(0, num_points):
            new_object = object.cloneNode('deep')
            new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
            new_bndbox = new_object.getElementsByTagName('bndbox')
            # pts[0].getElementsByTagName("x")[0].childNodes[0].data =
            if y1 <= y2:
                new_x1 = int(x1 + i_new*dy/k)
                new_y1 = int(y1 + i_new*dy)
                new_x2 = int(x1 + (i_new+1)*dy/k)
                new_y2 = int(y1 + (i_new+1)*dy)

                new_bndbox[0].getElementsByTagName("xmin")[0].childNodes[0].data = min(new_x1, new_x2)
                new_bndbox[0].getElementsByTagName("ymin")[0].childNodes[0].data = min(new_y1, new_y2)
                new_bndbox[0].getElementsByTagName("xmax")[0].childNodes[0].data = max(new_x1, new_x2)
                new_bndbox[0].getElementsByTagName("ymax")[0].childNodes[0].data = max(new_y1, new_y2)

                new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
            else:
                new_x1 = int(x1 - i_new*dy/k)
                new_y1 = int(y1 - i_new*dy)
                new_x2 = int(x1 - (i_new+1)*dy/k)
                new_y2 = int(y1 - (i_new+1)*dy)

                new_bndbox[0].getElementsByTagName("xmin")[0].childNodes[0].data = min(new_x1, new_x2)
                new_bndbox[0].getElementsByTagName("ymin")[0].childNodes[0].data = min(new_y1, new_y2)
                new_bndbox[0].getElementsByTagName("xmax")[0].childNodes[0].data = max(new_x1, new_x2)
                new_bndbox[0].getElementsByTagName("ymax")[0].childNodes[0].data = max(new_y1, new_y2)


                new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = new_x1
                new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = new_y1
                new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = new_x2
                new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = new_y2
            # print new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')[0].getElementsByTagName("x")[0].childNodes[0].data
            Data.appendChild(new_object)
            del new_object
        Data.removeChild(object)
    f = open((des_dir + '/' + xmlName),  'w')
    Data.writexml(f)




if not os.path.exists(des_dir):
    os.mkdir(des_dir)

xml_list = [files for root,dirs,files in os.walk(single_line_dataset)]
xml_all_list = [fileName for fileName in xml_list[0]]
#pool = ThreadPool(4)

#pool.map(trans_multi_box, xml_all_list)

#pool.close
#pool.join
for xmlName in xml_all_list:
    trans_multi_box(xmlName)




# print "name element : %s" % Data.getElementsByTagName("name")
