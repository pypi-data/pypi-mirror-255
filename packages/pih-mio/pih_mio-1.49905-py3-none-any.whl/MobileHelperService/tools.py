import ipih

from pih import Output, PIHThreadPoolExecutor
from DocsService.tools import Converter
from PIL import Image

import numpy as np


class Logger:
    def __init__(self, logger: Output, level: int = 0):
        self.output: Output = logger
        self.level: int = level
        self.executor: PIHThreadPoolExecutor = PIHThreadPoolExecutor(1)

    def write_image(self, caption: str, image_object: np.ndarray | Image.Image) -> None:
        def write_image_internal(
            caption: str, image_object: np.ndarray | Image.Image
        ) -> None:
            if isinstance(image_object, np.ndarray):
                image_object = Converter.image_array_to_image(image_object)
            self.output.write_image(caption, Converter.image_to_base64(image_object))

        if self.level > 0:
            if isinstance(image_object, Image.Image):
                image_object = image_object.copy()
            self.executor.submit(write_image_internal, caption, image_object)

    def write_line(self, text: str) -> None:
        def write_line_internal(text: str) -> None:
            self.output.write_line(text)

        if self.level > 0:
            self.executor.submit(write_line_internal, text)

    def error(self, value: str) -> None:
        if self.level > 0:
            self.output.error(value)
