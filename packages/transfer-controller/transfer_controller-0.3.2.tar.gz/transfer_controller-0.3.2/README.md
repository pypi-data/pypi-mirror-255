# Transfer Controller

A Python module for orchestrating asynchronous operations.

## Introduction

`transfer_controller` allows you to submit sequences of operations to be executed asynchronously by another process. It manages the sequencing and provides synchronization mechanisms to ensure the proper ordering of operation execution. Moreover, the module also handles responses, offering an easy-to-use mechanism to wait for sequence completions.

Asynchronous programming, especially with multiple devices or services, often leads to what developers call "callback hell" – a situation where callbacks are nested within callbacks, leading to code that is hard to read, maintain, or debug. With `transfer_controller`, this is no longer a concern. By providing an elegant way to sequence operations and handle responses, it allows for clearer code structures, freeing you from the spaghetti code that sometimes arises with asynchronous handling.

A pivotal aspect of the transfer_controller is its reliance on IDs to match operation requests with their corresponding operation responses. This ID-based mechanism ensures that each asynchronous operation can be tracked effectively. For the module to work optimally, the downstream mechanism, such as a device or service you're communicating with, must provide a means based on these IDs to correlate operation requests with operation responses.

Imagine that you have a robotic arm assembly controlled by a series of USB-connected devices, and each device requires a series of commands to execute its functions. In such a case, the coordination of these commands becomes critical. Some devices may need to wait for others to complete their tasks before beginning theirs, while some commands might be sent concurrently to improve efficiency. With `transfer_controller`, you can sequence these operations, ensuring that the robotic arm functions seamlessly, without being mired in layers of callbacks. Another use case could be an intricate LED light show controlled by multiple USB devices. Each LED device needs to flash or change color in a specific order to produce the desired effects. With the help of `transfer_controller`, you can manage these operations, letting you focus on the creativity of the light show, rather than getting lost in the intricacies of callback management.

## Features

- Threaded execution of function sequences.
- Synchronization locks to ensure ordered execution.
- Response management with callback functions.
- Supports waiting for a specific sequence or all sequences to complete.

## Installation

To install the `transfer_controller` module:

```bash
pip install transfer_controller
```

## Usage

The `transfer_controller` is designed to execute sequences of functions asynchronously with external devices, such as USB devices, that respond asynchronously. Below, we provide a usage guide focusing on sending operations to a USB device:

### Basic Initialization:

```python
from transfer_controller import TransferController

# An example ID generator function:
def id_gen():
    i = 0
    while True:
        i += 1
        yield i

# Create a TransferController instance
controller = TransferController(id_gen())
```

### Interfacing with USB Device:

Imagine having a USB device that allows you to send commands (or operations) containing a unique ID and a payload. In return, the device processes this data and sends back a response asynchronously. 

Here's a simplistic representation of interfacing with such a device:

```python
class USBDevice:
    def __init__(self):
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def send_operation(self, transfer_id, payload):
        # Code to send data to the USB device...
        pass

    def _internal_listener_for_responses(self, response):
        # This function listens for the USB device responses and calls the callback when received
        if self.callback:
            self.callback(response)
```

To use the `transfer_controller` with the `USBDevice`, you'll set up as:

```python
usb_device = USBDevice()

def usb_callback(response):
    controller.handle_response(transfer_id=response['id'], response=response)

usb_device.set_callback(usb_callback)
```

### Submitting Operations:

1. **Single Operation Submission**:

   Send a single operation to the USB device:

   ```python
   def send_single_operation(transfer_id):
       usb_device.send_operation(transfer_id, f"Payload{transfer_id}")

   seq_id = controller.submit(send_single_operation)
   ```

2. **Sequence Submission**:

   To send a series of operations:

   ```python
   def operation_1(transfer_id):
      usb_device.send_operation(transfer_id, "Payload1")

   def operation_2(transfer_id):
      usb_device.send_operation(transfer_id, "Payload2")

   def operation_3(transfer_id):
      usb_device.send_operation(transfer_id, "Payload3")

   seq_id = controller.submit(sequence=[operation_1, operation_2, operation_3])
   ```

3. **Handling Results**:
   
   Once sequences of operations are completed and the corresponding responses are received from the USB device, you might want to process or display these results. The `on_ready` callback function allows you to define how you want to handle the responses once they're ready. In this example, the `print_result` function prints the responses for `operation_1` and `operation_2`:

   ```python
   def print_result(responses):
       print(responses['operation_1'])
       print(responses['operation_2'])

   controller.submit(
     sequence=[operation_1, operation_2],
     on_ready=print_result
   )  
   ```

   When both operations complete and their responses are received, the `print_result` function is triggered, printing the results to the console.

4. **Chaining Sequences**:

   In some cases, you might want to execute a new sequence of operations only after a previous sequence has fully completed. The `wait_for` parameter helps you establish this dependency. Here, `seq2` is only executed once all the operations in `seq1` have been processed and their responses received:

   ```python
   seq1 = controller.submit(
     sequence=[operation_1, operation_2, operation_3],
     on_ready=print_result_seq1
   )

   seq2 = controller.submit(
     wait_for=seq1,
     sequence=[operation_4, operation_5],
     on_ready=print_result_seq2
   )
   ```

   `print_result_seq1` and `print_result_seq2` are callback functions that handle the results of their respective sequences. This chaining mechanism ensures that `operation_4` and `operation_5` are only sent to the USB device after `operation_1`, `operation_2`, and `operation_3` have completed and their responses have been received and processed.

### Waiting for Responses:

- **Wait for a Specific Operation's Response**:

  If you want to wait for a specific operation to get a response:

  ```python
  controller.wait_for(seq_id)
  ```

- **Wait for All Responses**:

  If you wish to wait for all submitted operations to receive their responses:

  ```python
  controller.wait_for_all()
  ```

### Callbacks and Responses:

The controller provides mechanisms to handle asynchronous responses from the USB device. As demonstrated in the `usb_callback`, when a response is received from the device, it's provided to the controller for appropriate handling.

### Error Handling

When submitting a sequence to the controller, the user can provide a callback function for custom error handling. This can be done through the `on_error` parameter. When an exception occurs during the execution of a sequence of functions, the functiong provided in `on_error` is invoked with two argument, a list of responses collected before the error and the exception object:

  ```python
  def handle_error(responses, error):
    print("Error occurred:", error)
    print("Responses received before error:", responses)
    
  controller.submit(sequence=sequence, on_error=handle_error)
  ```
This allows not only for custom error handling but also for graceful termination of the process.