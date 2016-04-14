from xml.dom.minidom import parse
import xml.dom.minidom
import string
import math
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import gc
import os


single_line_dataset = "E:/dataset/extra_diversity_lane/lane_images/All_annotation_labelme"
des_dir = "E:/dataset/extra_diversity_lane/lane_images/All_annotation_labelme_refine"


def refine(xmlName):
    print xmlName
    DOMTree = xml.dom.minidom.parse(single_line_dataset + '/' + xmlName)
    Data = DOMTree.documentElement
    objects = Data.getElementsByTagName("object")
    for object in objects:
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        # skip deleted lines
        if object.getElementsByTagName("deleted")[0].childNodes[0].data == '1':
            Data.removeChild(object)
        # skip line of no name
        elif len(object.getElementsByTagName("name")) == 0:
            Data.removeChild(object)
        elif len(object.getElementsByTagName("name")[0].childNodes) == 0:
            Data.removeChild(object)
        # incorrect anotation:single point
        elif len(pts) <= 1: # incorrect anotation
            Data.removeChild(object)
        else:
            object.getElementsByTagName("name")[0].childNodes[0].data = '1'




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
            refine(subfolder + '/' + fileName)

