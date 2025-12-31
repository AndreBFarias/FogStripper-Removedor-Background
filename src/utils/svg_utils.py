import logging

import vtracer

logger: logging.Logger = logging.getLogger(__name__)


def raster_to_svg(input_path: str, output_path: str, num_colors: int = 16) -> bool:
    try:
        vtracer.convert_image_to_svg_py(
            input_path,
            output_path,
            colormode="color",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=4,
            color_precision=6,
            layer_difference=16,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )
        logger.info(f"SVG vetorizado gerado em {output_path}")
        return True

    except Exception as e:
        logger.error(f"Falha ao gerar SVG: {e}")
        return False
