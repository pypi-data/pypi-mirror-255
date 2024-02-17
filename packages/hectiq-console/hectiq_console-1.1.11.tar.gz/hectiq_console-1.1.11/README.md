# Hectiq Console <!-- omit in toc -->

## Overview

The Hectiq Console Python Client is a comprehensive toolkit designed to interact with the Hectiq Console, a platform for managing various resources and incidents. This client provides functionalities to authenticate, manage resources, create incidents, handle files, and track metrics within the Hectiq environment.

**This service is for Hectiq's client only.**

- [Overview](#overview)
- [Middleware for API](#middleware-for-api)
  - [Installation](#installation)
  - [Starlette](#starlette)
  - [FastAPI](#fastapi)
  - [Send metrics](#send-metrics)
  - [Send annotations](#send-annotations)
- [Functional for workers](#functional-for-workers)
  - [Features](#features)
  - [Installation](#installation-1)
  - [Authentication](#authentication)
    - [Command Line Interface](#command-line-interface)
    - [Credential Storage](#credential-storage)
  - [Managing Resources](#managing-resources)
  - [Creating Incidents](#creating-incidents)
  - [File Handling](#file-handling)
  - [Metrics](#metrics)
  - [Annotations](#annotations)
  - [Timing Code Execution](#timing-code-execution)
- [Contact](#contact)

## Middleware for API

### Installation

```bash
pip install --upgrade 'hectiq-console[starlette]'
```

### Starlette 
Below is an example how to use the middleware for Starlette application. 

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from hectiq_console.starlette import HectiqConsoleStarletteMiddleware
middleware = [
    Middleware(HectiqConsoleStarletteMiddleware, 
                resource="hectiq-test")
]
app = Starlette(middleware=middleware)
```
### FastAPI

Below is an example how to use the middleware for FastAPI. It shares the same Middleware as Starlette.

```python
import time
import random
from fastapi import FastAPI, Request
from hectiq_console.starlette import HectiqConsoleStarletteMiddleware, store_metrics

app = FastAPI(title="Demo application")
app.add_middleware(HectiqConsoleStarletteMiddleware, 
                   resource="hectiq-demo",
                   include_paths=["/predict"])

@app.get("/")
async def root():
    return {"message": "🚨 This route is not monitored by the hectiq console."}

@app.get("/predict")
async def root(request: Request):
    # Store a random number
    return {"message": "✅ This route is monitored by the hectiq console."}
```

### Send metrics

By default, the middleware stores the latency and counts of the monitored requests. You may add other metrics using the `store_metrics` in a request handler.

```python
@app.get("/predict")
async def root(request: Request):
    store_metrics(request=request, key=metrics_key, value=metrics_value)
```
You can send as many metrics in the same request as you want. However, if you use the same key in the same request, the previous value is overwritten by the new one.

> Do not forget to create the metrics definition in the console beforehand. Otherwise, you'll get an error at handshake.

### Send annotations

Annotations are useful to track predictions in your application. For example, you may want to track the result of a model. Use the method `store_annotation`. You can send as many annotations as you want in the same request.

```python
@app.get("/predict")
async def root(request: Request):
    store_annotation(request=request, 
                        inputs={"y": [0,1,2,3,4], "x": [0,1,2,3,4]}, 
                        outputs={"y_true": [5,6,7,8], "y_pred": [5,6,7,8]}, 
                        label="high-accuracy",
                        metadata={"model": "demo-model", 
                                "accuracy": 0.89})
```

## Functional for workers


### Features

- **Authentication**: Securely authenticate with the Hectiq Console using API keys.
- **Resource Management**: Set and retrieve resources within the Hectiq Console.
- **Incident Management**: Create incidents with detailed descriptions and associated files.
- **File Handling**: Add files to resources and upload them to the Hectiq Console.
- **Metrics Tracking**: Add and manage metrics for resources.
- **Annotation Downloading**: Download annotations related to resources.
- **Code Timing**: Utilize a context manager to time code execution and add metrics to a resource.

### Installation

To use this client, ensure you have Python installed on your system. Install the package via pip:

```bash
pip install hectiq-console
```


### Authentication

#### Command Line Interface
Some requests require authentification. Run the CLI tool to authenticate:

```bash
hectiq-console authenticate
```

You'll be prompted to enter your email and password. The CLI tool will automatically generate and store a new API key for you. These steps are described below:

1. **Login**: Enter your email and password.
2. **API Key Alias**: Set an alias for your new API key. The default is your hostname.
3. **Select Organization**: Choose from the list of organizations associated with your account.
4. **API Key Generation**: Automatically generates and stores a new API key.

API Keys are associated with an organization. If you have access to multiple organizations, you will be prompted to select an organization. If you only have access to one organization, the CLI tool will automatically select it for you. 

Once you have a valid API key in the credentials file (or environment variable), you can use the client to make authenticated requests. If you have multiple organizations in your credentials file, you can switch organization using the `set_organization` method.

```python
import hectiq_console.functional as hc
hc.set_resource("demo-resource")
hc.set_organization("hectiq-ai") # Required if you have multiple organizations
is_logged = hc.authenticate() 
```

#### Credential Storage

The API key is stored locally in the `~/.hectiq-console/credentials.toml` file. This file is created if it does not exist. If you need to change the default location, you can set the `HECTIQ_CONSOLE_CREDENTIALS_FILE` environment variable to the path of your choice. 

You can also set the `HECTIQ_CONSOLE_API_KEY` environment variable to your API key. This variable is used by the client to authenticate requests. If the environment variable is set, the client will not use the credentials file.


### Managing Resources

Set your resource using the `set_resource` method. Place this method at the beginning of your script. It uses a ContextVar to store the resource. Therefore, you can use it in a multi-threaded environment. If you set the resource, it will be used for all requests. Otherwise, you'll need to specify the resource in each request.

```python
import hectiq_console.functional as hc
hc.set_resource("resource_id")
```

### Creating Incidents

Create incidents related to a resource:

```python
import hectiq_console.functional as hc
hc.create_incident(title="Incident Title", description="Detailed description")
```

You can also add files to the incident:

```python
import hectiq_console.functional as hc
hc.create_incident(title="Incident Title", 
                    description="Detailed description", 
                    filenames=["path/to/your/file"])
```

### File Handling

Add and upload files to a resource:

```python
import hectiq_console.functional as hc
hc.add_file("path/to/your/file")
```

### Metrics

Add metrics to a resource:

```python
import hectiq_console.functional as hc
hc.add_metrics(name="metric_name", value=123)
```

### Annotations
Download annotations related to a resource:

```python
import hectiq_console.functional as hc
annotation = hc.download_annotation("annotation_id")
```

### Timing Code Execution

Time a block of code execution:

```python
import hectiq_console.functional as hc
with hc.timer_context("timer_name"):
    # Your code here
    pass
```
The timer name is used as the metric name. The timer context manager automatically adds the metric to the resource. 

## Contact

For support or inquiries, please contact the project maintainer at [info@hectiq.ai].





