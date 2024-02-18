
from fractions import Fraction
import numpy as np
import math

class Point:
    def __init__(self, x, y):
        
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        
        return hash((self.x,self.y))
   
class Line(object):
    
    def __init__(self,startPoint,endPoint,slope,idx):
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.slope = slope
        self.idx = idx
    
    def __eq__(self, other):
        
        if isinstance(other, Line):
            return (self.startPoint == other.startPoint and
                    self.endPoint == other.endPoint and
                    self.slope == other.slope and
                    self.idx == other.idx)
        return False
    
    def line_in_list(self,lList):
        
        for line in lList:
            if self.idx == line:
                return True
            return False
        
    def __hash__(self):
        
        return hash((self.startPoint, self.endPoint, self.slope,self.idx))
    
    def is_startPoint(self, point):
        
        return point.x == self.startPoint.x and point.y == self.startPoint.y

    def is_endPoint(self, point):
        
        return point.x == self.endPoint.x and point.y == self.endPoint.y
    
def angle_finder(line1,line2):
    
    A = np.array([float(line1.startPoint.x), float(line1.startPoint.y)])
    B = np.array([float(line1.endPoint.x), float(line1.endPoint.y)])
    C = np.array([float(line2.startPoint.x), float(line2.startPoint.y)])
    D = np.array([float(line2.endPoint.x), float(line2.endPoint.y)])

    AB = B - A
    CD = D - C

    dot_product = np.dot(AB, CD)
    cross_product = np.cross(AB, CD)

    theta = np.arctan2(cross_product, dot_product)

    theta_degrees = np.degrees(theta)

    if theta_degrees < 0:
        theta_degrees += 360.0

    return theta_degrees

def vector_angle(line):

    vector_x = float(line[0])
    vector_y = float(line[1])

    angle_rad = math.atan2(vector_y, vector_x)
    if angle_rad < 0:
        angle_rad += 2 * math.pi

    angle_deg = math.degrees(angle_rad)
    return angle_deg

def left_or_right(segment,point):
    
    A = (segment.startPoint.x - segment.endPoint.x) * (segment.startPoint.y - point.y)
    B = (segment.startPoint.y - segment.endPoint.y) * (segment.startPoint.x - point.x)
    cross_product = (A) - (B)
    if cross_product > 0:
        return "left"
    elif cross_product < 0:
        return "right"
    else:
        return "parallel"
    
def find_intersection(line1,line2):
    
    x1 = Fraction(line1.startPoint.x)
    y1 = Fraction(line1.startPoint.y)
    x2 = Fraction(line1.endPoint.x)
    y2 = Fraction(line1.endPoint.y)
    x3 = Fraction(line2.startPoint.x)
    y3 = Fraction(line2.startPoint.y)
    x4 = Fraction(line2.endPoint.x)
    y4 = Fraction(line2.endPoint.y)
    if((x1 == x3 and y1 == y3) or (x1 == x4 and y1 == y4)):
        return Point(x1,y1)
    elif((x2 == x3 and y2 == y3) or (x2 == x4 and y2 == y4)):
        return Point(x2,y2)
    else:
        # Calculate the cross product
        cross_product = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)

        # Check if the line segments are collinear or parallel
        if cross_product == 0:
            return None

        # Calculate the parameters t1 and t2
        t1 = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / cross_product
        t2 = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / cross_product
        # #print(t1,t2)
        # Check if the intersection point lies within both line segments
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            intersection_x = x1 + t1 * (x2 - x1)
            intersection_y = y1 + t1 * (y2 - y1)
            return Point(intersection_x,intersection_y)

    return None

def find_intersectionSup(line1,line2):
    
    x1 = Fraction(line1.startPoint.x)
    y1 = Fraction(line1.startPoint.y)
    x2 = Fraction(line1.endPoint.x)
    y2 = Fraction(line1.endPoint.y)
    x3 = Fraction(line2.startPoint.x)
    y3 = Fraction(line2.startPoint.y)
    x4 = Fraction(line2.endPoint.x)
    y4 = Fraction(line2.endPoint.y)
    
    if(((x1 == x3 and y1 == y3) and (x2 == x4 and y2 == y4)) or((x1 == x4 and y1 == y4) and (x2 == x3 and y2 == y3))):
        return True
    
def tVectorFinder(p,edgesA,edgesB,cond1=True,cond2=False,l=None):
   
    if (cond2 == False):
        edgeA= next(filter(lambda e: e.is_startPoint(p)  , edgesA))
        edgeB= next(filter(lambda e: e.is_startPoint(p)  , edgesB))
        if(left_or_right(edgeA,edgeB.endPoint) == "left"):
            return (edgeB.startPoint.x - edgeB.endPoint.x, edgeB.startPoint.y - edgeB.endPoint.y),edgeA.startPoint
        elif ((left_or_right(edgeA,edgeB.endPoint) == "right")):
            return (edgeA.endPoint.x - edgeA.startPoint.x, edgeA.endPoint.y - edgeA.startPoint.y),edgeA.endPoint
        else:
            return (edgeA.endPoint.x - edgeA.startPoint.x, edgeA.endPoint.y - edgeA.startPoint.y),edgeA.startPoint
    else:   
        if (cond1):
            return(l.endPoint.x - p.x, l.endPoint.y - p.y),l.endPoint 
        else: 
            return(p.x - l.endPoint.x , p.y - l.endPoint.y),p


def feasibleTV(edgesA,edgesB,vector,pointList):
    
    for point in pointList:
        p = [point[4].x,point[4].y]
        translateV = Line(point[4],Point(point[4].x + vector[0],point[4].y + vector[1]),(((point[4].y + vector[1]) - point[4].y)/((point[4].x + vector[0]) - point[4].x)) if (point[4].x + vector[0] - point[4].x) != 0 else None,1)
        if (not point[3]):
            if(not point[2]):
                startEA = edgesA[point[5]]
                endEA = edgesA[point[5] - 1]
                startEB = point[1]
                endEB = edgesB[point[1].idx - 1]
                angleEA = angle_finder(endEA,startEA)
                angleEB = angle_finder(endEB,startEB)
                bStartsize = (startEB.endPoint.x - startEB.startPoint.x, startEB.endPoint.y - startEB.startPoint.y)
                bEndsize = (endEB.endPoint.x - endEB.startPoint.x, endEB.endPoint.y - endEB.startPoint.y)
                mirrorSEB = Line(startEB.startPoint,Point(startEB.startPoint.x - bStartsize[0],startEB.startPoint.y - bStartsize[1]),startEB.slope,1)
                mirrorEEB = Line(Point(endEB.endPoint.x + bEndsize[0],endEB.endPoint.y + bEndsize[1]),endEB.endPoint,endEB.slope,1)
                bound1 = None
                bound2 = None
                if (left_or_right(startEA,mirrorSEB.endPoint) == "left"):
                    bound1 = startEA
                else: 
                    bound1 = mirrorSEB
                if (left_or_right(endEA,mirrorEEB.startPoint) == "left"):
                    bound2 = endEA
                else:
                    bound2 = mirrorEEB
                if (angleEA < 180 and angleEB < 180):
                    if ((left_or_right(bound1,translateV.endPoint) == "left") and (left_or_right(bound2,translateV.endPoint) == "left")):
                        return False
                    else:
                        pass
                elif (angleEA > 180 and angleEB < 180):
                    if (((left_or_right(bound1,translateV.endPoint) == "right") or (left_or_right(bound1,translateV.endPoint) == "parallel")) and ((left_or_right(bound2,translateV.endPoint) == "right") or (left_or_right(bound2,translateV.endPoint) == "parallel"))):
                        pass
                    else:
                        return False
                elif (angleEB > 180 and angleEA < 180):
                    if (((left_or_right(bound1,translateV.endPoint) == "right") or (left_or_right(bound1,translateV.endPoint) == "parallel")) and ((left_or_right(bound2,translateV.endPoint) == "right") or (left_or_right(bound2,translateV.endPoint) == "parallel"))):
                        pass
                    else:
                        return False
            else:
                startEB= edgesB[point[5]]
                endEB = edgesB[point[5] - 1]
                startEA = point[1]
                endEA = edgesA[point[1].idx - 1]
                angleEA = angle_finder(endEA,startEA)
                angleEB = angle_finder(endEB,startEB)
                bStartsize = (startEB.endPoint.x - startEB.startPoint.x, startEB.endPoint.y - startEB.startPoint.y)
                bEndsize = (endEB.endPoint.x - endEB.startPoint.x, endEB.endPoint.y - endEB.startPoint.y)
                mirrorSEB = Line(startEB.startPoint,Point(startEB.startPoint.x - bStartsize[0],startEB.startPoint.y - bStartsize[1]),startEB.slope,1)
                mirrorEEB = Line(Point(endEB.endPoint.x + bEndsize[0],endEB.endPoint.y + bEndsize[1]),endEB.endPoint,endEB.slope,1)
                bound1 = None
                bound2 = None
                if (left_or_right(startEA,mirrorSEB.endPoint) == "left"):
                    bound1 = startEA
                else: 
                    bound1 = mirrorSEB
                if (left_or_right(endEA,mirrorEEB.startPoint) == "left"):
                    bound2 = endEA
                else:
                    bound2 = mirrorEEB
                if (angleEA < 180 and angleEB < 180):
                    if ((left_or_right(bound1,translateV.endPoint) == "left") and (left_or_right(bound2,translateV.endPoint) == "left")):
                        return False
                    else:
                        pass
                elif (angleEA > 180 and angleEB < 180):
                    if (((left_or_right(bound1,translateV.endPoint) == "right") or (left_or_right(bound1,translateV.endPoint) == "parallel")) and ((left_or_right(bound2,translateV.endPoint) == "right") or (left_or_right(bound2,translateV.endPoint) == "parallel"))):
                        pass
                    else:
                        return False
                elif (angleEB > 180 and angleEA < 180):
                    if (((left_or_right(bound1,translateV.endPoint) == "right") or (left_or_right(bound1,translateV.endPoint) == "parallel")) and ((left_or_right(bound2,translateV.endPoint) == "right") or (left_or_right(bound2,translateV.endPoint) == "parallel"))):
                        pass
                    else:
                        return False
        else:
            if (not point[2]):
                Tvec = tVectorFinder(point[4],edgesA,edgesB,False,True,point[1])[0]
                pTvec = Line(point[4],Point(point[4].x + Tvec[0],point[4].y + Tvec[1]),(((point[4].y + Tvec[1]) - point[4].y)/((point[4].x + Tvec[0]) - point[4].x)) if ((point[4].x + Tvec[0]) - point[4].x) != 0 else None,1)

                if ((left_or_right(pTvec,translateV.endPoint) == "right") or (left_or_right(pTvec,translateV.endPoint) == "parallel")):
                    pass
                else:
                    return False
            else:
                Tvec = tVectorFinder(point[4],edgesA,edgesB,True,True,point[1])[0]
                pTvec = Line(point[4],Point(point[4].x + Tvec[0],point[4].y + Tvec[1]),(((point[4].y + Tvec[1]) - point[4].y)/((point[4].x + Tvec[0]) - point[4].x)) if ((point[4].x + Tvec[0]) - point[4].x) != 0 else None,1)
                if ((left_or_right(pTvec,translateV.endPoint) == "right") or (left_or_right(pTvec,translateV.endPoint) == "parallel")):
                    pass
                else:
                    return False

