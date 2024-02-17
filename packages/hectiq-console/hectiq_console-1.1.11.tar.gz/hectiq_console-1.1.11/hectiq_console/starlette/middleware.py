import json
import time
import re
import requests
from typing import Optional, List, Dict
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask

from hectiq_console import CONSOLE_APP_URL

def response_callback(ressource: str,
                 path: Optional[str] = None,
                 latency: Optional[float] = None,
                 metrics: Optional[dict] = None,
                 annotations: Optional[List[dict]] = None):
    """This method is executed by the HectiqConsoleStarletteMiddleware when the response is sent to the client.
    You should not call this method directly. Instead, use the store_metrics and store_annotation methods.
    """
    headers = {
    }
    body = {
        "path": path,
        "latency": latency,
        "metrics": []
    }
    if metrics is not None:
        body["metrics"] = [{"name": key, "value": value} for key, value in metrics.items()]
    
    if annotations is not None:
        for annot in annotations:
            annot.get("metadata", {})["request_latency"] = latency
            annot.get("metadata", {})["request_path"] = path
    body["annotations"] = annotations

    url = f"{CONSOLE_APP_URL}/app/sender-client/{ressource}/on-request-completed"
    try:
        requests.post(url, data=json.dumps(body, default=str), headers=headers)
    except:
        # If the request fails, we do not want to crash the application
        pass

def send_heartbeat(ressource: str):
    """This method is executed by the HectiqConsoleStarletteMiddleware.
    You should not call this method directly.
    Instead, use the store_metrics and store_annotation methods.
    """
    headers = {
        "content-type": 'application/x-www-form-urlencoded'
    }
    body = {
    }
    url = f"{CONSOLE_APP_URL}/app/sender-client/{ressource}/heartbeat"
    try:
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 200:
            print(f"✅ Heartbeat succesful with the hectiq console. Your ressource {ressource} is monitored.")
        else:
            print(f"❌ Heartbeat failed with the hectiq console. Your ressource {ressource} is not monitored.")
    except:
        # If the request fails, we do not want to crash the application
        pass

class HectiqConsoleStarletteMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sends metrics to the hectiq console.

    Arguments:
        ressource: The ressource name
        secret_key: The secret key of the ressource
        include_paths: A list of routes to include in the metrics. If None, all routes are included (except the ones in exclude_paths). 
            If specified, only the routes in include_paths are included.
        exclude_paths: A list of routes to exclude from the metrics. If None, all routes are included.
            Example: exclude_paths=["/docs", "/openapi.json"]. You can also use wildcard, for example:
            exclude_paths=["/docs", r"/app/ressources/*/metrics"]
        default_config: A dict of default configuration. 
    """
    def __init__(self, app, 
                 ressource: str, 
                 include_paths: Optional[List] = None,
                 exclude_paths: Optional[List] = None,
                 config: Optional[dict] = {},
                 skip_heartbeat: Optional[bool] = False):
        super().__init__(app)
        self._ressource = ressource
        self.include_paths = include_paths
        self.exclude_paths = exclude_paths
        self.config = config or {}
        if not skip_heartbeat:
            send_heartbeat(ressource=ressource)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        request.state.hconsole_config = {k:v for k,v in self.config.items()}
        request.state.hconsole_metrics = {}
        request.state.hconsole_annotations = []

        # Include paths
        if self.include_paths is not None:
            for include_path in self.include_paths:
                if include_path == path or re.match(include_path, path):
                    break
            else:
                return await call_next(request)
            
        # Exclude paths
        if self.exclude_paths is not None:
            for exclude_path in self.exclude_paths:
                if exclude_path == path or re.match(exclude_path, path):
                    return await call_next(request)
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        if request.state.hconsole_config.get("latency_alias"):
            key = request.state.hconsole_config.get("latency_alias")
            if isinstance(key, str):
                request.state.hconsole_metrics[key] = process_time
            elif isinstance(key, list):
                for k in key:
                    request.state.hconsole_metrics[k] = process_time
                    
        if request.state.hconsole_config.get("call_alias"):
            key = request.state.hconsole_config.get("call_alias")
            if isinstance(key, str):
                request.state.hconsole_metrics[key] = 1
            elif isinstance(key, list):
                for k in key:
                    request.state.hconsole_metrics[k] = 1

        response.background = BackgroundTask(response_callback, 
                                             latency=process_time, 
                                             metrics=request.state.hconsole_metrics, 
                                             annotations=request.state.hconsole_annotations, 
                                             path=request.url.path,
                                             ressource=self._ressource)
        return response
    
def store_metrics(request: Request, key: str, value: float):
    """
    Store a metrics in the state of the request
    Should use ContextVar in future releases (remove request params).
    """
    if hasattr(request.state, "hconsole_metrics"):
        request.state.hconsole_metrics[key] = value

def update_config(request: Request, key: str, value: any):
    """
    Update the config in the state of the request.
    """
    if hasattr(request.state, "hconsole_config"):
        request.state.hconsole_config[key] = value

def store_annotation(request: Request, 
                     id: Optional[str] = None, 
                    inputs: Optional[Dict] = None,
                    outputs: Optional[Dict] = None,
                    metadata: Optional[Dict] = None,
                    labels: Optional[List[str]] = None):
    """Store an annotation.

    Params:
        request: The request object (Starlette)
        id: The id of the annotation. If None, the application will assign an unique id.
            We enforce that ids are unique for a given ressource. If you assign the id, then
            you may refer to this annotation id and ressource for updates.
        inputs: Any inputs that you want to store with the annotation. This field is typically the 
            input payload for the model. It must be JSON serializable.
        outputs: Any outputs that you want to store with the annotation. This field is typically the 
            prediction of the model. It must be JSON serializable.
        metadata: Any metadata that you want to store with the annotation. This field is typically the 
            metadata of the model or of the dataset. It must be JSON serializable.
        labels: A list of labels for the annotation. This field is typically the labels of the model.
    """
    if hasattr(request.state, "hconsole_annotations"):
        annotation = {
            "id": id,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": metadata,
            "labels": labels
        }
        request.state.hconsole_annotations.append(annotation)
    