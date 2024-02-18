import numpy as np    
import matplotlib.pyplot as plt
import matplotlib
        
def rand_col_seg(seg) -> np.ndarray:
    
    vals = np.unique(seg)
    colors = np.random.uniform(0.1, 1, (vals.max()+1, 3))
    colors[0] = [0, 0, 0]

    return colors[seg]
        
def plot_image_and_segmentation(image: np.ndarray, segmentation_mask: np.ndarray, figsize=(10, 5), axis="off", random_color_segmentation=True) -> matplotlib.figure.Figure:
        
    if random_color_segmentation:
        segmentation_mask = rand_col_seg(segmentation_mask)
        
    fig, axs = plt.subplots(1, 2, figsize=figsize)
    
    for ax, im in zip(axs.ravel(), [image, segmentation_mask]):
        ax.imshow(im)
        ax.axis(axis)
    
    return fig
    