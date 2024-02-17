import os
from image_deduplication import cluster_images

# Load images
path = "C:\\Users\\Desktop\\Downloads\\test-image-deduplication\\test-image-deduplication"
image_names = os.listdir(path)
image_names = [os.path.join(path, name) for name in image_names]

image_clusters = cluster_images(image_names)

# Print clusters
for cluster_label, images in image_clusters.items():
    print(f"Cluster {cluster_label}: {images}")