import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def raster_to_svg(input_path, output_path, num_colors=16):
    """
    Converts a raster image (PNG with alpha) to a multi-color vector SVG.
    Uses K-Means clustering to quantize colors and generates paths for each color layer.
    """
    try:

        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")

        height, width = img.shape[:2]

        if img.shape[2] == 4:
            alpha = img[:, :, 3]
            bgr = img[:, :, :3]
        else:
            alpha = np.ones((height, width), dtype=np.uint8) * 255
            bgr = img

        bgr = cv2.bilateralFilter(bgr, 9, 75, 75)

        pixels = bgr.reshape((-1, 3))
        pixels = np.float32(pixels)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = num_colors

        _, labels, centers = cv2.kmeans(pixels, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        centers = np.uint8(centers)

        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape((height, width, 3))

        with open(output_path, "w") as f:
            f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">')

            for i, color in enumerate(centers):

                labels_img = labels.reshape((height, width))

                mask = np.zeros((height, width), dtype=np.uint8)
                mask[(labels_img == i) & (alpha > 128)] = 255

                contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if not contours:
                    continue

                color_hex = "#{:02x}{:02x}{:02x}".format(color[2], color[1], color[0])

                for contour in contours:

                    epsilon = 0.001 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)

                    if len(approx) < 3:
                        continue

                    path_data = "M " + " L ".join(f"{pt[0][0]},{pt[0][1]}" for pt in approx) + " Z"
                    f.write(f'<path d="{path_data}" fill="{color_hex}" stroke="none" />')

            f.write('</svg>')

        logger.info(f"Multi-color SVG generated at {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to generate SVG: {e}")
        return False
