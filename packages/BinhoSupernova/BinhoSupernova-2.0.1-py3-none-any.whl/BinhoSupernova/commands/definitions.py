from enum import Enum
from ctypes import *

#================================================================================#
# USB ENDPOINT
#================================================================================#
ENDPOINT_ID                             = 0x00
INTERRUPT_IN_ENDPOINT_SIZE              = 64

ID_LSB_INDEX                            = 0
ID_MSB_INDEX                            = 1
COMMAND_CODE_INDEX                      = 2                                      # Constant that identify the position of the command code in the bytes stream.

#================================================================================#
# COMMANDs CODE
#
# Constants definition that represents the USB commands code.
#================================================================================#

# I3C commands
I3C_CONTROLLER_INIT                     = 0x01
I3C_INIT_BUS                            = 0x02
I3C_GET_TARGET_DEVICE_TABLE             = 0x03
I3C_SET_TARGET_DEVICE_CONFIG            = 0x04
I3C_CHANGE_DA                           = 0x05
I3C_GET_ADD_CHANGE_RESULT               = 0x06      # Not used
I3C_CLEAR_FEATURE                       = 0x07
I3C_SET_FEATURE                         = 0x08
I3C_GET_CAPABILITY                      = 0x09
I3C_GET_BUFFER_AVAILABLE                = 0x0A      # Not used
I3C_TRANSFER                            = 0x0B
I3C_IBI_NOTIFICATION                    = 0x0C
I3C_TARGET_INIT                         = 0x10
I3C_TARGET_SET_CONFIGURATION            = 0x11
I3C_TARGET_WRITE_MEMORY                 = 0x12
I3C_TARGET_READ_MEMORY                  = 0x13
I3C_TARGET_NOTIFICATION                 = 0x14

# I2C commands
I2C_SET_PARAMETERS                      = 0x21
I2C_WRITE                               = 0x22
I2C_READ                                = 0x23
I2C_WRITE_RS                            = 0x24
I2C_READ_RS                             = 0x25
I2C_WRITE_NO_STOP                       = 0x26
I2C_READ_FROM                           = 0x27

# SPI commands
SPI_CONTROLLER_INIT						= 0x31
SPI_CONTROLLER_SET_PARAMETERS 			= 0x32
SPI_CONTROLLER_TRANSFER 				= 0x33

# UART Commands
UART_CONTROLLER_INIT 				    = 0x41
UART_CONTROLLER_SET_PARAMETERS 		    = 0x42
UART_CONTROLLER_SEND 				    = 0x43
UART_CONTROLLER_RECEIVE_NOTIFICATION    = 0x44

# SYS commands
GET_USB_STRING 					        = 0x60
SET_I3C_BUS_VOLTAGE					    = 0x61
RESET_DEVICE					        = 0x62
ENTER_BOOT_MODE					        = 0x63
SET_I2C_SPI_UART_BUS_VOLTAGE            = 0x64

#================================================================================#
# Target mode related definitions
#================================================================================#
I3C_TARGET_MEMORY_LENGTH    = 1024

#================================================================================#
# COMMAND TYPE
#
# The commands can be sorted depending the type of their behavior. There are commands
# that are sent form the USB Host application to the Supernova device as a request,
# and wait for a response. There other commands tha tare sent asynchronous by the Supernova
# as notifications, without a previous request.
#================================================================================#

class CommandType(Enum):
    REQUEST_RESPONSE = 0
    NOTIFICATION     = 1

#================================================================================#
# COMMANDs DICTIONARY
#
# Python dictionary that holds the commands code as the key with the command name
# and the type of command that it is.
#================================================================================#

COMMANDS_DICTIONARY = {
    I2C_SET_PARAMETERS                   : {"name": "I2C SET PARAMETERS",                "type": CommandType.REQUEST_RESPONSE},
    I2C_WRITE                            : {"name": "I2C WRITE",                         "type": CommandType.REQUEST_RESPONSE},
    I2C_READ                             : {"name": "I2C READ",                          "type": CommandType.REQUEST_RESPONSE},
    I2C_WRITE_RS                         : {"name": "I2C WRITE WITH R-START",            "type": CommandType.REQUEST_RESPONSE},
    I2C_READ_RS                          : {"name": "I2C READ WITH R-START",             "type": CommandType.REQUEST_RESPONSE},
    I2C_WRITE_NO_STOP                    : {"name": "I2C WRITE WITHOUT STOP",            "type": CommandType.REQUEST_RESPONSE},
    I2C_READ_FROM                        : {"name": "I2C READ FROM",                     "type": CommandType.REQUEST_RESPONSE},
    I3C_CLEAR_FEATURE                    : {"name": "I3C CLEAR FEATURE",                 "type": CommandType.REQUEST_RESPONSE},
    I3C_SET_FEATURE                      : {"name": "I3C SET FEATURE",                   "type": CommandType.REQUEST_RESPONSE},
    I3C_GET_CAPABILITY                   : {"name": "I3C GET CAPABILITY",                "type": CommandType.REQUEST_RESPONSE},
    I3C_INIT_BUS                         : {"name": "I3C INIT BUS",                      "type": CommandType.REQUEST_RESPONSE},
    I3C_CONTROLLER_INIT                  : {"name": "I3C CONTROLLER INIT",               "type": CommandType.REQUEST_RESPONSE},
    I3C_GET_TARGET_DEVICE_TABLE          : {"name": "I3C GET TARGET DEVICE TABLE",       "type": CommandType.REQUEST_RESPONSE},
    I3C_SET_TARGET_DEVICE_CONFIG         : {"name": "I3C SET TARGET DEVICE CONFIG",      "type": CommandType.REQUEST_RESPONSE},
    I3C_CHANGE_DA                        : {"name": "I3C CHANGE DA",                     "type": CommandType.REQUEST_RESPONSE},
    I3C_GET_ADD_CHANGE_RESULT            : {"name": "I3C GET ADD CHANGE RESULT",         "type": CommandType.REQUEST_RESPONSE},
    I3C_GET_BUFFER_AVAILABLE             : {"name": "I3C GET BUFFER AVAILABLE",          "type": CommandType.REQUEST_RESPONSE},
    I3C_TRANSFER                         : {"name": "I3C TRANSFER",                      "type": CommandType.REQUEST_RESPONSE},
    I3C_IBI_NOTIFICATION                 : {"name": "I3C IBI NOTIFICATION",              "type": CommandType.NOTIFICATION},
    I3C_TARGET_INIT                      : {"name": "I3C TARGET INIT",                   "type": CommandType.REQUEST_RESPONSE},
    I3C_TARGET_SET_CONFIGURATION         : {"name": "I3C TARGET SET CONFIGURATION",      "type": CommandType.REQUEST_RESPONSE},
    I3C_TARGET_WRITE_MEMORY              : {"name": "I3C TARGET WRITE MEMORY",           "type": CommandType.REQUEST_RESPONSE},
    I3C_TARGET_READ_MEMORY               : {"name": "I3C TARGET READ MEMORY",            "type": CommandType.REQUEST_RESPONSE},
    I3C_TARGET_NOTIFICATION              : {"name": "I3C TARGET NOTIFICATION",           "type": CommandType.NOTIFICATION},
    SPI_CONTROLLER_INIT                  : {"name": "SPI CONTROLLER INIT",               "type": CommandType.REQUEST_RESPONSE},
    SPI_CONTROLLER_SET_PARAMETERS        : {"name": "SPI CONTROLLER SET PARAMETERS",     "type": CommandType.REQUEST_RESPONSE},
    SPI_CONTROLLER_TRANSFER              : {"name": "SPI CONTROLLER TRANSFER",           "type": CommandType.REQUEST_RESPONSE},
    UART_CONTROLLER_INIT                 : {"name": "UART CONTROLLER INIT",              "type": CommandType.REQUEST_RESPONSE},
    UART_CONTROLLER_SET_PARAMETERS       : {"name": " UART CONTROLLER SET PARAMETERS",   "type": CommandType.REQUEST_RESPONSE},
    UART_CONTROLLER_SEND                 : {"name": " UART CONTROLLER SEND MESSAGE",     "type": CommandType.REQUEST_RESPONSE},
    UART_CONTROLLER_RECEIVE_NOTIFICATION : {"name": " UART CONTROLLER RECEIVE MESSAGE",  "type": CommandType.NOTIFICATION},
    GET_USB_STRING 					     : {"name": "GET USB STRING",                    "type": CommandType.REQUEST_RESPONSE},
	SET_I3C_BUS_VOLTAGE				     : {"name": "SET I3C BUS VOLTAGE",               "type": CommandType.REQUEST_RESPONSE},
	RESET_DEVICE					     : {"name": "RESET DEVICE",                      "type": CommandType.REQUEST_RESPONSE},
	ENTER_BOOT_MODE	    				 : {"name": "ENTER BOOT MODE",                   "type": CommandType.REQUEST_RESPONSE},
    SET_I2C_SPI_UART_BUS_VOLTAGE         : {"name": "SET I2C-SPI-UART BUS VOLTAGE",      "type": CommandType.REQUEST_RESPONSE}
}

#================================================================================#
# ERROR STATUS
#
# Result for every command
#================================================================================#

class UsbCommandResponseStatus(Enum):
    '''
    This enum identifies different response status
    CMD_SUCCESSFUL: The command was successfully requested to the corresponding module manager
    CMD_DESTINATARY_BUSY: The destinatary module could not receive the command because it was busy
    CMD_NOT_AVAILABLE: The command does not belong to the list of available commands
    '''
    CMD_SUCCESSFUL          = 0x00
    CMD_DESTINATARY_BUSY    = 0x01  
    CMD_NOT_AVAILABLE       = 0x02

class ErrorStatus_t(Structure):
    _fields_ = [("usbErrorStatus", c_uint8),
                ("mgrErrorStatus", c_uint8 ),
                ("driverErrorStatus", c_uint16)]
    
#================================================================================#
# GET USB STRING COMMAND
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
GET_USB_STRING_REQ_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
GET_USB_STRING_REQ_HEADER_LENGTH	    = 4
GET_USB_STRING_REQ_PAYLOAD_LENGTH	    = GET_USB_STRING_REQ_LENGTH - GET_USB_STRING_REQ_HEADER_LENGTH

# Union array
GetUsbStringRequestArray_t              = c_uint8 * (GET_USB_STRING_REQ_LENGTH + 1)                         # Command length + endpoint ID.

# Union structure
class GetUsbStringRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("subCmd", c_uint8),
                ("reserved", c_uint8 * GET_USB_STRING_REQ_PAYLOAD_LENGTH)]

# Union command
class GetUsbStringRequest_t(Union):
    _fields_ = [("data", GetUsbStringRequestArray_t ),
                ("fields", GetUsbStringRequestFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"]
        }

# Response --------------------------------------------------------------------- #

# Constants
GET_USB_STRING_RES_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
GET_USB_STRING_RES_HEADER_LENGTH	    = 4
GET_USB_STRING_RES_PAYLOAD_LENGTH	    = GET_USB_STRING_RES_LENGTH - GET_USB_STRING_RES_HEADER_LENGTH

# Union array
GetUsbStringResponseArray_t             = c_uint8 * GET_USB_STRING_RES_LENGTH

# Union structure
class GetUsbStringResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("length", c_uint8),                                    # String length.
                ("data", c_uint8 * GET_USB_STRING_RES_PAYLOAD_LENGTH)]

# Union command
class GetUsbStringResponse_t(Union):
    _fields_ = [("data", GetUsbStringResponseArray_t ),
                ("fields", GetUsbStringResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a buffer object
        '''
        self.data = GetUsbStringResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:

        length = self.fields.length - 1
        data = str(self.fields.data,encoding='ascii')[:length]

        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'length' : length,
            'message' : data
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Enums ------------------------------------------------------------------------ #

class GetUsbStringSubCommand(Enum):
    '''
    Enum that represents the USB Descriptors that can be retrieved by GET USB STRING
    command. The values assigned match the string indexes in the string descriptor.
    '''
    MANUFACTURER    = 0x01
    PRODUCT_NAME    = 0X02
    SERIAL_NUMBER   = 0x03
    FW_VERSION      = 0x04
    HW_VERSION      = 0x05
    BL_VERSION      = 0x06

#================================================================================#
# SET I3C BUS VOLTAGE COMMAND
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SET_I3C_BUS_VOLT_REQ_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
SET_I3C_BUS_VOLT_REQ_HEADER_LENGHT	    = 3
SET_I3C_BUS_VOLT_REQ_PAYLOAD_LENGHT     = 2
SET_I3C_BUS_VOLT_REQ_UNUSED_LENGTH      = (SET_I3C_BUS_VOLT_REQ_LENGTH - SET_I3C_BUS_VOLT_REQ_HEADER_LENGHT - SET_I3C_BUS_VOLT_REQ_PAYLOAD_LENGHT)

# Union array
SetI3cBusVoltRequestArray_t             = c_uint8 * (SET_I3C_BUS_VOLT_REQ_LENGTH + 1)                         # Command length + endpoint ID.

# Union structure
class SetI3cBusVoltRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
		        ("i3cBusVoltage" , c_uint16 ),
                ("unusedData", c_uint8 * SET_I3C_BUS_VOLT_REQ_UNUSED_LENGTH)]

# Union command
class SetI3cBusVoltRequest_t(Union):
    _fields_ = [("data", SetI3cBusVoltRequestArray_t ),
                ("fields", SetI3cBusVoltRequestFields_t)]

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'i3cBusVoltage' : self.fields.i3cBusVoltage
        }
# Response --------------------------------------------------------------------- #

# Constants
SET_I3C_BUS_VOLT_RES_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
SET_I3C_BUS_VOLT_RES_HEADER_LENGTH	    = 3
SET_I3C_BUS_VOLT_RES_PAYLOAD_LENGTH	    = 1
SET_I3C_BUS_VOLT_RES_UNUSED_LENGTH	    = (SET_I3C_BUS_VOLT_RES_LENGTH - SET_I3C_BUS_VOLT_RES_HEADER_LENGTH - SET_I3C_BUS_VOLT_RES_PAYLOAD_LENGTH)

# Union array
SetI3cBusVoltResponseArray_t            = c_uint8 * SET_I3C_BUS_VOLT_RES_LENGTH

# Union structure
class SetI3cBusVoltResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("unusedData", c_uint8 * SET_I3C_BUS_VOLT_RES_UNUSED_LENGTH)]

# Union command
class SetI3cBusVoltResponse_t(Union):

    _fields_ = [("data", SetI3cBusVoltResponseArray_t ),
                ("fields", SetI3cBusVoltResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a buffer object
        '''
        self.data = SetI3cBusVoltResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : self.fields.result
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Enums ------------------------------------------------------------------------ #

class i3cBusVoltMode(Enum):
    '''
    Enum that represents the i3c Bus voltage mode
    '''
    I3C_LOW_VOLTAGE         = 0x00
    I3C_STANDARD_VOLTAGE    = 0X01

#================================================================================#
# RESET DEVICE
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SYS_RESET_DEVICE_REQ_LENGTH		        = INTERRUPT_IN_ENDPOINT_SIZE
SYS_RESET_DEVICE_REQ_HEADER_LENGTH	    = 3
SYS_RESET_DEVICE_REQ_UNUSED_LENGTH	    = SYS_RESET_DEVICE_REQ_LENGTH - SYS_RESET_DEVICE_REQ_HEADER_LENGTH

# Union array
SysResetDeviceRequestArray_t          = c_uint8 * (SYS_RESET_DEVICE_REQ_LENGTH + 1)                     # Command length + endpoint ID.

# Union structure
class SysResetDeviceRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("unused", c_uint8 * SYS_RESET_DEVICE_REQ_UNUSED_LENGTH )]

# Union command
class SysResetDeviceRequest_t(Union):
    _fields_ = [("data", SysResetDeviceRequestArray_t ),
                ("fields", SysResetDeviceRequestFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"]
        }

#================================================================================#
# ENTER BOOT MODE
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SYS_ENTER_BOOT_MODE_REQ_LENGTH		        = INTERRUPT_IN_ENDPOINT_SIZE
SYS_ENTER_BOOT_MODE_REQ_HEADER_LENGTH	    = 3
SYS_ENTER_BOOT_MODE_REQ_UNUSED_LENGTH	    = SYS_ENTER_BOOT_MODE_REQ_LENGTH - SYS_ENTER_BOOT_MODE_REQ_HEADER_LENGTH

# Union array
SysEnterBootModeRequestArray_t          = c_uint8 * (SYS_ENTER_BOOT_MODE_REQ_LENGTH + 1)                     # Command length + endpoint ID.

# Union structure
class SysEnterBootModeRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("unused", c_uint8 * SYS_ENTER_BOOT_MODE_REQ_UNUSED_LENGTH )]

# Union command
class SysEnterBootModeRequest_t(Union):
    _fields_ = [("data", SysEnterBootModeRequestArray_t ),
                ("fields", SysEnterBootModeRequestFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"]
        }

#================================================================================#
# SET I2C_SPI_UART BUS VOLTAGE COMMAND
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SET_I2C_SPI_UART_BUS_VOLT_REQ_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
SET_I2C_SPI_UART_BUS_VOLT_REQ_HEADER_LENGHT	        = 3
SET_I2C_SPI_UART_BUS_VOLT_REQ_PAYLOAD_LENGHT        = 2
SET_I2C_SPI_UART_BUS_VOLT_REQ_UNUSED_LENGTH         = (SET_I2C_SPI_UART_BUS_VOLT_REQ_LENGTH - SET_I2C_SPI_UART_BUS_VOLT_REQ_HEADER_LENGHT - SET_I2C_SPI_UART_BUS_VOLT_REQ_PAYLOAD_LENGHT)

# Union array
SetI2cSpiUartBusVoltRequestArray_t                  = c_uint8 * (SET_I2C_SPI_UART_BUS_VOLT_REQ_LENGTH + 1)                         # Command length + endpoint ID.

# Union structure
class SetI2cSpiUartBusVoltRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
		        ("i2cSpiUartBusVolt" , c_uint16 ),
                ("unused", c_uint8 * SET_I2C_SPI_UART_BUS_VOLT_REQ_UNUSED_LENGTH)]

# Union command
class SetI2cSpiUartBusVoltRequest_t(Union):
    _fields_ = [("data", SetI2cSpiUartBusVoltRequestArray_t ),
                ("fields", SetI2cSpiUartBusVoltRequestFields_t)]

# Response --------------------------------------------------------------------- #

# Constants
SET_I2C_SPI_UART_BUS_VOLT_RES_LENGTH			    = INTERRUPT_IN_ENDPOINT_SIZE
SET_I2C_SPI_UART_BUS_VOLT_RES_HEADER_LENGTH	        = 3
SET_I2C_SPI_UART_BUS_VOLT_RES_PAYLOAD_LENGTH	    = 1
SET_I2C_SPI_UART_BUS_VOLT_RES_UNUSED_LENGTH	        = (SET_I2C_SPI_UART_BUS_VOLT_RES_LENGTH - SET_I2C_SPI_UART_BUS_VOLT_RES_HEADER_LENGTH - SET_I2C_SPI_UART_BUS_VOLT_RES_PAYLOAD_LENGTH)

# Union array
SetI2cSpiUartBusVoltResponseArray_t                 = c_uint8 * SET_I2C_SPI_UART_BUS_VOLT_RES_LENGTH

# Union structure
class SetI2cSpiUartBusVoltResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("unused", c_uint8 * SET_I2C_SPI_UART_BUS_VOLT_RES_UNUSED_LENGTH)]

