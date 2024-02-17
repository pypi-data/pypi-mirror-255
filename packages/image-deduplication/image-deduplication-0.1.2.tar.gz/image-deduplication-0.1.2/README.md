# Image Deduplication

<div style="text-align:center">
    <img src="media/logo.webp" alt="drawing" style="width:200px;"/>
</div>

Easily find images that have a high degree of similarity using either:
- one line of code
- cli tool

## Installation
```
pip install image-deduplication
```

## Usage

### Find similar images in a folder tree
```python
from image_deduplication import get_image_paths, cluster_images

image_paths = get_image_paths("path/to/images") # Returns list of image paths
image_clusters = cluster_images(image_paths)

# Print clusters
for i, (group, images) in enumerate(image_clusters.items()):
    print(f"Group {i}: {images}")
```

### Find similar images from a list of files
```python
from image_deduplication import cluster_images

image_paths = [
    "image1.png",
    "image2.jpg",
    "image3.jpeg"
]

image_clusters = cluster_images(image_paths)

# Print clusters
for i, (group, images) in enumerate(image_clusters.items()):
    print(f"Group {i}: {images}")
```