def fractionalize(polygon):
    
    finalPolygon = []
    finalPolygon.append([[Fraction(x),Fraction(y)] for x,y in polygon[0]])
    for p in polygon[1:]:
        finalPolygon.append([[Fraction(x),Fraction(y)] for x,y in p])
    return finalPolygon

def lowest_key(polygon):
    
    lowest_key = min((point[1], point[0]) for point in polygon)
    return (lowest_key[1],lowest_key[0])


def highest_key(polygon):
   
    highest_key = max((point[1], point[0]) for point in polygon)
    return (highest_key[1],highest_key[0])


def slope(a,b):
    
    if (b[0] == a[0]):
        return None
    else:
        return (b[1] - a[1]) / (b[0] - a[0])
    

def rotate_point(point,angle):
    
    x = point.x
    y = point.y
    alpha = math.radians(angle)  
    x_rotated = x * math.cos(alpha) + y * math.sin(alpha)
    y_rotated = -x * math.sin(alpha) + y * math.cos(alpha)
    return (y_rotated)

def bounding(edge, tVector):
    
    if ((edge.slope == None or edge.slope == 0) or (tVector.slope == 0 or tVector.slope == None)):
        return True
    elif((min(edge.startPoint.x,edge.endPoint.x) <= max(tVector.startPoint.x,tVector.endPoint.x) and max(edge.startPoint.x,edge.endPoint.x) >= min(tVector.startPoint.x,tVector.endPoint.x) and
        min(edge.startPoint.y,edge.endPoint.y) <= max(tVector.startPoint.y,tVector.endPoint.y) and max(edge.startPoint.y,edge.endPoint.y) >= min(tVector.startPoint.y,tVector.endPoint.y))):
        return True
    else:
        return False

def distance(vector,point):
    
    temp1 = point.x - vector.endPoint.x
    temp2 = point.y - vector.endPoint.y
    result = math.sqrt(temp1**2 + temp2**2)
    return result

ntv=None
def trimmer(Points,filteredEdges,translateVector):
    
    global ntv
    ntv = translateVector
    for point in Points:
        tVec=((Line(Point(point[0],point[1]),Point(point[0] + ntv[0],point[1] + ntv[1]),slope(point,(point[0] + ntv[0],point[1] + ntv[1])),1)))
        try:    
            for edge in filteredEdges:
                if bounding(tVec,edge):
                    intersect = find_intersection(tVec,edge)
                    if (intersect is not None):
                        if (not(edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) or ((edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) and (not(tVec.is_startPoint(intersect)) and not(tVec.is_endPoint(intersect))))):
                            if(not(tVec.is_startPoint(intersect) and  left_or_right(edge,tVec.endPoint)=="right") and (intersect.x != (tVec.startPoint.x + translateVector[0]) or intersect.y != (tVec.startPoint.y + translateVector[1]))):
                                ntv= ((intersect.x - tVec.startPoint.x), (intersect.y - tVec.startPoint.y))
                                trimmer(Points,filteredEdges,ntv)
                                raise StopIteration
        except StopIteration:
            break
    return ntv


nTV=None
def trimmer2(Points,filteredEdges,translateVector,edges):
    
    global nTV
    nTV = translateVector
    for point in Points:
        tVec=((Line(Point(point[0],point[1]),Point(point[0] + nTV[0],point[1] + nTV[1]),slope(point,(point[0] + nTV[0],point[1] + nTV[1])),1)))
        try:    
            for edge in filteredEdges:
                if bounding(tVec,edge):
                    intersect = find_intersection(tVec,edge)
                    if (intersect is not None):
                        if (not(edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) or ((edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) and (not(tVec.is_startPoint(intersect)) and not(tVec.is_endPoint(intersect))))):
                            if(not(tVec.is_startPoint(intersect) and  left_or_right(edge,tVec.endPoint)=="right") and (intersect.x != (tVec.startPoint.x + translateVector[0]) or intersect.y != (tVec.startPoint.y + translateVector[1]))):
                                nTV= ((intersect.x - tVec.startPoint.x), (intersect.y - tVec.startPoint.y))
                                trimmer2(Points,filteredEdges,nTV,edges)
                                raise StopIteration
                        elif(edge.is_startPoint(intersect) and (tVec.is_startPoint(intersect) and  left_or_right(edge,tVec.endPoint)=="left" and left_or_right(edges[edge.idx -1],tVec.endPoint) == "left" )):
                            nTV = (0,0)
                            raise StopIteration
        except StopIteration:
            break
    return nTV

def holeTrimmer(Points,filteredEdges,translateVector,edges):
    global nTV
    nTV = translateVector
    for point in Points:
        tVec=((Line(Point(point[0],point[1]),Point(point[0] + nTV[0],point[1] + nTV[1]),slope(point,(point[0] + nTV[0],point[1] + nTV[1])),1)))
        try:    
            for edge in filteredEdges:
                if bounding(tVec,edge):
                    intersect = find_intersection(tVec,edge)
                    if (intersect is not None):
                        if (not(edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) or ((edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) and (not(tVec.is_startPoint(intersect)) and not(tVec.is_endPoint(intersect))))):
                            if(not(tVec.is_startPoint(intersect) and  left_or_right(edge,tVec.endPoint)=="right") and (intersect.x != (tVec.startPoint.x + translateVector[0]) or intersect.y != (tVec.startPoint.y + translateVector[1]))):
                                nTV= ((intersect.x - tVec.startPoint.x), (intersect.y - tVec.startPoint.y))
                                holeTrimmer(Points,filteredEdges,nTV,edges)
                                raise StopIteration
                        elif(edge.is_startPoint(intersect) and (tVec.is_startPoint(intersect) and  (left_or_right(edge,tVec.endPoint)=="left" and left_or_right(edges[edge.idx -1],tVec.endPoint) == "left"))):
                            nTV = (0,0)
                            raise StopIteration
                        elif(edge.is_startPoint(intersect)):
                            if((left_or_right(edges[edge.idx - 1],edge.endPoint) == "right" and left_or_right(edge,edges[edge.idx - 1].startPoint) == "right")):
                                if(edge.is_startPoint(intersect) and (tVec.is_startPoint(intersect) and  (left_or_right(edge,tVec.endPoint)=="parallel" and left_or_right(edges[edge.idx -1],tVec.endPoint) == "left"))):
                                    
                                    nTV = (0,0)
                                    raise StopIteration
                                elif(edge.is_startPoint(intersect) and (tVec.is_startPoint(intersect) and  (left_or_right(edge,tVec.endPoint)=="left" and left_or_right(edges[edge.idx -1],tVec.endPoint) == "parallel"))):
                                    nTV = (0,0)
                                    raise StopIteration
                                
        except StopIteration:
            break
    return nTV