# Union command
class SetI2cSpiUartBusVoltResponse_t(Union):

    _fields_ = [("data", SetI2cSpiUartBusVoltResponseArray_t ),
                ("fields", SetI2cSpiUartBusVoltResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a buffer object
        '''
        self.data = SetI2cSpiUartBusVoltResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
            return {
                'id': self.fields.id,
                'command' : self.fields.cmd,
                'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
                'result' : self.fields.result
            }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I2C SET PARAMETERs
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
I2C_SET_PARAMS_REQ_LENGTH		        = INTERRUPT_IN_ENDPOINT_SIZE
I2C_SET_PARAMS_REQ_HEADER_LENGTH	    = 7
I2C_SET_PARAMS_REQ_PAYLOAD_LENGTH	    = I2C_SET_PARAMS_REQ_LENGTH - I2C_SET_PARAMS_REQ_HEADER_LENGTH

# Union array
I2cSetParametersRequestArray_t          = c_uint8 * (I2C_SET_PARAMS_REQ_LENGTH + 1)                     # Command length + endpoint ID.

# Union structure
class I2cSetParametersRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("anyValue1", c_uint8),
                ("cancelCurrentI2cTransfer", c_uint8),
                ("setBaudrate", c_uint8),
                ("i2cDivider", c_uint8),
                ("anyValue2", c_uint8 * I2C_SET_PARAMS_REQ_PAYLOAD_LENGTH)]

# Union command
class I2cSetParametersRequest_t(Union):
    _fields_ = [("data", I2cSetParametersRequestArray_t ),
                ("fields", I2cSetParametersRequestFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'cancelTranfer' : self.fields.cancelCurrentI2cTransfer,
            'baudrate' : self.fields.setBaudrate
        }

# Response --------------------------------------------------------------------- #

# Constants
I2C_SET_PARAMS_RES_LENGTH		        = INTERRUPT_IN_ENDPOINT_SIZE
I2C_SET_PARAMS_RES_HEADER_LENGTH	    = 7
I2C_SET_PARAMS_RES_PAYLOAD_LENGTH	    = I2C_SET_PARAMS_RES_LENGTH - I2C_SET_PARAMS_RES_HEADER_LENGTH

# Union array
I2cSetParametersResponseArray_t          = c_uint8 * (I2C_SET_PARAMS_RES_LENGTH)

# Union structure
class I2cSetParametersResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("cmdCompleted", c_uint8),
                ("cancelCurrentI2cTransfer", c_uint8),
                ("setBaudrate", c_uint8),
                ("i2cDivider", c_uint8),
                ("anyValue2", c_uint8 * I2C_SET_PARAMS_REQ_PAYLOAD_LENGTH)]

# Union command
class I2cSetParametersResponse_t(Union):
    _fields_ = [("data", I2cSetParametersResponseArray_t ),
                ("fields", I2cSetParametersResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I2cSetParametersResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id': self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'completed' : self.fields.cmdCompleted,
            'cancelTransfer' : self.fields.cancelCurrentI2cTransfer,
            'baudrate' : self.fields.setBaudrate,
            'divider' : self.fields.i2cDivider
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Enums ------------------------------------------------------------------------ #

class I2cSetParametersSubCommand(Enum):
    I2C_SET_PARAMS_CANCEL_TRANSFER      = 0x10
    I2C_SET_PARAMS_BAUDRATE             = 0x20

#================================================================================#
# I2C TRANSFER
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
I2C_TRANSFER_REQ_LENGTH			        = INTERRUPT_IN_ENDPOINT_SIZE
I2C_TRANSFER_REQ_HEADER_LENGTH	        = 11
I2C_TRANSFER_REQ_PAYLOAD_LENGTH	        = I2C_TRANSFER_REQ_LENGTH - I2C_TRANSFER_REQ_HEADER_LENGTH

# Union arrays
I2cTransferRequestArray_t               = c_uint8 * (I2C_TRANSFER_REQ_LENGTH + 1)                       # Command length + endpoint ID.
I2cTransferRequestPayloadArray_t        = c_uint8 * I2C_TRANSFER_REQ_PAYLOAD_LENGTH

# Union structure
class I2cTransferRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("i2cTransfLength", c_uint16),
                ("i2cClientAddress", c_uint8),
                ("i2cSubAddressLength", c_uint8),
                ("i2cSubAddress", c_uint32),
                ("dataToBeSent", I2cTransferRequestPayloadArray_t)]

# Union command
class I2cTransferRequest_t(Union):
    _fields_ = [("data", I2cTransferRequestArray_t ),
                ("fields", I2cTransferRequestFields_t )]


# Response --------------------------------------------------------------------- #

# Constants
I2C_TRANSFER_RES_LENGTH			        = INTERRUPT_IN_ENDPOINT_SIZE
I2C_TRANSFER_RES_HEADER_LENGTH	        = 6
I2C_TRANSFER_RES_PAYLOAD_LENGTH	        = I2C_TRANSFER_RES_LENGTH - I2C_TRANSFER_RES_HEADER_LENGTH

# Union arrays
I2cTransferResponseArray_t              = c_uint8 * (I2C_TRANSFER_RES_LENGTH)
I2cTransferResponsePayloadArray_t       = c_uint8 * I2C_TRANSFER_RES_PAYLOAD_LENGTH

# Union structure
class I2cTransferResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("status", c_uint8),
                ("payloadLength", c_uint16),
                ("payload", I2cTransferResponsePayloadArray_t)]

# Union command
class I2cTransferResponse_t(Union):
    _fields_ = [("data", I2cTransferResponseArray_t ),
                ("fields", I2cTransferResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I2cTransferResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'status' : self.fields.status,
            'payloadLength' : self.fields.payloadLength,
            'payload' : list(self.fields.payload)
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - I2C TRANSFER
#================================================================================#

class I2cTransferHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.status = 0x00
        self.dataLength = 0x00
        self.data = []

    def set(self, data) -> bool:

        response = I2cTransferResponse_t.from_buffer_copy(data)

        # Header
        self.id         = response.fields.id
        self.command    = response.fields.cmd
        self.name       = COMMANDS_DICTIONARY[response.fields.cmd]["name"]
        self.status     = response.fields.status

        # Payload
        payload = list(response.fields.payload)

        if (response.fields.payloadLength <= I2C_TRANSFER_RES_PAYLOAD_LENGTH):
            self.dataLength += response.fields.payloadLength
            self.data += payload[:response.fields.payloadLength]
            return True
        else:
            # Append paylad, increment paylaod length, and wait for pending responses.
            self.dataLength += I2C_TRANSFER_RES_PAYLOAD_LENGTH
            self.data += payload
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : self.name,
            'status' : self.status,
            'payloadLength' : self.dataLength,
            'data' : self.data
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - GET CAPABILITIES
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_GET_CAPABILITIES_REQ_LENGTH 		    = INTERRUPT_IN_ENDPOINT_SIZE
I3C_GET_CAPABILITIES_REQ_HEADER_LENGTH      = 3
I3C_GET_CAPABILITIES_REQ_PAYLOAD_LENGTH     = I3C_GET_CAPABILITIES_REQ_LENGTH - I3C_GET_CAPABILITIES_REQ_HEADER_LENGTH

# Union array
I3cGetCapabilitiesRequestArray_t                   = c_uint8 * (I3C_GET_CAPABILITIES_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cGetCapabilitiesRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("dontCare", c_uint8 * I3C_GET_CAPABILITIES_REQ_PAYLOAD_LENGTH)]

# Union command
class I3cGetCapabilitiesRequest_t(Union):
    _pack_ = 1
    _fields_ = [("data", I3cGetCapabilitiesRequestArray_t ),
                ("fields", I3cGetCapabilitiesRequestFields_t )]

# Response --------------------------------------------------------------------- #

# Constants
I3C_GET_CAPABILITIES_RES_LENGTH 		    = INTERRUPT_IN_ENDPOINT_SIZE
I3C_GET_CAPABILITIES_RES_HEADER_LENGTH     = 7
I3C_GET_CAPABILITIES_RES_PAYLOAD_LENGTH    = 36
I3C_GET_CAPABILITIES_RES_UNUSED_LENGTH     = I3C_GET_CAPABILITIES_RES_LENGTH - I3C_GET_CAPABILITIES_RES_HEADER_LENGTH - I3C_GET_CAPABILITIES_RES_PAYLOAD_LENGTH

# Union array
I3cGetCapabilitiesResponseArray_t               = c_uint8 * I3C_GET_CAPABILITIES_RES_LENGTH

# Union structure
class I3cDeviceCapability_t(Structure):
    _pack_ = 1
    _fields_ = [("staticAddress", c_uint8 ),
                ("i2cDevicesPresent", c_uint8 ),
                ("i3cGeneralCharacteristics", c_uint16 ),
                ("i3cMinorVersionNumber", c_uint16 ),
                ("i3cMajorVersionNumber", c_uint16 ),
                ("i3cDisCoMinorVersionNumber", c_uint16 ),
                ("i3cDisCoMajorVersionNumber", c_uint16 ),
                ("i2cDataTransferRates", c_uint8 ),
                ("reserved", c_uint8 ),
                ("clkFreqI2cUdr1", c_uint16 ),
                ("clkFreqI2cUdr2", c_uint16 ),
                ("clkFreqI2cUdr3", c_uint16 ),
                ("i3cDataTransferModes", c_uint8 ),
                ("i3cDataTransferRates", c_uint8 ),
                ("transferModeExtendedCapabilityLength", c_uint16 ),
                ("i3cUdr1ClockFreq", c_uint32 ),
                ("i3cUdr2ClockFreq", c_uint32 ),
                ("maxIbiPayloadSize", c_uint32 )]

    def toDictionary(self) -> dict:
        return {
            'staticAddress' : self.staticAddress,
            'i2cDevicesPresent' : I2cDeviceType_t(self.i2cDevicesPresent).name,
            'i3cGeneralCharacteristics': [characteristic.name for characteristic in I3cGeneralCharacteristics_t if characteristic.value & self.i3cGeneralCharacteristics],
            'i3cMinorVersionNumber' : self.i3cMinorVersionNumber,
            'i3cMajorVersionNumber' : self.i3cMajorVersionNumber,
            'i3cDisCoMinorVersionNumber' : self.i3cDisCoMinorVersionNumber,
            'i3cDisCoMakorVersionNumber' : self.i3cDisCoMajorVersionNumber,
            'i2cDataTransferRates' : [rate.name for rate in I2cDataTransferRates_t if rate.value & self.i2cDataTransferRates],
            'i2cUdr1ClockFreq' : self.clkFreqI2cUdr1,
            'i2cUdr2ClockFreq' : self.clkFreqI2cUdr2,
            'i2cUdr3ClockFreq' : self.clkFreqI2cUdr3,
            'i3cDataTransferModes' : [mode.name for mode in I3cDataTransferModes_t if mode.value & self.i3cDataTransferModes],
            'i3cDataTransferRates' : [rate.name for rate in I3cDataTransferRates_t if rate.value & self.i3cDataTransferRates],
            'transferModeExtendedCapabilityLength' : self.transferModeExtendedCapabilityLength,
            'i3cUdr1ClockFreq' : self.i3cUdr1ClockFreq,
            'i3cUdr2ClockFreq' : self.i3cUdr2ClockFreq,
            'maxIbiPayloadSize' : self.maxIbiPayloadSize
        }

class I3cCapabilityHeader_t(Structure):
    _pack_ = 1
    _fields_ = [("totalLength", c_uint16 ),
                ("deviceRole", c_uint8, 2 ),
                ("dataType", c_uint8, 2 ),
                ("reserved", c_uint8, 4 ),
                ("errorCode", c_uint8)]

    def toDictionary(self) -> dict:
        return {
            'length' : self.totalLength,
            'deviceRole' : DeviceRole_t(self.deviceRole).name,   # Return enum element name.
            'dataType' : DataType_t(self.dataType).name,
            'reserved' : 0x00,
            'errorCode' : self.errorCode
        }

class I3cGetCapabilitiesResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("i3cCapabilityHeader", I3cCapabilityHeader_t ),
                ("i3cDeviceCapability", I3cDeviceCapability_t ),
                ("dontCare", c_uint8 * I3C_GET_CAPABILITIES_RES_UNUSED_LENGTH)]

# Union command
class I3cGetCapabilitiesResponse_t(Union):
    _fields_ = [("data", I3cGetCapabilitiesResponseArray_t ),
                ("fields", I3cGetCapabilitiesResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cGetCapabilitiesResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'header' : self.fields.i3cCapabilityHeader.toDictionary(),
            'capabilities' : self.fields.i3cDeviceCapability.toDictionary(),
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Enums ------------------------------------------------------------------------ #

class DeviceRole_t(Enum):
    '''
    Enum that identifies the role of the device that communicates via USB with the host
    '''
    RESERVED                                   = 0x00
    PRIMARY_CONTROLLER                         = 0x01
    TARGET                                     = 0x02
    TARGET_WITH_CONTROLLER_CAPABILITY          = 0x03

class DataType_t(Enum):
    '''
    Enum that defines the data held by the device, depending if it has previous knowledge of target devices on bus
    '''
    RESERVED_DATA   = 0x00
    STATIC_DATA     = 0x01
    NO_STATIC_DATA  = 0x02
    DYNAMIC_DATA    = 0x03

class I2cDeviceType_t(Enum):
    '''
    Enum that indicates what type of i2c devices are present on the bus if any
    '''
    NO_I2C_DEVICES                             = 0x00
    I2C_DEVICES_WITH_FILTER                    = 0x01
    I2C_DEVICES_WITHOUTFILTER                  = 0x02
    MIXED_I2C_DEVICES                          = 0x03
    RESERVED_2                                 = 0x04
    RESERVED_3                                 = 0x05
    RESERVED_4                                 = 0x06
    RESERVED_5                                 = 0x07

class I2cDataTransferRates_t(Enum):
    '''
    Enum that contains flags indicating i2c supported frequencies
    '''
    I2C_STANDARD_MODE  = 0x01   # 100 KHz
    I2C_FAST_MODE      = 0x02   # 400 KHz
    I2C_FAST_PLUS_MODE = 0x04   # 1   MHz
    SUPPORT_I2C_UDR1   = 0x08
    SUPPORT_I2C_UDR2   = 0x10
    SUPPORT_I2C_UDR3   = 0x20

class I3cDataTransferModes_t(Enum):
    '''
    Enum that contains flags indicating i3c supported modes
    '''
    SUPPORT_SDR = 0x01
    SUPPORT_HDR_DDR = 0x02
    SUPPORT_HDRTS = 0x04
    SUPPORT_HDRBT = 0x08

class I3cDataTransferRates_t(Enum):
    '''
    Enum that contains flags indicating i3c supported frequencies. These flags are assigned to the
    i3cDataTransferRates field in the response to the I3C GET CAPABILITY command.
    '''
    SUPPORT_3_75_MHZ    = 0x01
    SUPPORT_5_MHZ       = 0x02
    SUPPORT_6_25_MHZ    = 0x04
    SUPPORT_7_5_MHZ     = 0x08
    SUPPORT_10_MHZ      = 0x10
    SUPPORT_12_5_MHZ    = 0x20
    SUPPORT_I3C_UDR1    = 0x40
    SUPPORT_I3C_UDR2    = 0x80

class I3cGeneralCharacteristics_t(Enum):
    '''
    Enum that contains flags indicating capabilities
    '''
    HANDOFF_CONTROLLER_ROLE = 0x01
    HOTJOIN_CAPABILITY = 0x02
    INBAND_INT_CAPABILITY = 0x04
    PENDING_READ_CAPABILITY = 0x08
    SELF_INITIATED = 0x10
    DELAYED_PENDING_READ = 0x20
    PENDING_READ_SDR = 0x40
    PENDING_READ_HDR = 0x80
    SINGLE_CMD_PENDING_READ = 0x100

#================================================================================#
# I3C - TARGET RELATED CLASSES DEFINTION
#================================================================================#

# Bus Characteristics  Register (BCR) ------------------------------------------ #

# BCR Dictionary. This dictionary contains a description for every BCR bit fields.
BCR = {
    'deviceRole' : {
        0 : "I3C Target.",
        1 : "I3C Controller capable.",
        2 : "Reserved for future definition by MIPI Alliance I3C WG.",
        3 : "Reserved for future definition by MIPI Alliance I3C WG."
    },

    'advancedCapabilities' : {
        0 : "Does not support optional advanced capabilities.",
        1 : "Supports optional advanced capabilities. Use GETCAPS CCC to deremine which ones."
    },

    'virtualTargetSupport' : {
        0 : "Is not a Virtual Target and does not expose other downstream Device(s).",
        1 : "Is a Virtual Target, or exposes other downstream Device(s)."
    },

    'offlineCapable' : {
        0 : "Device retains the Dynamic Address and will always respond to I3C Bus commands.",
        1 : "Device will not always respond to I3C Bus commands."
    },

    'ibiPayload' : {
        0 : "No data bytes follow the accepted IBI.",
        1 : "One data byte (MDB) shall follow the accepted IBI, and additional data bytes may follow."
    },

    'ibiRequestCapable' : {
        0 : "Not capable.",
        1 : "Capable."
    },

    'maxDataSpeedLimitation' : {
        0 : "No Limitation.",
        1 : "Limitation. Controller shall use the GETMXDS CCC to interrogate the Target for specific limitation."
    }
}

# Bus Characteristics Register (BCR).
class I3cBcrRegisterBitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("maxDataSpeedLimitation", c_uint8, 1),
                ("ibiRequestCapable", c_uint8, 1),
                ("ibiPayload", c_uint8, 1),
                ("offlineCapable", c_uint8, 1),
                ("virtualTargetSupport", c_uint8, 1),
                ("advancedCapabilities", c_uint8, 1),
                ("deviceRole", c_uint8, 2)]

class I3cBcrRegister_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cBcrRegisterBitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'deviceRole' : BCR['deviceRole'][self.bits.deviceRole],
                'advancedCapabilities' : BCR['advancedCapabilities'][self.bits.advancedCapabilities],
                'virtualTargetSupport' : BCR['virtualTargetSupport'][self.bits.virtualTargetSupport],
                'offlineCapable' : BCR['offlineCapable'][self.bits.offlineCapable],
                'ibiPayload' : BCR['ibiPayload'][self.bits.ibiPayload],
                'ibiRequestCapable' : BCR['ibiRequestCapable'][self.bits.ibiRequestCapable],
                'maxDataSpeedLimitation' : BCR['maxDataSpeedLimitation'][self.bits.maxDataSpeedLimitation],
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Provisioned-ID (PID) --------------------------------------------------------- #
I3C_PID_SIZE                        = 6

class I3cPIDRegisterBytesFields_t(Structure):
    _pack_ = 1
    _fields_ = [("PID_5", c_uint8),
                ("PID_4", c_uint8),
                ("PID_3", c_uint8),
                ("PID_2", c_uint8),
                ("PID_1", c_uint8),
                ("PID_0", c_uint8)]

class I3cPIDRegister_t(Union):
    _fields_ = [("data", c_uint8 * I3C_PID_SIZE),
                ("bytes", I3cPIDRegisterBytesFields_t )]

# I3C Target features ---------------------------------------------------------- #

# Target features masks.
TARGET_INTERRUPT_REQUEST_MASK       = 0x0001
CONTROLLER_ROLE_REQUEST_MASK        = 0x0002
IBI_TIMESTAMP_MASK                  = 0x0004
ASSIGNMENT_FROM_STATIC_ADDRESS_MASK = 0x0018
DYN_ADDR_ASSIGNMENT_W_ENTDAA_MASK   = 0x0020
TARGET_TYPE_MASK                    = 0x0040
PENDING_READ_CAPABILITY_MASK        = 0x0080
VALID_PID_MASK                      = 0x0100

# Target devices features enums.

class TargetInterruptRequest(Enum):
    '''
    Enum that represents the Target Interrupt Request (TIR) feature options.

    This field is configurable. This field controls whether the Active I3C Controller
    will accept or reject interrupts from this Target device. If this bit is set to 0b,
    the Active I3C Controller shall ACCEPT interrupts from this Target device. If this
    bit is set to 1b, Active I3C Controller shall REJECT interrupts from this Target
    device.
    '''
    ACCEPT_INTERRUPT_REQUEST = 0x0000
    REJECT_INTERRUPT_REQUEST = 0x0001

class ControllerRoleRequest(Enum):
    '''
    Enum that represents the Controller Role Request (CRR) feature options.

    This field is configurable. This field controls whether the Active I3C Controller
    accepts or rejects the I3C Controller role request. If this bit is set to 0b,
    Active I3C Controller shall ACCEPT the I3C Controller role requests from Secondary
    I3C Controllers. If this bit is set to 1b, Active I3C Controller shall REJECT the
    I3C Controller role requests from Secondary I3C Controllers.
    '''
    ACCEPT_CRR = 0x0000
    REJECT_CRR = 0x0002

class IBiTimestamp(Enum):
    '''
    Enum that represents the IBI Timestamp (IBIT) feature options.

    This field is configurable. This field enables or disables timestamping of IBIs
    from the Target device. If this bit is set to 0b, Active I3C Controller shall
    not timestamp IBIs from this Target device. If this bit is set to 1b, Active I3C
    Controller shall timestamp IBIs from this Target device.
    '''
    DISABLE_IBIT = 0x0000
    ENABLE_IBIT  = 0x0004

class AssignmentFromStaticAddress(Enum):
    '''
    Enum that identifies the address assigment mode from the static address options.
    '''
    I3C_TARGET_DOES_NOT_HAVE_STATIC_ADDR       = 0x0000
    I3C_TARGET_SUPPORTS_SETDASA                = 0x0008
    I3C_TARGET_SUPPORTS_SETAASA                = 0x0010
    I3C_TARGET_SUPPORT_SETDASA_AND_SETAASA     = 0x0018

class DAaWithENTDAA(Enum):
    '''
    Enum that represents the Dynamic Address Assignment with ENTDAA (DAA) feature options.

    This field is configurable when the Host sends the Target Device Table to the I3C
    Function during I3C Bus initialization. If this bit is set to 0b, the Active I3C
    Controller shall not use the ENTDAA CCC to configure this I3C Target device. If this
    bit is set to 1b, the Active I3C Controller shall use the ENTDAA CCC to configure this
    I3C Target device.
    '''
    DISABLE_ENTDAA = 0x0000
    ENABLE_ENTDAA  = 0x0020

class TargetType(Enum):
    '''
    Enum that represents the Target Type feature options.

    If the Target device is an I3C device, this field shall be set to 0h. If the Target
    device is an I2C device, this field shall be set to 1h.
    '''
    I3C_DEVICE = 0x0000
    I2C_DEVICE = 0x0040

class PendingReadCapability(Enum):
    '''
    Enum that represents the Pending Read Capability feature options.

    This field indicates if the I3C Target device supports IBI pending read capability.
    If this bit is set to 0b, the I3C Device does not support IBI pending read. If this
    bit is set to 1b, the I3C Device supports IBI pending read.
    '''
    NOT_SUPPORT_IBI_READ_CAPABILITY = 0x0000
    SUPPORT_IBI_READ_CAPABILITY     = 0x0080

class ValidPID(Enum):
    '''
    Enum that represents the Valid PID (VPID) feature options.

    This field indicates if the I3C Target device has a valid 48-bit PID. If this bit is
    set to 0b, Provisional ID bytes fields shall not be populated. If this bit is set to
    1b, Provisional ID bytes fields shall be populated.
    '''
    HAS_NOT_VALID_PID = 0x0000
    HAS_VALID_PID     = 0x0100

# Supernova in target mode ----------------------------------------------------------------- #

class I3cOffline(Enum):
    '''
    If I3cOffline = 0x01 when the target enable (SCONFIG[SLVENA]) is set to 1, then the I3C module waits for 
    either 60 s of bus quiet or an HDR Exit Pattern. This waiting ensures that the bus is not in HDR mode, 
    and so can safely monitor for the next activity in Single Data Rate (SDR) mode
    '''
    OFFLINE_UNFIT       = 0x00
    OFFLINE_CAPABLE     = 0x01

class PartNOrandom(Enum):
    '''
    If PartNOramdom = 0x00, SIDPARTNO[PARTNO] is a part number and an instance.
    If PartNOrandom = 0x02, SIDPARTNO[PARTNO] is a random number
    '''
    PART_NUMB_DEFINED      = 0x00
    PART_NUMB_RANDOM       = 0x02

class DdrOk(Enum):
    '''
    Indicates whether HDR-DDR is allowed (DdrOk = 0x04) or not (DdrOk = 0x00)
    '''
    PROHIBITED_DDR      = 0x00
    ALLOWED_DDR         = 0x04

class IgnoreTE0TE1Errors(Enum):
    '''
    If IgnoreTE0TE1Errors = 0x08: the target does not detect TE0 or TE1 errors, so it does not lock up 
    waiting on an Exit Pattern.
    '''
    NOT_IGNORE_ERRORS    = 0x00
    IGNORE_ERRORS        = 0x08

class MatchStartStop(Enum):
    '''
    This setting allows START and STOP to be used to detect the end of a message to/from this target
    if MatchStartStop = 0x10
    '''
    NOT_MATCH   = 0x00
    MATCH       = 0x10

class AlwaysNack(Enum):
    '''
    If AlwaysNack = 0x20 the target rejects all requests to it, except for a Common Command 
    Code (CCC) broadcast
    '''
    NOT_ALWAYS_NACK     = 0x00
    ALWAYS_NACK         = 0x20

# Target device ----------------------------------------------------------------- #

class I3cTargetDeviceEntry_t(Structure):
    _pack_ = 1
    _fields_ = [("staticAddress", c_uint8),
                ("dynamicAddress", c_uint8),
                ("i3cFeatures", c_uint16),
                ("maxIbiPayloadSize", c_uint16),
                ("BCR", I3cBcrRegister_t),
                ("DCR", c_uint8),
                ("PID", I3cPIDRegister_t)]

    def toDictionary(self) -> dict:
        return {
            "staticAddress" : self.staticAddress,
            "dynamicAddress" : self.dynamicAddress,
            "bcr" : self.BCR.toDictionary(),
            "dcr" : self.DCR,
            "pid" : [ f'{self.PID.bytes.PID_5:#04x}', f'{self.PID.bytes.PID_4:#04x}', f'{self.PID.bytes.PID_3:#04x}', f'{self.PID.bytes.PID_2:#04x}' , f'{self.PID.bytes.PID_1:#04x}', f'{self.PID.bytes.PID_0:#04x}' ],
            "maxIbiPayloadSize" : self.maxIbiPayloadSize,
            "i3cFeatures" : {
                'targetInterruptRequest' : TargetInterruptRequest(self.i3cFeatures & TARGET_INTERRUPT_REQUEST_MASK).name,
                'controlerRoleRequest' : ControllerRoleRequest(self.i3cFeatures & CONTROLLER_ROLE_REQUEST_MASK).name,
                'ibiTimestamp' : IBiTimestamp(self.i3cFeatures & IBI_TIMESTAMP_MASK).name,
                'assignmentFromStaticAddress' : AssignmentFromStaticAddress(self.i3cFeatures & ASSIGNMENT_FROM_STATIC_ADDRESS_MASK).name,
                'assignmentFromENTDAA' : DAaWithENTDAA(self.i3cFeatures & DYN_ADDR_ASSIGNMENT_W_ENTDAA_MASK).name,
                'targetType' : TargetType(self.i3cFeatures & TARGET_TYPE_MASK).name,
                'pendingReadCapability' : PendingReadCapability(self.i3cFeatures & PENDING_READ_CAPABILITY_MASK).name,
                'validPid' : ValidPID(self.i3cFeatures & VALID_PID_MASK).name
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - INIT BUS
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_INIT_BUS_REQ_LENGTH 		         = INTERRUPT_IN_ENDPOINT_SIZE
I3C_INIT_BUS_REQ_HEADER                  = 4
I3C_INIT_BUS_DEVICE_ENTRY_LENGTH         = 14
I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER    = 4
I3C_INIT_BUS_REQ_UNUSED_DATA_LENGTH      = I3C_INIT_BUS_REQ_LENGTH - (I3C_INIT_BUS_REQ_HEADER + (I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER * I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER))

# Union array
I3cInitBusRequestArray_t                 = c_uint8 * (I3C_INIT_BUS_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cInitBusRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("targetCount", c_uint8 ),
                ("targetsList", I3cTargetDeviceEntry_t * I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER),
                ("unusedData", c_uint8 * I3C_INIT_BUS_REQ_UNUSED_DATA_LENGTH )]

# Union command
class I3cInitBusRequest_t(Union):
    _fields_ = [("data", I3cInitBusRequestArray_t ),
                ("fields", I3cInitBusRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class I3cInitBusError(Enum):
    I3C_BUS_INIT_SUCCESS                          = 0
    ADD_TO_TABLE_FAILED_BECAUSE_FULL_TABLE        = 1
    ADD_TO_TABLE_FAILED_BECAUSE_REPEATED_ADDR     = 2
    SET_SLOT_FAILED_BECAUSE_RESERVED_ADDR         = 3
    SET_SLOT_FAILED_BECAUSE_ALREADY_USED_ADDR     = 4
    RSTDAA_FAILED                                 = 5
    SETDASA_FAILED                                = 6
    SETAASA_FAILED                                = 7
    ENTDAA_FAILED                                 = 8
    I3C_BUS_INIT_DRIVER_TIMEOUT                   = 9
    I3C_BUS_INIT_SOFTWARE_TIMEOUT                 = 10

# Response --------------------------------------------------------------------- #

#Constants
I3C_INIT_BUS_RES_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_INIT_BUS_RES_HEADER                 = 6
I3C_INIT_BUS_RES_UNUSED_DATA_LENGTH     = I3C_INIT_BUS_RES_LENGTH - I3C_INIT_BUS_RES_HEADER

# Union array
I3cInitBusResponseArray_t               = c_uint8 * (I3C_INIT_BUS_RES_LENGTH)

# Union structure
class I3cInitBusResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("errorStatus", c_uint16),
                ("unusedData", c_uint8 * I3C_INIT_BUS_RES_UNUSED_DATA_LENGTH)]

# Union command
class I3cInitBusResponse_t(Union):
    _fields_ = [("data", I3cInitBusResponseArray_t),
                ("fields", I3cInitBusResponseFields_t)]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cInitBusResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:

        # Set error list
        errors = [ error.name for error in I3cTransferError if (error.value & self.fields.errorStatus) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(errors) == 0 ):
            errors.append(I3cTransferError.NO_TRANSFER_ERROR.name)

        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cInitBusError(self.fields.result).name,
            'errors' : errors
        }

    def __str__(self) -> str:
        return str(self.toDictionary())


#================================================================================#
# I3C - GET TARGET DEVICE TABLE
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_GET_TABLE_REQ_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_GET_TABLE_REQ_HEADER_LENGTH         = 3
I3C_GET_TABLE_REQ_PAYLOAD_LENGTH        = I3C_GET_TABLE_REQ_LENGTH - I3C_GET_TABLE_REQ_HEADER_LENGTH

# Union array
I3cGetTargetDeviceTableRequestArray_t   = c_uint8 * (I3C_GET_TABLE_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cGetTargetDeviceTableRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("dontCare", c_uint8 * I3C_GET_TABLE_REQ_PAYLOAD_LENGTH)]

# Union command
class I3cGetTargetDeviceTableRequest_t(Union):
    _fields_ = [("data", I3cGetTargetDeviceTableRequestArray_t ),
                ("fields", I3cGetTargetDeviceTableRequestFields_t )]

# Response --------------------------------------------------------------------- #

# Constants
I3C_GET_TABLE_RES_LENGTH 		                = INTERRUPT_IN_ENDPOINT_SIZE
I3C_GET_TABLE_RES_HEADER_LENGTH                 = 4
I3C_DEVICE_ENTRY_LENGTH                         = 14
I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER   = 4
I3C_GET_TABLE_RES_PAYLOAD_LENGTH                = I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER * I3C_DEVICE_ENTRY_LENGTH
I3C_GET_TABLE_RES_UNUSED_LENGTH                 = I3C_GET_TABLE_RES_LENGTH - I3C_GET_TABLE_RES_HEADER_LENGTH - I3C_GET_TABLE_RES_PAYLOAD_LENGTH

# Union array
I3cGetTargetDeviceTableResponseArray_t  = c_uint8 * I3C_GET_TABLE_RES_LENGTH

#Array of target entries in table
I3cTargetDeviceEntries_t = I3cTargetDeviceEntry_t * I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER

class I3cGetTargetDeviceTableResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("numberOfDevices", c_uint8 ),
                ("i3cTargetDeviceEntries", I3cTargetDeviceEntries_t),
                ("dontCare", c_uint8 * I3C_GET_TABLE_RES_UNUSED_LENGTH)]

# Union command
class I3cGetTargetDeviceTableResponse_t(Union):
    _fields_ = [("data", I3cGetTargetDeviceTableResponseArray_t ),
                ("fields", I3cGetTargetDeviceTableResponseFields_t )]

    def toDictionary(self):
        targets = []

        iterations = I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER
        if self.fields.numberOfDevices < I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER:
            iterations = self.fields.numberOfDevices

        for i in range(iterations):
            target = self.fields.i3cTargetDeviceEntries[i]
            targets.append(target.toDictionary())

        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'numberOfDevices' : self.fields.numberOfDevices,
            'targetsList' : targets
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - TRANSFER
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_TRANSFER_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TRANSFER_REQ_HEADER_LENGTH              = 3
I3C_TRANSFER_REQ_COMMAND_HEADER_LENGTH      = 3
I3C_TRANSFER_REQ_COMMAND_DESCRIPTOR_LENGTH  = 8
I3C_TRANSFER_REQ_DATA_LENGTH                = I3C_TRANSFER_REQ_LENGTH - I3C_TRANSFER_REQ_HEADER_LENGTH - I3C_TRANSFER_REQ_COMMAND_HEADER_LENGTH - I3C_TRANSFER_REQ_COMMAND_DESCRIPTOR_LENGTH

# Union array
I3cTransferRequestArray_t                   = c_uint8 * (I3C_TRANSFER_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Structure that contains the I3C Transfer Header.
class I3cTransferHeader_t(Structure):
    _pack_ = 1
    _fields_ = [("requestId", c_uint16),
                ("hasData", c_uint8) ]

    def toDictionary(self) -> dict:
        return {
            'requestId' : self.requestId,
            'hasData' : self.hasData
        }

# Structure that contains the I3C Transfer Description.
class I3cTransferCommandDescriptor_t(Structure):
    _pack_ = 1
    _fields_ = [("commandType", c_uint8, 3),
                ("readOrWrite", c_uint8, 1),
                ("errorHandling", c_uint8, 4),
                ("targetAddress", c_uint8),
                ("transferMode", c_uint8),
                ("transferRate", c_uint8),          # The 4 MSB represent the SCL frequency in Push-Pull, the 4 LSB in Open-Drain.
                ("dataLength", c_uint16),
                ("CCC", c_uint8),
                ("definingByte", c_uint8) ]

    def toDictionary(self) -> dict:
         return {
            'commandType' : I3cCommandType(self.commandType).name,
            'readOrWrite' : TransferDirection(self.readOrWrite).name,
            'errorHandling' : self.errorHandling,
            'targetAddress' : self.targetAddress,
            'transferMode' : TransferMode(self.transferMode).name,
            'pushPullRate' : I3cPushPullTransferRate(self.transferRate & I3C_PUSH_PULL_RATE_MASK).name,
            'openDrainPullRate' : I3cOpenDrainTransferRate(self.transferRate & I3C_OPEN_DRAIN_RATE_MASK).name,
            'definingByte' : self.definingByte,
            'ccc' : self.CCC,
            'dataLength' : self.dataLength
        }

# Union structure
class I3cTransferRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("header", I3cTransferHeader_t),
                ("descriptor", I3cTransferCommandDescriptor_t),
                ("dataBlock", c_uint8 * I3C_TRANSFER_REQ_DATA_LENGTH) ]

# Union command
class I3cTransferRequest_t(Union):
    _fields_ = [("data", I3cTransferRequestArray_t ),
                ("fields", I3cTransferRequestFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'header' : self.fields.header.toDictionary(),
            'descriptor' : self.fields.descriptor.toDictionary(),
            'dataBlock' : list(self.fields.dataBlock)
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Enums ------------------------------------------------------------------------ #

class I3cCommandType(Enum):
    '''
    This enum represents the possible values to be assgined to the command type byte in the command descriptor.

    Defined in the USB I3C Device class specification V1.0
    '''
    REGULAR_COMMAND             = 0x00
    CCC_WITHOUT_DEFINING_BYTE   = 0x01
    CCC_WITH_DEFINING_BYTE      = 0x02
    TARGET_RESET_PATTERN        = 0x03
    # 0x04 - 0x07 Reserved for future use.

class TransferDirection(Enum):
    '''
    This enum represent the transfer directions Read and Write.

    Defined in the USB I3C Device class specification V1.0
    '''
    WRITE = 0x00
    READ  = 0x01

class TransferMode(Enum):
    '''
    This enum represents the possible values to be assgined to the transfer mode bits in the command descriptor.

    Defined in the USB I3C Device class specification V1.0
    '''
    I3C_SDR     = 0x00
    I3C_HDR_DDR = 0x01
    I3C_HDR_TS  = 0x02        # Not supported.
    I3C_HDR_BT  = 0x03        # Not supported.
    I2C_MODE    = 0x08
    # 0x04 - 0x07 Reserved for future HDR modes.

I3C_PUSH_PULL_RATE_MASK = 0xF0

class I3cPushPullTransferRate(Enum):
    '''
    This enum represents the possible values to be assgined to the transfer rate bits in the command descriptor.

    Defined in the USB I3C Device class specification V1.0, but then some values were changed to values that
    were defined in the I3C driver.
    '''
    PUSH_PULL_3_75_MHZ      = 0x00
    PUSH_PULL_5_MHZ         = 0x10
    PUSH_PULL_6_25_MHZ      = 0x20
    PUSH_PULL_7_5_MHZ       = 0x30
    PUSH_PULL_10_MHZ        = 0x40
    PUSH_PULL_12_5_MHZ      = 0x50

I3C_OPEN_DRAIN_RATE_MASK = 0x0F

class I3cOpenDrainTransferRate(Enum):
    '''
    This enum represents the possible values to be assgined to the transfer rate bits in the command descriptor.

    Defined in the USB I3C Device class specification V1.0, but then some values were changed to values that
    were defined in the I3C driver.
    '''
    OPEN_DRAIN_100_KHZ 		= 0x00
    OPEN_DRAIN_250_KHZ 		= 0x01
    OPEN_DRAIN_500_KHZ 		= 0x02
    OPEN_DRAIN_1_25_MHZ 	= 0x03
    OPEN_DRAIN_2_5_MHZ		= 0x04
    OPEN_DRAIN_3_125_MHZ	= 0x05
    OPEN_DRAIN_4_17_MHZ		= 0x06

class I2cTransferRate(Enum):
    '''
    This enum represents the possible values to be assgined to the transfer rate bits in the command descriptor.

    Defined in the USB I3C Device class specification V1.0
    '''
    _100KHz         = 0x00
    _400KHz         = 0x01
    _1MHz           = 0x02
    USER_DEFINED_1  = 0x03
    USER_DEFINED_2  = 0x04
    USER_DEFINED_3  = 0x05

class I3cTargetResetDefByte(Enum):
    '''
    This enum represents the possible values of the definingByte for RSTACT CCC used to perform a Target Reset.

    Defined in the USB I3C Device class specification V1.0
    '''
    NO_RESET                            = 0x00
    RESET_I3C_PERIPHERAL                = 0x01
    RESET_WHOLE_TARGET                  = 0x02
    RESET_DEBUG_NETWORK                 = 0x03
    VIRTUAL_TARGET_DETECT               = 0x04
    RETURN_TIME_RESET_PERIPHERAL        = 0x81
    RETURN_TIME_RESET_WHOLE_TARGET      = 0x82
    RETURN_TIME_DEBUG_NETWORK_RESET     = 0x83
    RETURN_VIRTUAL_TARGET_INDICATION    = 0x84

class I3cTransferResponseTag(Enum):
    '''
    This enum represents the possible values to be assigned to the tag field in the response header.

    Defined in the USB I3C Device class specification V1.0
    '''
    RESPONSE_TO_REGULAR_REQUEST = 0x00
    INTERRUPT_NOTIFICATION      = 0X01
    VENDOR_SPECIFIC_RESPONSE    = 0x02

class I3cTransferError(Enum):
    '''
    This enum represents the possible values to be assigned to the error status field.

    Values defined in the NXP LPC5536 I3C Peripheral.
    '''
    NO_TRANSFER_ERROR		= 0x0000
    TIMEOUT_ERROR 			= 0x0001
    INVALID_REQUEST_ERROR 	= 0x0002
    MESSAGE_ERROR			= 0x0004
    OVER_WRITE_ERROR		= 0x0008
    OVER_READ_ERROR			= 0x0010
    DDR_CRC_ERROR			= 0x0020
    DDR_PARITY_ERROR		= 0x0040
    WRITE_ABORT_ERROR		= 0x0080
    NACK_ERROR				= 0x0100

class I3cTransferResult(Enum):
	I3C_TRANSFER_SUCCESS            = 0
	I3C_TRANSFER_FAIL               = 1
	I3C_TRANSFER_DRIVER_TIMEOUT     = 2
	I3C_TRANSFER_SOFTWARE_TIMEOUT   = 3

# Response --------------------------------------------------------------------- #

# Constants
I3C_TRANSFER_RES_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TRANSFER_RES_HEADER_LENGTH              = 3
I3C_TRANSFER_RES_COMMAND_HEADER_LENGTH      = 3
I3C_TRANSFER_RES_COMMAND_DESCRIPTOR_LENGTH  = 4
I3C_TRANSFER_RES_DATA_LENGTH                = I3C_TRANSFER_RES_LENGTH - I3C_TRANSFER_RES_HEADER_LENGTH - I3C_TRANSFER_RES_COMMAND_HEADER_LENGTH - I3C_TRANSFER_RES_COMMAND_DESCRIPTOR_LENGTH

# Union array
I3cTransferResponseArray_t                  = c_uint8 * I3C_TRANSFER_RES_LENGTH

# Structure that contains the I3C Transfer Header.
class I3cTransferResponseHeader_t(Structure):
    _pack_ = 1
    _fields_ = [("tag", c_uint8),
                ("result", c_uint8),
                ("hasData", c_uint8) ]

    def toDictionary(self) -> dict:
        return {
            'tag' : I3cTransferResponseTag(self.tag).name,
            'result' : I3cTransferResult(self.result).name,
            'hasData' : bool(self.hasData)
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Structure that contains the I3C Transfer Description.
class I3cTransferResponseDescriptor_t(Structure):
    _pack_ = 1
    _fields_ = [("dataLength", c_uint16),
                ("errorStatus", c_uint16) ]

    def toDictionary(self) -> dict:
        # Set error list
        errors = [ error.name for error in I3cTransferError if (error.value & self.errorStatus) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(errors) == 0 ):
            errors.append(I3cTransferError.NO_TRANSFER_ERROR.name)

        return {
            'dataLength' : self.dataLength,
            'errors' : errors
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Union structure
class I3cTransferResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("header", I3cTransferResponseHeader_t),
                ("descriptor", I3cTransferResponseDescriptor_t),
                ("dataBlock", c_uint8 * I3C_TRANSFER_RES_DATA_LENGTH) ]

# Union command
class I3cTransferResponse_t(Union):
    _fields_ = [("data", I3cTransferResponseArray_t ),
                ("fields", I3cTransferResponseFields_t )]

#================================================================================#
# I3C - CLEAR FEATURE
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_CLEAR_FEATURE_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CLEAR_FEATURE_REQ_HEADER_LENGTH             = 5
I3C_CLEAR_FEATURE_REQ_UNUSED_LENGTH               = I3C_CLEAR_FEATURE_REQ_LENGTH - I3C_CLEAR_FEATURE_REQ_HEADER_LENGTH

# Union array
I3cClearFeatureRequestArray_t                     = c_uint8 * (I3C_CLEAR_FEATURE_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cClearFeatureRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("selector", c_uint8),
                ("targetAddress", c_uint8),
                ("unusedData", c_uint8 * I3C_CLEAR_FEATURE_REQ_UNUSED_LENGTH) ]

# Union command
class I3cClearFeatureRequest_t(Union):
    _fields_ = [("data", I3cClearFeatureRequestArray_t ),
                ("fields", I3cClearFeatureRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class I3cClearFeatureSelector(Enum):
    I3C_BUS                             = 0x00
    REGULAR_IBI                         = 0x01
    I3C_CONTROLLER_ROLE_HANDOFF         = 0x02
    RESERVED_1                          = 0x04
    HOT_JOIN                            = 0x08
    REGULAR_IBI_WAKE                    = 0x10
    HOT_JOIN_WAKE                       = 0x20
    I3C_CONTROLLER_ROLE_REQUEST_WAKE    = 0x40
    HDR_MODE_EXIT_RECOVERY              = 0x80

class I3cClearFeatureError(Enum):
    I3C_CLEAR_FEATURE_SUCCESS                 = 0
    I3C_CLEAR_FEATURE_FAIL                    = 1
    I3C_CLEAR_FEATURE_SELECTOR_NOT_SUPPORTED  = 2
    I3C_CLEAR_FEATURE_DRIVER_TIMEOUT          = 3
    I3C_CLEAR_FEATURE_SOFTWARE_TIMEOUT        = 4

# Response ---------------------------------------------------------------------- #

#Constants
I3C_CLEAR_FEATURE_RES_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CLEAR_FEATURE_RES_HEADER_LENGTH             = 6
I3C_CLEAR_FEATURE_RES_UNUSED_LENGTH             = I3C_CLEAR_FEATURE_RES_LENGTH - I3C_CLEAR_FEATURE_RES_HEADER_LENGTH

# Union array
I3cClearFeatureResponseArray_t                  = c_uint8 * I3C_CLEAR_FEATURE_RES_LENGTH

# Union structure
class I3cClearFeatureResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("result", c_uint8),
                ("errorStatus", c_uint16),
                ("unusedData", c_uint8 * I3C_CLEAR_FEATURE_RES_UNUSED_LENGTH) ]

# Union command
class I3cClearFeatureResponse_t(Union):
    _fields_ = [("data", I3cClearFeatureResponseArray_t ),
                ("fields", I3cClearFeatureResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cClearFeatureResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        # Set error list
        errors = [ error.name for error in I3cTransferError if (error.value & self.fields.errorStatus) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(errors) == 0 ):
            errors.append(I3cTransferError.NO_TRANSFER_ERROR.name)

        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cClearFeatureError(self.fields.result).name,
            'errors' : errors
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - SET FEATURE
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_SET_FEATURE_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_SET_FEATURE_REQ_HEADER_LENGTH           = 5
I3C_SET_FEATURE_REQ_UNUSED_LENGTH           = I3C_SET_FEATURE_REQ_LENGTH - I3C_SET_FEATURE_REQ_HEADER_LENGTH

# Union array
I3cSetFeatureRequestArray_t               = c_uint8 * (I3C_SET_FEATURE_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cSetFeatureRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("selector", c_uint8),
                ("targetAddress", c_uint8),
                ("unusedData", c_uint8 * I3C_SET_FEATURE_REQ_UNUSED_LENGTH) ]

# Union command
class I3cSetFeatureRequest_t(Union):
    _fields_ = [("data", I3cSetFeatureRequestArray_t ),
                ("fields", I3cSetFeatureRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class I3cSetFeatureSelector(Enum):
    RESERVED_1                          = 0x00
    REGULAR_IBI                         = 0x01
    I3C_CONTROLLER_ROLE_HANDOFF         = 0x02
    RESERVED_2                          = 0x04
    HOT_JOIN                            = 0x08
    REGULAR_IBI_WAKE                    = 0x10
    HOT_JOIN_WAKE                       = 0x20
    I3C_CONTROLLER_ROLE_REQUEST_WAKE    = 0x40
    RESERVED_3                          = 0x80

class I3cSetFeatureError(Enum):
    I3C_SET_FEATURE_SUCCESS                 = 0
    I3C_SET_FEATURE_FAIL                    = 1
    I3C_SET_FEATURE_SELECTOR_NOT_SUPPORTED  = 2
    I3C_SET_FEATURE_DRIVER_TIMEOUT          = 3
    I3C_SET_FEATURE_SOFTWARE_TIMEOUT        = 4

# Response ---------------------------------------------------------------------- #

#Constants
I3C_SET_FEATURE_RES_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_SET_FEATURE_RES_HEADER_LENGTH           = 6
I3C_SET_FEATURE_RES_UNUSED_LENGTH           = I3C_SET_FEATURE_RES_LENGTH - I3C_SET_FEATURE_RES_HEADER_LENGTH

# Union array
I3cSetFeatureResponseArray_t                = c_uint8 * I3C_SET_FEATURE_RES_LENGTH

# Union structure
class I3cSetFeatureResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("result", c_uint8),
                ("errorStatus", c_uint16),
                ("unusedData", c_uint8 * I3C_SET_FEATURE_RES_UNUSED_LENGTH) ]

# Union command
class I3cSetFeatureResponse_t(Union):
    _fields_ = [("data", I3cSetFeatureResponseArray_t ),
                ("fields", I3cSetFeatureResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cSetFeatureResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:

        # Set error list
        errors = [ error.name for error in I3cTransferError if (error.value & self.fields.errorStatus) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(errors) == 0 ):
            errors.append(I3cTransferError.NO_TRANSFER_ERROR.name)

        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cSetFeatureError(self.fields.result).name,
            'errors' : errors
        }

    def __str__(self) -> str:
        return str(self.toDictionary())


#================================================================================#
# I3C - CHANGE DYNAMIC ADDRESS
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_CHANGE_DYN_ADDR_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CHANGE_DYN_ADDR_REQ_HEADER_LENGTH           = 5
I3C_CHANGE_DYN_ADDR_REQ_DATA_LENGTH             = I3C_CHANGE_DYN_ADDR_REQ_LENGTH - I3C_CHANGE_DYN_ADDR_REQ_HEADER_LENGTH

# Union array
I3cChangeDynAddrRequestArray_t                  = c_uint8 * (I3C_CHANGE_DYN_ADDR_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cChangeDynAddrRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("currentDynamicAddress", c_uint8),
                ("newDynamicAddress", c_uint8),
                ("unusedData", c_uint8 * I3C_CHANGE_DYN_ADDR_REQ_DATA_LENGTH) ]

# Union command
class I3cChangeDynAddrRequest_t(Union):
    _fields_ = [("data", I3cChangeDynAddrRequestArray_t ),
                ("fields", I3cChangeDynAddrRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class I3cChangeDynAddrError(Enum):
    I3C_CHANGE_DYNAMIC_ADDRESS_SUCCESS          = 0
    I3C_CHANGE_DYNAMIC_ADDRESS_FAIL             = 1
    I3C_CHANGE_DYNAMIC_ADDRESS_DEVICE_NOT_FOUND = 2
    I3C_CHANGE_DYNAMIC_ADDRESS_NOT_AVAILABLE    = 3
    I3C_CHANGE_DYN_ADDR_DRIVER_TIMEOUT          = 4
    I3C_CHANGE_DYN_ADDR_SOFTWARE_TIMEOUT        = 5

# Response ---------------------------------------------------------------------- #

#Constants
I3C_CHANGE_DYN_ADDR_RES_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CHANGE_DYN_ADDR_RES_HEADER_LENGTH           = 6
I3C_CHANGE_DYN_ADDR_RES_DATA_LENGTH             = I3C_CHANGE_DYN_ADDR_RES_LENGTH - I3C_CHANGE_DYN_ADDR_RES_HEADER_LENGTH

# Union array
I3cChangeDynAddrResponseArray_t                = c_uint8 * I3C_CHANGE_DYN_ADDR_RES_LENGTH

# Union structure
class I3cChangeDynAddrResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("result", c_uint8),
                ("errorStatus", c_uint16),
                ("unusedData", c_uint8 * I3C_CHANGE_DYN_ADDR_RES_DATA_LENGTH) ]

# Union command
class I3cChangeDynAddrResponse_t(Union):
    _fields_ = [("data", I3cChangeDynAddrResponseArray_t ),
                ("fields", I3cChangeDynAddrResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cChangeDynAddrResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:

        # Set error list
        errors = [ error.name for error in I3cTransferError if (error.value & self.fields.errorStatus) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(errors) == 0 ):
            errors.append(I3cTransferError.NO_TRANSFER_ERROR.name)

        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cChangeDynAddrError(self.fields.result).name,
            'errors' : errors
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - SET TARGET DEVICE CONFIG
#================================================================================#

I3C_MAX_TARGET_DEVICE_CONFIG    = 11
I3C_TARGET_DEVICE_CONFIG_LENGTH = 5

class I3cTargetDeviceConfig_t(Structure):
    _pack_ = 1
    _fields_ = [("targetAddress", c_uint8),
                ("i3cFeatures", c_uint16),
                ("maxIbiPayloadLength", c_uint16)]

# Request ---------------------------------------------------------------------- #

#Constants
I3C_SET_TARGET_DEVICE_CONFIG_REQ_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_SET_TARGET_DEVICE_CONFIG_REQ_HEADER_LENGTH          = 4
I3C_SET_TARGET_DEVICE_CONFIG_REQ_PAYLOAD_LENGTH         = I3C_MAX_TARGET_DEVICE_CONFIG * I3C_TARGET_DEVICE_CONFIG_LENGTH
I3C_SET_TARGET_DEVICE_CONFIG_REQ_UNUSED_DATA_LENGTH     = I3C_SET_TARGET_DEVICE_CONFIG_REQ_LENGTH - I3C_SET_TARGET_DEVICE_CONFIG_REQ_HEADER_LENGTH - I3C_SET_TARGET_DEVICE_CONFIG_REQ_PAYLOAD_LENGTH

# Union array
I3cSetTargetDevConfigRequestArray_t                     = c_uint8 * (I3C_SET_TARGET_DEVICE_CONFIG_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cSetTargetDevConfigRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("numEntries", c_uint8),
                ("targetConfigList", I3cTargetDeviceConfig_t * I3C_MAX_TARGET_DEVICE_CONFIG),
                ("unusedData", c_uint8 * I3C_SET_TARGET_DEVICE_CONFIG_REQ_UNUSED_DATA_LENGTH) ]

# Union command
class I3cSetTargetDevConfigRequest_t(Union):
    _fields_ = [("data", I3cSetTargetDevConfigRequestArray_t ),
                ("fields", I3cSetTargetDevConfigRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class I3cSetTargetDevConfigError(Enum):
    I3C_SET_TARGET_DEVICE_CONFIG_SUCCESS              = 0
    I3C_SET_TARGET_DEVICE_CONFIG_DEVICE_NOT_FOUND     = 1

# Response ---------------------------------------------------------------------- #

#Constants
I3C_SET_TARGET_DEVICE_CONFIG_RES_LENGTH 		    = INTERRUPT_IN_ENDPOINT_SIZE
I3C_SET_TARGET_DEVICE_CONFIG_RES_HEADER_LENGTH      = 6
I3C_SET_TARGET_DEVICE_CONFIG_RES_DATA_LENGTH        = I3C_SET_TARGET_DEVICE_CONFIG_RES_LENGTH - I3C_SET_TARGET_DEVICE_CONFIG_RES_HEADER_LENGTH

# Union array
I3cSetTargetDevConfigResponseArray_t                = c_uint8 * I3C_SET_TARGET_DEVICE_CONFIG_RES_LENGTH

# Union structure
class I3cSetTargetDevConfigResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("result", c_uint8),
                ("changesRequested", c_uint8),
                ("changesCompleted", c_uint8),
                ("unusedData", c_uint8 * I3C_SET_TARGET_DEVICE_CONFIG_RES_DATA_LENGTH) ]

# Union command
class I3cSetTargetDevConfigResponse_t(Union):
    _fields_ = [("data", I3cSetTargetDevConfigResponseArray_t ),
                ("fields", I3cSetTargetDevConfigResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cSetTargetDevConfigResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cSetTargetDevConfigError(self.fields.result).name,
            'changesRequested' : self.fields.changesRequested,
            'changesCompleted' : self.fields.changesCompleted,
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - IBI NOTIFICATION
#================================================================================#

MDB_INTERRUPT_GROUP_IDENTIFIER_MASK     = 0xE0
MDB_INTERRUPT_GROUP_IDENTIFIER_SHIFT    = 5

MDB_INTERRUPT_GROUP_IDENTIFIER = {
    0 : {
        'category' : "User defined.",
        'description' : "Defined by the vendor and reserved for vendor definition."
    },

    1 : {
        'category' : "I3C WG.",
        'description' : "Defined and interpreted based on some reserved values allocated by MIPI Alliance I3C WG. \
                         Indicates that the interrupt is related to a specific functionality."
    },

    2 : {
        'category' : "MIPI Groups.",
        'description' : "Allocated and reserved by MIPI Alliance Working Groups. Indicates that the interrupt is \
                         generated by a Device that wants to send a specific MIPI Alliance WG-related interrupt."
    },

    3 : {
        'category' : "Non MIPI reserved.",
        'description' : "Allocated for uses outside of MIPI Alliance."
    },

    4 : {
        'category' : "Timing information.",
        'description' : "Vendor reserved. May have any value defined by the vendor."
    },

    5 : {
        'category' : "Pending Read Notification.",
        'description' : "Indicates that the interrupt is generated by a Device that wants to send a specific \
                        MIPI Alliance WG-related or vendor-specific interrupt, and has a data message that will \
                        be returned on the next Private Read if ACKed."
    }
}

# Index of the IBI type of the response sent to the USB host
IBI_TYPE_INDEX          = 5

class I3cIbiType(Enum):
    '''
    This enum represents the In-Band Interrupt request type.

    This value is read from MSTATUS register.
    '''
    IBI_NONE            = 0
    IBI_NORMAL          = 1
    IBI_MASTER_REQUEST  = 2
    IBI_HOT_JOIN        = 3

class I3cIbiResponse(Enum):
    '''
    This enum respresents the In-Band Interrupt response type.

    This value is set in the MCTRL register to respond the IBI request manually.
    '''
    IBI_ACKED               = 0
    IBI_NACKED              = 1
    IBI_ACKED_WITH_PAYLOAD  = 2
    IBI_MANUAL              = 3

# Constants
I3C_IBI_NOTIFICATION_LENGTH 		= INTERRUPT_IN_ENDPOINT_SIZE
I3C_IBI_NOTIFICATION_HEADER_LENGTH  = 11
I3C_IBI_NOTIFICATION_PAYLOAD_LENGTH = I3C_IBI_NOTIFICATION_LENGTH - I3C_IBI_NOTIFICATION_HEADER_LENGTH

# Union array
I3cIbiNotificationArray_t           = c_uint8 * I3C_IBI_NOTIFICATION_LENGTH

# Structure that contains the I3C Transfer Header.
class I3cIbiNotificationHeader_t(Structure):
    _pack_ = 1
    _fields_ = [("tag", c_uint8),
                ("address", c_uint8),
                ("type", c_uint8),
                ("response", c_uint8),
                ("hasData", c_uint8),
                ("length", c_uint8),
                ("status", c_uint16) ]

    def toDictionary(self) -> dict:
        return {
            'tag' : I3cTransferResponseTag(self.tag).name,
            'address' : self.address,
            'type' : I3cIbiType(self.type).name,
            'response' : I3cIbiResponse(self.response).name,
            'hasData' : bool(self.hasData),
            'length' : self.length,
            'status' : self.status
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# Union structure
class I3cIbiNotificationFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("header", I3cIbiNotificationHeader_t),
                ("payload", c_uint8 * I3C_IBI_NOTIFICATION_PAYLOAD_LENGTH) ]

# Union command
class I3cIbiNotification_t(Union):
    _fields_ = [("data", I3cIbiNotificationArray_t ),
                ("fields", I3cIbiNotificationFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'header' : self.fields.header.toDictionary(),
            'MDB' : {
                'value' : self.fields.payload[0],
                'description' : MDB_INTERRUPT_GROUP_IDENTIFIER[ ( (self.fields.payload[0] &  MDB_INTERRUPT_GROUP_IDENTIFIER_MASK) >> MDB_INTERRUPT_GROUP_IDENTIFIER_SHIFT ) ]
            },
            'payload' : list(self.fields.payload)
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

class I3cHotJoinIbiNotification_t(Union):
    _fields_ = [("data", I3cIbiNotificationArray_t ),
                ("fields", I3cIbiNotificationFields_t )]

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'header' : self.fields.header.toDictionary(),
            'pid' : [ f'{self.fields.payload[i]:#04x}' for i in range(I3C_PID_SIZE) ],
            'bcr' : self.fields.payload[6],
            'dcr' : self.fields.payload[7]
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
    
#================================================================================#
# I3C - INITIALIZE SUPERNOVA IN CONTROLLER MODE
#================================================================================#

# Request ---------------------------------------------------------------------- #
    
#Constants
I3C_CONTROLLER_INIT_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CONTROLLER_INIT_REQ_HEADER_LENGTH           = 3
I3C_CONTROLLER_INIT_REQ_UNUSED_DATA_LENGTH      = I3C_CONTROLLER_INIT_REQ_LENGTH - I3C_CONTROLLER_INIT_REQ_HEADER_LENGTH

# Union array
I3cControllerInitRequestArray_t                 = c_uint8 * (I3C_CONTROLLER_INIT_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cControllerInitRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("unusedData", c_uint8 * I3C_CONTROLLER_INIT_REQ_UNUSED_DATA_LENGTH)]

# Union command
class I3cControllerInitRequest_t(Union):
    _fields_ = [("data", I3cControllerInitRequestArray_t ),
                ("fields", I3cControllerInitRequestFields_t )]

# Result  ------------------------------------------------------------------------------- #

#Constants
I3C_CONTROLLER_INIT_RESPONSE_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_CONTROLLER_INIT_RESPONSE_HEADER_LENGTH          = 4
I3C_CONTROLLER_INIT_RESPONSE_UNUSED_DATA_LENGTH 	= (I3C_CONTROLLER_INIT_RESPONSE_LENGTH - I3C_CONTROLLER_INIT_RESPONSE_HEADER_LENGTH)

class I3cControllerInitResult_t(Enum):
	I3C_CONTROLLER_INIT_SUCCESS = 0x00
	I3C_CONTROLLER_INIT_ERROR   = 0x01

# Union array
I3cControllerInitResponseArray_t                = c_uint8 * (I3C_CONTROLLER_INIT_RESPONSE_LENGTH)

# Union structure
class I3cControllerInitResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("unusedData", c_uint8 * I3C_CONTROLLER_INIT_RESPONSE_UNUSED_DATA_LENGTH)]
    
# Union command
class I3cControllerInitResponse_t(Union):
    _fields_ = [("data", I3cControllerInitResponseArray_t),
                ("fields", I3cControllerInitResponseFields_t)]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cControllerInitResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
    
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cControllerInitResult_t(self.fields.result).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - INITIALIZE SUPERNOVA IN TARGET MODE
#================================================================================#

# Target configuration masks
I3C_OFFLINE_MASK        = 0x01
PART_NO_RANDOM_MASK     = 0x02
DDR_OK_MASK             = 0x04
IGNORE_ERRORS_MASK      = 0x08
MATCH_START_STOP_MASK   = 0x10
ALWAYS_NACK_MASK        = 0x20

# Target configuration shifts
I3C_OFFLINE_SHIFT           = 0x00
PART_NO_RANDOM_SHIFT        = 0x01
DDR_OK_SHIFT                = 0x02
IGNORE_ERRORS_SHIFT         = 0x03
MATCH_START_STOP_SHIFT      = 0x04
ALWAYS_NACK_SHIFT           = 0x05

# Request ---------------------------------------------------------------------- #

# Structure that contains the I3C Target Configuration for the Supernova in target mode
class I3cTargetFeatures_t(Structure):
    _pack_ = 1
    _fields_ = [("i3cOffline", c_uint8, 1),
                ("partNOrandom", c_uint8, 1),
                ("ddrOk", c_uint8, 1),          
                ("ignoreTE0TE1Errors", c_uint8, 1),
                ("matchStartStop", c_uint8, 1),
                ("alwaysNack", c_uint8, 1),
                ("reserved", c_uint8, 2)]

    def toDictionary(self) -> dict:
         return {
            'i3cOffline' : self.i3cOffline,
            'partNOrandom' : self.partNOrandom,
            'ddrOk' : self.ddrOk,
            'ignoreTE0TE1Errors' : self.ignoreTE0TE1Errors,
            'matchStartStop' : self.matchStartStop,
            'alwaysNack' : self.alwaysNack,
        }
    
# Constants
I3C_TARGET_INIT_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_INIT_REQ_HEADER_LENGTH           = 3
I3C_TARGET_INIT_REQ_CONFIGURATION_LENGTH    = 7
I3C_TARGET_INIT_REQ_UNUSED_DATA_LENGTH      = I3C_TARGET_INIT_REQ_LENGTH - I3C_TARGET_INIT_REQ_HEADER_LENGTH - I3C_TARGET_INIT_REQ_CONFIGURATION_LENGTH

# Union array
I3cTargetInitRequestArray_t                 = c_uint8 * (I3C_TARGET_INIT_REQ_LENGTH + 1)                       # Command length + endpoint ID.

class I3cTargetMemoryLayout_t(Enum):
    '''
    Different memory layouts the Supernova as an I3C target can represent
    '''
    MEM_1_BYTE  = 0x00
    MEM_2_BYTES = 0x01
    MEM_4_BYTES = 0x02

# Union structure
class I3cTargetInitRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("memoryLayout", c_uint8),
                ("uSecondsToWaitForIbi", c_uint8),
                ("maxReadLength", c_uint16),
                ("maxWriteLength", c_uint16),
                ("targetFeatures", I3cTargetFeatures_t),
                ("unusedData", c_uint8 * I3C_TARGET_INIT_REQ_UNUSED_DATA_LENGTH)]

# Union command
class I3cTargetInitRequest_t(Union):
    _fields_ = [("data", I3cTargetInitRequestArray_t ),
                ("fields", I3cTargetInitRequestFields_t )]

# Result  ------------------------------------------------------------------------------- #

#Constants
I3C_TARGET_INIT_RESPONSE_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_INIT_RESPONSE_HEADER_LENGTH          = 4
I3C_TARGET_INIT_RESPONSE_UNUSED_DATA_LENGTH 	= (I3C_TARGET_INIT_RESPONSE_LENGTH - I3C_TARGET_INIT_RESPONSE_HEADER_LENGTH)

class I3cTargetInitResult_t(Enum):
	I3C_TARGET_INIT_SUCCESS = 0x00
	I3C_TARGET_INIT_ERROR   = 0x01

# Union array
I3cTargetInitResponseArray_t                = c_uint8 * (I3C_TARGET_INIT_RESPONSE_LENGTH)

# Union structure
class I3cTargetInitResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("unusedData", c_uint8 * I3C_TARGET_INIT_RESPONSE_UNUSED_DATA_LENGTH )]
    
# Union command
class I3cTargetInitResponse_t(Union):
    _fields_ = [("data", I3cTargetInitResponseArray_t),
                ("fields", I3cTargetInitResponseFields_t )]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cTargetInitResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
    
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cTargetInitResult_t(self.fields.result).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - TARGET SET CONFIGURATION
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_TARGET_SET_CONF_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_SET_CONF_REQ_HEADER_LENGTH           = 3
I3C_TARGET_SET_CONF_REQ_CONFIGURATION_LENGTH    = 6
I3C_TARGET_SET_CONF_REQ_UNUSED_DATA_LENGTH      = I3C_TARGET_SET_CONF_REQ_LENGTH - I3C_TARGET_SET_CONF_REQ_HEADER_LENGTH - I3C_TARGET_SET_CONF_REQ_CONFIGURATION_LENGTH

# Union array
I3cTargetSetConfRequestArray_t                 = c_uint8 * (I3C_TARGET_SET_CONF_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cTargetSetConfRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("uSecondsToWaitForIbi", c_uint8),
                ("maxReadLength", c_uint16),
                ("maxWriteLength", c_uint16),
                ("targetFeatures", I3cTargetFeatures_t),
                ("unusedData", c_uint8 * I3C_TARGET_SET_CONF_REQ_UNUSED_DATA_LENGTH)]

# Union command
class I3cTargetSetConfRequest_t(Union):
    _fields_ = [("data", I3cTargetSetConfRequestArray_t ),
                ("fields", I3cTargetSetConfRequestFields_t )]

# Result  ------------------------------------------------------------------------------- #

#Constants
I3C_TARGET_SET_CONF_RESPONSE_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_SET_CONF_RESPONSE_HEADER_LENGTH          = 4
I3C_TARGET_SET_CONF_RESPONSE_UNUSED_DATA_LENGTH 	= (I3C_TARGET_SET_CONF_RESPONSE_LENGTH - I3C_TARGET_SET_CONF_RESPONSE_HEADER_LENGTH)

class I3cTargetSetConfResult_t(Enum):
	I3C_TARGET_SET_CONF_SUCCESS = 0x00
	I3C_TARGET_SET_CONF_ERROR   = 0x01

# Union array
I3cTargetSetConfResponseArray_t                = c_uint8 * (I3C_TARGET_SET_CONF_RESPONSE_LENGTH)

# Union structure
class I3cTargetSetConfResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("unusedData", c_uint8 * I3C_TARGET_SET_CONF_RESPONSE_UNUSED_DATA_LENGTH)]
    
# Union command
class I3cTargetSetConfResponse_t(Union):
    _fields_ = [("data", I3cTargetSetConfResponseArray_t),
                ("fields", I3cTargetSetConfResponseFields_t)]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cTargetSetConfResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
    
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cTargetSetConfResult_t(self.fields.result).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - TARGET MEMORY WRITE
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_TARGET_WRITE_MEM_REQ_LENGTH 		         = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_WRITE_MEM_REQ_HEADER_LENGTH           = 3
I3C_TARGET_WRITE_MEM_REQ_DESC_LENGTH             = 4
I3C_TARGET_WRITE_MEM_REQ_DATA_LENGTH             = I3C_TARGET_WRITE_MEM_REQ_LENGTH - I3C_TARGET_WRITE_MEM_REQ_HEADER_LENGTH - I3C_TARGET_WRITE_MEM_REQ_DESC_LENGTH

# MSB of the memory address to work with using I3C_TARGET_MEMORY_WRITE, indicates if all the data is sent to the Supernova or not (so that the response that comes from the firmware then indicates the error)
I3C_TARGET_MEMORY_LESS_DATA_MASK		         = 0x8000

# Union array
I3cTargetWriteMemRequestArray_t                  = c_uint8 * (I3C_TARGET_WRITE_MEM_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cTargetWriteMemRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("memoryAddress", c_uint16),
                ("length", c_uint16),
                ("dataBlock", c_uint8 * I3C_TARGET_WRITE_MEM_REQ_DATA_LENGTH) ]

# Union command
class I3cTargetWriteMemRequest_t(Union):
    _fields_ = [("data", I3cTargetWriteMemRequestArray_t ),
                ("fields", I3cTargetWriteMemRequestFields_t )]

# Result  ------------------------------------------------------------------------------- #

#Constants
I3C_TARGET_WRITE_MEM_RESPONSE_LENGTH 		         = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_WRITE_MEM_RESPONSE_HEADER_LENGTH          = 7
I3C_TARGET_WRITE_MEM_RESPONSE_UNUSED_DATA_LENGTH 	 = (I3C_TARGET_WRITE_MEM_RESPONSE_LENGTH - I3C_TARGET_WRITE_MEM_RESPONSE_HEADER_LENGTH)

class I3cTargetWriteMemResult_t(Enum):
	I3C_TARGET_WRITE_MEM_SUCCESS = 0x00
	I3C_TARGET_WRITE_MEM_ERROR   = 0x01
        
class I3cTargetMemError_t(Enum):
    NO_ERROR                    = 0x00
    SURPASSED_MEMORY_RANGE      = 0x01

# Union array
I3cTargetWriteMemResponseArray_t                = c_uint8 * (I3C_TARGET_WRITE_MEM_RESPONSE_LENGTH)

# Union structure
class I3cTargetWriteMemResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("error", c_uint8),
                ("dataWrittenLength", c_uint16),
                ("unusedData", c_uint8 * I3C_TARGET_WRITE_MEM_RESPONSE_UNUSED_DATA_LENGTH)]
    
# Union command
class I3cTargetWriteMemResponse_t(Union):
    _fields_ = [("data", I3cTargetWriteMemResponseArray_t),
                ("fields", I3cTargetWriteMemResponseFields_t)]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cTargetWriteMemResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
    
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cTargetWriteMemResult_t(self.fields.result).name,
            'error' : I3cTargetMemError_t(self.fields.error).name,
            'command' : self.fields.cmd
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - TARGET MEMORY READ
#================================================================================#

# Request ---------------------------------------------------------------------- #

#Constants
I3C_TARGET_READ_MEM_REQ_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_READ_MEM_REQ_HEADER_LENGTH           = 3
I3C_TARGET_READ_MEM_REQ_CONF_LENGTH             = 4
I3C_TARGET_READ_MEM_REQ_UNUSED_DATA_LENGTH      = I3C_TARGET_READ_MEM_REQ_LENGTH - I3C_TARGET_READ_MEM_REQ_HEADER_LENGTH - I3C_TARGET_READ_MEM_REQ_CONF_LENGTH

# Union array
I3cTargetReadMemRequestArray_t                  = c_uint8 * (I3C_TARGET_READ_MEM_REQ_LENGTH + 1)                       # Command length + endpoint ID.

# Union structure
class I3cTargetReadMemRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8 ),
                ("memoryAddress", c_uint16),
                ("length", c_uint16),
                ("unusedData", c_uint8 * I3C_TARGET_READ_MEM_REQ_UNUSED_DATA_LENGTH)]

# Union command
class I3cTargetReadMemRequest_t(Union):
    _fields_ = [("data", I3cTargetReadMemRequestArray_t ),
                ("fields", I3cTargetReadMemRequestFields_t )]

# Result  ------------------------------------------------------------------------------- #

#Constants
I3C_TARGET_READ_MEM_RESPONSE_LENGTH 		         = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_READ_MEM_RESPONSE_HEADER_LENGTH           = 3
I3C_TARGET_READ_MEM_RESPONSE_RESULT_LENGTH           = 4
I3C_TARGET_READ_MEM_RESPONSE_DATA_LENGTH 	         = (I3C_TARGET_READ_MEM_RESPONSE_LENGTH - I3C_TARGET_READ_MEM_RESPONSE_HEADER_LENGTH - I3C_TARGET_READ_MEM_RESPONSE_RESULT_LENGTH)

class I3cTargetReadMemResult_t(Enum):
	I3C_TARGET_READ_MEM_SUCCESS = 0x00
	I3C_TARGET_READ_MEM_ERROR   = 0x01

# Union array
I3cTargetReadMemResponseArray_t                = c_uint8 * (I3C_TARGET_READ_MEM_RESPONSE_LENGTH)

# Union structure
class I3cTargetReadMemResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("result", c_uint8),
                ("error", c_uint8),
                ("dataLength", c_uint16),
                ("readData", c_uint8 * I3C_TARGET_READ_MEM_RESPONSE_DATA_LENGTH)]
    
# Union command
class I3cTargetReadMemResponse_t(Union):
    _fields_ = [("data", I3cTargetReadMemResponseArray_t),
                ("fields", I3cTargetReadMemResponseFields_t)]

    def set(self, data) -> bool:
        '''
        This function set the ctypes Array data from a data buffer.
        '''
        self.data = I3cTargetReadMemResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
    
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'result' : I3cTargetReadMemResult_t(self.fields.result).name,
            'error' : I3cTargetMemError_t(self.fields.error).name,
            'dataLength' : self.fields.dataLength,
            'readData' : list(self.fields.readData)

        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# I3C - TARGET NOTIFICATION
#================================================================================#

class I3cTargetTransferType_t(Enum):
    '''
    This enum represents the type of transfer when the Supernova acts an I3C target
    '''
    I3C_TARGET_WRITE    = 1
    I3C_TARGET_READ     = 2

# Constants
I3C_TARGET_NOTIFICATION_LENGTH 		            = INTERRUPT_IN_ENDPOINT_SIZE
I3C_TARGET_NOTIFICATION_HEADER_LENGTH           = 3
I3C_TARGET_NOTIFICATION_RESULT_LENGTH           = 10
I3C_TARGET_NOTIFICATION_DATA_LENGTH             = I3C_TARGET_NOTIFICATION_LENGTH - I3C_TARGET_NOTIFICATION_HEADER_LENGTH - I3C_TARGET_NOTIFICATION_RESULT_LENGTH

# Union array
I3cTargetNotificationArray_t                    = c_uint8 * I3C_TARGET_NOTIFICATION_LENGTH

# Union structure
class I3cTargetNotificationFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("transferError", ErrorStatus_t),
                ("typeOfTransfer", c_uint8),
                ("targetAddress", c_uint8),
                ("memoryAddress", c_uint16),
                ("transferLength", c_uint16),
                ("payload", c_uint8 * I3C_TARGET_NOTIFICATION_DATA_LENGTH)]

# Union command
class I3cTargetNotification_t(Union):
    _fields_ = [("data", I3cTargetNotificationArray_t ),
                ("fields", I3cTargetNotificationFields_t )]
      
#================================================================================#
# I3C RESPONSES - HIGH LEVEL ABSTRACTION
#================================================================================#

#================================================================================#
# HLA RESPONSE - I3C GET TARGET DEVICE TABLE
#================================================================================#

class I3cGetTargetDeviceTableHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.numberOfTargets = 0x00
        self.table = []

    def set(self, data) -> bool:

        response = I3cGetTargetDeviceTableResponse_t.from_buffer_copy(data)

        # Header
        self.id         = response.fields.id
        self.command    = response.fields.cmd
        self.name       = COMMANDS_DICTIONARY[response.fields.cmd]["name"]

        if (response.fields.numberOfDevices <= I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER):
            iterations = response.fields.numberOfDevices
        else:
            iterations = I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER

        targets = []

        for i in range(iterations):
            targets.append(response.fields.i3cTargetDeviceEntries[i].toDictionary())

        if (response.fields.numberOfDevices <= I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER):
            self.numberOfTargets += response.fields.numberOfDevices
            self.table += targets
            return True
        else:
            # Append paylad, increment paylaod length, and wait for pending responses.
            self.numberOfTargets += I3C_GET_TABLE_MAX_NUMBER_TARGETS_PER_TRANSFER
            self.table += targets
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : self.name,
            'numberOfTargets' : self.numberOfTargets,
            'table' : self.table
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - I3C TRANSFER
#================================================================================#

class I3cTransferHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = {
            'dataLength' : 0x00,
            'errors' : []
        }
        self.data = []

    def set(self, data) -> bool:

        response = I3cTransferResponse_t.from_buffer_copy(data)

        # Header
        self.id         = response.fields.id
        self.command    = response.fields.cmd
        self.name       = COMMANDS_DICTIONARY[response.fields.cmd]["name"]
        self.header     = response.fields.header

        self.descriptor["errors"] = [ error.name for error in I3cTransferError if (error.value & response.fields.descriptor.errorStatus) ]
        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(self.descriptor["errors"]) == 0 ):
            self.descriptor["errors"].append(I3cTransferError.NO_TRANSFER_ERROR.name)

        # Payload
        payload = list(response.fields.dataBlock)

        if (response.fields.descriptor.dataLength <= I3C_TRANSFER_RES_DATA_LENGTH):
            self.descriptor["dataLength"] += response.fields.descriptor.dataLength
            self.data += payload[:response.fields.descriptor.dataLength]
            return True
        else:
            # Append payload, increment payload length, and wait for pending responses.
            self.descriptor["dataLength"] += I3C_TRANSFER_RES_DATA_LENGTH
            self.data += payload
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : self.name,
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor,
            'data' : self.data
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETBCR
#================================================================================#

class I3cGetBcrHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.bcr = I3cBcrRegister_t()

    def set(self, data) -> bool:

        response = I3cTransferResponse_t.from_buffer_copy(data)

        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor
        self.bcr.byte = response.fields.dataBlock[0]
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'bcr' : self.bcr.toDictionary()
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETDCR
#================================================================================#

class I3cGetDcrHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.dcr = 0x00

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor
        self.dcr = response.fields.dataBlock[0]
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'dcr' :  f'{self.dcr:#04x}'
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETPID
#================================================================================#

class I3cGetPidHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.pid = I3cPIDRegister_t()

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor

        self.pid.data[0:6] = response.fields.dataBlock[0:6]

        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'pid' :[ f'{self.pid.bytes.PID_5:#04x}', f'{self.pid.bytes.PID_4:#04x}', f'{self.pid.bytes.PID_3:#04x}', f'{self.pid.bytes.PID_2:#04x}' , f'{self.pid.bytes.PID_1:#04x}', f'{self.pid.bytes.PID_0:#04x}' ]
        }

    def __str__(self) -> str:
        return str(self.toDictionary())


#================================================================================#
# HLA RESPONSE - GETMXDS
#================================================================================#

# maxWr byte format

GETMXDS_MAX_WR = {
    'maxSustainedDataRate' : {
        0 : "fSCL Max (default value)",
        1 : "8 MHz",
        2 : "6 MHz",
        3 : "4 MHz",
        4 : "2 MHz",
        5 : "Reserved for future use by MIPI Alliance",
        6 : "Reserved for future use by MIPI Alliance",
        7 : "Reserved for future use by MIPI Alliance"
    },

    'definingByteSupport' : {
        0 : 'Defining byte not supported',
        1 : 'Defining bute supported. ControlLer can perform GETMXDS Format 3.'
    },

    'reserved' : "Reserved for future use by MIPI Alliance"
}

class I3cGetmxdsMaxWrBitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("maxSustainedDataRate", c_uint8, 3),
                ("definingByteSupport", c_uint8, 1),
                ("reserved", c_uint8, 4)]

class I3cGetmxdsMaxWrByte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetmxdsMaxWrBitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'maxSustainedDataRate' : GETMXDS_MAX_WR['maxSustainedDataRate'][self.bits.maxSustainedDataRate],
                'definingByteSupport' : GETMXDS_MAX_WR['definingByteSupport'][self.bits.definingByteSupport],
                'reserved' : GETMXDS_MAX_WR['reserved'],
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# maxRd byte format

GETMXDS_MAX_RD = {
    'maxSustainedDataRate' : {
        0 : "fSCL Max (default value)",
        1 : "8 MHz",
        2 : "6 MHz",
        3 : "4 MHz",
        4 : "2 MHz",
        5 : "Reserved for future use by MIPI Alliance",
        6 : "Reserved for future use by MIPI Alliance",
        7 : "Reserved for future use by MIPI Alliance"
    },

    'clockToDataTurnaroundTime' : {
        0 : "fSCL Max (default value)",
        1 : "8 MHz",
        2 : "6 MHz",
        3 : "4 MHz",
        4 : "2 MHz",
        5 : "Reserved for future use by MIPI Alliance",
        6 : "Reserved for future use by MIPI Alliance",
        7 : "Tsco is > 12 ns, and is reported by private agreement"
    },

    'writeToReadPermitsStopBetween' : {
        0 : "STOP would cancel the Read",
        1 : "The Target permits the Write-to-Read to be split by a STOP"
    },

    'reserved' : "Reserved for future use by MIPI Alliance"
}

class I3cGetmxdsMaxRdBitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("maxSustainedDataRate", c_uint8, 3),
                ("clockToDataTurnaroundTime", c_uint8, 3),
                ("writeToReadPermitsStopBetween", c_uint8, 1),
                ("reserved", c_uint8, 1), ]

class I3cGetmxdsMaxRdByte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetmxdsMaxRdBitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'maxSustainedDataRate' : GETMXDS_MAX_RD['maxSustainedDataRate'][self.bits.maxSustainedDataRate],
                'clockToDataTurnaroundTime' : GETMXDS_MAX_RD['clockToDataTurnaroundTime'][self.bits.clockToDataTurnaroundTime],
                'writeToReadPermitsStopBetween' : GETMXDS_MAX_RD['writeToReadPermitsStopBetween'][self.bits.writeToReadPermitsStopBetween],
                'reserved' : GETMXDS_MAX_RD['reserved'],
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# maxRdTurn byte
I3cGetmxdsMaxRdTurn_t = c_uint8 * 3

class I3cGetmxdsHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.maxWr = I3cGetmxdsMaxWrByte_t()
        self.maxRd = I3cGetmxdsMaxRdByte_t()
        self.maxRdTurn = I3cGetmxdsMaxRdTurn_t()

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        # Header
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor
        # MaxWr byte
        self.maxWr.byte = response.fields.dataBlock[0]
        # MaxRd byte
        self.maxRd.byte = response.fields.dataBlock[1]
        # MaxRd turnaround
        self.maxRdTurn[0] = response.fields.dataBlock[2]
        self.maxRdTurn[1] = response.fields.dataBlock[3]
        self.maxRdTurn[2] = response.fields.dataBlock[4]
        return True

    def toDictionary(self) -> dict:
        time_us = (self.maxRdTurn[2] | self.maxRdTurn[1] << 8 | self.maxRdTurn[0] << 16)
        time_ms = time_us / 1000.0

        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'maxWr' : self.maxWr.toDictionary(),
            'maxRd' : self.maxRd.toDictionary(),
            'maxRdTurn' : [f'{time_us:d} us', f'{time_ms:6f} ms']
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
        
#================================================================================#
# HLA RESPONSE - GETMRL
#================================================================================#

I3cGetmrlMaxReadLength_t     = c_uint8 * 2
I3cGetmrlMaxIbiPayloadSize_t = c_uint8 * 5

class I3cGetmrlHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.maxReadLength = I3cGetmrlMaxReadLength_t()
        self.maxIbiPayloadSize = I3cGetmrlMaxIbiPayloadSize_t()

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        # Header
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor

        # Max Read Length
        self.maxReadLength[0]     = response.fields.dataBlock[0]
        self.maxReadLength[1]     = response.fields.dataBlock[1]

        # Max IBI Payload Size
        self.maxIbiPayloadSize[0] = response.fields.dataBlock[2]
        self.maxIbiPayloadSize[1] = response.fields.dataBlock[3]
        self.maxIbiPayloadSize[2] = response.fields.dataBlock[4]
        self.maxIbiPayloadSize[3] = response.fields.dataBlock[5]
        self.maxIbiPayloadSize[4] = response.fields.dataBlock[6]

        return True

    def toDictionary(self) -> dict:

        maxReadLength       = (self.maxReadLength[0]<<8 | self.maxReadLength[1])
        maxIbiPayloadSize   = [self.maxIbiPayloadSize[0], self.maxIbiPayloadSize[1], self.maxIbiPayloadSize[2], self.maxIbiPayloadSize[3], self.maxIbiPayloadSize[4] ]

        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'maxReadLength' : maxReadLength,
            'maxIbiPayloadSize' : maxIbiPayloadSize
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETMWL
#================================================================================#

I3cGetmrlMaxWriteLength_t     = c_uint8 * 2

class I3cGetmwlHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.maxWriteLength = I3cGetmrlMaxWriteLength_t()

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        # Header
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor

        # Max Write Length
        self.maxWriteLength[0]     = response.fields.dataBlock[0]
        self.maxWriteLength[1]     = response.fields.dataBlock[1]

        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'maxWriteLength' : (self.maxWriteLength[0]<<8 | self.maxWriteLength[1]),
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETXTIME
#================================================================================#

# Supported Modes Byte

GETXTIME_SUPPORTED_MODES_BYTE = {
    'syncMode' : {
        0 : "Not support Sync Mode (Not included in I3C Basic)",
        1 : "Supports Sync Mode (Not included in I3C Basic)",
    },

    'asyncMode0' : {
        0 : "Not support Async Mode 0",
        1 : "Supports Async Mode 0",
    },

    'asyncMode1' : {
        0 : "Not support Async Mode 1 (Not included in I3C Basic)",
        1 : "Supports Async Mode 1 (Not included in I3C Basic)",
    },

    'asyncMode2' : {
        0 : "Not support Async Mode 2 (Not included in I3C Basic)",
        1 : "Supports Async Mode 2 (Not included in I3C Basic)",
    },

    'asyncMode3' : {
        0 : "Not support Async Mode 3 (Not included in I3C Basic)",
        1 : "Supports Async Mode 3 (Not included in I3C Basic)",
    },

    'reserved' : "Reserved"
}

class I3cGetxtimeSupportedModesBitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("syncMode", c_uint8, 1),
                ("asyncMode0", c_uint8, 1),
                ("asyncMode1", c_uint8, 1),
                ("asyncMode2", c_uint8, 1),
                ("asyncMode3", c_uint8, 1),
                ("reserved", c_uint8, 3) ]

class I3cGetxtimeSupportedModesByte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetxtimeSupportedModesBitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'syncMode' : GETXTIME_SUPPORTED_MODES_BYTE['syncMode'][self.bits.syncMode],
                'asyncMode0' : GETXTIME_SUPPORTED_MODES_BYTE['asyncMode0'][self.bits.asyncMode0],
                'asyncMode1' : GETXTIME_SUPPORTED_MODES_BYTE['asyncMode1'][self.bits.asyncMode1],
                'asyncMode2' : GETXTIME_SUPPORTED_MODES_BYTE['asyncMode2'][self.bits.asyncMode2],
                'asyncMode3' : GETXTIME_SUPPORTED_MODES_BYTE['asyncMode3'][self.bits.asyncMode3],
                'reserved' : GETXTIME_SUPPORTED_MODES_BYTE['reserved'],
            }
        }

GETXTIME_STATE_BYTE = {
    'syncMode' : {
        0 : "Not enabled (Not included in I3C Basic)",
        1 : "Enabled  (Not included in I3C Basic)",
    },

    'asyncMode0' : {
        0 : "Not enabled Async Mode 0",
        1 : "Enabled Async Mode 0",
    },

    'asyncMode1' : {
        0 : "Not enabled Async Mode 1 (Not included in I3C Basic)",
        1 : "Enabled Async Mode 1 (Not included in I3C Basic)",
    },

    'asyncMode2' : {
        0 : "Not enabled Async Mode 2 (Not included in I3C Basic)",
        1 : "Enabled Async Mode 2 (Not included in I3C Basic)",
    },

    'asyncMode3' : {
        0 : "Not enabled Async Mode 3 (Not included in I3C Basic)",
        1 : "Enabled Async Mode 3 (Not included in I3C Basic)",
    },

    'reserved' : "Reserved",

    'overflow' : {
        0 : "Target hasn't experienced a counter overflow since the most recent previous check.",
        1 : "Target has experienced a counter overflow since the most recent previous check.",
    },

}

class I3cGetxtimeStateBitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("syncMode", c_uint8, 1),
                ("asyncMode0", c_uint8, 1),
                ("asyncMode1", c_uint8, 1),
                ("asyncMode2", c_uint8, 1),
                ("asyncMode3", c_uint8, 1),
                ("reserved", c_uint8, 2),
                ("overflow", c_uint8, 1) ]

class I3cGetxtimeStateByte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetxtimeStateBitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'syncMode' : GETXTIME_STATE_BYTE['syncMode'][self.bits.syncMode],
                'asyncMode0' : GETXTIME_STATE_BYTE['asyncMode0'][self.bits.asyncMode0],
                'asyncMode1' : GETXTIME_STATE_BYTE['asyncMode1'][self.bits.asyncMode1],
                'asyncMode2' : GETXTIME_STATE_BYTE['asyncMode2'][self.bits.asyncMode2],
                'asyncMode3' : GETXTIME_STATE_BYTE['asyncMode3'][self.bits.asyncMode3],
                'reserved' : GETXTIME_STATE_BYTE['reserved'],
                'overflow' : GETXTIME_STATE_BYTE['overflow'][self.bits.overflow],
            }
        }

I3C_GETXTIME_FREQUENCY_INCREMENT  = 0.5 # MHz
I3C_GETXTIME_INACCURACY_INCREMENT = 0.1 # %

class I3cGetxtimeHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.supportedModes = I3cGetxtimeSupportedModesByte_t()
        self.state = I3cGetxtimeStateByte_t()
        self.frequency = 0
        self.inaccuracy = 0

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        # Header
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor

        # Supported Modes Byte
        self.supportedModes.byte = response.fields.dataBlock[0]
        # State Byte
        self.state.byte = response.fields.dataBlock[1]
        # Frequency
        self.frequency = response.fields.dataBlock[2]
        # Inaccuracy
        self.inaccuracy = response.fields.dataBlock[3]

        return True

    def toDictionary(self) -> dict:

        # Calculate frequency.
        frequency = self.frequency * I3C_GETXTIME_FREQUENCY_INCREMENT

        # Define frequency value description.
        if frequency == 0.0:
            frequencyDescription = "The value 0 is an exception, and indicates an internal oscillator frequency of approximately 32 KHz."
        else:
            frequencyDescription = f'Target internal oscillator: {frequency:.1f} MHz'

        # Calculate frequency inaccuracy.
        inaccuracy = self.inaccuracy * I3C_GETXTIME_INACCURACY_INCREMENT

        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'supportedModes' : self.supportedModes.toDictionary(),
            'state' : self.state.toDictionary(),
            'frequency' : {
                'value' : self.frequency,
                'description' : frequencyDescription
            },
            'inaccuracy' : {
                'value' : self.inaccuracy,
                'description' : f'Maximum variation of the Target internal oscillator: {inaccuracy:.1f} %'
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETCAPS
#================================================================================#

# GETCAP1

GETCAP1 = {
    'hdrMode0' : {
        0 : "HDR Mode 0 (HDR-DDR) not supported",
        1 : "HDR Mode 0 (HDR-DDR) supported"
    },

    'hdrMode1' : {
        0 : "HDR Mode 1 not supported (Not included in I3C Basic)",
        1 : "HDR Mode 1 supported (Not included in I3C Basic)"
    },

    'hdrMode2' : {
        0 : "HDR Mode 2 not supported (Not included in I3C Basic)",
        1 : "HDR Mode 2 supported (Not included in I3C Basic)"
    },

    'hdrMode3' : {
        0 : "HDR Mode 3 (HDR-BT) not supported",
        1 : "HDR Mode 3 (HDR-BT) supported"
    },

    'hdrMode4' : {
        0 : "Reserved",
        1 : "Reserved"
    },

    'hdrMode5' : {
        0 : "Reserved",
        1 : "Reserved"
    },

    'hdrMode6' : {
        0 : "Reserved",
        1 : "Reserved"
    },

    'hdrMode7' : {
        0 : "Reserved",
        1 : "Reserved"
    }
}

class I3cGetcapsCap1BitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("hdrMode0", c_uint8, 1),
                ("hdrMode1", c_uint8, 1),
                ("hdrMode2", c_uint8, 1),
                ("hdrMode3", c_uint8, 1),
                ("hdrMode4", c_uint8, 1),
                ("hdrMode5", c_uint8, 1),
                ("hdrMode6", c_uint8, 1),
                ("hdrMode7", c_uint8, 1) ]

class I3cGetcapsCap1Byte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetcapsCap1BitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'hdrMode0' : GETCAP1['hdrMode0'][self.bits.hdrMode0],
                'hdrMode1' : GETCAP1['hdrMode1'][self.bits.hdrMode1],
                'hdrMode2' : GETCAP1['hdrMode2'][self.bits.hdrMode2],
                'hdrMode3' : GETCAP1['hdrMode3'][self.bits.hdrMode3],
                'hdrMode4' : GETCAP1['hdrMode4'][self.bits.hdrMode4],
                'hdrMode5' : GETCAP1['hdrMode5'][self.bits.hdrMode5],
                'hdrMode6' : GETCAP1['hdrMode6'][self.bits.hdrMode6],
                'hdrMode7' : GETCAP1['hdrMode7'][self.bits.hdrMode7],
            }
        }

# GETCAP2

GETCAP2 = {
    'i3cVersion' : {
        0  : "0 is an illegal value",
        1  : "Device complies with I3C Basic v1.1.1 or possible future v1.1.y",
        2  : "Device complies with possible future I3C Basic v1.2 or v1.2.y",
        3  : "Device complies with possible future I3C Basic v1.3 or v1.3.y",
        4  : "Device complies with possible future I3C Basic v1.4 or v1.4.y",
        5  : "Device complies with possible future I3C Basic v1.5 or v1.5.y",
        6  : "Device complies with possible future I3C Basic v1.6 or v1.6.y",
        7  : "Device complies with possible future I3C Basic v1.7 or v1.7.y",
        8  : "Device complies with possible future I3C Basic v1.8 or v1.8.y",
        9  : "Device complies with possible future I3C Basic v1.9 or v1.9.y",
        10 : "Device complies with possible future I3C Basic v1.10 or v1.10.y",
        11 : "Device complies with possible future I3C Basic v1.11 or v1.11.y",
        12 : "Device complies with possible future I3C Basic v1.12 or v1.12.y",
        13 : "Device complies with possible future I3C Basic v1.13 or v1.13.y",
        14 : "Device complies with possible future I3C Basic v1.14 or v1.14.y",
        15 : "Device complies with possible future I3C Basic v1.15 or v1.15.y"
    },

    'groupAddressCapabilities' : {
        0 : "Does not support Group Address function",
        1 : "Can be assigned one Group Address",
        2 : "Can be assigned two Group Addresses",
        3 : "Can be assigned three or more Group Addresses"
    },

    'hdrDrrWriteAbort' : {
        0 : "I3C Target is not capable of issuing the Write Abort in HDR-DDR Mode",
        1 : "I3C Target is capable of issuing the Write Abort in HDR-DDR Mode"
    },

    'hddrDdrAbortCRC' : {
        0 : "I3C Target is not capable of emitting the CRC Word when a transaction in HDR-DDR Mode is aborted",
        1 : "I3C Target is capable of emitting the CRC Word when a transaction in HDR-DDR Mode is aborted"
    }

}

class I3cGetcapsCap2BitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("i3cVersion", c_uint8, 4),
                ("groupAddressCapabilities", c_uint8, 2),
                ("hdrDrrWriteAbort", c_uint8, 1),
                ("hddrDdrAbortCRC", c_uint8, 1)]

class I3cGetcapsCap2Byte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetcapsCap2BitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'i3cVersion' : GETCAP2['i3cVersion'][self.bits.i3cVersion],
                'groupAddressCapabilities' : GETCAP2['groupAddressCapabilities'][self.bits.groupAddressCapabilities],
                'hdrDrrWriteAbort' : GETCAP2['hdrDrrWriteAbort'][self.bits.hdrDrrWriteAbort],
                'hddrDdrAbortCRC' : GETCAP2['hddrDdrAbortCRC'][self.bits.hddrDdrAbortCRC]
            }
        }

# GETCAP3

GETCAP3 = {
    'multiLaneDataTransferSupport' : {
        0 : "Multi-Lane (ML) Data Transfer not supported",
        1 : "Multi-Lane (ML) Data Transfer supported"
    },

    'devicetoDeviceTransferSupport' : "Device to Device Transfer (D2DXFER) Support not included in the I3C Basic Specification.",

    'devicetoDeviceTransferIbiCapable' : "Device to Device Transfer (D2DXFER) IBI Capable not included in the I3C Basic Specification.",

    'GETCAPSdefiningByteSupport' : {
        0 : "I3C Target does not support an optional Defining Byte for the GETCAPS CCC",
        1 : "I3C Target supports an optional Defining Byte for the GETCAPS CCC"
    },

    'GETSTATUSdefiningByteSupport' : {
        0 : "I3C Target does not support an optional Defining Byte for the GETSTATUS CCC",
        1 : "I3C Target supports an optional Defining Byte for the GETSTATUS CCC"
    },

    'hdrBtCrc32support' : {
        0 : "I3C Target does not support CRC-32 data integrity verification in HDR Bulk Transport Mode",
        1 : "I3C Target supports CRC-32 data integrity verification in HDR Bulk Transport Mode"
    },

    'ibiMdbSupportForPendingReadNotification' : {
        0 : "I3C Target does not expect that it can send In-Band Interrupt requests with a specific range of Mandatory Data Byte values to indicate a Pending Read Notification",
        1 : "I3C Target expects that it can send In-Band Interrupt requests with a specific range of Mandatory Data Byte values to indicate a Pending Read Notification"
    },

    'reserved' : "Reserved for future definition by MIPI Alliance I3C WG"
}

class I3cGetcapsCap3BitFields_t(Structure):
    _pack_ = 1
    _fields_ = [("multiLaneDataTransferSupport", c_uint8, 1),
                ("devicetoDeviceTransferSupport", c_uint8, 1),
                ("devicetoDeviceTransferIbiCapable", c_uint8, 1),
                ("GETCAPSdefiningByteSupport", c_uint8, 1),
                ("GETSTATUSdefiningByteSupport", c_uint8, 1),
                ("hdrBtCrc32support", c_uint8, 1),
                ("ibiMdbSupportForPendingReadNotification", c_uint8, 1),
                ("reserved", c_uint8, 1) ]

class I3cGetcapsCap3Byte_t(Union):
    _fields_ = [("byte", c_uint8 ),
                ("bits", I3cGetcapsCap3BitFields_t )]

    def toDictionary(self) -> dict:
        return {
            'value' : [f'{self.byte:#010b}', self.byte, f'{self.byte:#04x}'],
            'description' : {
                'multiLaneDataTransferSupport' : GETCAP3['multiLaneDataTransferSupport'][self.bits.multiLaneDataTransferSupport],
                'devicetoDeviceTransferSupport' : GETCAP3['devicetoDeviceTransferSupport'],
                'devicetoDeviceTransferIbiCapable' : GETCAP3['devicetoDeviceTransferIbiCapable'],
                'GETCAPSdefiningByteSupport' : GETCAP3['GETCAPSdefiningByteSupport'][self.bits.GETCAPSdefiningByteSupport],
                'GETSTATUSdefiningByteSupport' : GETCAP3['GETSTATUSdefiningByteSupport'][self.bits.GETSTATUSdefiningByteSupport],
                'hdrBtCrc32support' : GETCAP3['hdrBtCrc32support'][self.bits.hdrBtCrc32support],
                'ibiMdbSupportForPendingReadNotification' : GETCAP3['ibiMdbSupportForPendingReadNotification'][self.bits.ibiMdbSupportForPendingReadNotification],
                'reserved' : GETCAP3['reserved']
            }
        }

class I3cGetcapsHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.caps1 = I3cGetcapsCap1Byte_t()
        self.caps2 = I3cGetcapsCap2Byte_t()
        self.caps3 = I3cGetcapsCap3Byte_t()
        self.caps4 = 0

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        # Header
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor

        # Caps 1
        self.caps1.byte = response.fields.dataBlock[0]
        # Caps 1
        self.caps2.byte = response.fields.dataBlock[1]
        # Caps 1
        self.caps3.byte = response.fields.dataBlock[2]
       # Caps 1
        self.caps4 = response.fields.dataBlock[3]

        return True

    def toDictionary(self) -> dict:

        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'caps1' : self.caps1.toDictionary(),
            'caps2' : self.caps2.toDictionary(),
            'caps3' : self.caps3.toDictionary(),
            'caps4' : {
                'value' : self.caps4,
                'description' : "Reserved for future definition by MIPI Alliance I3C WG"
            }
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - GETACCCR
#================================================================================#

class I3cGetAcccrHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.header = I3cTransferResponseHeader_t()
        self.descriptor = I3cTransferResponseDescriptor_t()
        self.acccr = 0

    def set(self, data) -> bool:
        response = I3cTransferResponse_t.from_buffer_copy(data)
        self.id = response.fields.id
        self.cmd = response.fields.cmd
        self.header = response.fields.header
        self.descriptor = response.fields.descriptor
        self.acccr = response.fields.dataBlock[0]
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.cmd,
            'name' : COMMANDS_DICTIONARY[self.cmd]["name"],
            'header' : self.header.toDictionary(),
            'descriptor' : self.descriptor.toDictionary(),
            'acccr' : self.acccr
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - I3C TARGET READ MEMORY 
#================================================================================#

class I3cTargetReadMemHighLevelResponse_t:

    def __init__(self) -> None:
        self.id = 0x00
        self.command = 0x00
        self.name = ""
        self.result = I3cTargetReadMemResult_t.I3C_TARGET_READ_MEM_SUCCESS
        self.error = I3cTargetMemError_t.NO_ERROR
        self.readDataLength = 0x00
        self.data = []

    def set(self, data) -> bool:

        response = I3cTargetReadMemResponse_t.from_buffer_copy(data)

        # Header
        self.id                 = response.fields.id
        self.command            = response.fields.cmd
        self.name               = COMMANDS_DICTIONARY[response.fields.cmd]["name"]
        self.result             = response.fields.result
        self.error              = response.fields.error
        self.readDataLength     = response.fields.dataLength

        # Payload
        payload = list(response.fields.readData)

        if (response.fields.dataLength <= I3C_TARGET_READ_MEM_RESPONSE_DATA_LENGTH):
            self.data += payload[:response.fields.dataLength]
            self.readDataLength = len(self.data)
            return True
        else:
            # Append paylad, increment payload length, and wait for pending responses.
            self.data += payload
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : COMMANDS_DICTIONARY[self.command]["name"],
            'result' : I3cTargetReadMemResult_t(self.result).name,
            'error' : I3cTargetMemError_t(self.error).name,
            'readDataLength' : self.readDataLength,
            'data' : self.data
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA NOTIFICATION - I3C TARGET NOTIFICATION
#================================================================================#

class I3cTargetTransferResult_t(Enum):
    '''
    Represents the result of a transfer from the Supernova in I3C target mode
    '''
    I3C_TARGET_TRANSFER_SUCCESS     = 0
    I3C_TARGET_TRANSFER_FAIL        = 1

class I3cTargetTransferError_t(Enum):
    '''
    Represents the error of a transfer from the Supernova in I3C target mode
    '''
    NO_ERROR            = 0x0000
    ORUN_ERROR          = 0x0001
    URUN_ERROR          = 0x0002
    URUNNACK_ERROR      = 0x0004
    ABORT_CONDITION     = 0x0008
    INVSTART_ERROR      = 0x0010
    SPAR_ERROR          = 0x0020
    HPAR_ERROR          = 0x0040
    HCRC_ERROR          = 0x0080
    S0S1_ERROR          = 0x0100
    OREAD_ERROR         = 0x1000
    OWRITE_ERROR        = 0x2000

class I3cTargetHighLevelNotification_t:

    def __init__(self) -> None:
        self.id                 = 0x00
        self.command            = 0x00
        self.name               = ""
        self.typeOfTransfer     = I3cTargetTransferType_t.I3C_TARGET_WRITE
        self.targetAddress      = 0x00
        self.transferLength     = 0x0000
        self.usbError           = UsbCommandResponseStatus.CMD_SUCCESSFUL
        self.mgrError           = I3cTargetTransferResult_t.I3C_TARGET_TRANSFER_SUCCESS
        self.driverError        = I3cTargetTransferError_t.NO_ERROR

        self.data = []

    def set(self, data) -> bool:

        notification = I3cTargetNotification_t.from_buffer_copy(data)

        # Header
        self.id                 = notification.fields.id
        self.command            = notification.fields.cmd
        self.name               = COMMANDS_DICTIONARY[notification.fields.cmd]["name"]
        self.typeOfTransfer     = notification.fields.typeOfTransfer
        self.targetAddress      = notification.fields.targetAddress
        self.memoryAddress      = notification.fields.memoryAddress
        self.transferLength     = notification.fields.transferLength
        self.usbError           = notification.fields.transferError.usbErrorStatus
        self.mgrError           = notification.fields.transferError.mgrErrorStatus
        self.driverError        = notification.fields.transferError.driverErrorStatus

        # Payload
        payload = list(notification.fields.payload)

        if (notification.fields.transferLength <= I3C_TARGET_NOTIFICATION_DATA_LENGTH):
            self.data += payload[:notification.fields.transferLength]
            self.transferLength = len(self.data)
            return True
        else:
            # Append payload, increment payload length, and wait for pending responses
            self.data += payload
            return False

    def toDictionary(self) -> dict:

        # Set error list
        driverErrors = [ error.name for error in I3cTargetTransferError_t if (error.value & self.driverError) ]

        # If there wasn't any error, set NO_TRANSFER_ERROR
        if ( len(driverErrors) == 0 ):
            driverErrors.append(I3cTargetTransferError_t.NO_ERROR.name)
            
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : COMMANDS_DICTIONARY[self.command]["name"],
            'transfer_type' : I3cTargetTransferType_t(self.typeOfTransfer).name,
            'target_address' : self.targetAddress,
            'memory_address' : self.memoryAddress,
            'transfer_length' : self.transferLength,
            'usb_result' : UsbCommandResponseStatus(self.usbError).name,
            'manager_result' : I3cTargetTransferResult_t(self.mgrError).name,
            'driver_result' : driverErrors,
            'data' : self.data  
        }

    def __str__(self) -> str:
        return str(self.toDictionary())    
    
#================================================================================#
# I3C COMMON COMMAND CODE DEFINITIONS
#================================================================================#

class CCC(Enum):
    '''
    Enum that identifies all the CCC values.
    '''
    B_ENEC      = 0x00
    B_DISEC     = 0x01
    B_ENTAS0    = 0x02
    B_ENTAS1    = 0x03
    B_ENTAS2    = 0x04
    B_ENTAS3    = 0x05
    B_RSTDAA    = 0x06
    B_ENTDAA    = 0x07
    B_DEFTGTS   = 0x08
    B_SETMWL    = 0x09
    B_SETMRL    = 0x0A
    B_ENTTM     = 0x0B
    B_SETBUSCON = 0x0C
    MIPI_RS_0D  = 0x0D  # 0x0D – 0x11 - MIPI Reserved
    MIPI_RS_0E  = 0x0E
    MIPI_RS_0F  = 0x0F
    MIPI_RS_10  = 0x10
    MIPI_RS_11  = 0x11
    B_ENDXFER   = 0x12
    MIPI_RS_13  = 0x13  # 0x13 – 0x1E - MIPI Reserved
    MIPI_RS_14  = 0x14
    MIPI_RS_15  = 0x15
    MIPI_RS_16  = 0x16
    MIPI_RS_17  = 0x17
    MIPI_RS_18  = 0x18
    MIPI_RS_19  = 0x19
    MIPI_RS_1A  = 0x1A
    MIPI_RS_1B  = 0x1B
    MIPI_RS_1C  = 0x1C
    MIPI_RS_1D  = 0x1D
    MIPI_RS_1E  = 0x1E
    RES_1F      = 0x1F  	# 0x1F Reserved
    B_ENTHDR0   = 0x20
    B_ENTHDR1   = 0x21
    B_ENTHDR2   = 0x22
    B_ENTHDR3   = 0x23
    B_ENTHDR4   = 0x24
    B_ENTHDR5   = 0x25
    B_ENTHDR6   = 0x26
    B_ENTHDR7   = 0x27
    B_SETXTIME  = 0x28
    B_SETAASA   = 0x29
    B_RSTACT    = 0x2A
    B_DEFGRPA   = 0x2B
    B_RSTGRPA   = 0x2C
    B_MLANE     = 0x2D
    MIPI_WG_2E  = 0x2E  # 0x2E – 0x48 - MIPI I3C WG Reserved
    MIPI_WG_2F  = 0x2F
    MIPI_WG_30  = 0x30
    MIPI_WG_31  = 0x31
    MIPI_WG_32  = 0x32
    MIPI_WG_33  = 0x33
    MIPI_WG_34  = 0x34
    MIPI_WG_35  = 0x35
    MIPI_WG_36  = 0x36
    MIPI_WG_37  = 0x37
    MIPI_WG_38  = 0x38
    MIPI_WG_39  = 0x39
    MIPI_WG_3A  = 0x3A
    MIPI_WG_3B  = 0x3B
    MIPI_WG_3C  = 0x3C
    MIPI_WG_3D  = 0x3D
    MIPI_WG_3E  = 0x3E
    MIPI_WG_3F  = 0x3F
    MIPI_WG_40  = 0x40
    MIPI_WG_41  = 0x41
    MIPI_WG_42  = 0x42
    MIPI_WG_43  = 0x43
    MIPI_WG_44  = 0x44
    MIPI_WG_45  = 0x45
    MIPI_WG_46  = 0x46
    MIPI_WG_47  = 0x47
    MIPI_WG_48  = 0x48
    MIPI_CAM_49 = 0x49  # 0x49 – 0x4C - MIPI Camera WG Reserved – Broadcast CCCs
    MIPI_CAM_4A = 0x4A
    MIPI_CAM_4B = 0x4B
    MIPI_CAM_4C = 0x4C
    MIPI_RS_4D  = 0x4D  # 0x4D – 0x57 - MIPI Reserved – Broadcast CCCs
    MIPI_RS_4E  = 0x4E
    MIPI_RS_4F  = 0x4F
    MIPI_RS_50  = 0x50
    MIPI_RS_51  = 0x51
    MIPI_RS_52  = 0x52
    MIPI_RS_53  = 0x53
    MIPI_RS_54  = 0x54
    MIPI_RS_55  = 0x55
    MIPI_RS_56  = 0x56
    MIPI_RS_57  = 0x57
    MIPI_DWG_58 = 0x58  # 0x58 – 0x5B - MIPI Debug WG Reserved – Broadcast CCCs
    MIPI_DWG_59 = 0x59
    MIPI_DWG_5A = 0x5A
    MIPI_DWG_5B = 0x5B
    MIPIRIOWG5C = 0x5C  # 0x5C – 0x60 - MIPI RIO WG Reserved – Broadcast CCCs
    MIPIRIOWG5D = 0x5D
    MIPIRIOWG5E = 0x5E
    MIPIRIOWG5F = 0x5F
    MIPIRIOWG60 = 0x60
    B_VENCCC_61 = 0x61  # 0x61 – 0x7F - Vendor / Standards Extension – Broadcast CCCs
    B_VENCCC_62 = 0x62
    B_VENCCC_63 = 0x63
    B_VENCCC_64 = 0x64
    B_VENCCC_65 = 0x65
    B_VENCCC_66 = 0x66
    B_VENCCC_67 = 0x67
    B_VENCCC_68 = 0x68
    B_VENCCC_69 = 0x69
    B_VENCCC_6A = 0x6A
    B_VENCCC_6B = 0x6B
    B_VENCCC_6C = 0x6C
    B_VENCCC_6D = 0x6D
    B_VENCCC_6E = 0x6E
    B_VENCCC_6F = 0x6F
    B_VENCCC_70 = 0x70
    B_VENCCC_71 = 0x71
    B_VENCCC_72 = 0x72
    B_VENCCC_73 = 0x73
    B_VENCCC_74 = 0x74
    B_VENCCC_75 = 0x75
    B_VENCCC_76 = 0x76
    B_VENCCC_77 = 0x77
    B_VENCCC_78 = 0x78
    B_VENCCC_79 = 0x79
    B_VENCCC_7A = 0x7A
    B_VENCCC_7B = 0x7B
    B_VENCCC_7C = 0x7C
    B_VENCCC_7D = 0x7D
    B_VENCCC_7E = 0x7E
    B_VENCCC_7F = 0x7F
    D_ENEC      = 0x80  # DIRECT CCCs
    D_DISEC     = 0x81
    D_ENTAS0    = 0x82
    D_ENTAS1    = 0x83
    D_ENTAS2    = 0x84
    D_ENTAS3    = 0x85
    D_RSTDAA    = 0x86  # 0x86 - DEPRECATED: RSTDAA Direct. Reset Dynamic Address Assignment
    D_SETDASA   = 0x87
    D_SETNEWDA  = 0x88
    D_SETMWL    = 0x89
    D_SETMRL    = 0x8A
    D_GETMWL    = 0x8B
    D_GETMRL    = 0x8C
    D_GETPID    = 0x8D
    D_GETBCR    = 0x8E
    D_GETDCR    = 0x8F
    D_GETSTATUS = 0x90
    D_GETACCCR  = 0x91
    D_ENDXFER   = 0x92
    D_SETBRGTGT = 0x93
    D_GETMXDS   = 0x94
    D_GETCAPS   = 0x95
    D_SETROUTE  = 0x96
    D_D2DXFER   = 0x97
    D_SETXTIME  = 0x98
    D_GETXTIME  = 0x99
    D_RSTACT    = 0x9A
    D_SETGRPA   = 0x9B
    D_RSTGRPA   = 0x9C
    D_MLANE     = 0x9D
    MIPI_WG_9E  = 0x9E  # 0x9E – 0xBF - MIPI I3C WG Reserved – Direct CCCs
    MIPI_WG_9F  = 0x9F
    MIPI_WG_A0  = 0xA0
    MIPI_WG_A1  = 0xA1
    MIPI_WG_A2  = 0xA2
    MIPI_WG_A3  = 0xA3
    MIPI_WG_A4  = 0xA4
    MIPI_WG_A5  = 0xA5
    MIPI_WG_A6  = 0xA6
    MIPI_WG_A7  = 0xA7
    MIPI_WG_A8  = 0xA8
    MIPI_WG_A9  = 0xA9
    MIPI_WG_AA  = 0xAA
    MIPI_WG_AB  = 0xAB
    MIPI_WG_AC  = 0xAC
    MIPI_WG_AD  = 0xAD
    MIPI_WG_AE  = 0xAE
    MIPI_WG_AF  = 0xAF
    MIPI_WG_B0  = 0xB0
    MIPI_WG_B1  = 0xB1
    MIPI_WG_B2  = 0xB2
    MIPI_WG_B3  = 0xB3
    MIPI_WG_B4  = 0xB4
    MIPI_WG_B5  = 0xB5
    MIPI_WG_B6  = 0xB6
    MIPI_WG_B7  = 0xB7
    MIPI_WG_B8  = 0xB8
    MIPI_WG_B9  = 0xB9
    MIPI_WG_BA  = 0xBA
    MIPI_WG_BB  = 0xBB
    MIPI_WG_BC  = 0xBC
    MIPI_WG_BD  = 0xBD
    MIPI_WG_BE  = 0xBE
    MIPI_WG_BF  = 0xBF
    MIPI_CAM_C0 = 0xC0  # 0xC0 – 0xC3 - MIPI Camera WG Reserved – Direct CCCs
    MIPI_CAM_C1 = 0xC1
    MIPI_CAM_C2 = 0xC2
    MIPI_CAM_C3 = 0xC3
    MIPI_RS_C4  = 0xC4  # 0xC4 – 0xD6 - MIPI Reserved – Direct CCCs
    MIPI_RS_C5  = 0xC5
    MIPI_RS_C6  = 0xC6
    MIPI_RS_C7  = 0xC7
    MIPI_RS_C8  = 0xC8
    MIPI_RS_C9  = 0xC9
    MIPI_RS_CA  = 0xCA
    MIPI_RS_CB  = 0xCB
    MIPI_RS_CC  = 0xCC
    MIPI_RS_CD  = 0xCD
    MIPI_RS_CE  = 0xCE
    MIPI_RS_CF  = 0xCF
    MIPI_RS_D0  = 0xD0
    MIPI_RS_D1  = 0xD1
    MIPI_RS_D2  = 0xD2
    MIPI_RS_D3  = 0xD3
    MIPI_RS_D4  = 0xD4
    MIPI_RS_D5  = 0xD5
    MIPI_RS_D6  = 0xD6
    MIPI_DWG_D7 = 0xD7  # 0xD7 – 0xDA - MIPI Debug WG Reserved – Direct CCCs
    MIPI_DWG_D8 = 0xD8
    MIPI_DWG_D9 = 0xD9
    MIPI_DWG_DA = 0xDA
    MIPIRIOWGDB = 0xDB  # 0xDB – 0xDF - MIPI RIO WG Reserved – Direct CCCs
    MIPIRIOWGDC = 0xDC
    MIPIRIOWGDD = 0xDD
    MIPIRIOWGDE = 0xDE
    MIPIRIOWGDF = 0xDF
    D_VENCCC_E0 = 0xE0  # 0xE0 – 0xFE - Vendor / Standards Extension – Direct CCCs
    D_VENCCC_E1 = 0xE1
    D_VENCCC_E2 = 0xE2
    D_VENCCC_E3 = 0xE3
    D_VENCCC_E4 = 0xE4
    D_VENCCC_E5 = 0xE5
    D_VENCCC_E6 = 0xE6
    D_VENCCC_E7 = 0xE7
    D_VENCCC_E8 = 0xE8
    D_VENCCC_E9 = 0xE9
    D_VENCCC_EA = 0xEA
    D_VENCCC_EB = 0xEB
    D_VENCCC_EC = 0xEC
    D_VENCCC_ED = 0xED
    D_VENCCC_EE = 0xEE
    D_VENCCC_EF = 0xEF
    D_VENCCC_F0 = 0xF0
    D_VENCCC_F1 = 0xF1
    D_VENCCC_F2 = 0xF2
    D_VENCCC_F3 = 0xF3
    D_VENCCC_F4 = 0xF4
    D_VENCCC_F5 = 0xF5
    D_VENCCC_F6 = 0xF6
    D_VENCCC_F7 = 0xF7
    D_VENCCC_F8 = 0xF8
    D_VENCCC_F9 = 0xF9
    D_VENCCC_FA = 0xFA
    D_VENCCC_FB = 0xFB
    D_VENCCC_FC = 0xFC
    D_VENCCC_FD = 0xFD
    D_VENCCC_FE = 0xFE
    MIPI_WG_FF  = 0xFF  # 0xFF - MIPI I3C WG Reserved

class ENEC(Enum):
    ENINT   = 0x01
    ENCR    = 0x02
    ENHJ    = 0x08

class DISEC(Enum):
    DISINT  = 0x01
    DISCR   = 0x02
    DISHJ   = 0x08

CCC_RESPONSE_INSTANCE = {
    CCC.D_GETBCR    : I3cGetBcrHighLevelResponse_t,
    CCC.D_GETDCR    : I3cGetDcrHighLevelResponse_t,
    CCC.D_GETPID    : I3cGetPidHighLevelResponse_t,
    CCC.D_GETMXDS   : I3cGetmxdsHighLevelResponse_t,
    CCC.D_GETMRL    : I3cGetmrlHighLevelResponse_t,
    CCC.D_GETMWL    : I3cGetmwlHighLevelResponse_t,
    CCC.D_GETXTIME  : I3cGetxtimeHighLevelResponse_t,
    CCC.D_GETCAPS   : I3cGetcapsHighLevelResponse_t,
    CCC.D_ENEC      : I3cTransferHighLevelResponse_t,
    CCC.D_DISEC     : I3cTransferHighLevelResponse_t,
    CCC.D_SETDASA   : I3cTransferHighLevelResponse_t,
    CCC.D_SETNEWDA  : I3cTransferHighLevelResponse_t,
    CCC.B_RSTDAA    : I3cTransferHighLevelResponse_t,
    CCC.B_ENEC      : I3cTransferHighLevelResponse_t,
    CCC.B_DISEC     : I3cTransferHighLevelResponse_t,
    CCC.D_SETMRL   : I3cTransferHighLevelResponse_t,
    CCC.D_SETMWL   : I3cTransferHighLevelResponse_t,
    CCC.B_SETMRL   : I3cTransferHighLevelResponse_t,
    CCC.B_SETMWL   : I3cTransferHighLevelResponse_t,
    CCC.D_SETGRPA  : I3cTransferHighLevelResponse_t,
    CCC.B_RSTGRPA  : I3cTransferHighLevelResponse_t,
    CCC.D_RSTGRPA  : I3cTransferHighLevelResponse_t,
    CCC.D_GETACCCR  : I3cGetAcccrHighLevelResponse_t,
    CCC.B_SETAASA   : I3cTransferHighLevelResponse_t,
    CCC.B_ENDXFER   : I3cTransferHighLevelResponse_t,
    CCC.D_ENDXFER   : I3cTransferHighLevelResponse_t,
    CCC.B_SETXTIME  : I3cTransferHighLevelResponse_t,
    CCC.D_SETXTIME  : I3cTransferHighLevelResponse_t,
    CCC.B_SETBUSCON : I3cTransferHighLevelResponse_t,
    CCC.B_ENTAS0    : I3cTransferHighLevelResponse_t,
    CCC.B_ENTAS1    : I3cTransferHighLevelResponse_t,
    CCC.B_ENTAS2    : I3cTransferHighLevelResponse_t,
    CCC.B_ENTAS3    : I3cTransferHighLevelResponse_t,
    CCC.D_GETSTATUS : I3cTransferHighLevelResponse_t,
}

#================================================================================#
# SPI COMMON COMMAND CODE DEFINITIONS
#================================================================================#

SPI_CONTROLLER_MIN_FREQUENCY = 10000       # In Hz -> 10 kHz
SPI_CONTROLLER_MAX_FREQUENCY = 50000000    # In Hz -> 50 MHz

class SpiManagerError(Enum):
    """ This enum represents the possible values to be assigned to the SPI manager error field. """
    SPI_NO_ERROR                    = 0x00
    SPI_DATA_FORMAT_ERROR           = 0x01
    SPI_NOT_INITIALIZED_ERROR       = 0x02
    SPI_ALREADY_INITIALIZED_ERROR   = 0x03

class SpiDriverError(Enum):
    """ 
    This enum represents the possible values to be assigned to the SPI driver error field. 

    Values defined in the NXP LPC5536 SPI Peripheral.   
    """        
    SPI_DRIVER_NO_TRANSFER_ERROR       = 0x00
    SPI_DRIVER_FAIL                    = 0x01
    SPI_DRIVER_READ_ONLY               = 0x02
    SPI_DRIVER_OUT_OF_RANGE            = 0x03
    SPI_DRIVER_INVALID_ARGUMENT        = 0x04
    SPI_DRIVER_TIMEOUT                 = 0x05
    SPI_DRIVER_NO_TRANSFER_IN_PROGRESS = 0x06
    SPI_DRIVER_BUSY                    = 0x07
    SPI_DRIVER_NO_DATA                 = 0x08

#================================================================================#
# SPI - INITIALIZE SPI CONTROLLER
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_INIT_REQUEST_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_INIT_REQUEST_HEADER_LENGTH       = 12
SPI_CONTROLLER_INIT_REQUEST_UNUSED_LENGTH       = SPI_CONTROLLER_INIT_REQUEST_LENGTH - SPI_CONTROLLER_INIT_REQUEST_HEADER_LENGTH

# Union array
SpiControllerInitRequestArray_t                 = c_uint8 * (SPI_CONTROLLER_INIT_REQUEST_LENGTH + 1) # Command length + endpoint ID.

# Union structure
class SpiControllerInitRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("bitOrder", c_uint8),
                ("mode", c_uint8),
                ("dataWidth", c_uint8),
                ("chipSelect", c_uint8),
                ("chipSelectPol", c_uint8),
                ("frequency", c_uint32),
                ("unusedData", c_uint8 * SPI_CONTROLLER_INIT_REQUEST_UNUSED_LENGTH)]

# Union command
class SpiControllerInitRequest_t(Union):
    _fields_ = [("data", SpiControllerInitRequestArray_t ),
                ("fields", SpiControllerInitRequestFields_t )]

# Enums ------------------------------------------------------------------------ #

class SpiControllerBitOrder(Enum):
    MSB    = 0x00
    LSB    = 0x01

class SpiControllerMode(Enum):
    MODE_0    = 0x00
    MODE_1    = 0x01
    MODE_2    = 0x02
    MODE_3    = 0x03

class SpiControllerDataWidth(Enum):
    _8_BITS_DATA    = 0x00
    _16_BITS_DATA   = 0x01

class SpiControllerChipSelect(Enum):
    CHIP_SELECT_0   = 0x00
    CHIP_SELECT_1   = 0x01
    CHIP_SELECT_2   = 0x02
    CHIP_SELECT_3   = 0x03

class SpiControllerChipSelectPolarity(Enum):
    ACTIVE_LOW  = 0x00
    ACTIVE_HIGH = 0x01

# Response --------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_INIT_RESP_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_INIT_RESP_HEADER_LENGTH          = 7
SPI_CONTROLLER_INIT_RESP_UNUSED_LENGTH          = SPI_CONTROLLER_INIT_RESP_LENGTH - SPI_CONTROLLER_INIT_RESP_HEADER_LENGTH

# Union array
SpiControllerInitResponseArray_t                = c_uint8 * (SPI_CONTROLLER_INIT_RESP_LENGTH)

# Union structure
class SpiControllerInitResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("errorStatus", ErrorStatus_t),
                ("unusedData", c_uint8 * SPI_CONTROLLER_INIT_RESP_UNUSED_LENGTH)]

# Union command
class SpiControllerInitResponse_t(Union):
    _fields_ = [("data", SpiControllerInitResponseArray_t ),
                ("fields", SpiControllerInitResponseFields_t )]

    def set(self, data) -> bool:
        """ This function set the ctypes Array data from a data buffer. """
        self.data = SpiControllerInitResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        """ This function returns a dictionary with the response fields. """
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error' : UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : SpiManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : SpiDriverError(self.fields.errorStatus.driverErrorStatus).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
    
#================================================================================#
# SPI - SET PARAMETERS SPI CONTROLLER
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_SET_PARAMS_REQUEST_LENGTH 		      = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_SET_PARAMS_REQUEST_HEADER_LENGTH       = 12
SPI_CONTROLLER_SET_PARAMS_REQUEST_UNUSED_LENGTH       = SPI_CONTROLLER_SET_PARAMS_REQUEST_LENGTH - SPI_CONTROLLER_SET_PARAMS_REQUEST_HEADER_LENGTH

# Union array
SpiControllerSetParameterRequestArray_t               = c_uint8 * (SPI_CONTROLLER_SET_PARAMS_REQUEST_LENGTH + 1) # Command length + endpoint ID.

# Union structure
class SpiControllerSetParameterRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("bitOrder", c_uint8),
                ("mode", c_uint8),
                ("dataWidth", c_uint8),
                ("chipSelect", c_uint8),
                ("chipSelectPol", c_uint8),
                ("frequency", c_uint32),
                ("unusedData", c_uint8 * SPI_CONTROLLER_SET_PARAMS_REQUEST_UNUSED_LENGTH)]

# Union command
class SpiControllerSetParameterRequest_t(Union):
    _fields_ = [("data", SpiControllerSetParameterRequestArray_t ),
                ("fields", SpiControllerSetParameterRequestFields_t )]
    
# Response --------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_SET_PARAMS_RESP_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_SET_PARAMS_RESP_HEADER_LENGTH        = 7
SPI_CONTROLLER_SET_PARAMS_RESP_UNUSED_LENGTH        = SPI_CONTROLLER_SET_PARAMS_RESP_LENGTH - SPI_CONTROLLER_SET_PARAMS_RESP_HEADER_LENGTH

# Union array
SpiControllerSetParameterResponseArray_t            = c_uint8 * (SPI_CONTROLLER_SET_PARAMS_RESP_LENGTH)

# Union structure
class SpiControllerSetParameterResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8),
                ("errorStatus", ErrorStatus_t),
                ("unusedData", c_uint8 * SPI_CONTROLLER_SET_PARAMS_RESP_UNUSED_LENGTH)]

# Union command
class SpiControllerSetParameterResponse_t(Union):
    _fields_ = [("data", SpiControllerSetParameterResponseArray_t ),
                ("fields", SpiControllerSetParameterResponseFields_t )]

    def set(self, data) -> bool:
        """ This function set the ctypes Array data from a data buffer. """
        self.data = SpiControllerSetParameterResponseArray_t.from_buffer_copy(data)
        return True
    
    def toDictionary(self) -> dict:
        """ This function returns a dictionary with the response fields. """
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error' : UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : SpiManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : SpiDriverError(self.fields.errorStatus.driverErrorStatus).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
    
#================================================================================#
# SPI - TRANSFER SPI CONTROLLER
#================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_TRANSFER_REQUEST_LENGTH 		        = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_TRANSFER_REQUEST_HEADER_LENGTH       = 7
SPI_CONTROLLER_TRANSFER_REQUEST_PAYLOAD_LENGTH		= SPI_CONTROLLER_TRANSFER_REQUEST_LENGTH - SPI_CONTROLLER_TRANSFER_REQUEST_HEADER_LENGTH

# Union array
SpiControllerTransferRequestArray_t                 = c_uint8 * (SPI_CONTROLLER_TRANSFER_REQUEST_LENGTH + 1)                       # Command length + endpoint ID.
SpiControllerTransferRequestPayloadArray_t          = c_uint8 * SPI_CONTROLLER_TRANSFER_REQUEST_PAYLOAD_LENGTH

# Union structure
class SpiControllerTransferRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [("endpointId", c_uint8),
                ("id", c_uint16),
                ("cmd", c_uint8),
                ("payloadLength", c_uint16),
                ("transferLength", c_uint16),
                ("payload", SpiControllerTransferRequestPayloadArray_t)]

# Union command
class SpiControllerTransferRequest_t(Union):
    _fields_ = [("data", SpiControllerTransferRequestArray_t ),
                ("fields", SpiControllerTransferRequestFields_t )]
    
# Response --------------------------------------------------------------------- #

# Constants
SPI_CONTROLLER_TRANSFER_RESP_LENGTH 		      = INTERRUPT_IN_ENDPOINT_SIZE
SPI_CONTROLLER_TRANSFER_RESP_HEADER_LENGTH        = 9
SPI_CONTROLLER_TRANSFER_RESP_PAYLOAD_LENGTH       = SPI_CONTROLLER_TRANSFER_RESP_LENGTH - SPI_CONTROLLER_TRANSFER_RESP_HEADER_LENGTH

# Union array
SpiControllerTransferResponseArray_t                = c_uint8 * (SPI_CONTROLLER_TRANSFER_RESP_LENGTH)
SpiControllerTransferResponsePayloadArray_t         = c_uint8 * (SPI_CONTROLLER_TRANSFER_RESP_PAYLOAD_LENGTH)

# Union structure
class SpiControllerTransferResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [("id", c_uint16),
                ("cmd", c_uint8 ),
                ("errorStatus", ErrorStatus_t),
                ("payloadLength", c_uint16),
                ("payload", SpiControllerTransferResponsePayloadArray_t)]

# Union command
class SpiControllerTransferResponse_t(Union):
    _fields_ = [("data", SpiControllerTransferResponseArray_t ),
                ("fields", SpiControllerTransferResponseFields_t )]

    def set(self, data) -> bool:
        """ This function set the ctypes Array data from a data buffer. """
        self.data = SpiControllerTransferResponseArray_t.from_buffer_copy(data)
        return True
    
    def toDictionary(self) -> dict:
        """ This function returns a dictionary with the response fields. """
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error' : UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : SpiManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : SpiDriverError(self.fields.errorStatus.driverErrorStatus).name,
            'payload_length' : self.fields.payloadLength,
            'payload' : list(self.fields.payload)
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

#================================================================================#
# HLA RESPONSE - TRANSFER SPI CONTROLLER
#================================================================================#

class SpiControllerTransferHighLevelResponse_t:

    def __init__(self) -> None:
        self.id             = 0x00
        self.command        = 0x00
        self.errorStatus    = ErrorStatus_t()
        self.payloadLength  = 0
        self.payload        = []

    def set(self, data) -> bool:

        response = SpiControllerTransferResponse_t.from_buffer_copy(data)

        # Header
        self.id             = response.fields.id
        self.command        = response.fields.cmd
        self.errorStatus    = response.fields.errorStatus

        # Payload
        payload_chunk = list(response.fields.payload)

        # Last payload chunk received
        if (response.fields.payloadLength <= SPI_CONTROLLER_TRANSFER_RESP_PAYLOAD_LENGTH):
            self.payloadLength += response.fields.payloadLength
            self.payload += payload_chunk[:response.fields.payloadLength]
            return True
        else:
            # Append payload chunk, increment paylaod length and wait for pending responses
            self.payloadLength += SPI_CONTROLLER_TRANSFER_RESP_PAYLOAD_LENGTH
            self.payload += payload_chunk
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : COMMANDS_DICTIONARY[self.command]["name"],
            'usb_error' : UsbCommandResponseStatus(self.errorStatus.usbErrorStatus).name,
            'manager_error' : SpiManagerError(self.errorStatus.mgrErrorStatus).name,
            'driver_error' : SpiDriverError(self.errorStatus.driverErrorStatus).name,
            'payload_length' : self.payloadLength,
            'payload' : self.payload
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
    
# ================================================================================#
#  UART ERROR
# ================================================================================#

class UartManagerError(Enum):
    """ This enum represents the possible values to be assigned to the UART manager error field. """
    UART_NO_ERROR                  = 0x00
    UART_DATA_FORMAT_ERROR         = 0x01
    UART_NOT_INITIALIZED_ERROR     = 0x02
    UART_ALREADY_INITIALIZED_ERROR = 0x03

class UartTransferError(Enum):
        
    """ 
    This enum represents the possible values to be assigned to the UART driver error field. 

    Values defined in the NXP LPC5536 I3C Peripheral.   
    """
    NO_TRANSFER_ERROR       = 0x00
    FAIL                    = 0x01
    READ_ONLY               = 0x02
    OUT_OF_RANGE            = 0x03
    INVALID_ARGUMENT        = 0x04
    TIMEOUT                 = 0x05
    NO_TRANSFER_IN_PROGRESS = 0x06
    BUSY                    = 0x07
    NO_DATA                 = 0x08

# ================================================================================#
#  UART INIT
# ================================================================================#

# Request ---------------------------------------------------------------------- #

UART_CONTROLLER_INIT_REQ_LENGTH             = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_INIT_REQ_HEADER_LENGTH      = 8
UART_CONTROLLER_INIT_REQ_UNUSED_LENGTH      = UART_CONTROLLER_INIT_REQ_LENGTH - UART_CONTROLLER_INIT_REQ_HEADER_LENGTH

# Union array
UartControllerInitRequestArray_t            = c_uint8 * (UART_CONTROLLER_INIT_REQ_LENGTH + 1)
# Command length + endpoint ID.

# Union structure
class UartControllerInitRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("endpointId", c_uint8),
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("baudRate", c_uint8),
        ("hardwareHandshake", c_uint8),
        ("parityMode", c_uint8),
        ("dataSize", c_uint8),
        ("stopBitType", c_uint8),
        ("unusedData", c_uint8 * UART_CONTROLLER_INIT_REQ_UNUSED_LENGTH),
    ]

# Union command
class UartControllerInitRequest_t(Union):
    _fields_ = [
        ("data", UartControllerInitRequestArray_t),
        ("fields", UartControllerInitRequestFields_t),
    ]

# Enums ------------------------------------------------------------------------ #

# This enum represents the UART baudrate options
class UartControllerBaudRate(Enum):
    UART_BAUD_600    = 0x00
    UART_BAUD_1200   = 0x01
    UART_BAUD_2400   = 0x02
    UART_BAUD_4800   = 0x03
    UART_BAUD_9600   = 0x04
    UART_BAUD_14400  = 0x05
    UART_BAUD_19200  = 0x06
    UART_BAUD_38400  = 0x07
    UART_BAUD_56000  = 0x08
    UART_BAUD_57600  = 0x09
    UART_BAUD_115200 = 0x0A

# This enum represents the UART parity options 
class UartControllerParity(Enum):
    UART_NO_PARITY   = 0x00
    UART_EVEN_PARITY = 0x01
    UART_ODD_PARITY  = 0x02

# This enum represents the UART data character size
class UartControllerDataSize(Enum):
    UART_7BIT_BYTE = 0x00
    UART_8BIT_BYTE = 0x01

# This enum represents the UART stop bit options 
class UartControllerStopBit(Enum):
    UART_ONE_STOP_BIT = 0x00
    UART_TWO_STOP_BIT = 0x01

# Response --------------------------------------------------------------------- #

UART_CONTROLLER_INIT_RES_LENGTH              = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_INIT_RES_HEADER_LENGTH       = 7
UART_CONTROLLER_INIT_RES_UNUSED_LENGTH       = UART_CONTROLLER_INIT_RES_LENGTH - UART_CONTROLLER_INIT_RES_HEADER_LENGTH

# Union array
UartControllerInitResponseArray_t            = c_uint8 * UART_CONTROLLER_INIT_RES_LENGTH

# Union structure
class UartControllerInitResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("errorStatus", ErrorStatus_t),
        ("unusedData", c_uint8 * UART_CONTROLLER_INIT_RES_UNUSED_LENGTH),
    ]

# Union command
class UartControllerInitResponse_t(Union):
    _fields_ = [("data", UartControllerInitResponseArray_t ),
                ("fields", UartControllerInitResponseFields_t )]

    def set(self, data) -> bool:
        """This function set the ctypes Array data from a data buffer.""" 
        self.data = UartControllerInitResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error': UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : UartManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : UartTransferError(self.fields.errorStatus.driverErrorStatus).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary()) 
    
# ================================================================================#
#  UART SET
# ================================================================================#

# Request ---------------------------------------------------------------------- #

UART_CONTROLLER_SET_PARAM_REQ_LENGTH             = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_SET_PARAM_REQ_HEADER_LENGTH      = 8
UART_CONTROLLER_SET_PARAM_REQ_UNUSED_LENGTH      = UART_CONTROLLER_SET_PARAM_REQ_LENGTH - UART_CONTROLLER_SET_PARAM_REQ_HEADER_LENGTH

# Union array
UartControllerSetParamsRequestArray_t            = c_uint8 * (UART_CONTROLLER_SET_PARAM_REQ_LENGTH + 1)
# Command length + endpoint ID.

# Union structure
class UartControllerSetParamsRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("endpointId", c_uint8),
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("baudRate", c_uint8),
        ("hardwareHandshake", c_uint8),
        ("parityMode", c_uint8),
        ("dataSize", c_uint8),
        ("stopBitType", c_uint8),
        ("unusedData", c_uint8 * UART_CONTROLLER_SET_PARAM_REQ_UNUSED_LENGTH),
    ]

# Union command
class UartControllerSetParamsRequest_t(Union):
    _fields_ = [
        ("data", UartControllerSetParamsRequestArray_t),
        ("fields", UartControllerSetParamsRequestFields_t),
    ]

# Response --------------------------------------------------------------------- #

UART_CONTROLLER_SET_PARAM_RES_LENGTH              = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_SET_PARAM_RES_HEADER_LENGTH       = 7
UART_CONTROLLER_SET_PARAM_RES_UNUSED_LENGTH       = UART_CONTROLLER_SET_PARAM_RES_LENGTH - UART_CONTROLLER_SET_PARAM_RES_HEADER_LENGTH

# Union array
UartControllerSetParamsResponseArray_t            = c_uint8 * UART_CONTROLLER_SET_PARAM_RES_LENGTH

# Union structure
class UartControllerSetParamsResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("errorStatus", ErrorStatus_t),
        ("unusedData", c_uint8 * UART_CONTROLLER_SET_PARAM_RES_UNUSED_LENGTH),
    ]

# Union command
class UartControllerSetParamsResponse_t(Union):
    _fields_ = [("data", UartControllerSetParamsResponseArray_t ),
                ("fields", UartControllerSetParamsResponseFields_t )]

    def set(self, data) -> bool:
        """This function set the ctypes Array data from a data buffer.""" 
        self.data = UartControllerSetParamsResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            'id' : self.fields.id,
            'command' : self.fields.cmd,
            'name' : COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error': UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : UartManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : UartTransferError(self.fields.errorStatus.driverErrorStatus).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary()) 
    
# ================================================================================#
#  UART SEND
# ================================================================================#

# Request ---------------------------------------------------------------------- #

# Constants
UART_CONTROLLER_SEND_MAX_PAYLOAD_LENGTH         = 1024
UART_CONTROLLER_SEND_REQ_COMMAND_LENGTH         = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_SEND_REQ_COMMAND_HEADER_LENGTH  = 5
UART_CONTROLLER_SEND_REQ_COMMAND_PAYLOAD_LENGTH = UART_CONTROLLER_SEND_REQ_COMMAND_LENGTH - UART_CONTROLLER_SEND_REQ_COMMAND_HEADER_LENGTH

# Union arrays
UartControllerSendRequestArray_t                = c_uint8 * (UART_CONTROLLER_SEND_REQ_COMMAND_LENGTH + 1)  # Command length + endpoint ID.

UartControllerSendRequestPayloadArray_t         = c_uint8 * UART_CONTROLLER_SEND_REQ_COMMAND_PAYLOAD_LENGTH

# Union structure
class UartControllerSendRequestFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("endpointId", c_uint8),
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("payloadLength", c_uint16),
        ("payload", UartControllerSendRequestPayloadArray_t)
    ]

# Union command
class UartControllerSendRequest_t(Union):
    _fields_ = [
        ("data", UartControllerSendRequestArray_t),
        ("fields", UartControllerSendRequestFields_t),
    ]

# Response --------------------------------------------------------------------- #

# Constants
UART_CONTROLLER_SEND_RES_COMMAND_LENGTH        = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_SEND_RES_COMMAND_HEADER_LENGTH = 6
UART_CONTROLLER_SEND_RES_COMMAND_UNUSED_LENGTH = UART_CONTROLLER_SEND_RES_COMMAND_LENGTH - UART_CONTROLLER_SEND_RES_COMMAND_HEADER_LENGTH

# Union arrays
UartControllerSendResponseArray_t              = c_uint8 * UART_CONTROLLER_SEND_RES_COMMAND_LENGTH

# Union structure
class UartControllerSendResponseFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("errorStatus", ErrorStatus_t),
        ("unusedData", c_uint8 * UART_CONTROLLER_SEND_RES_COMMAND_UNUSED_LENGTH),
    ]

# Union command
class UartControllerSendResponse_t(Union):
    _fields_ = [
        ("data", UartControllerSendResponseArray_t),
        ("fields", UartControllerSendResponseFields_t),
    ]

    def set(self, data) -> bool:
        """
        This function set the ctypes Array data from a data buffer.
        """
        self.data = UartControllerSendResponseArray_t.from_buffer_copy(data)
        return True

    def toDictionary(self) -> dict:
        return {
            "id": self.fields.id,
            "command": self.fields.cmd,
            "name": COMMANDS_DICTIONARY[self.fields.cmd]["name"],
            'usb_error': UsbCommandResponseStatus(self.fields.errorStatus.usbErrorStatus).name,
            'manager_error' : UartManagerError(self.fields.errorStatus.mgrErrorStatus).name,
            'driver_error' : UartTransferError(self.fields.errorStatus.driverErrorStatus).name
        }

    def __str__(self) -> str:
        return str(self.toDictionary())

# ================================================================================#
#  UART READ NOTIFICATION
# ================================================================================#

# Response --------------------------------------------------------------------- #

# Constants
UART_CONTROLLER_RECEIVE_NOTIFICATION_LENGTH                = INTERRUPT_IN_ENDPOINT_SIZE
UART_CONTROLLER_RECEIVE_NOTIFICATION_HEADER_LENGTH         = 9
UART_CONTROLLER_RECEIVE_NOTIFICATION_PAYLOAD_LENGTH        = (UART_CONTROLLER_RECEIVE_NOTIFICATION_LENGTH - UART_CONTROLLER_RECEIVE_NOTIFICATION_HEADER_LENGTH)

# Union arrays
UartControllerReceiveNotificationArray_t                   = c_uint8 * UART_CONTROLLER_RECEIVE_NOTIFICATION_LENGTH
UartControllerReceiveNotificationPayloadArray_t            = c_uint8 * UART_CONTROLLER_RECEIVE_NOTIFICATION_PAYLOAD_LENGTH

# Union structure
class UartControllerReceiveNotificationFields_t(Structure):
    _pack_ = 1
    _fields_ = [
        ("id", c_uint16),
        ("cmd", c_uint8),
        ("errorStatus", ErrorStatus_t),
        ("payloadLength", c_uint16),
        ("payload", UartControllerReceiveNotificationPayloadArray_t),
    ]

# Union command
class UartControllerReceiveNotification_t(Union):
    _fields_ = [
        ("data", UartControllerReceiveNotificationArray_t),
        ("fields", UartControllerReceiveNotificationFields_t),
    ]

# ================================================================================#
# HLA RESPONSE - UART READ NOTIFICATION
# ================================================================================#

class UartControllerReceiveHighLevelNotification_t:

    def __init__(self) -> None:
        self.id                 = 0x00
        self.command            = 0x00
        self.errorStatus        = ErrorStatus_t()
        self.payloadLength      = 0
        self.payload            = []

    def set(self, data) -> bool:

        notification = UartControllerReceiveNotification_t.from_buffer_copy(data)

        # Header
        self.id                 = notification.fields.id
        self.command            = notification.fields.cmd
        self.errorStatus        = notification.fields.errorStatus

        # Payload
        package_chunk_data = list(notification.fields.payload)
        # last package received
        if (notification.fields.payloadLength <= UART_CONTROLLER_RECEIVE_NOTIFICATION_PAYLOAD_LENGTH):
            self.payload += package_chunk_data[:notification.fields.payloadLength]
            return True
        else:
            # Append payload, increment payload length, and wait for pending responses
            self.payload += package_chunk_data
            return False

    def toDictionary(self) -> dict:
        return {
            'id' : self.id,
            'command' : self.command,
            'name' : COMMANDS_DICTIONARY[self.command]["name"],
            'usb_error' :UsbCommandResponseStatus(self.errorStatus.usbErrorStatus).name,
            'manager_error' : UartManagerError(self.errorStatus.mgrErrorStatus).name,
            'driver_error' :  UartTransferError(self.errorStatus.driverErrorStatus).name,
            'payload_length' : len(self.payload),
            'payload' : self.payload 
        }

    def __str__(self) -> str:
        return str(self.toDictionary()) 
