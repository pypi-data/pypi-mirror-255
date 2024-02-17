class Point(object):
    """ Creates a point class to represent a single feature vector
    """
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.n = len(coordinates)

    def __repr__(self):
        return str(self.coordinates)