from __future__ import annotations

from typing import TYPE_CHECKING

from bec_lib import MessageEndpoints, bec_logger, messages

logger = bec_logger.logger

if TYPE_CHECKING:
    from scihub.scibec import SciBecConnector


class SciBecMetadataHandler:
    def __init__(self, scibec_connector: SciBecConnector) -> None:
        self.scibec_connector = scibec_connector
        self._scan_status_consumer = None
        self._start_scan_subscription()
        self._file_subscription = None
        self._start_file_subscription()

    def _start_scan_subscription(self):
        self._scan_status_consumer = self.scibec_connector.connector.consumer(
            MessageEndpoints.scan_status(), cb=self._handle_scan_status, parent=self
        )
        self._scan_status_consumer.start()

    def _start_file_subscription(self):
        self._file_subscription = self.scibec_connector.connector.consumer(
            MessageEndpoints.file_content(), cb=self._handle_file_content, parent=self
        )
        self._file_subscription.start()

    @staticmethod
    def _handle_scan_status(msg, *, parent, **_kwargs) -> None:
        msg = messages.ScanStatusMessage.loads(msg.value)
        try:
            scan = parent.update_scan_status(msg)
        except Exception as exc:
            logger.exception(f"Failed to update scan status: {exc}")
            logger.warning("Failed to write to SciBec")
            return

        # if msg.content["status"] != "open":
        #     parent.update_event_data(scan)

    def update_scan_status(self, msg) -> dict:
        """
        Update the scan status in SciBec

        Args:
            msg(messages.ScanStatusMessage): The message containing the scan data

        Returns:
            dict: The updated scan data
        """
        scibec = self.scibec_connector.scibec
        if not scibec:
            return
        scibec_info = self.scibec_connector.scibec_info
        experiment_id = scibec_info["activeExperiment"]["id"]
        # session_id = scibec_info["activeSession"][0]["id"]
        # experiment_id = scibec_info["activeSession"][0]["experimentId"]
        logger.debug(f"Received new scan status {msg}")
        scan = scibec.scan.scan_controller_find(
            query_params={"filter": {"where": {"scanId": msg.content["scanID"]}}}
        ).body
        if not scan:
            info = msg.content["info"]
            dataset_number = info.get("dataset_number")
            dataset = scibec.dataset.dataset_controller_find(
                query_params={
                    "filter": {"where": {"number": dataset_number, "experimentId": experiment_id}}
                }
            ).body
            if dataset:
                dataset = dataset[0]
            else:
                dataset = scibec.dataset.dataset_controller_create(
                    body=scibec.models.Dataset(
                        **{
                            "readACL": scibec_info["activeExperiment"]["readACL"],
                            "writeACL": scibec_info["activeExperiment"]["readACL"],
                            "owner": scibec_info["activeExperiment"]["owner"],
                            "number": dataset_number,
                            "experimentId": experiment_id,
                            "name": info.get("dataset_name", ""),
                        }
                    )
                ).body

            scan_data = {
                "readACL": scibec_info["activeExperiment"]["readACL"],
                "writeACL": scibec_info["activeExperiment"]["readACL"],
                "owner": scibec_info["activeExperiment"]["owner"],
                "scanType": info.get("scan_name", ""),
                "scanId": info.get("scanID", ""),
                "queueId": info.get("queueID", ""),
                "requestId": info.get("RID", ""),
                "exitStatus": msg.content["status"],
                # "queue": info.get("stream", ""),
                "metadata": info,
                # "sessionId": session_id,
                "datasetId": dataset["id"],
                "scanNumber": info.get("scan_number", 0),
            }
            scan = scibec.scan.scan_controller_create(body=scibec.models.Scan(**scan_data)).body
            # scan = scibec.add_scan(scan_data)
        else:
            info = msg.content["info"]
            scan = scibec.scan.scan_controller_update_by_id(
                path_params={"id": scan[0]["id"]},
                body={"metadata": info, "exitStatus": msg.content["status"]},
            )
        return scan

    @staticmethod
    def _handle_file_content(msg, *, parent, **_kwargs) -> None:
        msg = messages.FileContentMessage.loads(msg.value)
        try:
            logger.debug(f"Received new file content {msg}")
            if not msg.content["data"]:
                return
            parent.update_scan_data(**msg.content)
        except Exception as exc:
            logger.exception(f"Failed to update scan data: {exc}")
            logger.warning("Failed to write to SciBec")
            return

    def update_scan_data(self, file_path: str, data: dict):
        """
        Update the scan data in SciBec

        Args:
            file_path(str): The path to the original NeXuS file
            data(dict): The scan data
        """
        scibec = self.scibec_connector.scibec
        if not scibec:
            return
        scan = scibec.scan.scan_controller_find(
            query_params={"filter": {"where": {"scanId": data["metadata"]["scanID"]}}}
        ).body
        if not scan:
            logger.warning(
                f"Could not find scan with scanID {data['metadata']['scanID']}. Cannot write scan"
                " data to SciBec."
            )
            return
        scan = scan[0]
        scibec.scan_data.scan_data_controller_create_many(
            body=scibec.models.ScanData(
                **{
                    "readACL": scan["readACL"],
                    "writeACL": scan["readACL"],
                    "owner": scan["owner"],
                    "scanId": scan["id"],
                    "filePath": file_path,
                    "data": data,
                }
            )
        )
        logger.info(f"Wrote scan data to SciBec for scanID {data['metadata']['scanID']}")

    def shutdown(self):
        """
        Shutdown the metadata handler
        """
        if self._scan_status_consumer:
            self._scan_status_consumer.shutdown()
        if self._file_subscription:
            self._file_subscription.shutdown()
