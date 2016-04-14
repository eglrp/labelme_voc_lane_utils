# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
import xml.dom.minidom
import string
import math
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import gc
import os
import copy

dy = 100
round_r = 10
# deleted_thresh_dy = 50
single_line_dataset = "E:/dataset/extra_diversity_lane/lane_images/All_annotation_labelme_refine"
des_dir = "E:/dataset/extra_diversity_lane/lane_images/All_annotation_labelme_refine_mergeby_" + str(dy)


def merge_list(src_list):
    if len(src_list) == 0:
        return src_list
    else:
        inter_set = False # there is not intersection

        for i in range(0, len(src_list)):
            for j in range(i+1,len(src_list)):
                xxx = len(set(src_list[i]) & set(src_list[j]))
                if len(set(src_list[i]) & set(src_list[j])) >= 1:
                    inter_set = True
                    break



        if not inter_set:
            #dst_list = copy.deepcopy(src_list)

            return src_list
        else:
            #merge_lines_set = list()

            for i in range(0, len(src_list)):
                for j in range(i+1,len(src_list)):
                    if len(set(src_list[i]) & set(src_list[j])) >= 1:
                        src_list.append(list(set(src_list[i]) | set(src_list[j])))
                        src_list.remove(src_list[i+1])
                        src_list.remove(src_list[i])
                        merge_list(src_list)
                        print "src_list"
                        print src_list
                        break
                        break


    # print src_list
    #return src_list


def mergeLines(xmlName):
    print xmlName
    #folder = xmlName.split("_")[0]
    # if not os.path.exists(des_dir+'/'+ folder):
    #     os.mkdir(des_dir+'/'+ folder)
    DOMTree = xml.dom.minidom.parse(single_line_dataset + '/' + xmlName)
    Data = DOMTree.documentElement
    objects = Data.getElementsByTagName("object")

    center_points = list()
    # center point
    for object in objects:
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
        y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
        x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
        y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)

        xc = (int)((x1 + x2)/2)
        yc = (int)((y1 + y2)/2)
        center_points.append((xc, yc))

    # to do two lines set e.g.[(1,2),(2,3)]
    merge_edges = list()
    x1_list = list()
    y1_list = list()
    x2_list = list()
    y2_list = list()
    index_object = 0

    for object in objects:
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
        y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
        x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
        y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)

        x1_list.append(x1)
        y1_list.append(y1)
        x2_list.append(x2)
        y2_list.append(y2)

        k = (y1-y2)/(x1-x2 + 0.00001)
        b = -k*x1 + y1

        #
        index_point = index_object + 1

        for i in range(index_point, len(center_points), 1):
            cpoint = center_points[i]
            if abs(k*cpoint[0] - cpoint[1] + b)/math.sqrt(1 + k*k) < round_r:
                # if the both lines' dy are more than dy, the edge of mergeline is not appended
                pts1 = objects[index_object].getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                pts2 = objects[i].getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                dy_1 = abs(string.atoi(pts1[0].getElementsByTagName("y")[0].childNodes[0].data) \
                                       - \
                           string.atoi(pts1[1].getElementsByTagName("y")[0].childNodes[0].data) \
                           )
                dy_2 = abs(string.atoi(pts2[0].getElementsByTagName("y")[0].childNodes[0].data) \
                                       - \
                           string.atoi(pts2[1].getElementsByTagName("y")[0].childNodes[0].data)
                           )
                if dy_1 <= dy and dy_2 <= dy:
                    merge_edges.append([index_object, i])
        index_object += 1

    # e.g. [(1,2),(2,3)]-->[(1,2,3)]
    print "merge_edges"
    print merge_edges
    # merge_edges = [[1,2],[2,3],[4,5],[5,6]]
    dst_list = list()
    tmp_list = list()
    merge_list(merge_edges)
   # print "mergeddd_edges"
    #print merge_edges


    # merge_lines_set:[(1,2,3),(4,5)]
    deleted_list = list()
    for lines_set in merge_edges:
        # get k
        new_object = objects[0].cloneNode('deep')
        new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        # voc has bndbox; but labelme hasn't it

        #new_bndbox = new_object.getElementsByTagName('bndbox')

        #set-->list
        lines_list = [line for line in lines_set]
        #left or right
        pts_k = get_points(objects[lines_set[0]])
        k = (pts_k[3]-pts_k[1])/(pts_k[2]-pts_k[0] + 0.000001)

        #selected values of specific items
        x1_selected = [x1_list[i] for i in lines_list]
        y1_selected = [y1_list[i] for i in lines_list]
        x2_selected = [x2_list[i] for i in lines_list]
        y2_selected = [y2_list[i] for i in lines_list]

        x1_selected.extend(x2_selected)
        y1_selected.extend(y2_selected)

        xmin = min(x1_selected)
        xmax = max(x1_selected)
        ymin = min(y1_selected)
        ymax = max(y1_selected)

        # voc has bndbox; but labelme hasn't it
        # new_bndbox[0].getElementsByTagName("xmin")[0].childNodes[0].data = xmin
        # new_bndbox[0].getElementsByTagName("ymin")[0].childNodes[0].data = ymin
        # new_bndbox[0].getElementsByTagName("xmax")[0].childNodes[0].data = xmax
        # new_bndbox[0].getElementsByTagName("ymax")[0].childNodes[0].data = ymax

        if k>=0:
            new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = xmax
            new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = ymax
            new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = xmin
            new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = ymin
        else:
            new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = xmin
            new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = ymax
            new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = xmax
            new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = ymin
        Data.appendChild(new_object)
        del new_object

        for i in lines_list:
            deleted_list.append(i)

    deleted_list.sort(None,None,True)
    print "deleted"
    print deleted_list
    for i in deleted_list:
        Data.removeChild(objects[i])

    f = open((des_dir + '/' + xmlName),  'w')
    Data.writexml(f)




def get_points(object):
    pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
    x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
    y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
    x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
    y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)
    return x1, y1, x2, y2









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
            mergeLines(subfolder + '/' + fileName)
# mergeLines("ChangeLane/Changelane_0330.xml")