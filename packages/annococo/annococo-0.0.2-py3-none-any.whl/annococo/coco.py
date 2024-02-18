"""
COCOformatの定義は以下のURLを参照
https://cocodataset.org/#format-data
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel


class Info(BaseModel):
    """COCOformatのinfoを管理するクラス"""

    year: Optional[int] = None
    version: Optional[str] = None
    description: Optional[str] = None
    contributor: Optional[str] = None
    url: Optional[str] = None
    date_created: Optional[str] = None


class Images(BaseModel):
    """COCOformatのimagesを管理するクラス"""

    id: int
    width: int
    height: int
    file_name: str
    license: Optional[int] = None
    flickr_url: Optional[str] = None
    coco_url: Optional[str] = None
    date_captured: Optional[str] = None


class Annotations(BaseModel):
    """COCOformatのannotationsを管理するクラス"""

    id: Optional[int]
    image_id: Optional[int]
    category_id: Optional[int]
    segmentation: Optional[List[List[float]]]
    area: Optional[float]
    bbox: Optional[List[int]]
    iscrowd: Optional[Literal[0, 1]]


class Licenses(BaseModel):
    """COCOformatのlicensesを管理するクラス"""

    id: Optional[int]
    name: Optional[str]
    url: Optional[str]


class Categories(BaseModel):
    """COCOformatのcategoriesを管理するクラス"""

    id: Optional[int]
    name: Optional[str]
    supercategory: Optional[str]


class COCO:
    """COCOformatのアノテーションデータを扱うクラス"""

    def __init__(self, json_data: dict):
        self.json_data = json_data

        # COCOformatの各要素を登録
        self._info: Info = self._registry_info()
        self._images: List[Images] = self._registry_images()
        self._annotations: List[Annotations] = self._registry_annotations()
        self._licenses: List[Licenses] = self._registry_licenses()
        self._categories: List[Categories] = self._registry_categories()

    @property
    def info(self) -> dict[str, Any]:
        """infoを取得. dict[str, Any]形式に変換して返す

        Returns:
            dict[str, Any]: info
        """
        return self._info.model_dump()

    @property
    def images(self) -> List[dict[str, Any]]:
        """imagesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: images
        """
        return [image.model_dump() for image in self._images]

    @property
    def annotations(self) -> List[dict[str, Any]]:
        """annotationsを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: annotations
        """
        return [annotation.model_dump() for annotation in self._annotations]

    @property
    def licenses(self) -> List[dict[str, Any]]:
        """licensesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: licenses
        """
        return [license.model_dump() for license in self._licenses]

    @property
    def categories(self) -> List[dict[str, Any]]:
        """categoriesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: categories
        """
        return [category.model_dump() for category in self._categories]

    @classmethod
    def load(cls, json_path: Union[str, Path]) -> COCO:
        """COCOformat形式の.jsonファイルからCOCOインスタンスを生成

        Args:
            json_path (str | Path): COCOformat形式の.jsonファイル

        Returns:
            COCO: json_pathから生成したCOCOインスタンス
        """
        with open(json_path, "r") as f:
            _json_data = json.load(f)
        return cls(_json_data)

    def save(self, save_path: Union[str, Path], indent: Optional[int] = None) -> None:
        """json形式でファイル保存

        Args:
            save_path (str | Path): 保存先のパス
        """
        with open(save_path, "w") as f:
            json.dump(self.json_data, f, indent=indent)

    def _registry_info(self) -> Info:
        """COCOformatのinfoを登録

        Returns:
            Info: 登録したInfoクラス
        """
        if "info" not in self.json_data:
            return Info()
        else:
            return Info(**self.json_data["info"])

    def _registry_images(self) -> List[Images]:
        """COCOformatのimagesを登録

        Returns:
            list[Image]: 登録したImageクラスのリスト
        """
        if "images" not in self.json_data:
            return []
        else:
            return [Images(**image) for image in self.json_data["images"]]

    def _registry_annotations(self) -> List[Annotations]:
        """COCOformatのannotationsを登録

        Returns:
            list[Annotations]: 登録したAnnotationsクラスのリスト
        """
        if "annotations" not in self.json_data:
            return []
        else:
            return [Annotations(**annotation) for annotation in self.json_data["annotations"]]

    def _registry_licenses(self) -> List[Licenses]:
        """COCOformatのlicensesを登録

        Returns:
            list[Licenses]: 登録したLicensesクラスのリスト
        """
        if "licenses" not in self.json_data:
            return []
        else:
            return [Licenses(**license) for license in self.json_data["licenses"]]

    def _registry_categories(self) -> List[Categories]:
        """COCOformatのcategoriesを登録

        Returns:
            list[Categories]: 登録したCategoriesクラスのリスト
        """
        if "categories" not in self.json_data:
            return []
        else:
            return [Categories(**category) for category in self.json_data["categories"]]
