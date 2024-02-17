# -*- coding: utf-8 -*-
"""
    src.k-means recommendation
    ~~~~~~~~~~~~~~~~
    This module takes a series of pack ids and recommends the canister location for the robots.
    The robot can be numbered 1 to n. The output will be set of ndcs which should be put into
    each of the robots.
model.model_pack
    IN the core we use k-means-clustering algorithm to make recommendation for the canisters for the
    robots. The number of clusters will be equal to to the number of robots. The error will be less than
    0.1 percent before the algorithm converges to the optimal point.

    Todo:

    :copyright: (c) 2015 by Dosepack LLC.

"""
import logging
from src.point import Point
from src.cluster import Cluster
from dosepack.error_handling.error_handler import create_response, error
import math
import random
from functools import reduce
from collections import defaultdict

# get the logger for the canister
logger = logging.getLogger("root")


def k_means(points, k, cutoff):
    """ Takes the feature vector with the input feature vector , the number of clusters to
    be formed and the error cutoff and runs the k-means-algorithm on the dataset.

    Args:
        points (list): The input feature vector
        k (int): The number of clusters to be formed
        cutoff (float): The maximum error rate to be allowed

    Returns:
        The data points assigned to each of the clusters.

    Examples:
        >>> k_means([])
        {}
    """

    # Pick out k random points to use as our initial centroids
    initial = random.sample(points, k)

    # Create k clusters using those centroids
    clusters = [Cluster([p]) for p in initial]
    # Loop through the dataset until the clusters stabilize
    loop_counter = 0

    while True:
        # Create a list of lists to hold the points in each cluster
        lists = [[] for c in clusters]
        cluster_count = len(clusters)

        # Start counting loops
        loop_counter += 1
        # For every point in the dataset ...
        for p in points:
            # Get the distance between that point and the centroid of the first
            # cluster.
            smallest_distance = get_distance(p, clusters[0].centroid)
            # Set the cluster this point belongs to
            cluster_index = 0

            # For the remainder of the clusters ...
            for i in range(cluster_count - 1):
                # calculate the distance of that point to each other cluster's
                # centroid.
                distance = get_distance(p, clusters[i + 1].centroid)
                # If it's closer to that cluster's centroid update what we
                # think the smallest distance is, and set the point to belong
                # to that cluster
                if distance < smallest_distance:
                    smallest_distance = distance
                    cluster_index = i + 1
            lists[cluster_index].append(p)

        # Set our biggest_shift to zero for this iteration
        biggest_shift = 0.0

        # As many times as there are clusters ...
        for i in range(cluster_count):
            # Calculate how far the centroid moved in this iteration
            shift = clusters[i].update(lists[i])
            # Keep track of the largest move from all cluster centroid updates
            biggest_shift = max(biggest_shift, shift)

        # If the centroids have stopped moving much, say we're done!
        if biggest_shift < cutoff:
            print("Converged after %s iterations", loop_counter)
            break
    return clusters


def get_distance(a, b):
    """
    calculates the euclidean distance between two vectors
    """
    if a.n != b.n:
        raise Exception("ILLEGAL: non comparable points")

    ret = reduce(lambda x, y: x + pow((a.coordinates[y]-b.coordinates[y]), 2), range(a.n), 0.0)
    return math.sqrt(ret)


def run_k_means(data, num_clusters, drug_ids_list, patient_name_list, opt_cutoff=0.1):
    """ Takes the input parameters and runs k-means-clustering algorithm
    on it and returns the data points which are assigned to each of the
    cluster.

    Args:
        data (list): The input feature vector
        num_clusters (int): The number of clusters to be formed
        drug_ids_list (list): The drug ids list
        patient_name_list (list): The list of patient ids
        opt_cutoff (float): The maximum error rate to be allowed

    Returns:
        {}

    Examples:
        >>> run_k_means([])
        None
    """
    # Generate some points
    points = [Point(item) for item in data]
    print("Total number of data points is: " + str(len(points)))
    # Cluster those data!
    clusters = k_means(points, num_clusters, opt_cutoff)

    # Print our clusters
    clust = defaultdict(set)
    drug_ids_list = list(drug_ids_list)
    patient_name_list = list(patient_name_list)

    for i, c in enumerate(clusters):
        print("Cluster:" + str(i))
        print("No of points: " + str(len(c.points)))
        for p in c.points:
            for index, item in enumerate(p.coordinates):
                if item == 1:
                    clust[i].add(drug_ids_list[index])

    return create_response(clust)
