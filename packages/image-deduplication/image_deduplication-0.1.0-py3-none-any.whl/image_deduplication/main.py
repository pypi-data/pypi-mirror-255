import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def extract_orb_features(image: np.ndarray):
    # Initialize ORB
    orb = cv2.ORB_create()

    # Find the keypoints with ORB
    keypoints = orb.detect(image, None)

    # Compute the descriptors with ORB
    keypoints, descriptors = orb.compute(image, keypoints)

    return keypoints, descriptors

def calculate_similarity_matrix(image_descs: list[tuple]):
    num_images = len(image_descs)
    similarity_matrix = np.zeros((num_images, num_images))

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    for i in range(num_images):
        for j in range(i + 1, num_images):
            matches = bf.knnMatch(image_descs[i][1], image_descs[j][1], k=2)
            good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
            similarity_matrix[i][j] = len(good_matches)

    return similarity_matrix

def cluster_images(indexed_images_names):
    indexed_images_names = [name for name in indexed_images_names if name.endswith('.png')]
    indexed_images = [cv2.imread(name) for name in indexed_images_names]

# Create descriptors for indexed images
    indexed_img_descs = [extract_orb_features(image) for image in indexed_images]

# Calculate similarity matrix
    similarity_matrix = calculate_similarity_matrix(indexed_img_descs)

# Standardize the similarity matrix
    scaler = StandardScaler()
    standardized_similarity_matrix = scaler.fit_transform(similarity_matrix)

# Perform DBSCAN clustering
    dbscan = DBSCAN(eps=1, min_samples=2, metric='euclidean')
    cluster_labels = dbscan.fit_predict(standardized_similarity_matrix)

# Group images into clusters
    image_clusters = {}
    for image_name, cluster_label in zip(indexed_images_names, cluster_labels):
        if cluster_label not in image_clusters:
            image_clusters[cluster_label] = []
        image_clusters[cluster_label].append(image_name)
    return image_clusters