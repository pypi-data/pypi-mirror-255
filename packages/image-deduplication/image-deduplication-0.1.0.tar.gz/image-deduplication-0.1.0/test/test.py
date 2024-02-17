import os
from image_deduplication import cluster_images

# Load indexed images
path = "C:\\Users\\Desktop\\Downloads\\test-image-deduplication\\test-image-deduplication"
indexed_images_names = os.listdir("C:\\Users\\Desktop\\Downloads\\test-image-deduplication\\test-image-deduplication")
indexed_images_names = [os.path.join(path, name) for name in indexed_images_names]

image_clusters = cluster_images(indexed_images_names)
print(__file__)
# Print clusters
for cluster_label, images in image_clusters.items():
    print(f"Cluster {cluster_label}: {images}")