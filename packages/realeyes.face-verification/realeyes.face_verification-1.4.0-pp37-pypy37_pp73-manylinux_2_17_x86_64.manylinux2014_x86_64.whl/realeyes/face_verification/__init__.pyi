"""Realeyes C++ SDK bindings for Python"""
from __future__ import annotations
import typing
import numpy
import numpy.typing


class BoundingBox():
    """
    Bounding Box class for the faces
    """
    def __init__(self, x: int, y: int, width: int, height: int) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def height(self) -> int:
        """
        Height of the bounding box in pixels.
        """

    @height.setter
    def height(self, arg0: int) -> None:
        """
        Height of the bounding box in pixels.
        """

    @property
    def width(self) -> int:
        """
        Width of the bounding box in pixels.
        """

    @width.setter
    def width(self, arg0: int) -> None:
        """
        Width of the bounding box in pixels.
        """

    @property
    def x(self) -> int:
        """
        x coordinate of the top-left corner.
        """

    @x.setter
    def x(self, arg0: int) -> None:
        """
        x coordinate of the top-left corner.
        """

    @property
    def y(self) -> int:
        """
        y coordinate of the top-left corner.
        """

    @y.setter
    def y(self, arg0: int) -> None:
        """
        y coordinate of the top-left corner.
        """


class Point2d():
    """
    Point2d class
    """

    def __init__(self, x: float, y: float) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def x(self) -> float:
        """
        x coordinate of the point
        """

    @x.setter
    def x(self, arg0: float) -> None:
        """
        x coordinate of the point
        """

    @property
    def y(self) -> float:
        """
        y coordinate of the point
        """

    @y.setter
    def y(self, arg0: float) -> None:
        """
        y coordinate of the point
        """


class Face():
    """
    Face Class
    """
    def __init__(self, image: numpy.typing.NDArray[numpy.uint8], landmarks: typing.List[Point2d],
                 bbox: BoundingBox = BoundingBox(x=0, y=0, width=0, height=0), confidence: float = 0.0) -> None: ...

    def __repr__(self) -> str: ...

    def bounding_box(self) -> BoundingBox:
        """
        Returns the bounding box of the detected face.
        """

    def confidence(self) -> float:
        """
        Returns the confidence value of the detected face.
        """

    def landmarks(self) -> list[Point2d]:
        """
        Returns the landmarks of the detected face.
        """


class FaceVerifier():
    """
    The Face Verifier class
    """

    def __init__(self, model_file: str, max_concurrency: int = 0) -> None: ...

    def __repr__(self) -> str: ...

    def detect_faces(self, image: numpy.typing.NDArray[numpy.uint8]) -> typing.List[Face]:
        """
        Detects the faces on an image.

            image: image to detect faces on, it needs to be in RGB format [h x w x c]
        """

    def embed_face(self, face: Face) -> typing.List[float]:
        """
        Returns the embedding of the detected face.

            face: face object to create the embedding for
        """

    def compare_faces(self, embedding1: typing.List[float], embedding2: typing.List[float]) -> Match:
        """
        Compares the embeddings of two faces.

            embedding1: 1st embedding to compare
            embedding2: 2nd mebedding to compare
        """

    def get_model_name(self) -> str:
        """
        Returns the name (version etc) of the loaded model.
        """


class Match():
    """
    Face match class
    """
    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def similarity(self) -> float:
        """
        Similarity of the faces
        """

    @similarity.setter
    def similarity(self, arg0: float) -> None:
        """
        Similarity of the faces
        """


def get_sdk_version_string() -> str:
    """
    Returns the version string of the SDK (and not the model)
    """
