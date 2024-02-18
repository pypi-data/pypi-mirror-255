"""
COCOformatの定義は以下のURLを参照
https://cocodataset.org/#format-data
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel


class Info(BaseModel):
    year: int | None = None
    version: str | None = None
    description: str | None = None
    contributor: str | None = None
    url: str | None = None
    date_created: datetime | None = None


class Images(BaseModel):
    id: int
    width: int
    height: int
    file_name: str
    license: int | None = None
    flickr_url: str | None = None
    coco_url: str | None = None
    date_captured: datetime | None = None


class Annotations(BaseModel):
    id: int | None
    image_id: int | None
    category_id: int | None
    segmentation: list[list[float]] | None
    area: float | None
    bbox: list[int] | None
    iscrowd: Literal[0, 1] | None


class Licenses(BaseModel):
    id: int | None
    name: str | None
    url: str | None


class Categories(BaseModel):
    id: int | None
    name: str | None
    supercategory: str | None


class COCO:
    """COCOformatのアノテーションデータを扱うクラス"""

    def __init__(self, json_data: dict):
        self.json_data = json_data

        self._info: Info = self._registry_info()
        self._images: list[Images] = self._registry_images()
        self._annotations: list[Annotations] = self._registry_annotations()
        self._licenses: list[Licenses] = self._registry_licenses()
        self._categories: list[Categories] = self._registry_categories()

    @property
    def info(self) -> dict[str, Any]:
        """infoを取得. dict[str, Any]形式に変換して返す

        Returns:
            dict[str, Any]: info
        """
        return self._info.model_dump()

    @property
    def images(self) -> list[dict[str, Any]]:
        """imagesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: images
        """
        return [image.model_dump() for image in self._images]

    @property
    def annotations(self) -> list[dict[str, Any]]:
        """annotationsを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: annotations
        """
        return [annotation.model_dump() for annotation in self._annotations]

    @property
    def licenses(self) -> list[dict[str, Any]]:
        """licensesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: licenses
        """
        return [license.model_dump() for license in self._licenses]

    @property
    def categories(self) -> list[dict[str, Any]]:
        """categoriesを取得. list[dict[str, Any]]形式に変換して返す

        Returns:
            list[dict[str, Any]]: categories
        """
        return [category.model_dump() for category in self._categories]

    @classmethod
    def load(cls, json_path: str | Path) -> COCO:
        """COCOformat形式の.jsonファイルからCOCOインスタンスを生成

        Args:
            json_path (str | Path): COCOformat形式の.jsonファイル

        Returns:
            COCO: json_pathから生成したCOCOインスタンス
        """
        with open(json_path, "r") as f:
            _json_data = json.load(f)
        return cls(_json_data)

    def save(self, save_path: str | Path, indent: int | None = None) -> None:
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
        if "info" in self.json_data:
            return Info()
        else:
            return Info(**self.json_data["info"])

    def _registry_images(self) -> list[Images]:
        """COCOformatのimagesを登録

        Returns:
            list[Image]: 登録したImageクラスのリスト
        """
        if "images" not in self.json_data:
            return []
        else:
            return [Images(**image) for image in self.json_data["images"]]

    def _registry_annotations(self) -> list[Annotations]:
        """COCOformatのannotationsを登録

        Returns:
            list[Annotations]: 登録したAnnotationsクラスのリスト
        """
        if "annotations" not in self.json_data:
            return []
        else:
            return [Annotations(**annotation) for annotation in self.json_data["annotations"]]

    def _registry_licenses(self) -> list[Licenses]:
        """COCOformatのlicensesを登録

        Returns:
            list[Licenses]: 登録したLicensesクラスのリスト
        """
        if "licenses" not in self.json_data:
            return []
        else:
            return [Licenses(**license) for license in self.json_data["licenses"]]

    def _registry_categories(self) -> list[Categories]:
        """COCOformatのcategoriesを登録

        Returns:
            list[Categories]: 登録したCategoriesクラスのリスト
        """
        if "categories" not in self.json_data:
            return []
        else:
            return [Categories(**category) for category in self.json_data["categories"]]
