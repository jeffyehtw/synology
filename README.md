# Syno - Synology Download Station API Wrapper

A Python wrapper for the Synology Download Station API, providing a simple interface to manage download tasks.

## Structure

```
syno/
├── api.py      # Main API entry point (Syno class)
├── base.py     # Base authentication and API info
├── ds.py       # Download Station module
└── task.py     # Task management operations
```

## Classes

### `Syno` (api.py)

Main entry point for interacting with Synology Download Station. It inherits from `BaseTorrentClient` and provides a unified interface for torrent operations.

**Methods:**
- `login()` - Manually login (if not using context manager)
- `logout()` - Manually logout
- `list_tasks()` - List all tasks
- `create_task(uri=None, file=None, destination=None)` - Create a new download task
- `delete_tasks(tasks)` - Delete tasks by ID
- `resume_tasks(tasks)` - Resume paused tasks
- `pause_tasks(tasks)` - Pause active tasks

**Usage:**
```python
from syno.api import Syno

with Syno(ip='192.168.0.100', port='5000', account='user', password='pass') as syno:
    tasks = syno.list_tasks()
    for task in tasks:
        print(task['title'])
```

### `Base` (base.py)

Handles authentication and basic API operations.

**Methods:**
- `info(query='ALL')` - Get API information
- `auth(account, password, fmt='cookie', opt_code=None)` - Authenticate and get session ID
- `logout()` - Logout from the session

### `DS` (ds.py)

Download Station module that provides access to task operations.

**Attributes:**
- `task` - Task management instance

### `Task` (task.py)

Manages download tasks on Synology Download Station.

**Methods:**
- `list(offset=0, limit=-1)` - List all tasks with details
- `info(tasks)` - Get information about specific tasks
- `create(uri, file, unzip_password=None, destination=None)` - Create a new download task
- `delete(tasks, force_complete=False)` - Delete tasks
- `pause(tasks)` - Pause tasks
- `resume(tasks, destination=None)` - Resume tasks

## Example Usage

### List All Tasks

```python
from syno.api import Syno

with Syno(ip='192.168.0.100', port='5000', account='user', password='pass') as syno:
    tasks = syno.list_tasks()

    for task in tasks:
        print(f"ID: {task['id']}")
        print(f"Title: {task['title']}")
        print(f"Status: {task['status']}")
        print(f"Size: {task['size']} bytes")
        print('---')
```

### Delete Tasks

```python
from syno.api import Syno

task_ids = ['dbid_12345', 'dbid_67890']

with Syno(ip='192.168.0.100', port='5000', account='user', password='pass') as syno:
    syno.delete_tasks(tasks=task_ids)
```

### Resume Tasks

```python
from syno.api import Syno

task_ids = ['dbid_12345']

with Syno(ip='192.168.0.100', port='5000', account='user', password='pass') as syno:
    syno.resume_tasks(tasks=task_ids)
```

## Task Object Structure

When calling `task.list()`, each task object contains:

```python
{
    'id': 'dbid_12345',
    'title': 'Example.File.Name',
    'status': 'downloading',  # or 'waiting', 'seeding', 'error', etc.
    'size': 1234567890,
    'type': 'bt',
    'username': 'user',
    'additional': {
        'detail': {
            'completed_time': 1234567890,
            'connected_leechers': 5,
            'connected_seeders': 10,
            'create_time': 1234567890,
            'destination': 'home/Download',
            'started_time': 1234567890,
            'uri': '12345.torrent',
            # ... more fields
        },
        'transfer': {
            'downloaded_pieces': 100,
            'size_downloaded': 123456789,
            'size_uploaded': 12345678,
            'speed_download': 1024000,
            'speed_upload': 102400
        }
    }
}
```

## Configuration

The submodule expects credentials to be passed explicitly during initialization. An example configuration (`syno.json.example`) is provided in the project root:

```json
{
    "ip": "192.168.1.100",
    "port": "5000",
    "account": "your-account",
    "password": "your-password"
}
```

The wrapper uses context managers for automatic session management. Authentication is handled automatically when entering the context.

## Error Handling

The wrapper will exit if authentication fails. Make sure to provide valid credentials.

## Dependencies

- `requests` - For HTTP API calls
- `logging` - For debug logging
