#!/usr/bin/env python3

import importlib
import json
import os
import sys
import threading
from pathlib import Path
from queue import Queue

import dill
import requests

from lambchop.datastructures import Task
from lambchop.server import Server


class Worker:
    def __init__(self, q: Queue):
        self.q = q

    def _deserialize(self, msg: bytes) -> Task:
        msg = json.loads(msg)
        msg = bytes.fromhex(msg)
        msg = dill.loads(msg)
        return msg

    def get_fun(self, task: Task) -> None:
        f = Path(task.file)
        sys.path.append(str(f.parent))
        module = importlib.import_module(f.stem)
        return getattr(module, task.func)

    def execute(self, task: Task):
        func = self.get_fun(task)
        args = task.args
        kwargs = task.kwargs
        return func(*args, **kwargs)

    def run(self):
        print("Worker running", flush=True)
        while True:
            if not self.q.empty():
                print("Task in q, executing ...", flush=True)
                task = self.q.get()
                task = self._deserialize(task)
                self.execute(task)


class LambdaExtension(Server):
    def __init__(self, name, port=1956):
        self.port = port
        super().__init__(self.port)
        self.name = name
        self.agent_id = None

        self.rt_api_address = os.environ["AWS_LAMBDA_RUNTIME_API"]
        self.rt_api_url = f"http://{self.rt_api_address}/2020-01-01/extension"
        self.logs_api_base_url = f"http://{self.rt_api_address}/2020-08-15"
        self.headers = {}

        self.register()

    def _handler_error(self, r, msg):
        print(msg, flush=True)
        print(f"Status: {r.status_code}", flush=True)
        print(f"Response: {r.text}", flush=True)
        sys.exit(1)

    def register(self):
        """Register the extension with the Lambda runtime API

        Its required to register the extension with the Lambda runtime API before it can be used.
        """
        print("Registering Extension", flush=True)
        URL = f"{self.rt_api_url}/register"
        headers = {
            "Lambda-Extension-Name": self.name,
            "Content-Type": "application/json",
        }
        body = {"events": ["INVOKE", "SHUTDOWN"]}
        try:
            r = requests.post(URL, headers=headers, json=body)

            if r.status_code != 200:
                self._handler_error(r, "Failed to register to extention")

            self.agent_id = r.headers.get("Lambda-Extension-Identifier")
            self.headers = {
                "Lambda-Extension-Identifier": self.agent_id,
                "Content-Type": "application/json",
            }
            return self.agent_id
        except Exception as e:
            raise Exception(f"Failed to register to extention") from e

    def get_event(self):
        """Get the next event from the Lambda runtime API

        The Lambda runtime API will send an event to the extension when there
        is a new invocation or the Lambda runtime is shutting down.
        """
        URL = f"{self.rt_api_url}/event/next"
        r = requests.get(URL, headers=self.headers)
        if r.status_code != 200:
            self._handler_error(r, "Failed to get event.")
        return r.json()

    def subscribe_to_runtime_api(self):
        # https://docs.aws.amazon.com/lambda/latest/dg/runtimes-api.html
        pass

    def subscibe_to_logs(self):
        print(f"Subscribing to Logs API on {self.logs_api_base_url}")
        URL = f"{self.logs_api_base_url}/logs"
        body = {
            "destination": {
                "protocol": "HTTP",
                "URI": f"http://sandbox:{self.port}/logs",
            },
            "types": ["platform", "function"],
            "buffering": {"timeoutMs": 1000, "maxBytes": 262144, "maxItems": 10000},
        }
        r = requests.put(URL, json=body, headers=self.headers)
        if r.status_code != 200:
            self._handler_error(r, "Failed to subscribe to logs.")

        print("Subscribed to Logs API")
        print(r.text)

    def run(self):
        print(f"Starting thread for HTTP job server...", flush=True)

        s_thread = threading.Thread(target=self.serve)
        s_thread.start()

        while True:
            event = self.get_event()
            if event["eventType"] == "SHUTDOWN":
                print("Received SHUTDOWN event. Exiting.", flush=True)
                sys.exit(0)

            while s_thread.is_alive():
                if len(self.q) > 0:
                    print("joining thread", flush=True)
                    t = self.q.pop()
                    t.join()


def main():
    print("Starting Extension", flush=True)
    name = os.path.basename(__file__)
    extension = LambdaExtension(name=name)
    extension.run()


if __name__ == "__main__":
    main()
