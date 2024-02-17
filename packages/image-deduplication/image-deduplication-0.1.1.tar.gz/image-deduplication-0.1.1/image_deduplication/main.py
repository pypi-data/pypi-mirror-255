import os
import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def get_image_paths(folder_path: str, depth: int=None, sanity_check: bool=False) -> list[str]:
    """
    Get the paths of readable images within the specified folder.

    Args:
        folder_path (str): The path of the folder to search for images.
        depth (int, optional): The maximum depth to search for images. Defaults to None.
        sanity_check (bool, optional): Whether to perform sanity checks when reading images. Defaults to False.

    Returns:
        list[str]: A list of paths to readable images within the folder.
    """
    # Supported image extensions by cv2.imread
    supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

    # List to hold the paths of images that can be read
    readable_image_paths = []

    if depth is None:
        depth = float('inf')

    current_depth = 0
    # Iterate over each item in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # If item is a file and has a supported extension, try reading it
        if os.path.isfile(item_path) and os.path.splitext(item_path)[1].lower() in supported_extensions:
            try:
                if sanity_check:
                    img = cv2.imread(item_path)
                    if img is not None:
                        readable_image_paths.append(item_path)
                else: readable_image_paths.append(item_path)
            except Exception as e:
                print(f"Error reading {item_path}: {e}")
        
        # If item is a directory and the search depth allows, recurse into it
        elif os.path.isdir(item_path) and current_depth < depth:
            readable_image_paths += get_image_paths(item_path, depth, current_depth + 1)

    return readable_image_paths

def extract_orb_features(image: np.ndarray):
    """
    Function to extract ORB features from an image.

    Parameters:
    - image: np.ndarray, the input image

    Returns:
    - keypoints: list of keypoints
    - descriptors: list of descriptors
    """
    # Initialize ORB
    orb = cv2.ORB_create()

    # Find the keypoints with ORB
    keypoints = orb.detect(image, None)

    # Compute the descriptors with ORB
    keypoints, descriptors = orb.compute(image, keypoints)

    return keypoints, descriptors

def calculate_similarity_matrix(image_descs: list[tuple]):
    """
    Calculate the similarity matrix for a list of image descriptors.

    Args:
    - image_descs: a list of tuples containing image descriptors

    Returns:
    - similarity_matrix: a 2D array representing the similarity between images
    """
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
    """
    Cluster images based on their features using the DBSCAN algorithm.

    Parameters:
    - indexed_images_names: list of strings, the names of the indexed images

    Returns:
    - image_clusters: dictionary, mapping cluster labels to lists of image names
    """
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