nTv=None

def trimmerSup(Points,filteredEdges,translateVector):
    global nTv
    nTv = translateVector
    for point in Points:
        tVec=((Line(Point(point[0],point[1]),Point(point[0] + nTv[0],point[1] + nTv[1]),slope(point,(point[0] + nTv[0],point[1] + nTv[1])),1)))
        try:
            for edge in filteredEdges:
                
                if bounding(tVec,edge):
                    intersect = find_intersection(tVec,edge)
                    if (intersect is not None):
                        if (not(edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) or ((edge.is_startPoint(intersect) or edge.is_endPoint(intersect)) and (not(tVec.is_startPoint(intersect)) and not(tVec.is_endPoint(intersect))))):
                            if(not(tVec.is_startPoint(intersect) ) and (intersect.x != (tVec.startPoint.x + translateVector[0]) or intersect.y != (tVec.startPoint.y + translateVector[1]))):
                                diff = ((tVec.endPoint.x - intersect.x),(tVec.endPoint.y - intersect.y)) 
                                nTv= ((nTv[0] - diff[0]), (nTv[1] - diff[1]))
                                trimmerSup(Points,filteredEdges,nTv)
                                raise StopIteration
        except StopIteration:
            break
    return nTv

def boundry(polygon,edges,vector):
    
    angle = vector_angle(vector)
    rotated_points =[]
    for point in polygon:
        rotated_points.append(rotate_point(Point(point[0],point[1]),angle))
    minVal = polygon[rotated_points.index(min(rotated_points))]
    maxVal = polygon[rotated_points.index(max(rotated_points))]
    seg1 = Line(Point(minVal[0],minVal[1]),Point(minVal[0] + vector[0],minVal[1] + vector[1]),0,1)
    seg2 = Line(Point(maxVal[0],maxVal[1]),Point(maxVal[0] + vector[0],maxVal[1] + vector[1]),0,1)
    filtered_edges = []
    for edge in edges:
        if(not 
           ((((left_or_right(seg1,edge.startPoint) == "left") and (left_or_right(seg1,edge.endPoint) == "left")) and ((left_or_right(seg2,edge.startPoint) == "left") and (left_or_right(seg2,edge.endPoint) == "left"))) 
           or
           (((left_or_right(seg1,edge.startPoint) == "right") and (left_or_right(seg1,edge.endPoint) == "right")) and ((left_or_right(seg2,edge.startPoint) == "right") and (left_or_right(seg2,edge.endPoint) == "right")))
           )):
            filtered_edges.append(edge)
    return filtered_edges

def is_point_on_segment(point,line):
    
    min_y=min(line.startPoint.y,line.endPoint.y)
    max_y=max(line.startPoint.y,line.endPoint.y)
    min_x=min(line.startPoint.x,line.endPoint.x)
    max_x=max(line.startPoint.x,line.endPoint.x)
    if left_or_right(line,point) == "parallel":
        if ((point.x >= min_x)and(point.x <= max_x) and (point.y >= min_y) and (point.y <= max_y)):
            return point
        else:
            return None

def trimFun(polygonM,filteredES,translateV,p):
    
    tVectors = []
    infos= []
    intersection = None
    for point in polygonM:
        tVectors.append((Line(Point(point[0],point[1]),Point(point[0] + translateV[0],point[1] + translateV[1]),slope(point,(point[0] + translateV[0],point[1] + translateV[1])),1)))
    for i,point1 in enumerate(polygonM):
        tVector=Point(point1[0],point1[1])
        for edge in filteredES:
            intersection = is_point_on_segment(tVector,edge)
            if intersection is not None:
                if (edge.is_startPoint(intersection)):
                    infos.append([Point(polygonM[i][0], polygonM[i][1]),edge,p,False,intersection,i,edge.idx])
                elif (edge.is_endPoint(intersection)):
                    pass
                else:
                    infos.append([Point(polygonM[i][0], polygonM[i][1]),edge,p,True,intersection,i,edge.idx])
    return (infos)

def edgeRemover(info,remainedEdgesA,remainedEdgesB,edgesA,edgesB):
    
    if(info[3]): 
        if (info[2]):
            remainedEdgesA.add(info[-1]) 
            edgeSB = next(filter(lambda e: e.is_startPoint(info[4])  , edgesB))
            edgeEB = next(filter(lambda e: e.is_endPoint(info[4])  , edgesB))
            remainedEdgesB.add(edgeSB.idx)
            remainedEdgesB.add(edgeEB.idx)
        else:
            remainedEdgesB.add(info[-1])
    else:
        edgeSA =next(filter(lambda e: e.is_startPoint(info[0])  , edgesA))
        edgeEA =next(filter(lambda e: e.is_endPoint(info[0])  , edgesA))
        remainedEdgesA.add(edgeSA.idx)
        remainedEdgesA.add(edgeEA.idx)
        edgeSB = next(filter(lambda e: e.is_startPoint(info[0])  , edgesB))
        edgeEB = next(filter(lambda e: e.is_endPoint(info[0])  , edgesB))
        remainedEdgesB.add(edgeSB.idx)
        remainedEdgesB.add(edgeEB.idx)
    return [remainedEdgesA,remainedEdgesB]

def vectorDiff(vec1,vec2):
    
    return (vec1[0] - vec2[0],vec1[1] - vec2[1])

def compareFunc(point1,point2):
    
    if(point1[1] > point2[1]):
        return True
    elif(point1[1] == point2[1] and point1[0] < point2[0]):
        return True
    else:
        return False

