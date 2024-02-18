# SupernovaSDK: Python SDK for Binho Supernova USB Host Adapter

SupernovaSDK is a Python package that facilitates seamless interaction with the innovative Supernova USB host adapter developed by Binho. Designed to simplify device orchestration during embedded system development and testing, the Supernova host adapter enhances hardware control for developers and engineers.

The SupernovaSDK currently supports I2C and I3C protocols, allowing effortless communication with I2C and I3C devices as the host adapter acts as a controller device.

# Prerequisites

Before installing and using the SupernovaSDK, please ensure your system meets the following requirements:

- Python 3.6 or higher.
- Windows, MacOS or Linux operating systems.
- Binho Supernova USB host adapter with up-to-date firmware.

# Installation From PyPi

For the most recent update of the BinhoSupernova Python package on PyPi, follow these steps:

1. Open your terminal or command prompt.

3. Use pip to install the SupernovaSDK:

```sh
pip install BinhoSupernova
```

Now, the SupernovaSDK is installed and ready to be used in your Python projects. You can import and use it as shown in the usage example.

# Installation From the Git Repository

Remember to activate your virtual environment (if you're using one) before running the installation command.

To install the SupernovaSDK from your local file system, follow these steps:

1. Download the SupernovaSDK package.

2. Extract the downloaded package to a folder on your local file system.

3. Open a terminal or command prompt and navigate to the folder containing the extracted SupernovaSDK.

4. Install the SDK using pip with the local file path:

```sh
pip install .
```

**Note**: Make sure to include the period (.) at the end, indicating the current directory.

Now, the SupernovaSDK is installed and ready to be used in your Python projects. You can import and use it as shown in the usage example.

# Basic Usage Example

This example showcases how to use the Supernova SDK with a Supernova device. Since the Supernova operates in a non-blocking manner, each method of the SDK sends a command to the host adapter and immediately receives an SUCCESS or error message. The actual command response is provided through a callback function.

```python
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import *

# Initialize and open a Supernova object for communication with the Supernova device
supernova = Supernova()
supernova.open()

# Define a callback function to handle command responses from the Supernova device
def callback_function(supernova_message: dict, system_message: dict) -> None:
    print(f"Transaction ID: {supernova_message['id']}")
    print(f"Command Code: {supernova_message['command']}")
    print(f"Command Name: {supernova_message['name']}")
    print(f"Message Length: {supernova_message['length']}")
    print(f"Message Content: {supernova_message['message']}")

# Register the callback function to link with Supernova events
supernova.onEvent(callback_function)

# Define a transaction ID to match the command request with its response
transaction_id = 0

# Send a request for the manufacturer's string from a connected USB device (non-blocking)
# The response will be handled by the registered callback
request_result = supernova.getUsbString(transaction_id, GetUsbStringSubCommand.MANUFACTURER)
# E.g., request_result: {'type': 'request_validation_result', 'id': 0, 'command': 96, 'code value': 0, 'code name': 'SUCCESS', 'message': 'GET USB STRING requests success'}
```

# Advanced Usage Example

The following code demonstrates how to make sequential calls to the host adapter using the Supernova SDK. Sequential calls require triggering a new call after the response of the previous call has been received. This is achieved by using a threading Event and a shared list to synchronize the calls and share the result between the callback function and the decorated method.

The code includes a decorator function sequential_call, which surrounds the Supernova method call with `call_event.clear()` and `call_event.wait()` calls. The `sequential_call`` decorator ensures that each method call waits for the response from the previous call before proceeding.

```python
from BinhoSupernova.Supernova import Supernova
from BinhoSupernova.commands.definitions import *
import threading

# Initialize and open a Supernova object for communication with the Supernova device
supernova = Supernova()
supernova.open()

# Define a callback function to handle command responses from the Supernova device
def callback_function(supernova_message: dict, system_message: dict) -> None:
    shared_result[0] = supernova_message # Store the result in the shared list
    call_event.set() # Signal that the response has been received

# Register the callback function to link with Supernova events
supernova.onEvent(callback_function)

# Define a threading Event to control the synchronization between calls
call_event = threading.Event()

# Shared list to store the result
shared_result = [None]

# Decorator function to handle synchronization around the Supernova method call
def sequential_call(method):
    def wrapper(*args, **kwargs):
        call_event.clear() # Reset the event
        method(*args, **kwargs)
        call_event.wait() # Wait for the callback to signal that the response has been received
        return shared_result[0] # Return the result stored by the callback
    return wrapper

# Make sequential calls to the host adapter, using the decorator for synchronization
@sequential_call
def get_manufacturer_string(transaction_id):
    return supernova.getUsbString(transaction_id, GetUsbStringSubCommand.MANUFACTURER)

@sequential_call
def get_product_name_string(transaction_id):
    return supernova.getUsbString(transaction_id, GetUsbStringSubCommand.PRODUCT_NAME)

@sequential_call
def get_serial_number_string(transaction_id):
    return supernova.getUsbString(transaction_id, GetUsbStringSubCommand.SERIAL_NUMBER)

@sequential_call
def get_fw_version_string(transaction_id):
    return supernova.getUsbString(transaction_id, GetUsbStringSubCommand.FW_VERSION)

@sequential_call
def get_hw_version_string(transaction_id):
    return supernova.getUsbString(transaction_id, GetUsbStringSubCommand.HW_VERSION)

manufacturer = get_manufacturer_string(0)
product_name = get_product_name_string(0)
serial_number = get_serial_number_string(0)
fw_version = get_fw_version_string(0)
hw_version = get_hw_version_string(0)

print(manufacturer)
print(product_name)
print(serial_number)
print(fw_version)
print(hw_version)
```

# More Examples

For additional examples and detailed use cases, please refer to the `Examples/Notebooks` folder in the repository. This folder contains various Jupyter Notebooks with hands-on demonstrations and tutorials for working with the Supernova SDK, including:

- **I2C-Protocol-Supernova-API.ipynb:** Tutorial on the I2C protocol with Supernova API.
- **I3C-Protocol-Supernova-API.ipynb:** Comprehensive tutorial on I3C Protocol with Supernova API.
