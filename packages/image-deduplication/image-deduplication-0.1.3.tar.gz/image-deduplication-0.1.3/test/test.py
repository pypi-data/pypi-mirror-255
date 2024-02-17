import os
from image_deduplication import cluster_images, get_image_paths
import json

# Load images
paths = get_image_paths("C:\\Users\\Desktop\\Downloads\\test-image-deduplication\\test-image-deduplication")
image_clusters = cluster_images(paths)

for i, cluster in enumerate(image_clusters):
    print(f"""Cluster {i}: {cluster}\n""")