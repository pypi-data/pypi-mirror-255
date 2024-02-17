from flask_appbuilder import expose
from .decorators import has_access_gcp
from flask import send_file
from superset import event_logger
from superset.views.base import BaseSupersetView

from google.cloud import storage

GCP_BUCKET = ''

class GCPFilesView(BaseSupersetView):
    @event_logger.log_this
    @has_access_gcp
    @expose("/gcp/<filePath>",methods=["GET"])
    def downloadFile(self,oppId,fileName):
        service_account_json = {}
        storage_client=storage.Client.from_service_account_info(service_account_json)
        bucket = storage_client.bucket(GCP_BUCKET)
        blob = bucket.blob(f"{oppId}/{fileName}")
        blob.download_to_filename(f"/tmp/{fileName}")
        return send_file(f"/tmp/{fileName}",attachment_filename=fileName)






