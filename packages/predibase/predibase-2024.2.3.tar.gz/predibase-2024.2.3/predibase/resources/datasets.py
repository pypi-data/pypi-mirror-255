from __future__ import annotations

import mimetypes
import os
from os import PathLike
from typing import TYPE_CHECKING

import requests
from google.protobuf.json_format import MessageToJson

from predibase_api.artifacts.v1.artifacts_pb2 import (
    PresignedUrlForUploadRequest,
    ARTIFACT_TYPE_DATASET,
    PresignedUrlForUploadResponse,
    RegisterUploadedFileAsDatasetRequest,
)

from predibase.resource.dataset import Dataset

if TYPE_CHECKING:
    from predibase.pql import Session


class Datasets:
    def __init__(self, session: Session):
        self._session = session

    def from_file(self, file_path: PathLike, *, name: str | None = None) -> Dataset:
        with open(file_path, "rb") as f:
            file_name = os.path.basename(file_path)
            mime_type = mimetypes.guess_type(file_path)[0] or "text/plain"

            # Get presigned url for upload
            presigned_url_req = MessageToJson(
                PresignedUrlForUploadRequest(
                    mime_type=mime_type,
                    expiry_seconds=3600,
                    artifact_type=ARTIFACT_TYPE_DATASET,
                ),
                preserving_proto_field_name=True,
            )
            resp = PresignedUrlForUploadResponse(
                **self._session.post(
                    "/datasets/get_presigned_url",
                    data=presigned_url_req,
                ),
            )

            # Unpack response data
            presigned_url = resp.url
            object_name = resp.object_name
            required_headers = resp.required_headers

            # Get required headers for presigned url upload
            headers = {"Content-Type": mime_type}
            for k, v in required_headers:
                headers[k] = v

            # Upload file to blob storage with pre-signed url
            requests.put(presigned_url, data=f, headers=headers).raise_for_status()

            # Register uploaded file as dataset
            register_dataset_req = MessageToJson(
                RegisterUploadedFileAsDatasetRequest(
                    dataset_name=name,
                    object_name=object_name,
                    file_name=file_name,
                ),
                preserving_proto_field_name=True,
            )
            resp = self._session.post("/datasets/register_uploaded_file", data=register_dataset_req)

            dataset_id = resp["id"]
            endpoint = f"/datasets/{dataset_id}"
            resp = self._session.wait_for_dataset(endpoint, until_fully_connected=True)

            from predibase.resource_util import build_dataset

            return build_dataset(resp, self._session)
