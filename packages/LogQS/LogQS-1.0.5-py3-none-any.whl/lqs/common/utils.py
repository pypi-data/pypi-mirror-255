import io
import os
import inspect
import logging

from pythonjsonlogger import jsonlogger
import s3path
import numpy as np
from PIL import Image as ImagePIL
import bz2
import lz4.frame
import lz4.block
import zstd


class ContextLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, kwargs

    def log(self, level, msg, *args, **kwargs):
        """
        Override the default 'log' method to inject custom contextual information into the LogRecord.
        """
        if self.isEnabledFor(level):
            frame = inspect.currentframe()
            # the frame is two levels up
            stack_info = inspect.getouterframes(frame)[3][0]
            if stack_info:
                # Extracting filename, line number, and function name from the frame
                filename = stack_info.f_code.co_filename
                lineno = stack_info.f_lineno
                func_name = stack_info.f_code.co_name
                record = self.logger.makeRecord(
                    self.logger.name,
                    level,
                    filename,
                    lineno,
                    msg,
                    args,
                    None,
                    func_name,
                    None,
                )
                self.logger.handle(record)


def get_logger(
    name,
    level: str | None = None,
    log_to_file: bool = False,
    json_logging: bool = False,
):
    log_level = level or os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    # logger.propagate = False
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "%(asctime)s  (%(levelname)s - %(name)s): %(message)s"
    )
    if json_logging:
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(filename)s %(funcName)s %(lineno)s %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if log_to_file:
            handler = logging.FileHandler("lqs.log")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    return ContextLoggerAdapter(logger, {})


def get_relative_object_path(object_key: str, source: str):
    if source is None:
        return object_key
    if not object_key.endswith("/"):
        object_key = object_key.rsplit("/", 1)[0] + "/"
    return str(s3path.PureS3Path(object_key + source))


def decompress_chunk_bytes(chunk_bytes, chunk_compression, chunk_length=None):
    if chunk_compression == "bz2":
        decompressed_bytes = bz2.decompress(chunk_bytes)
    elif chunk_compression == "lz4":
        decompressed_bytes = lz4.frame.decompress(chunk_bytes)
    elif chunk_compression == "zstd":
        decompressed_bytes = zstd.decompress(chunk_bytes)
    elif chunk_compression == "lz4_block":
        if chunk_length is None:
            raise ValueError("Must specify chunk_length when decompressing lz4_block")
        decompressed_bytes = lz4.block.decompress(chunk_bytes, chunk_length)
    else:
        raise ValueError(f"Unknown chunk compression type: {chunk_compression}")
    return decompressed_bytes


def get_record_image(
    record_data,
    max_size: int | None = None,
    format: str = "WEBP",
    format_params: dict = {},
    reset_position: bool = True,
    return_bytes: bool = False,
) -> ImagePIL.Image | io.BytesIO | None:
    img_modes = {
        "16UC1": "I;16",
        "mono8": "L",
        "mono16": "I;16",
        "32FC1": "F",
        "8UC1": "L",
        "8UC3": "RGB",
        "rgb8": "RGB",
        "bgr8": "RGB",
        "rgba8": "RGBA",
        "bgra8": "RGBA",
        "bayer_rggb": "L",
        "bayer_rggb8": "L",
        "bayer_gbrg": "L",
        "bayer_gbrg8": "L",
        "bayer_grbg": "L",
        "bayer_grbg8": "L",
        "bayer_bggr": "L",
        "bayer_bggr8": "L",
        "yuv422": "YCbCr",
        "yuv411": "YCbCr",
    }

    record_image_format = record_data.get("format", None)
    if record_image_format is None:
        encoding = record_data.get("encoding", None)
        if not encoding:
            return None

        mode = img_modes[encoding]
        img = ImagePIL.frombuffer(
            mode,
            (record_data["width"], record_data["height"]),
            bytes(record_data["data"]),
            "raw",
            mode,
            0,
            1,
        )
        if encoding == "bgr8":
            b, g, r = img.split()
            img = ImagePIL.merge("RGB", (r, g, b))

        if encoding in ["mono16", "16UC1", "32FC1"]:
            pixels = np.asarray(img)
            pixel_range = np.max(pixels) - np.min(pixels)
            if pixel_range == 0:
                pixels = np.zeros_like(pixels)
            else:
                pixels = ((pixels - np.min(pixels)) / pixel_range) * 255.0
            img = ImagePIL.fromarray(pixels)
            img = img.convert("L")
    else:
        if record_data["format"] == "h264":
            import av

            codec = av.CodecContext.create("h264", "r")
            packets = av.packet.Packet(bytes(record_data["data"]))
            img = codec.decode(packets)[0].to_image()
        else:
            img = ImagePIL.open(io.BytesIO(record_data["data"]))

    if max_size is not None:
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size))

    if return_bytes:
        buffered_img = io.BytesIO()
        img.save(buffered_img, format=format, **format_params)
        if reset_position:
            buffered_img.seek(0)
        return buffered_img
    else:
        return img


