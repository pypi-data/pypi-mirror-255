import logging
import uuid
import json
import asyncio
import requests

from WebexCompassSDK.ws import websocketWrapper
from WebexCompassSDK.version import sdk_version

class WebexCompassClient:
    def __init__(self, host_address,client_id='',client_secret=''):
        self.sesssion_id = str(uuid.uuid4())
        self.client_id = client_id
        self.client_secret = client_secret

        server_parts = host_address.split(":")
        if len(server_parts) == 2:
            server = server_parts[0]
            web_port = int(server_parts[1])
        else:
            server = server_parts[0]
            web_port = int("9000")

        websocket_port = int(web_port) + 1

        self.websocket_uri = f"ws://{server}:{websocket_port}/{self.sesssion_id}?client_id={self.client_id}&client_secret={self.client_secret}&sdk_version={sdk_version}&client_type=webex-compass-sdk"
        self.upload_uri = f"http://{server}:{web_port}/upload/"

        self.websocket_connection = None
        self.started = False
        self.login_status = True
        self.ready = asyncio.Future()
        self.websocket : websocketWrapper = websocketWrapper()
        self.pending_messages = {}

    async def start(self, on_ready=None,on_broken=None):
        if self.client_id == '' or self.client_secret == '':
            raise Exception("client_id and client_secret are required")

        if self.login_status == False:
            raise Exception("Not logged in")
        if self.started == True:
            raise Exception("Already started")
        await self._do_start(on_ready=on_ready,on_broken=on_broken)
       
    async def stop(self):
        logging.info(f"stop")
        if self.started == False:
            raise Exception("Not started")
        if self.websocket_connection is None:
            raise Exception("Not connected")
        await self.websocket.disconnect()

    async def logout(self):
        pass

    '''
    Do fast anomaly check for logs file
    - download_link_or_local_file: 
          download link of the log file, jira link or controlhub link
    - local_file: local file path of the log file
            local file is expected to current_log.txt or last_run_current_log.txt
            zip file
    '''
    async def generate_anomaly_report(self,download_link_or_local_file):
        if download_link_or_local_file.startswith("http"):
            return await self._generate_anomaly_report_from_url(download_link_or_local_file)
        else:
            return await self._generate_anomaly_report_from_local_file(download_link_or_local_file)
    
    # Do deep anomaly check for given domain
    # - log_hash: hash of the log file
    # - topic: domain of the log file
    # - log_file: log file name returned by generate_anomaly_report
    async def generate_anomaly_deep_analysis_report(self,log_hash,topic,log_file):
        msg = {
            "target": "webex_agent",
            "instruction": "anomaly-deep-analysis",
            "log-hash": log_hash,
            "topic": topic,
            "log-file": log_file,
            "report-name": "anomaly-deep-analysis",
            "report-format": "json"
        }
        report = await self._send_command(msg)
        report = json.loads(report["chat-body"])
        return report

    # Do classification for given input_message
    # - input_message: input message to be classified
    async def classify_problem_report(self, input_message:str):
        msg = {
            "target": "llama_agent",
            "instruction": "classify-problem",
            "input-message": input_message,
            "report-name": "classify-problem",
            "report-format": "json"
        }
        report = await self._send_command(msg)
        report = json.loads(report["chat-body"])
        return report

    # Do fast anomaly check for all supported domains
    # - download_link: download link of the log file, jira link or controlhub link
    async def _generate_anomaly_report_from_url(self,download_link):
        msg = {
            "target": "webex_agent",
            "instruction": "anomaly-check",
            "download-link": download_link,
            "report-name": "anomaly-check",
            "report-format": "json"
        }
        report = await self._send_command(msg)
        try:
            report = json.loads(report["chat-body"])
        except Exception as e:
            logging.error(f"Error when parsing anomaly report: {e}, download_link: {download_link}")
            logging.error(f"==>     report: {report}")
            report = None
        return report

    async def _generate_anomaly_report_from_local_file(self,local_file):
        with open(local_file, 'rb') as file:
            files = {'file': (local_file, file)}

            message_id = str(uuid.uuid4())
            future = asyncio.Future()
            self.pending_messages[message_id] = future

            params = {'ws-session-id': self.sesssion_id,
                    'message-id': message_id,
                    "report-name": "anomaly-check",
                    "report-format": "json"}
            response = requests.post(self.upload_uri, files=files,data=params)
            await future
            report = future.result()
            try:
                report = json.loads(report["chat-body"])
            except Exception as e:
                logging.error(f"Error when parsing anomaly report: {e}, local_file: {local_file}")
                logging.error(f"==>     report: {report}")
                report = None
        return report

    async def _send_command(self, command):
        message_id = str(uuid.uuid4())
        command["message-id"] = message_id

        future = asyncio.Future()
        self.pending_messages[message_id] = future
        await self.websocket.send_message(json.dumps(command))
        await future
        received_message = future.result()
        return received_message
    
    async def _do_start(self,on_ready=None,on_broken=None):

        logging.info(f"_do_start to {self.websocket_uri}")
        def _on_ws_connected(websocket):
            self.websocket_connection = websocket
            self.started = True
            logging.info(f"Connected to {self.websocket_uri}")
            if on_ready:
                on_ready()
            self.ready.set_result(True)

        def _on_ws_disconnected(websocket):
            self.websocket_connection = None
            self.started = False
            logging.info(f"Disconnected to {self.websocket_uri}")
            if on_broken:
                on_broken()
            self.ready.set_result(False)

        def _on_ws_message(message):
            message = json.loads(message)
            command_id = message["message-id"]

            future = self.pending_messages.get(command_id)
            if future is None:
                logging.debug(f"Received message without a pending message: {message}")
                return
            self.pending_messages.pop(command_id)
            future.set_result(message)

        self.started = True
        await self.websocket.connect(self.websocket_uri, on_message=_on_ws_message, on_connected=_on_ws_connected, on_disconnected=_on_ws_disconnected)
