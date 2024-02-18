from apis.inference.v1 import open_inference_pb2 as _open_inference_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InferImageRequest(_message.Message):
    __slots__ = ("model_name", "model_version", "id", "image", "image_url", "option")
    class ImageScale(_message.Message):
        __slots__ = ("image_height", "image_width", "max_image_size", "image_size_unit")
        IMAGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
        IMAGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
        MAX_IMAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
        IMAGE_SIZE_UNIT_FIELD_NUMBER: _ClassVar[int]
        image_height: int
        image_width: int
        max_image_size: int
        image_size_unit: int
        def __init__(self, image_height: _Optional[int] = ..., image_width: _Optional[int] = ..., max_image_size: _Optional[int] = ..., image_size_unit: _Optional[int] = ...) -> None: ...
    class InferImageOption(_message.Message):
        __slots__ = ("scale", "use_cv2_color", "normalization")
        SCALE_FIELD_NUMBER: _ClassVar[int]
        USE_CV2_COLOR_FIELD_NUMBER: _ClassVar[int]
        NORMALIZATION_FIELD_NUMBER: _ClassVar[int]
        scale: InferImageRequest.ImageScale
        use_cv2_color: bool
        normalization: bool
        def __init__(self, scale: _Optional[_Union[InferImageRequest.ImageScale, _Mapping]] = ..., use_cv2_color: bool = ..., normalization: bool = ...) -> None: ...
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    OPTION_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    model_version: str
    id: str
    image: bytes
    image_url: str
    option: InferImageRequest.InferImageOption
    def __init__(self, model_name: _Optional[str] = ..., model_version: _Optional[str] = ..., id: _Optional[str] = ..., image: _Optional[bytes] = ..., image_url: _Optional[str] = ..., option: _Optional[_Union[InferImageRequest.InferImageOption, _Mapping]] = ...) -> None: ...

class InferImageResponse(_message.Message):
    __slots__ = ("model_response", "input_image_height", "input_image_width")
    MODEL_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    INPUT_IMAGE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INPUT_IMAGE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    model_response: _open_inference_pb2.ModelInferResponse
    input_image_height: int
    input_image_width: int
    def __init__(self, model_response: _Optional[_Union[_open_inference_pb2.ModelInferResponse, _Mapping]] = ..., input_image_height: _Optional[int] = ..., input_image_width: _Optional[int] = ...) -> None: ...
