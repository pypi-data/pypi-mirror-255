import argparse
from image_deduplication import get_image_paths, cluster_images

def main():
    parser = argparse.ArgumentParser(description='Find similar images.')
    parser.add_argument('image_folder', type=str, help='Path to the image folder')
    
    args = parser.parse_args()

    image_paths = get_image_paths(args.image_folder) # Returns list of image paths
    image_clusters = cluster_images(image_paths)

    # Print clusters
    for i, (group, images) in enumerate(image_clusters.items()):
        print(f"Group {i}: {images}")