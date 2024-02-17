from src.point import Point
from functools import reduce
import math


class Cluster(object):
    """ Creates a cluster class to represent a single cluster class.
    """
    def __init__(self, points):
        if len(points) == 0:
            raise Exception("ILLEGAL: empty cluster")

        # The points that belong to this cluster
        self.points = points

        # The dimensionality of the points in this cluster
        self.n = points[0].n

        # Assert that all points are of the same dimensionality
        for p in points:
            if p.n != self.n:
                raise Exception("ILLEGAL: wrong dimensions")

        # Set up the initial centroid (this is usually based off one point)
        self.centroid = self.calculate_centroid()

    def __repr__(self):
        return str(self.points)

    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculate_centroid()
        shift = self.get_distance(old_centroid, self.centroid)
        return shift

    def calculate_centroid(self):
        num_points = len(self.points)
        # Get a list of all coordinates in this cluster
        coords = [p.coordinates for p in self.points]
        # Reformat that so all x's are together, all y'z etc.
        unzipped = zip(*coords)
        # Calculate the mean for each dimension
        centroid_coordinates = [math.fsum(dList) / num_points for dList in unzipped]

        return Point(centroid_coordinates)

    def get_distance(self, a, b):
        if a.n != b.n:
            raise Exception("ILLEGAL: non comparable points")

        ret = reduce(lambda x, y: x + pow((a.coordinates[y] - b.coordinates[y]), 2), range(a.n), 0.0)
        return math.sqrt(ret)