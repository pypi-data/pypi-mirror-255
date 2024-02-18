import threading
from ..utils.system_message import SystemMessage, SystemOpcode, SystemModules
from ..commands.definitions import *

class UsbReceiver:
    '''
    This class represents the process/service responsible for receiving USB HID
    INTERRUPT IN transfers, sent by the USB Host Adapter.
    When a new transfer is received, its associated via ID to a request response,
    it is processed accordingly and sent to the Supernova callback.

    Attributes
    ----------
    usbHostAdapter: hid usbHostAdapter
        This is the instance of the USB port.
    endpointSize: int
        Number that identifies the size of the IN ENDPOINT.
        usbHostAdapters based on MCU LPC5536 are USB Full Speed usbHostAdapters and the size is 64.
        usbHostAdapters based on MCU LPC55S16 are USB High Speed usbHostAdapters and the size is 1024.
    '''
    def __init__(self, usbHostAdapter, endpointSize):
        self.thread = threading.Thread(target = self.main, name='USB Receiver', daemon=True)
        self.usbHostAdapter = usbHostAdapter
        self.endpointSize = endpointSize
        self.responsesMap = {}
        self.onEventCallback = None
        self.run = False
        # Auxiliary notification for the UART read
        self.uart_receive_notification = UartControllerReceiveHighLevelNotification_t()
        # Auxiliary notification for I3C transfers in target mode
        self.i3c_target_notification = I3cTargetHighLevelNotification_t()

    def start(self):
        '''
        This function starts the Thread target function.
        '''
        self.run = True
        self.thread.start()

    def setOnEventCallback(self, callback) -> None:
        """
        This function sets the USB receiver callback function.
        """
        self.onEventCallback = callback
        
    def endProcess(self) -> None:
        """
        This function ends the USB receiver process 
        """
        self.run = False

    def addTransactionResponse(self,id,response):
        """
        This function associates a response type to the transaction ID
        """
        self.responsesMap[id] = response
    
    def main(self):
        """
        This function is the Thread target function.
        """
        while self.run == True:
            try:
                # Block for 100 ms to wait for a new message receive in the USB port from the Supernova.
                usbHostAdapterMessage = bytes(self.usbHostAdapter.read(self.endpointSize, 100))

                # If the Supernova sent a new message, process it.
                if usbHostAdapterMessage:
                    # Send message received from the USB Host to the Supernova.
                    self.send_to_callback(usbHostAdapterMessage)
                    
            except OSError:     # This exception is raised from self.usbHostAdapter.read when the Supernova is removed.
                # Create a custom error.
                error = SystemMessage(SystemModules.SYSTEM, SystemOpcode.UNEXPECTED_DISCONNECTION, f"Error {SystemOpcode.UNEXPECTED_DISCONNECTION.name}: Unexpected Supernova disconnection.")
                # Notify to the Supernova.
                self.onEventCallback(None, error)
                # Kill process
                self.run = False

    def send_to_callback(self, usbHostAdapterMessage):
        """
        This function identifies the response type given the transaction ID 
        and creates the associated response to invoke the Supernova Callback
        """
        # Get command id to search the response in the transfers map.
        id = (usbHostAdapterMessage[ID_LSB_INDEX] | usbHostAdapterMessage[ID_MSB_INDEX] << 8)

        # Look for the receiver of the message.
        command = usbHostAdapterMessage[COMMAND_CODE_INDEX]

        # Check if the message command exists in the dictionary command.
        if command in COMMANDS_DICTIONARY.keys():

            # Check if the message from the USB Host Adapter corresponds to a request from the USB Host.
            if COMMANDS_DICTIONARY[command]["type"] == CommandType.REQUEST_RESPONSE:

                # Get response from response map with the id.
                response = self.responsesMap.get(id)
                
                if response is not None:
                    isComplete = response.set(usbHostAdapterMessage)
                    if isComplete:
                        # Invoke callback
                        self.onEventCallback(response.toDictionary(), None)
                        self.responsesMap.pop(id, None)
                else:
                    # TODO: Raise an Unexpected response exception or similar.
                    pass

            # If the message is a notification
            elif COMMANDS_DICTIONARY[command]["type"] == CommandType.NOTIFICATION:

                # Identify what notification it is.
                if command == I3C_IBI_NOTIFICATION:
                    ibiType = usbHostAdapterMessage[IBI_TYPE_INDEX]

                    if ibiType == I3cIbiType.IBI_NORMAL.value:
                        response = I3cIbiNotification_t.from_buffer_copy(usbHostAdapterMessage)
                    else:
                        response = I3cHotJoinIbiNotification_t.from_buffer_copy(usbHostAdapterMessage)

                    # Invoke callback
                    self.onEventCallback(response.toDictionary(), None)

                # Check if its a UART read notification
                elif command == UART_CONTROLLER_RECEIVE_NOTIFICATION:
                    isComplete = self.uart_receive_notification.set(usbHostAdapterMessage)
                    if isComplete:
                        # Invoke callback
                        self.onEventCallback(self.uart_receive_notification.toDictionary(), None)
                        # Delete previous notification
                        self.uart_receive_notification = UartControllerReceiveHighLevelNotification_t()
                elif (command == I3C_TARGET_NOTIFICATION):
                    isComplete = self.i3c_target_notification.set(usbHostAdapterMessage)
                    if isComplete:
                        # Invoke callback
                        self.onEventCallback(self.i3c_target_notification.toDictionary(), None)
                        # Delete previous notification
                        self.i3c_target_notification = I3cTargetHighLevelNotification_t()

                else:
                    # TODO: Raise a "command not supported exception" or similar.
                    pass

        # If the command doesn't exist in the command dictionary.
        else:
            # TODO: Raise a "command not supported exception" or similar.
            pass
