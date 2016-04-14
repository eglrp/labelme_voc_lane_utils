# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
import xml.dom.minidom
import string
import math

class xmlUtils(object):

    # rename the object name
    def rename_object(self, xml_objects, src_name, dst_name):

        for object in xml_objects:
            # skip line of no name
            if len(object.getElementsByTagName("name")) == 0:
                continue
            if len(object.getElementsByTagName("name")[0].childNodes) == 0:
                continue
            # skip deleted lines
            if object.getElementsByTagName("deleted")[0].childNodes[0].data == '1':
                continue

            if object.getElementsByTagName("name")[0].childNodes[0].data == src_name:
                object.getElementsByTagName("name")[0].childNodes[0].data = dst_name

    # delete some deteled objects, some imcomplete annotations(e.g. one point):
    def refine_dataset(self, Data, xml_objects):
        for object in xml_objects:
            pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
            # delete deleted lines
            if object.getElementsByTagName("deleted")[0].childNodes[0].data == '1':
                Data.removeChild(object)
            # delete line of no name
            elif len(object.getElementsByTagName("name")) == 0:
                Data.removeChild(object)
            elif len(object.getElementsByTagName("name")[0].childNodes) == 0:
                Data.removeChild(object)
            # incorrect anotation:single point
            elif len(pts) <= 1: # incorrect anotation
                Data.removeChild(object)
            # have refined...

            # if only one object, the below code will set all exsisted objects as label "1"
            # else:
            #    object.getElementsByTagName("name")[0].childNodes[0].data = '1'



    # segment long lane
    def devided_lanes(self, Data, xml_objects, dataset, devide_dy, last_lane_thresh_dy):

        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')

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
            num_points = int(math.fabs(y1-y2)/devide_dy)
            # k!==0
            k = (y1-y2)/(x1-x2 + 0.0000001)

            # start point (x1,y1), end point (x2,y2)
            for i_new in range(0, num_points):
                new_object = object.cloneNode('deep')
                new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')

                # new_bndbox = new_object.getElementsByTagName('bndbox')
                # pts[0].getElementsByTagName("x")[0].childNodes[0].data =
                if y1 <= y2:
                    new_x1 = int(x1 + i_new*devide_dy/k)
                    new_y1 = int(y1 + i_new*devide_dy)
                    new_x2 = int(x1 + (i_new+1)*devide_dy/k)
                    new_y2 = int(y1 + (i_new+1)*devide_dy)

                    self.set_pts(new_pts, new_x1, new_y1, new_x2, new_y2)
                    if dataset == 'voc':
                        self.set_bndbox(new_bndbox,new_x1, new_y1, new_x2, new_y2)
                else:
                    new_x1 = int(x1 - i_new*devide_dy/k)
                    new_y1 = int(y1 - i_new*devide_dy)
                    new_x2 = int(x1 - (i_new+1)*devide_dy/k)
                    new_y2 = int(y1 - (i_new+1)*devide_dy)

                    self.set_pts(new_pts, new_x1, new_y1, new_x2, new_y2)
                    if dataset == 'voc':
                        self.set_bndbox(new_bndbox,new_x1, new_y1, new_x2, new_y2)
                # print new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')[0].getElementsByTagName("x")[0].childNodes[0].data
                Data.appendChild(new_object)
                del new_object

            # the last seg line: >20   (last_lane_thresh_dy)
            if abs(y1-y2) - num_points*devide_dy >= last_lane_thresh_dy:
                new_object = object.cloneNode('deep')
                new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')

                new_bndbox = None
                if dataset == 'voc':
                    new_bndbox = new_object.getElementsByTagName('bndbox')


                if y1 <= y2:
                    new_x1 = int(x1 + num_points*devide_dy/k)
                    new_y1 = int(y1 + num_points*devide_dy)
                    new_x2 = x2
                    new_y2 = y2

                    self.set_pts(new_pts, new_x1, new_y1, new_x2, new_y2)

                    if dataset == 'voc':
                        self.set_bndbox(new_bndbox,new_x1, new_y1, new_x2, new_y2)
                else:
                    new_x1 = int(x1 - num_points*devide_dy/k)
                    new_y1 = int(y1 - num_points*devide_dy)
                    new_x2 = x2
                    new_y2 = y2

                    self.set_pts(new_pts, new_x1, new_y1, new_x2, new_y2)

                    if dataset == 'voc':
                        self.set_bndbox(new_bndbox,new_x1, new_y1, new_x2, new_y2)
                # print new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')[0].getElementsByTagName("x")[0].childNodes[0].data
                Data.appendChild(new_object)
                del new_object

        # deleted long lines
        #if abs(string.atoi(pt_list[0].getElementsByTagName("y")[0].childNodes[0].data) - \
        #               string.atoi(pt_list[len(pt_list - 1)].getElementsByTagName("y")[0].childNodes[0].data)) > 30:
        Data.removeChild(object)


    def mergeLine(self, Data, xml_objects, dataset, merge_dy, round_r):
        center_points = list()
        # center point
        for object in xml_objects:

            [x1, y1, x2, y2] = self.get_points(object)
            # pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
            # x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
            # y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
            # x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
            # y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)

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

        for object in xml_objects:
            [x1, y1, x2, y2] = self.get_points(object)
            #pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
            #x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
            #y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
            #x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
            #y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)

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
                    pts1 = xml_objects[index_object].getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                    pts2 = xml_objects[i].getElementsByTagName("polygon")[0].getElementsByTagName('pt')
                    dy_1 = abs(string.atoi(pts1[0].getElementsByTagName("y")[0].childNodes[0].data) - \
                               string.atoi(pts1[1].getElementsByTagName("y")[0].childNodes[0].data))
                    dy_2 = abs(string.atoi(pts2[0].getElementsByTagName("y")[0].childNodes[0].data) - \
                               string.atoi(pts2[1].getElementsByTagName("y")[0].childNodes[0].data))
                    if dy_1 <= merge_dy and dy_2 <= merge_dy:
                        merge_edges.append([index_object, i])
            index_object += 1

        # e.g. [(1,2),(2,3)]-->[(1,2,3)]
        print "merge_edges"
        print merge_edges
        # merge_edges = [[1,2],[2,3],[4,5],[5,6]]
        dst_list = list()
        tmp_list = list()
        self.merge_list(merge_edges)
       # print "mergeddd_edges"
        #print merge_edges


        # merge_lines_set:[(1,2,3),(4,5)]
        deleted_list = list()
        for lines_set in merge_edges:
            # get k
            new_object = xml_objects[0].cloneNode('deep')
            new_pts = new_object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
            # voc has bndbox; but labelme hasn't it

            #new_bndbox = new_object.getElementsByTagName('bndbox')

            #set-->list
            lines_list = [line for line in lines_set]
            #left or right
            pts_k = self.get_points(xml_objects[lines_set[0]])
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
            new_bndbox = None
            if dataset == 'voc':
                new_bndbox = new_object.getElementsByTagName('bndbox')
                self.set_bndbox(new_bndbox,xmin, ymin, xmax, ymax)
            # new_bndbox[0].getElementsByTagName("xmin")[0].childNodes[0].data = xmin
            # new_bndbox[0].getElementsByTagName("ymin")[0].childNodes[0].data = ymin
            # new_bndbox[0].getElementsByTagName("xmax")[0].childNodes[0].data = xmax
            # new_bndbox[0].getElementsByTagName("ymax")[0].childNodes[0].data = ymax

            if k>=0:
                self.set_pts(new_pts, xmax, ymax, xmin, ymin)
                # new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = xmax
                # new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = ymax
                # new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = xmin
                # new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = ymin
            else:
                self.set_pts(new_pts, xmin, ymax, xmax, ymin)
                # new_pts[0].getElementsByTagName("x")[0].childNodes[0].data = xmin
                # new_pts[0].getElementsByTagName("y")[0].childNodes[0].data = ymax
                # new_pts[1].getElementsByTagName("x")[0].childNodes[0].data = xmax
                # new_pts[1].getElementsByTagName("y")[0].childNodes[0].data = ymin
            Data.appendChild(new_object)
            del new_object

            for i in lines_list:
                deleted_list.append(i)

        deleted_list.sort(None,None,True)
        print "deleted"
        print deleted_list
        for i in deleted_list:
            Data.removeChild(xml_objects[i])






    #----------- some samall tools
    def set_pts(self, pts, x1, y1, x2, y2):
        pts[0].getElementsByTagName("x")[0].childNodes[0].data = x1
        pts[0].getElementsByTagName("y")[0].childNodes[0].data = y1
        pts[1].getElementsByTagName("x")[0].childNodes[0].data = x2
        pts[1].getElementsByTagName("y")[0].childNodes[0].data = y2

    def set_bndbox(self, bndbox, x1, y1, x2, y2):
        bndbox[0].getElementsByTagName("xmin")[0].childNodes[0].data = min(x1, x2)
        bndbox[0].getElementsByTagName("ymin")[0].childNodes[0].data = min(y1, y2)
        bndbox[0].getElementsByTagName("xmax")[0].childNodes[0].data = max(x1, x2)
        bndbox[0].getElementsByTagName("ymax")[0].childNodes[0].data = max(y1, y2)

    def get_points(self, object):
        pts = object.getElementsByTagName("polygon")[0].getElementsByTagName('pt')
        x1 = string.atoi(pts[0].getElementsByTagName("x")[0].childNodes[0].data)
        y1 = string.atoi(pts[0].getElementsByTagName("y")[0].childNodes[0].data)
        x2 = string.atoi(pts[1].getElementsByTagName("x")[0].childNodes[0].data)
        y2 = string.atoi(pts[1].getElementsByTagName("y")[0].childNodes[0].data)
        return x1, y1, x2, y2

    def merge_list(self, src_list):
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