def overlapTest(polygonA,polygonB,edgesA,edgesB,point):
    intersection = []
    for edgeA in edgesA:
        try:
            for edgeB in edgesB:
                if bounding(edgeA,edgeB):
                    intersect = find_intersection(edgeA,edgeB)
                    if( intersect!= None):
                        if(not(edgeA.is_startPoint(intersect)) and (not(edgeA.is_endPoint(intersect))) and (not(edgeB.is_startPoint(intersect))) and (not(edgeB.is_endPoint(intersect)))):
                            intersection.append(intersect)
                            raise StopIteration
                        elif((not edgeA.is_startPoint(intersect)  and not edgeA.is_endPoint(intersect))):
                            if (edgeB.is_startPoint(intersect)):
                                if((left_or_right(edgeA,edgeB.endPoint) ==  "left" or left_or_right(edgeA,edgesB[edgeB.idx -1].startPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                            elif(edgeB.is_endPoint(intersect)):
                                if(edgeB.idx == (len(edgesB) -1)):
                                    nEdgeB = edgesB[0]
                                else:
                                    nEdgeB = edgesB[edgeB.idx +1]
                                if((left_or_right(edgeA,edgeB.startPoint) ==  "left" or left_or_right(edgeA,nEdgeB.endPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                        elif((not edgeB.is_startPoint(intersect) and not edgeB.is_endPoint(intersect))):
                            if(edgeA.is_startPoint(intersect)):
                                if((left_or_right(edgeB,edgeA.endPoint) ==  "left" or left_or_right(edgeB,edgesA[edgeA.idx -1].startPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                            elif(edgeA.is_endPoint(intersect)):
                                if(edgeA.idx == (len(edgesA) -1)):
                                    nEdgeA = edgesA[0]
                                else:
                                    nEdgeA = edgesA[edgeA.idx +1]
                                if((left_or_right(edgeB,edgeA.startPoint) ==  "left" or left_or_right(edgeB,nEdgeA.endPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                        else:
                            if(edgeB.is_startPoint(intersect)):
                                pEdgeB = edgesB[edgeB.idx -1]
                                if(edgeA.is_startPoint(intersect)):
                                    pEdgeA = edgesA[edgeA.idx -1]
                                    if(left_or_right(edgeB,pEdgeB.startPoint) == "left" or left_or_right(pEdgeB,edgeB.endPoint) == "left"):#convex
                                        if(left_or_right(edgeA,pEdgeA.startPoint) == "left" or left_or_right(pEdgeA,edgeA.endPoint) == "left"):#convex
                                            if(left_or_right(pEdgeA,edgeB.endPoint) == "left" and left_or_right(edgeA,pEdgeB.startPoint) == "left"):
                                                intersection.append(intersect)
                                                raise StopIteration
                                        elif(left_or_right(edgeA,pEdgeA.startPoint) == "right" or left_or_right(pEdgeA,edgeA.endPoint) == "right"):#concave
                                            if(left_or_right(pEdgeA,edgeB.endPoint) == "left" or left_or_right(pEdgeA,pEdgeB.startPoint) == "left"):
                                                intersection.append(intersect)
                                                raise StopIteration 
                                            elif(left_or_right(edgeA,edgeB.endPoint) == "left" or left_or_right(edgeA,pEdgeB.startPoint) == "left"):
                                                intersection.append(intersect)
                                                raise StopIteration
                                    elif(left_or_right(edgeB,pEdgeB.startPoint) == "right" or left_or_right(pEdgeB,edgeB.endPoint) == "right"):#concave
                                        if(left_or_right(edgeA,pEdgeA.startPoint) == "left" or left_or_right(pEdgeA,edgeA.endPoint) == "left"):#convex
                                            if(left_or_right(edgeB,edgeA.endPoint) == "left" and left_or_right(edgeB,pEdgeA.startPoint) == "left"):
                                                intersection.append(intersect)
                                                raise StopIteration 
                                        elif(left_or_right(edgeA,pEdgeA.startPoint) == "right" or left_or_right(pEdgeA,edgeA.endPoint) == "right"):#concave
                                            intersection.append(intersect)
                                            raise StopIteration 
        except StopIteration:
            break
   
    
    if(len(intersection)==0):
        return True
    else:
        return False
    
def holeOverlapTest(hole,polygonB,holeEdges,edgesB,point):
    intersection = []
    for holeEdge in holeEdges:
        try:
            for edgeB in edgesB:
                if bounding(holeEdge,edgeB):
                    intersect = find_intersection(holeEdge,edgeB)
                    if( intersect!= None):
                        if(not(holeEdge.is_startPoint(intersect)) and (not(holeEdge.is_endPoint(intersect))) and (not(edgeB.is_startPoint(intersect))) and (not(edgeB.is_endPoint(intersect)))):
                            intersection.append(intersect)
                            raise StopIteration
                        elif((not holeEdge.is_startPoint(intersect)  and not holeEdge.is_endPoint(intersect))):
                            if (edgeB.is_startPoint(intersect)):
                                if((left_or_right(holeEdge,edgeB.endPoint) ==  "left" or left_or_right(holeEdge,edgesB[edgeB.idx -1].startPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                            elif(edgeB.is_endPoint(intersect)):
                                if(edgeB.idx == (len(edgesB) -1)):
                                    nEdgeB = edgesB[0]
                                else:
                                    nEdgeB = edgesB[edgeB.idx +1]
                                if((left_or_right(holeEdge,edgeB.startPoint) ==  "left" or left_or_right(holeEdge,nEdgeB.endPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                        elif((not edgeB.is_startPoint(intersect) and not edgeB.is_endPoint(intersect))):
                            if(holeEdge.is_startPoint(intersect)):
                                if(not(left_or_right(edgeB,holeEdge.endPoint) ==  "right" and left_or_right(edgeB,holeEdges[holeEdge.idx -1].startPoint) ==  "right")):
                                    intersection.append(intersect)
                                    raise StopIteration
                            elif(holeEdge.is_endPoint(intersect)):
                                if(holeEdge.idx == (len(holeEdges) -1)):
                                    nEdgeHole = holeEdges[0]
                                else:
                                    nEdgeHole = holeEdges[holeEdge.idx +1]
                                if((left_or_right(edgeB,holeEdge.startPoint) ==  "left" or left_or_right(edgeB,nEdgeHole.endPoint) ==  "left")):
                                    intersection.append(intersect)
                                    raise StopIteration
                        else:
                            if(edgeB.is_startPoint(intersect)):
                                pEdgeB = edgesB[edgeB.idx -1]
                                if(holeEdge.is_startPoint(intersect)):
                                    pEdgeHole = holeEdges[holeEdge.idx -1]
                                    if(left_or_right(edgeB,pEdgeB.startPoint) == "left" or left_or_right(pEdgeB,edgeB.endPoint) == "left"):#convex
                                        if(left_or_right(holeEdge,pEdgeHole.startPoint) == "right" or left_or_right(pEdgeHole,holeEdge.endPoint) == "right"):#convex
                                            if(left_or_right(pEdgeHole,edgeB.endPoint) == "left" or left_or_right(holeEdge,pEdgeB.startPoint) == "left"):#changed the and to or and it fixed the problem
                                                intersection.append(intersect)
                                                raise StopIteration
                                        elif(left_or_right(holeEdge,pEdgeHole.startPoint) == "left" or left_or_right(pEdgeHole,holeEdge.endPoint) == "left"):#concave
                                            if((left_or_right(pEdgeHole,edgeB.endPoint) == "left" and left_or_right(holeEdge,edgeB.endPoint) == "left")
                                               or
                                               (left_or_right(pEdgeHole,pEdgeB.startPoint) == "left" and left_or_right(holeEdge,pEdgeB.startPoint) == "left")
                                               ):
                                                intersection.append(intersect)
                                                raise StopIteration 
                                            elif((left_or_right(pEdgeHole,edgeB.endPoint) == "left" and left_or_right(holeEdge,edgeB.endPoint) == "parallel")
                                               or
                                               (left_or_right(pEdgeHole,pEdgeB.startPoint) == "parallel" and left_or_right(holeEdge,pEdgeB.startPoint) == "left")):
                                                intersection.append(intersect)
                                                raise StopIteration
                                    elif(left_or_right(edgeB,pEdgeB.startPoint) == "right" or left_or_right(pEdgeB,edgeB.endPoint) == "right"):#concave
                                        if(left_or_right(holeEdge,pEdgeHole.startPoint) == "right" or left_or_right(pEdgeHole,holeEdge.endPoint) == "right"):#convex
                                            intersection.append(intersect)
                                            raise StopIteration 
                                        elif(left_or_right(holeEdge,pEdgeHole.startPoint) == "left" or left_or_right(pEdgeHole,holeEdge.endPoint) == "left"):#concave
                                            if((left_or_right(pEdgeHole,edgeB.endPoint) == "left" and left_or_right(holeEdge,edgeB.endPoint) == "left")
                                               or
                                               (left_or_right(pEdgeHole,pEdgeB.startPoint) == "left" and left_or_right(holeEdge,pEdgeB.startPoint) == "left")
                                               ):
                                                intersection.append(intersect)
                                                raise StopIteration 
        except StopIteration:
            break
   
    
    
   
    if(len(intersection)==0):
        return True
    else:
        return False

def NFP2(startPoint,touchPoint,polygonA,polygonB,edgesA,cond2,cond1=True,touchingEdge=None):
    
    polygonB2 = polygonB[:]
    diff_vec = (touchPoint[0]- startPoint[0], touchPoint[1] - startPoint[1])
    polygonB2= [[x - diff_vec[0], y - diff_vec[1]] for x,y in polygonB2]
    y=0
    nfp = []
    x=(None,None)
    wCond = lowest_key(polygonB2)
    point = Point(startPoint[0],startPoint[1])
    edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
    nextTv =  tVectorFinder(point,edgesA,edgesB,cond1,cond2,touchingEdge)[0]
    if(cond2 == True):
        edgeA= touchingEdge
    else:
        edgeA= next(filter(lambda e: e.is_startPoint(point)  , edgesA))
    edgeB= next(filter(lambda e: e.is_startPoint(point)  , edgesB))
    p = Point(point.x + nextTv[0],point.y + nextTv[1])
    if((edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[0] and (edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[1]):
        next_info = [point,edgeA,True,False,p,polygonA.index([point.x,point.y])]
    else:
        next_info = [point,edgeB,False,True,p,polygonB2.index([point.x,point.y])]
        
    visitedEdgesA =set() 
    visitedEdgesB =set() 
    vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB)
     
    visitedEdgesA = vE[0] 
    visitedEdgesB = vE[1] 

    
    c = 0
    
    while (((x[0] != wCond[0]) or(x[1] != wCond[1]) or y <2) and c!=2):
        edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 

        filteredEdgesA = boundry(polygonB2,edgesA,nextTv)
        filteredEdgesB = boundry(polygonA,edgesB,(-nextTv[0],-nextTv[1]))
        t1 = trimmer2(polygonB2,filteredEdgesA,nextTv,edgesA)

        t2 = trimmer2(polygonA,filteredEdgesB,(-t1[0],-t1[1]),edgesB)
      
        polygonB2 = [[x + (-t2[0]), y + (-t2[1])] for x, y in polygonB2]
        trim1 = trimFun(polygonB2,filteredEdgesA,(-t2[0],-t2[1]),True)
        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b), idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
        filteredEdgesB2 = boundry(polygonA,edgesB2,(-t2[0],-t2[1]))
        trim2 = trimFun(polygonA,filteredEdgesB2,t2,False)
        vecList = []
        if(nfp.__contains__(lowest_key(polygonB2))):
            c +=1
        nfp.append(lowest_key(polygonB2))

        idealTV=[]
        trimResults = trim1 + trim2
        
        for i,info in enumerate(trimResults):
            possibleNextVector = tVectorFinder(info[4],edgesA,edgesB2,info[2],info[3],info[1])[0]
            vecList.append(possibleNextVector)

        
        for j,vector in enumerate(vecList):
            if(feasibleTV(edgesA,edgesB2,vector,trimResults) == False):
                pass
            else:
                idealTV.append((vector,trimResults[j][4],trimResults[j]))
        
        distanceL = []
        
        if(len(idealTV) == 0 ):
            break
        for l in idealTV:
            tvec = Line(point,Point(point.x + (-t2[0]/2),point.y + (-t2[1]/2)),5,1)
            distanceL.append(distance(tvec,l[1]))
        index = distanceL.index(min(distanceL))
        next_info = idealTV[index][2]
        
        nextTv = idealTV[index][0]
        point = idealTV[index][1]
        x = nfp[-1]
        
        vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB2)
        visitedEdgesA = vE[0]
        visitedEdgesB = vE[1]
        y += 1 
    return (nfp,visitedEdgesA,visitedEdgesB)


def nfpSup(polygonA,polygonB,remainedEdgesA,nfpPointList):
    navigatedA = []
    navigatedB = []
    nfpList = []
    edgesA = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonA, polygonA[1:] + [polygonA[0]]))] 
    for edge in remainedEdgesA:
        mPoint = (edge.startPoint.x,edge.startPoint.y)
        for indx,point in enumerate(polygonB):
            if( edge.idx not in navigatedA):
                polygonB2 = polygonB[:]
                tvec = (mPoint[0] - point[0],mPoint[1] - point[1])
                polygonB2 = [[x + tvec[0], y + tvec[1]] for [x,y] in polygonB2]
                endPoint = None
                startPoint = (polygonB2[indx][0],polygonB2[indx][1])
                if( indx == len(polygonB2) -1):
                    endPoint = (polygonB2[0][0],polygonB2[0][1])
                else:
                    endPoint = (polygonB2[indx + 1][0],polygonB2[indx + 1][1])
                edgeSB = Line(Point(startPoint[0],startPoint[1]),Point(endPoint[0],endPoint[1]),slope(startPoint,endPoint),indx)
                startpoint = (polygonB2[indx][0],polygonB2[indx][1])
                endPoint = (polygonB2[indx - 1][0],polygonB2[indx - 1][1])
                edgeEB = Line(Point(endPoint[0],endPoint[1]),Point(startpoint[0],startpoint[1]),slope(endPoint,startpoint),indx-1)
                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
                if(left_or_right(edge,edgeSB.endPoint) == "left" or left_or_right(edge,edgeEB.startPoint) == "left" ):
                    pass
                else:
                    tVec = (edge.endPoint.x - edge.startPoint.x, edge.endPoint.y - edge.startPoint.y)
                    if(find_intersectionSup(edge,edgeSB) or ((find_intersectionSup(edge,edgeEB)))):
                            pass
                    else:
                        orgtVec = tVec
                        cond1 = True
                        cond2 = False
                        l = None
                        startPoint = mPoint
                        touchPoint = (point[0] + tvec[0], point[1] + tvec[1])
                        while(vectorDiff(orgtVec,tVec) != orgtVec):    
                            try:
                                filteredEdgesA = boundry(polygonB2,edgesA,tVec)
                                filteredEdgesB2 = boundry(polygonA,edgesB2,tVec)
                                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
                                if(overlapTest(polygonA,polygonB2,edgesA,edgesB2,touchPoint)):
                                    
                                    if(lowest_key(polygonB2) not in nfpPointList ):
                                        inner_nfp = NFP2(startPoint,touchPoint,polygonA,polygonB2,edgesA,cond2,cond1,l)
                                        # #print(f"inner NFP:{inner_nfp}")
                                        nfpList.append(inner_nfp[0])
                                        navigatedA = inner_nfp[1]
                                        navigatedB.extend(inner_nfp[2])
                                        
                                        nfpPointList.extend(inner_nfp[0])
                                        raise StopIteration
                                    else:
                                        break
                                else:
                                    t = trimmerSup(polygonB2,filteredEdgesA,tVec)
                                    t1 = trimmerSup(polygonA,filteredEdgesB2,(-t[0],-t[1]))
                                    polygonB2 = [[x + (-t1[0]), y + (-t1[1])] for x, y in polygonB2]
                                    cond2 = True
                                    l = edge
                                    tVec = (tVec[0] - (-t1[0]),tVec[1] - (-t1[1]))
                                    touchPoint = (touchPoint[0] + (-t1[0]), touchPoint[1] + (-t1[1]))
                                    startPoint = touchPoint
                            except StopIteration:
                                break
    return (nfpList,navigatedB)


def NFP2B2A(startPoint,touchPoint,polygonA,polygonB,edgesA,cond2,cond1=True,touchingEdge=None):
    polygonB2 = polygonB[:]
    diff_vec = (touchPoint[0]- startPoint[0], touchPoint[1] - startPoint[1])
    polygonB2= [[x - diff_vec[0], y - diff_vec[1]] for x,y in polygonB2]
    y=0
    nfp = []
    x=(None,None)
    wCond = lowest_key(polygonB2)
    point = Point(startPoint[0],startPoint[1])
   
    edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
    nextTv =  tVectorFinder(point,edgesA,edgesB,cond1,cond2,touchingEdge)[0]
    if(cond2 == True):
        edgeA= touchingEdge
    else:
        edgeA= next(filter(lambda e: e.is_startPoint(point)  , edgesA))
    edgeB= next(filter(lambda e: e.is_startPoint(point)  , edgesB))
   
    p = Point(point.x + nextTv[0],point.y + nextTv[1])
    if((edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[0] and (edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[1]):
        next_info = [point,edgeA,True,False,p,polygonA.index([point.x,point.y])]
    else:
        next_info = [point,edgeB,False,True,p,polygonB2.index([point.x,point.y])]
        
    visitedEdgesA =set() 
    visitedEdgesB =set() 
    vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB)
     
    visitedEdgesA = vE[0] 
    visitedEdgesB = vE[1] 
    c = 0
    while (((x[0] != wCond[0]) or(x[1] != wCond[1]) or y <2) and c!=2):
        edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 

        filteredEdgesA = boundry(polygonB2,edgesA,nextTv)
        filteredEdgesB = boundry(polygonA,edgesB,(-nextTv[0],-nextTv[1]))
        t1 = trimmer2(polygonB2,filteredEdgesA,nextTv,edgesA)
        t2 = trimmer2(polygonA,filteredEdgesB,(-t1[0],-t1[1]),edgesB)

        polygonB2 = [[x + (-t2[0]), y + (-t2[1])] for x, y in polygonB2]
        trim1 = trimFun(polygonB2,filteredEdgesA,(-t2[0],-t2[1]),True)
        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b), idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
        filteredEdgesB2 = boundry(polygonA,edgesB2,(-t2[0],-t2[1]))
        trim2 = trimFun(polygonA,filteredEdgesB2,t2,False)
        vecList = []
        if(nfp.__contains__(lowest_key(polygonB2))):
            c +=1
        nfp.append(lowest_key(polygonB2))

        idealTV=[]
        trimResults = trim1 + trim2
        for info in trimResults:
            possibleNextVector = tVectorFinder(info[4],edgesA,edgesB2,info[2],info[3],info[1])[0]
            vecList.append(possibleNextVector)
        for j,vector in enumerate(vecList):
            if(feasibleTV(edgesA,edgesB2,vector,trimResults) == False):
                pass
            else:
                idealTV.append((vector,trimResults[j][4],trimResults[j]))
        distanceL = []
        if(len(idealTV) == 0 ):
            break
        for l in idealTV:
            tvec = Line(point,Point(point.x + (-t2[0]/2),point.y + (-t2[1]/2)),5,1)
            distanceL.append(distance(tvec,l[1]))
        index = distanceL.index(min(distanceL))
        next_info = idealTV[index][2]
        nextTv = idealTV[index][0]
        point = idealTV[index][1]
        x = nfp[-1]
       
        vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB2)
        visitedEdgesA = vE[0]
        visitedEdgesB = vE[1]
        y += 1 
    return (nfp,visitedEdgesA,visitedEdgesB)

def nfpSupB2A(polygonA,polygonB,remainedEdgesB,nfpPointList,edgesA):
    navigated = []
    nfpList = []
    for edge in remainedEdgesB:
        sPoint = (edge.startPoint.x,edge.startPoint.y)
        for idx,point in enumerate(polygonA):
            if( edge.idx not in navigated):
                polygonB2 = polygonB[:]
                difference_vec = (point[0] - sPoint[0],point[1] - sPoint[1])
                polygonB2 = [[x + difference_vec[0], y + difference_vec[1]] for [x,y] in polygonB2]
                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                startingEdgeA = edgesA[idx]
                endingEdgeA = edgesA[idx - 1]
                
                if(left_or_right(edgesB2[edge.idx],startingEdgeA.endPoint) == "left" or left_or_right(edgesB2[edge.idx],endingEdgeA.startPoint) == "left"):# or left_or_right(edgesB2[edge.idx - 1],startingEdgeA.endPoint) == "left" or left_or_right(edgesB2[edge.idx - 1],endingEdgeA.startPoint) == "left" )  :
                    pass
                else:
                    tVec = (edge.startPoint.x - edge.endPoint.x, edge.startPoint.y - edge.endPoint.y)
                    if(find_intersectionSup(edgesB2[edge.idx],startingEdgeA) or ((find_intersectionSup(edgesB2[edge.idx],endingEdgeA)))):
                       
                        pass
                    else:
                        orgtVec = tVec
                        cond1 = True
                        cond2 = False
                        l = None
                        startPoint = point
                        touchPoint = startPoint
                        while(vectorDiff(orgtVec,tVec) != orgtVec):
                            try:
                                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                                filteredEdgesA = boundry(polygonB2,edgesA,tVec)
                                filteredEdgesB2 = boundry(polygonA,edgesB2,tVec)
                                if(overlapTest(polygonA,polygonB2,edgesA,edgesB2,touchPoint)):
                                    if(lowest_key(polygonB2) not in nfpPointList ):
                                        inner_nfp = NFP2B2A(startPoint,touchPoint,polygonA,polygonB2,edgesA,cond2,cond1,l)
                                        nfpList.append(inner_nfp[0])
                                        navigated = inner_nfp[2]
                                        
                                        nfpPointList.extend(inner_nfp[0])
                                        raise StopIteration
                                    else:
                                        break
                                else:
                                    t = trimmerSup(polygonB2,filteredEdgesA,tVec)
                                    t1 = trimmerSup(polygonA,filteredEdgesB2,(-t[0],-t[1]))
                                    
                                    polygonB2 = [[x + (-t1[0]), y + (-t1[1])] for x, y in polygonB2]
                                    cond2 = True
                                    cond1 = False
                                    edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                                    l = edgesB2[edge.idx]
                                    tVec = (tVec[0] - (-t1[0]),tVec[1] - (-t1[1]))
                                    touchPoint = (touchPoint[0] + (-t1[0]), touchPoint[1] + (-t1[1]))
                                    startPoint = touchPoint
                            except StopIteration:
                                break
    
    return nfpList

def NFPHole2(startPoint,touchPoint,polygonA,polygonB,edgesA,cond2,cond1=True,touchingEdge=None):
    polygonB2 = polygonB[:]
    diff_vec = (touchPoint[0]- startPoint[0], touchPoint[1] - startPoint[1])
    polygonB2= [[x - diff_vec[0], y - diff_vec[1]] for x,y in polygonB2]
    y=0
    nfp = []
    x=(None,None)
    wCond = lowest_key(polygonB2)
    point = Point(startPoint[0],startPoint[1])
    edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
    nextTv =  tVectorFinder(point,edgesA,edgesB,cond1,cond2,touchingEdge)[0]
    if(cond2 == True):
        edgeA= touchingEdge
    else:
        edgeA= next(filter(lambda e: e.is_startPoint(point)  , edgesA))
    edgeB= next(filter(lambda e: e.is_startPoint(point)  , edgesB))
    p = Point(point.x + nextTv[0],point.y + nextTv[1])
    if((edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[0] and (edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[1]):
        next_info = [point,edgeA,True,False,p,polygonA.index([point.x,point.y])]
    else:
        next_info = [point,edgeB,False,True,p,polygonB2.index([point.x,point.y])]
        
    visitedEdgesA =set() 
    visitedEdgesB =set() 
    vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB)
     
    visitedEdgesA = vE[0] 

    
    c = 0
    
    while (((x[0] != wCond[0]) or(x[1] != wCond[1]) or y <2) and c!=2):
        edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 

        filteredEdgesA = boundry(polygonB2,edgesA,nextTv)
        filteredEdgesB = boundry(polygonA,edgesB,(-nextTv[0],-nextTv[1]))
        t1 = holeTrimmer(polygonB2,filteredEdgesA,nextTv,edgesA)
        t2 = holeTrimmer(polygonA,filteredEdgesB,(-t1[0],-t1[1]),edgesB)
      
        polygonB2 = [[x + (-t2[0]), y + (-t2[1])] for x, y in polygonB2]
        trim1 = trimFun(polygonB2,filteredEdgesA,(-t2[0],-t2[1]),True)
        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b), idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
        filteredEdgesB2 = boundry(polygonA,edgesB2,(-t2[0],-t2[1]))
        trim2 = trimFun(polygonA,filteredEdgesB2,t2,False)
        vecList = []
        if(nfp.__contains__(lowest_key(polygonB2))):
            c +=1
        nfp.append(lowest_key(polygonB2))

        idealTV=[]
        trimResults = trim1 + trim2
        
        for i,info in enumerate(trimResults):
            possibleNextVector = tVectorFinder(info[4],edgesA,edgesB2,info[2],info[3],info[1])[0]
            vecList.append(possibleNextVector)

        
        for j,vector in enumerate(vecList):
            if(feasibleTV(edgesA,edgesB2,vector,trimResults) == False):
                pass
            else:
                idealTV.append((vector,trimResults[j][4],trimResults[j]))
        
        distanceL = []
        
        if(len(idealTV) == 0 ):
            break
        for l in idealTV:
            tvec = Line(point,Point(point.x + (-t2[0]/2),point.y + (-t2[1]/2)),5,1)
            distanceL.append(distance(tvec,l[1]))
        index = distanceL.index(min(distanceL))
        next_info = idealTV[index][2]
        
        nextTv = idealTV[index][0]
        point = idealTV[index][1]
        x = nfp[-1]
        
        vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB2)
        visitedEdgesA = vE[0]
        y += 1 
    return (nfp,visitedEdgesA)


def nfpSupHole2(polygonA,polygonB,remainedEdgesA,nfpPointList):
    
    navigatedA = []
    nfpList = []
    edgesA = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonA, polygonA[1:] + [polygonA[0]]))] 
    for edge in remainedEdgesA:
        mPoint = (edge.startPoint.x,edge.startPoint.y)
        for indx,point in enumerate(polygonB):
            if( edge.idx not in navigatedA):
                polygonB2 = polygonB[:]
                tvec = (mPoint[0] - point[0],mPoint[1] - point[1])
                polygonB2 = [[x + tvec[0], y + tvec[1]] for [x,y] in polygonB2]
                endPoint = None
                startPoint = (polygonB2[indx][0],polygonB2[indx][1])
                if( indx == len(polygonB2) -1):
                    endPoint = (polygonB2[0][0],polygonB2[0][1])
                else:
                    endPoint = (polygonB2[indx + 1][0],polygonB2[indx + 1][1])
                edgeSB = Line(Point(startPoint[0],startPoint[1]),Point(endPoint[0],endPoint[1]),slope(startPoint,endPoint),indx)
                startpoint = (polygonB2[indx][0],polygonB2[indx][1])
                endPoint = (polygonB2[indx - 1][0],polygonB2[indx - 1][1])
                edgeEB = Line(Point(endPoint[0],endPoint[1]),Point(startpoint[0],startpoint[1]),slope(endPoint,startpoint),indx-1)
                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
                
                if(left_or_right(edge,edgeSB.endPoint) == "left" or left_or_right(edge,edgeEB.startPoint) == "left"):# or left_or_right(edgesA[edge.idx - 1],edgeSB.endPoint) == "left" or left_or_right(edgesA[edge.idx - 1],edgeEB.startPoint) == "left" )  :
                    pass
                else:
                    tVec = (edge.endPoint.x - edge.startPoint.x, edge.endPoint.y - edge.startPoint.y)
                    if(find_intersectionSup(edge,edgeSB) or ((find_intersectionSup(edge,edgeEB)))):
                            pass
                    else:
                        orgtVec = tVec
                        cond1 = True
                        cond2 = False
                        l = None
                        startPoint = mPoint
                        touchPoint = (point[0] + tvec[0], point[1] + tvec[1])
                        while(vectorDiff(orgtVec,tVec) != orgtVec):    
                            try:
                                filteredEdgesA = boundry(polygonB2,edgesA,tVec)
                                filteredEdgesB2 = boundry(polygonA,edgesB2,tVec)
                                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
                                if(holeOverlapTest(polygonA,polygonB2,edgesA,edgesB2,touchPoint)):
                                    
                                    if(lowest_key(polygonB2) not in nfpPointList ):
                                        inner_nfp = NFPHole2(startPoint,touchPoint,polygonA,polygonB2,edgesA,cond2,cond1,l)
                                        nfpList.append(inner_nfp[0]) 
                                        
                                        navigatedA=inner_nfp[1]
                                        nfpPointList.extend(inner_nfp[0])
                                        raise StopIteration
                                    else:
                                        break
                                else:
                                    t = trimmerSup(polygonB2,filteredEdgesA,tVec)
                                    t1 = trimmerSup(polygonA,filteredEdgesB2,(-t[0],-t[1]))
                                    polygonB2 = [[x + (-t1[0]), y + (-t1[1])] for x, y in polygonB2]
                                    cond2 = True
                                    l = edge
                                    tVec = (tVec[0] - (-t1[0]),tVec[1] - (-t1[1]))
                                    touchPoint = (touchPoint[0] + (-t1[0]), touchPoint[1] + (-t1[1]))
                                    startPoint = touchPoint
                            except StopIteration:
                                break
    return nfpList
                  
def NFPHole(startPoint,touchPoint,polygonA,polygonB,edgesA,cond2,cond1=True,touchingEdge=None):
    
    polygonB2 = polygonB[:]
    diff_vec = (touchPoint[0]- startPoint[0], touchPoint[1] - startPoint[1])
    polygonB2= [[x - diff_vec[0], y - diff_vec[1]] for x,y in polygonB2]
    y=0
    
    nfp = []
    x=(None,None)
    wCond = lowest_key(polygonB2)
    point = Point(startPoint[0],startPoint[1])
   
    edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
    nextTv =  tVectorFinder(point,edgesA,edgesB,cond1,cond2,touchingEdge)[0]
    if(cond2 == True):
        edgeA= touchingEdge
    else:
        edgeA= next(filter(lambda e: e.is_startPoint(point)  , edgesA))
    edgeB= next(filter(lambda e: e.is_startPoint(point)  , edgesB))
   
    p = Point(point.x + nextTv[0],point.y + nextTv[1])
    if((edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[0] and (edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[1]):
        next_info = [point,edgeA,True,False,p,polygonA.index([point.x,point.y])]
    else:
        next_info = [point,edgeB,False,True,p,polygonB2.index([point.x,point.y])]
        
    visitedEdgesA =set() 
    visitedEdgesB =set() 
    vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB)
     
    visitedEdgesB = vE[1] 
    c = 0
    while (((x[0] != wCond[0]) or(x[1] != wCond[1]) or y <2) and c!=2):
        edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 

        filteredEdgesA = boundry(polygonB2,edgesA,nextTv)
        filteredEdgesB = boundry(polygonA,edgesB,(-nextTv[0],-nextTv[1]))
        t1 = holeTrimmer(polygonB2,filteredEdgesA,nextTv,edgesA)
        t2 = holeTrimmer(polygonA,filteredEdgesB,(-t1[0],-t1[1]),edgesB)

        polygonB2 = [[x + (-t2[0]), y + (-t2[1])] for x, y in polygonB2]
        trim1 = trimFun(polygonB2,filteredEdgesA,(-t2[0],-t2[1]),True)
        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b), idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
        filteredEdgesB2 = boundry(polygonA,edgesB2,(-t2[0],-t2[1]))
        trim2 = trimFun(polygonA,filteredEdgesB2,t2,False)
        vecList = []
        if(nfp.__contains__(lowest_key(polygonB2))):
            c +=1
        nfp.append(lowest_key(polygonB2))

        idealTV=[]
        trimResults = trim1 + trim2
    
        for info in trimResults:
            possibleNextVector = tVectorFinder(info[4],edgesA,edgesB2,info[2],info[3],info[1])[0]
            vecList.append(possibleNextVector)
        for j,vector in enumerate(vecList):
            if(feasibleTV(edgesA,edgesB2,vector,trimResults) == False):
                pass
            else:
                idealTV.append((vector,trimResults[j][4],trimResults[j]))
        distanceL = []
        if(len(idealTV) == 0 ):
            break
        for l in idealTV:
            tvec = Line(point,Point(point.x + (-t2[0]/2),point.y + (-t2[1]/2)),5,1)
            distanceL.append(distance(tvec,l[1]))
        index = distanceL.index(min(distanceL))
        next_info = idealTV[index][2]
        nextTv = idealTV[index][0]
        point = idealTV[index][1]
        x = nfp[-1]
        vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB2)
        visitedEdgesB = vE[1]
        y += 1 
    return (nfp,visitedEdgesB)

def nfpSupHole(polygonA,polygonB,remainedEdgesB,nfpPointList,edgesA):
   
    navigated = []
    nfpList = []
    for edge in remainedEdgesB:
        sPoint = (edge.startPoint.x,edge.startPoint.y)
        for idx,point in enumerate(polygonA):
            if( edge.idx not in navigated):
                polygonB2 = polygonB[:]
                difference_vec = (point[0] - sPoint[0],point[1] - sPoint[1])
                polygonB2 = [[x + difference_vec[0], y + difference_vec[1]] for [x,y] in polygonB2]
                edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                startingEdgeA = edgesA[idx]
                endingEdgeA = edgesA[idx - 1]
                
                if(left_or_right(edgesB2[edge.idx],startingEdgeA.endPoint) == "left" or left_or_right(edgesB2[edge.idx],endingEdgeA.startPoint) == "left"):
                    pass
                
                else:
                        tVec = (edge.startPoint.x - edge.endPoint.x, edge.startPoint.y - edge.endPoint.y)
                        if(find_intersectionSup(edgesB2[edge.idx],startingEdgeA) or ((find_intersectionSup(edgesB2[edge.idx],endingEdgeA)))):
                            pass
                        else:
                            orgtVec = tVec
                            cond1 = True
                            cond2 = False
                            l = None
                            startPoint = point
                            touchPoint = startPoint
                            while(vectorDiff(orgtVec,tVec) != orgtVec):    
                                try:
                                    edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                                    filteredEdgesA = boundry(polygonB2,edgesA,tVec)
                                    filteredEdgesB2 = boundry(polygonA,edgesB2,tVec)
                                    if(holeOverlapTest(polygonB2,polygonA,edgesB2,edgesA,touchPoint)):
                                        if(lowest_key(polygonB2) not in nfpPointList ):
                                            inner_nfp = NFPHole(startPoint,touchPoint,polygonA,polygonB2,edgesA,cond2,cond1,l)
                                            nfpList.append(inner_nfp[0])
                                            
                                            navigated = inner_nfp[1]
                                            nfpPointList.extend(inner_nfp[0])
                                            raise StopIteration
                                        else:
                                            break
                                    else:
                                        t = trimmerSup(polygonB2,filteredEdgesA,tVec)
                                        t1 = trimmerSup(polygonA,filteredEdgesB2,(-t[0],-t[1]))
                                        polygonB2 = [[x + (-t1[0]), y + (-t1[1])] for x, y in polygonB2]
                                        cond2 = True
                                        cond1 = False
                                        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
                                        l = edgesB2[edge.idx]
                                        tVec = (tVec[0] - (-t1[0]),tVec[1] - (-t1[1]))
                                        touchPoint = (touchPoint[0] + (-t1[0]), touchPoint[1] + (-t1[1]))
                                        startPoint = touchPoint
                                except StopIteration:
                                    break
    return nfpList

def NFP(startPoint,touchPoint,polygonA,polygonB,edgesA):
    
    polygonB2 = polygonB[:]
    diff_vec = (touchPoint[0]- startPoint[0], touchPoint[1] - startPoint[1])
    polygonB2= [[x - diff_vec[0], y - diff_vec[1]] for x,y in polygonB2]
    nfp = []
    y=0
    x=(None,None)
    wCond = lowest_key(polygonB2)
    point = Point(startPoint[0],startPoint[1])
    edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
    nextTv =  tVectorFinder(point,edgesA,edgesB)[0]
    edgeA= next(filter(lambda e: e.is_startPoint(point)  , edgesA))
    edgeB= next(filter(lambda e: e.is_startPoint(point)  , edgesB))
    p = Point(point.x + nextTv[0],point.y + nextTv[1])
    if((edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[0] and (edgeA.endPoint.x - edgeA.startPoint.x) == nextTv[1]):
        next_info = [point,edgeA,True,False,p,polygonA.index([point.x,point.y])]
    else:
        next_info = [point,edgeB,False,False,p,polygonB2.index([point.x,point.y])]
    visitedEdgesA =set() 
    visitedEdgesB = set()
    vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB)
    visitedEdgesA = vE[0]
    visitedEdgesB = vE[1]
        
    
    while (((x[0] != wCond[0]) or(x[1] != wCond[1]) or y <2)):
        edgesB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))] 
        filteredEdgesA = boundry(polygonB2,edgesA,nextTv)
        filteredEdgesB = boundry(polygonA,edgesB,(-nextTv[0],-nextTv[1]))
        t1 = trimmer(polygonB2,filteredEdgesA,nextTv)
        t2 = trimmer(polygonA,filteredEdgesB,(-t1[0],-t1[1]))

        polygonB2 = [[x + (-t2[0]), y + (-t2[1])] for x, y in polygonB2]
        trim1 = trimFun(polygonB2,filteredEdgesA,(-t2[0],-t2[1]),True)
        edgesB2 = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b), idx)  for idx, (a, b) in enumerate(zip(polygonB2, polygonB2[1:] + [polygonB2[0]]))]
        filteredEdgesB2 = boundry(polygonA,edgesB2,(-t2[0],-t2[1]))
        trim2 = trimFun(polygonA,filteredEdgesB2,t2,False)
        vecList = []
        nfp.append(lowest_key(polygonB2))

        idealTV=[]
        trimResults = trim1 + trim2
        

        for i,info in enumerate(trimResults):
            possibleNextVector = tVectorFinder(info[4],edgesA,edgesB2,info[2],info[3],info[1])[0]
            vecList.append(possibleNextVector)

        
        for j,vector in enumerate(vecList):
            if(feasibleTV(edgesA,edgesB2,vector,trimResults) == False):
                pass
            else:
                idealTV.append((vector,trimResults[j][4],trimResults[j]))
        
        distanceL = []
        for l in idealTV:
            tvec = Line(point,Point(point.x + (-t2[0]/2),point.y + (-t2[1]/2)),5,1)
            distanceL.append(distance(tvec,l[1]))
        index = distanceL.index(min(distanceL))
        next_info = idealTV[index][2]
        
        nextTv = idealTV[index][0]
        point = idealTV[index][1]
        x = nfp[-1] 
        
        vE = edgeRemover(next_info,visitedEdgesA,visitedEdgesB,edgesA,edgesB2)
        visitedEdgesA = vE[0]
        visitedEdgesB = vE[1]
        y += 1
       
    remainedEdgeA = edgesA[:]
    
    for idx in visitedEdgesA:
        remainedEdgeA.remove(edgesA[idx])
    return (nfp,remainedEdgeA,visitedEdgesB)

#calculating the bounding box and it's height and length
def calculate_bounding_box_dimensions(vertices):
    # Initialize min and max coordinates
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')

    # Iterate through all vertices to find min and max coordinates
    for x, y in vertices:
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    # Calculate length and height of bounding box
    length = max_x - min_x
    height = max_y - min_y

    return [length, height]

def finalNFP(polygonA,polygonB):
    edgesA = None
    a_RefPoint = None
    edgesOrgB = None
    b_highPoint = None
    result = []
    if(len(polygonA[0]) > 2 ):
        polygonA = fractionalize(polygonA)
        edgesA = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonA[0], polygonA[0][1:] + [polygonA[0][0]]))]
        a_RefPoint = lowest_key(polygonA[0])
    else: 
        polygonA = [[Fraction(x),Fraction(y)] for x,y in polygonA]
        edgesA = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonA, polygonA[1:] + [polygonA[0]]))]
        a_RefPoint = lowest_key(polygonA)
    
    if(len(polygonB[0]) > 2 ):
        polygonB = fractionalize(polygonB)
        edgesOrgB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB[0], polygonB[0][1:] + [polygonB[0][0]]))]
        b_highPoint = highest_key(polygonB[0])
    else: 
        polygonB = [[Fraction(x),Fraction(y)] for x,y in polygonB]
        edgesOrgB = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(polygonB, polygonB[1:] + [polygonB[0]]))]
        b_highPoint = highest_key(polygonB)

    if(len(polygonA[0]) > 2 and len(polygonB[0]) > 2 ):
        nfp = NFP(a_RefPoint,b_highPoint,polygonA[0],polygonB[0],edgesA)
        result.append(nfp[0])
    elif(len(polygonA[0]) > 2 ):
        nfp = NFP(a_RefPoint,b_highPoint,polygonA[0],polygonB,edgesA)
        result.append(nfp[0])
    elif(len(polygonB[0]) > 2 ):
        nfp = NFP(a_RefPoint,b_highPoint,polygonA,polygonB[0],edgesA)
        result.append(nfp[0])
    else:
        nfp = NFP(a_RefPoint,b_highPoint,polygonA,polygonB,edgesA)
        result.append(nfp[0])

    remainedEdge  = edgesOrgB[:]
    remainedEdgesA = nfp[1]
    remainedEdgesB = nfp[2]
    visitedB = None
    
    if(len(remainedEdgesA) > 0):
        if(len(polygonA[0]) > 2):
            if(len(polygonB[0]) > 2 ):
                innerNfp = nfpSup(polygonA[0],polygonB[0],remainedEdgesA,nfp[0])
                visitedB = set(innerNfp[1])
                for supNfp in innerNfp[0]:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)                    
            else:
                innerNfp = nfpSup(polygonA[0],polygonB,remainedEdgesA,nfp[0])
                visitedB = set(innerNfp[1])
                for supNfp in innerNfp[0]:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)
        else:
            if(len(polygonB[0]) > 2 ):
                innerNfp = nfpSup(polygonA,polygonB[0],remainedEdgesA,nfp[0])
                visitedB = set(innerNfp[1])
                for supNfp in innerNfp[0]:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)
            else:
                innerNfp = nfpSup(polygonA,polygonB,remainedEdgesA,nfp[0])
                visitedB = set(innerNfp[1])
                for supNfp in innerNfp[0]:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)

    vistededgesB = None
    if((visitedB is not None) and (remainedEdgesB is not None)):
        vistededgesB = remainedEdgesB | visitedB
    elif(visitedB is None): 
        vistededgesB = remainedEdgesB
    elif(remainedEdgesB is None):
        vistededgesB = visitedB
    if(vistededgesB is not None):
        for idx in vistededgesB:
            remainedEdge.remove(edgesOrgB[idx])

    if(len(remainedEdge) > 0):
        if(len(polygonA[0]) > 2):
            if(len(polygonB[0]) > 2 ):
                innerNfp2 = nfpSupB2A(polygonA[0],polygonB[0],remainedEdge,nfp[0],edgesA)
                for supNfp in innerNfp2:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)
            else:
                innerNfp2 = nfpSupB2A(polygonA[0],polygonB,remainedEdge,nfp[0],edgesA)
                for supNfp in innerNfp2:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)
        else:
            if(len(polygonB[0]) > 2 ):
                innerNfp2 = nfpSupB2A(polygonA,polygonB[0],remainedEdge,nfp[0],edgesA)
                for supNfp in innerNfp2:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp)
            else:
                innerNfp2 = nfpSupB2A(polygonA,polygonB,remainedEdge,nfp[0],edgesA)
                for supNfp in innerNfp2:
                    if(len(supNfp) == 0):
                        pass
                    else:
                        result.append(supNfp) 
                
    innerPNFPs = []
    if(len(polygonA[0]) > 2):
        for innerP in polygonA[1:]:
            innerEdges = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(innerP, innerP[1:] + [innerP[0]]))]
            innerPBB = calculate_bounding_box_dimensions(innerP)
            if(len(polygonB[0])>2):
                polygonBBB = calculate_bounding_box_dimensions(polygonB[0])
                if(innerPBB[0]>= polygonBBB[0] and innerPBB[1] >= polygonBBB[1]):
                    lp = nfpSupHole2(innerP,polygonB[0],innerEdges,[])
                    for supNfp in lp:
                        if(len(supNfp) == 0):
                            pass
                        else:
                            result.append(supNfp) 
            else:
                polygonBBB = calculate_bounding_box_dimensions(polygonB)
                if(innerPBB[0]>= polygonBBB[0] and innerPBB[1] >= polygonBBB[1]):
                    lp = nfpSupHole2(innerP,polygonB,innerEdges,[])
                    for supNfp in lp:
                        if(len(supNfp) == 0):
                            pass
                        else:
                            result.append(supNfp) 
    
    
    if(len(polygonB[0]) > 2):
        holeNfp= []
        lowp1= lowest_key(polygonB[0])
        for innerP in polygonB[1:]:
            innerPBB = calculate_bounding_box_dimensions(innerP)
            lowi = lowest_key(innerP)
            difference = (lowp1[0] - lowi[0], lowp1[1] - lowi[1])
            innerEdges = [Line(Point(a[0],a[1]),Point(b[0],b[1]),slope(a,b),idx)  for idx, (a, b) in enumerate(zip(innerP, innerP[1:] + [innerP[0]]))]
            if(len(polygonA[0]) > 2 ):
                polygonABB = calculate_bounding_box_dimensions(polygonA[0])
                if(innerPBB[0]>= polygonABB[0] and innerPBB[1] >= polygonABB[1]):
                    holeNfp = nfpSupHole(polygonA[0],innerP,innerEdges,[],edgesA)
            else:
                polygonABB = calculate_bounding_box_dimensions(polygonA)
                if(innerPBB[0]>= polygonABB[0] and innerPBB[1] >= polygonABB[1]):
                    holeNfp = nfpSupHole(polygonA,innerP,innerEdges,[],edgesA)
            for nfp in holeNfp:
                if(len(nfp) == 0):
                    pass
                else:
                    result.append([[x[0] + difference[0],x[1] + difference[1]] for x in nfp])
    return result