def get_image_from_ark_json_msg(
    record_data,
    max_size: int | None = None,
    format: str = "WEBP",
    format_params: dict = {},
    reset_position: bool = True,
):
    data = bytes(record_data["data"])
    image_format = record_data["data_format"]
    image_format_mapping = {
        42: "BayerRg10",
        44: "BayerRg12",
        43: "BayerRg16",
        41: "BayerRg8",
        31: "Bgr",
        33: "Bgra",
        51: "DepthZ16",
        21: "Grey",
        81: "H264",
        2: "Jpeg",
        1: "MotionJpeg",
        71: "Nv12",
        32: "Rgb",
        34: "Rgba",
        0: "Unset",
        27: "Uv8",
        26: "Yuv420",
        25: "Yuyv",
    }
    if image_format in image_format_mapping:
        image_format = image_format_mapping[image_format]
    else:
        raise NotImplementedError(f"Message type {image_format} not supported.")

    image_format = image_format.lower()

    if image_format == "depthz16":
        ark_img = np.frombuffer(data, dtype=np.float16)
        pixel_range = np.max(ark_img) - np.min(ark_img)

        if pixel_range != 0:
            ark_img = ((ark_img - np.min(ark_img)) / pixel_range) * 65535.0

        ark_img = ark_img.astype(np.uint16)
        data = ark_img
        image_mode = "I;16"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
    elif image_format == "grey":
        image_mode = "L"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
    elif image_format == "rgb" or image_format == "bgr":
        image_mode = "RGB"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
        if image_format == "bgr":
            b, g, r = img.split()
            img = ImagePIL.merge("RGB", (r, g, b))
    elif image_format == "rgba" or image_format == "bgra":
        image_mode = "RGBA"
        img = ImagePIL.frombuffer(
            image_mode,
            (record_data["width"], record_data["height"]),
            data,
            "raw",
            image_mode,
            0,
            1,
        )
        if image_format == "bgra":
            b, g, r, a = img.split()
            img = ImagePIL.merge("RGBA", (r, g, b, a))
    else:
        if image_format == "h264":
            import av

            codec = av.CodecContext.create("h264", "r")
            packets = av.packet.Packet(record_data.data)
            img = codec.decode(packets)[0].to_image()
            # this may not work
        elif image_format.lower() == "nv12":
            width = record_data["width"]
            height = record_data["height"]
            data = record_data["data"]
            Y_size = width * height
            UV_size = (
                Y_size // 2
            )  # There are half as many UV samples as Y samples in NV12

            # Separate Y, U, and V values
            Y = np.array(data[:Y_size], dtype=np.uint8).reshape((height, width))
            UV = np.array(data[Y_size : Y_size + UV_size], dtype=np.uint8).reshape(
                (height // 2, width)
            )

            # Deinterleave U and V components
            U = UV[:, ::2]
            V = UV[:, 1::2]

            # Up-sample U and V components to match Y's dimension
            U_upsampled = np.repeat(np.repeat(U, 2, axis=0), 2, axis=1)
            V_upsampled = np.repeat(np.repeat(V, 2, axis=0), 2, axis=1)

            # Stack the YUV components together to form the YUV image
            YUV = np.stack((Y, U_upsampled, V_upsampled), axis=-1).astype(np.uint8)

            # Convert YUV to RGB
            rgb_image = ImagePIL.fromarray(YUV, "YCbCr").convert("RGB")

            # Save image as png
            img = rgb_image
        else:
            raise NotImplementedError(
                f"Message type {image_format} not supported for image conversion."
            )

    if max_size is not None:
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size))
    buffered_img = io.BytesIO()
    img.save(buffered_img, format=format, **format_params)
    if reset_position:
        buffered_img.seek(0)
    return buffered_img
