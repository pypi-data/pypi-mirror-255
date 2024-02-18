from cast_ai.se.constants import PROD_BUCKET, GCP_AUTH_CMD

from datetime import datetime, timezone, timedelta
from google.cloud.storage import Client
from google.cloud.exceptions import Forbidden

import subprocess
import json
import logging
import os


class SnapshotController:
    def __init__(self, cast_api_key: str, default_cluster_id: str, json_key_path: str):
        self._logger = logging.getLogger(__name__)
        self._api_key = cast_api_key
        self._cluster_id = default_cluster_id
        self._json_key_path = json_key_path
        self.raw_snapshot = None
        self._storage_client = None
        if os.path.isfile(self._json_key_path):
            self._storage_client = Client.from_service_account_json(self._json_key_path)
        self._get_raw_snapshot()

    def _is_json_key_auth_sufficient(self) -> bool:
        if self._storage_client:
            try:
                list(self._storage_client.list_blobs(bucket_or_name=PROD_BUCKET,
                                                     max_results=1,
                                                     prefix=self._cluster_id))
                return True
            except Forbidden:
                self._logger.warning("Authenticated using specified key file, but access denied.")
            except Exception as e:
                self._logger.error(f"Error trying to authenticate using json: {e}")
        else:
            return False

    def _authenticate_via_gcloud(self):
        try:
            subprocess.check_output(GCP_AUTH_CMD, text=True, shell=True)
            self._check_bucket_access()
            return
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Error running gcloud auth application-default login: {e}")
        except Forbidden:
            self._logger.error("Authenticated using gcloud, but access denied.")
        except Exception as e:
            self._logger.critical(f"Error trying to authenticate via gcloud: {e}")
        raise RuntimeError("Error during gcloud authentication")

    def _already_authenticated(self) -> bool:
        try:
            self._check_bucket_access()
            return True
        except Forbidden:
            self._logger.error("Assumed Authenticated,...but access denied")
        except Exception as e:
            self._logger.critical(f"Error trying to list buckets when assuming already authenticated: {e}")
        return False

    def _check_bucket_access(self):
        self._storage_client = Client()
        list(self._storage_client.list_blobs(bucket_or_name=PROD_BUCKET,
                                             max_results=1,
                                             prefix=self._cluster_id))

    def _gcp_authenticate(self):
        if self._already_authenticated():
            return
        if not self._is_json_key_auth_sufficient():
            self._authenticate_via_gcloud()

    def _get_snapshot_prefix(self):
        current_utc_time = datetime.now(timezone.utc)
        previous_minute_time = current_utc_time - timedelta(minutes=1)
        formatted_previous_minute_time = previous_minute_time.strftime("%Y-%m-%dT%H:%M")
        prefix = f"{self._cluster_id}/{formatted_previous_minute_time}"
        return prefix

    def _get_raw_snapshot(self) -> None:
        self._gcp_authenticate()
        prefix = self._get_snapshot_prefix()
        blobs = list(self._storage_client.list_blobs(bucket_or_name=PROD_BUCKET, max_results=3, prefix=prefix))
        if not len(blobs):
            self._logger.error("No snapshots found for current time")
            raise RuntimeError("No snapshots found for current time")
        blob = blobs[-1]
        self.raw_snapshot = json.loads(blob.download_as_bytes().decode('utf-8'))
