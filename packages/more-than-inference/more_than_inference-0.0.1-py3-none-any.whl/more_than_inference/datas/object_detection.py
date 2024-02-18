import base64
import builtins
import json
from typing import Any, List, Optional

import cv2
import numpy as np
from addict import Dict

from more_than_inference.protos.object_detection_pb2 import (ObjectDetectionArrayInput, ObjectDetectionBase64Input,
                                                             ObjectDetectionJsonOutput, ObjectDetectionPbOutput,
                                                             ObjectDetectionResult)
from more_than_inference.utils.serializer import BaseSerializer, ProtoSerializer


class ObjectDetectionInputSerializer(BaseSerializer):
    @property
    def image(self) -> Optional[np.ndarray]: raise NotImplementedError
    @image.setter
    def image(self, image: np.ndarray): raise NotImplementedError


class ObjectDetectionResultSerializer(BaseSerializer):
    @property
    def result(self) -> Optional[np.ndarray]: raise NotImplementedError
    @result.setter
    def result(self, value: Dict[str, Any]): raise NotImplementedError


class ObjectDetectionOutputSerializer(BaseSerializer):
    @property
    def result(self) -> Optional[np.ndarray]: raise NotImplementedError
    @result.setter
    def result(self, value: List[Dict[str, Any]]): raise NotImplementedError


class TypedObjectDetectionArrayInput(ObjectDetectionInputSerializer, metaclass=ProtoSerializer):
    _data_class = ObjectDetectionArrayInput
    _protected = ["Key", "ArrayData", "Width", "Height", "Channels"]

    Key: builtins.str
    ArrayData: builtins.bytes
    Width: builtins.int
    Height: builtins.int
    Channels: builtins.int

    @property
    def image(self) -> Optional[np.ndarray]:
        if self.ArrayData is not None:
            image = np.frombuffer(self.ArrayData, dtype=np.uint8)
            return image.reshape((self.Height, self.Width, self.Channels))
        return None

    @image.setter
    def image(self, image: np.ndarray):
        self.Height, self.Width, self.Channels = image.shape
        self.ArrayData = image.tobytes()


class TypedObjectDetectionBase64Input(ObjectDetectionInputSerializer, metaclass=ProtoSerializer):
    _data_class = ObjectDetectionBase64Input
    _protected = ["Key", "B64Data"]

    Key: builtins.str
    B64Data: builtins.str

    @property
    def image(self) -> Optional[np.ndarray]:
        if self.B64Data:
            image_data = base64.b64decode(self.B64Data)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            return image
        return None

    @image.setter
    def image(self, image: np.ndarray):
        _, buffer = cv2.imencode('.jpg', image)
        self.B64Data = base64.b64encode(buffer)


class TypedObjectDetectionJsonOutput(ObjectDetectionInputSerializer, metaclass=ProtoSerializer):
    _data_class = ObjectDetectionJsonOutput
    _protected = ["Key", "JsonData"]

    Key: builtins.str
    JsonData: builtins.str

    @property
    def image(self) -> Optional[np.ndarray]:
        json_data = json.loads(self.JsonData)
        image_b64 = json_data.get('image')
        if image_b64:
            image_data = base64.b64decode(image_b64)
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            return image
        return None

    @image.setter
    def image(self, image: np.ndarray):
        _, buffer = cv2.imencode('.jpg', image)
        image_b64 = base64.b64encode(buffer).decode('utf-8')
        json_data = json.loads(self.JsonData)
        json_data['image'] = image_b64
        self.JsonData = json.dumps(json_data)


class TypedObjectDetectionResult(ObjectDetectionResultSerializer, metaclass=ProtoSerializer):
    _data_class = ObjectDetectionResult
    _registed = {"Result": list[builtins.float]}

    Type: builtins.str
    Points: list[builtins.float]
    Confidence: builtins.float
    Label: builtins.str

    @property
    def result(self) -> Optional[np.ndarray]:
        return {
            "type": getattr(self, "Type", None),
            "points": list(getattr(self, "Points", None)),
            "confidence": getattr(self, "Confidence", None),
            "label": getattr(self, "Label", None),
        }

    @result.setter
    def result(self, value: Dict[str, Any]):
        self.Type = value.get("type", None)
        if "points" in value:
            self.Points = value.get("points")
        self.Confidence = value.get("confidence", None)
        self.Label = value.get("label", None)


class TypedObjectDetectionPbOutput(ObjectDetectionOutputSerializer, metaclass=ProtoSerializer):
    _data_class = ObjectDetectionPbOutput
    _registed = {"Result": list[TypedObjectDetectionResult]}

    Key: builtins.str
    Result: list[TypedObjectDetectionResult]

    @property
    def result(self) -> Optional[np.ndarray]:
        return {
            "key": getattr(self, "Key", None),
            "result": [i.result for i in getattr(self, "Result", [])]
        }

    @result.setter
    def result(self, value: List[Dict[str, Any]]):
        self.Key = value.get("key", None)
        self.Result = []
        for i in value.get("result", []):
            rr = TypedObjectDetectionResult()
            rr.result = i
            self.Result.append(rr)
