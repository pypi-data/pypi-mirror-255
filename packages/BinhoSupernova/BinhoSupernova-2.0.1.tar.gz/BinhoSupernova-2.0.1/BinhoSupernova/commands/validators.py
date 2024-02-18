from .serializers import *
from ..utils.system_message import SystemMessage, SystemModules,RequestValidatorOpcode

#####################################################################
# --------------------- FORMAT VALIDATORS ---------------------------
#####################################################################

def check_type(value, expected_type):
    return isinstance(value, expected_type)

def check_range(value, expected_type, min_val, max_val):
    return isinstance(value, expected_type) and min_val <= value <= max_val

def check_byte_array(data, max_size):
    if( len(data) > max_size):
        return False
    return all(check_range(value, int, 0x00, 0xFF) for value in data)

#####################################################################
# ----------------------------- SYSTEM ------------------------------
#####################################################################

def getUsbStringValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = getUsbStringSerializer(metadata["id"], metadata["subcommand"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "GET USB STRING requests success")

def setI3cBusVoltageValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.

    requests, response = setI3cBusVoltSerializer(metadata["id"], metadata["i3cBusVoltage"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SET I3C BUS VOLTAGE requests success")

def resetDeviceValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = resetDeviceSerializer(metadata["id"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "RESET DEVICE requests success")

def enterBootModeValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = enterBootModeSerializer(metadata["id"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "ENTER BOOT MODE requests success")

def setI2cSpiUartBusVoltValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.

    requests, response = setI2cSpiUartBusVoltSerializer(metadata["id"], metadata["i2cSpiUartBusVolt"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SET I2C SPI UART BUS VOLTAGE requests success")

#####################################################################
# ------------------------------ I2C --------------------------------
#####################################################################

def i2cSetParametersValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i2cSetParametersSerializer(metadata["id"], metadata["cancelTransfer"], metadata["baudrate"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I2C SET PARAMETERS requests success")

def i2cWriteValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i2cWriteSerializer(metadata["id"], metadata["command"], metadata["slaveAddress"], metadata["registerAddress"], metadata["data"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I2C WRITE requests success")

def i2cWriteNonStopValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i2cWriteSerializer(metadata["id"], metadata["command"], metadata["slaveAddress"], metadata["registerAddress"], metadata["data"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I2C WRITE NON STOP requests success")

def i2cReadValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i2cReadSerializer(metadata["id"], metadata["command"], metadata["slaveAddress"], metadata["dataLength"], metadata["registerAddress"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I2C READ requests success")

def i2cReadFromValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i2cReadSerializer(metadata["id"], metadata["command"], metadata["slaveAddress"], metadata["dataLength"], metadata["registerAddress"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I2C READ FROM requests success")

#####################################################################
# ------------------------------ I3C --------------------------------
#####################################################################

def i3cControllerInitValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cControllerInitSerializer(metadata["id"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "INITIALIZE I3C CONTROLLER requests success")
    return requests, response, result

def i3cInitBusValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cInitBusSerializer(metadata["id"], metadata["targetDeviceTable"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "INITIALIZE I3C BUS requests success")

def i3cGetTargetDeviceTableValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cGetTargetDeviceTableSerializer(metadata["id"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C GET TARGET DEVICE TABLE requests success")

def i3cSetTargetDeviceConfigValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cSetTargetDeviceConfigSerializer(metadata["id"], metadata["entries"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C SET TARGET DEVICE CONFIG requests success")
    return requests, response, result    

def i3cChangeDynamicAddressValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cChangeDynamicAddressSerializer(metadata["id"], metadata["currentAddress"], metadata["newAddress"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C CHANGE DYNAMIC ADDRESS requests success")
    return requests, response, result     

def i3cClearFeatureValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cClearFeatureSerializer(metadata["id"], metadata["selector"], metadata["targetAddress"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C CLEAR FEATURE requests success")

def i3cSetFeatureValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cSetFeatureSerializer(metadata["id"], metadata["selector"], metadata["targetAddress"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C SET FEATURE requests success")

def i3cGetCapabilityValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cGetCapabilitySerializer(metadata["id"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C GET CAPABILITY requests success")
    return requests, response, result     

def i3cWriteValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cWriteSerializer(metadata["id"], metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["registerAddress"], metadata["data"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C WRITE requests success")

def i3cReadValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cReadSerializer(metadata["id"], metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["registerAddress"], metadata["length"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C READ requests success")

def i3cSendCccValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cSendCccSerializer(metadata["id"], metadata["commandType"], metadata["isReadOrWrite"],  metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["defByte"], metadata["ccc"], metadata["length"], metadata["data"])
    return requests, response, SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C SEND CCC requests success")

def i3cTargetResetValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cTargetResetSerializer(metadata["id"], metadata["isReadOrWrite"], metadata["targetAddress"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["defByte"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C TARGET RESET requests success")
    return requests, response, result  
    
def i3cTargetInitValidator(metadata: dict) :

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cTargetInitSerializer(metadata["id"], metadata["memoryLayout"], metadata["uSecondsToWaitForIbi"], metadata["maxReadLength"], metadata["maxWriteLength"], metadata["i3cTargetFeatures"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "INITIALIZE I3C PERIPHERAL IN TARGET MODE requests success")
    return requests, response, result

def i3cTargetSetConfValidator(metadata: dict) :

    '''
    This function validates the data set by the user for the I3C_TARGET_SET_CONFIGURATION command and serializes the data into i3cTargetSetConfSerializer using
    i3cTargetSetConfSerializer if the validation is successful.

    Arguments
    ---------
    dict: dictionary of metadata that represents the fields for I3cTargetSetConfRequest_t

    Returns
    -------
    requests
        variable of type I3cTargetSetConfRequest_t to later send to the Supernova via USB to request an I3C_TARGET_SET_CONFIGURATION command

    response
        instance of I3cTargetSetConfResponse_t to match the message sent by the Supernova (the response for the command) with the request

    RequestValidatorSuccess
        indicates if the validation was successful or not

    '''

    # TODO: Check data validation. Use module inspect and/or try-except block.
    # TODO: Ckeck command value.

    requests, response = i3cTargetSetConfSerializer(metadata["id"], metadata["uSecondsToWaitForIbi"], metadata["maxReadLength"], metadata["maxWriteLength"], metadata["i3cTargetFeatures"])
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SET CONFIGURATION OF SUPERNOVA IN TARGET MODE requests success")
    return requests, response, result

def i3cTargetWriteMemValidator(metadata: dict) :
    '''
    This function validates the data set by the user for the I3C_TARGET_WRITE_MEMORY command and serializes the data into I3cTargetWriteMemRequest_t using
    i3cTargetWriteMemSerializer if the validation is successful.
    It verifies that the address set by the user does not surpass the end of the memory, the request is not even sent to the Supernova thanks to this validation.

    Arguments
    ---------
    dict: dictionary of metadata that represents the fields for I3cTargetWriteMemRequest_t

    Returns
    -------
    requests
        variable of type I3cTargetWriteMemRequest_t to later send to the Supernova via USB to request an I3C_TARGET_WRITE_MEMORY command

    response
        instance of I3cTargetWriteMemResponse_t to match the message sent by the Supernova (the response for the command) with the request

    RequestValidatorSuccess
        indicates if the validation was successful or not

    '''

    requests = None
    response = None
    result = None
    
    # Check memory address value.
    if (metadata["memoryAddr"] is not None):
        
        # Check there is data to be sent.
        if (metadata["data"] is not None) and (len(metadata['data']) > 0):

            # Check if all the data is valid data
            if all(0 <= value <= 0xFF for value in metadata["data"]) == True:
                requests, response = i3cTargetWriteMemSerializer(metadata["id"], metadata["memoryAddr"], metadata["data"])
                result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C TARGET WRITE MEMORY requests success")
            else:
                result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.FAIL, "I3C TARGET WRITE MEMORY request failed, invalid data input")
        else:
            result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.FAIL, "I3C TARGET WRITE MEMORY request failed, no data input")
    else:
        result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.FAIL, "I3C TARGET WRITE MEMORY request failed, no memory address input")

    return requests, response, result

def i3cTargetReadMemValidator(metadata: dict) :
    '''
    This function validates the data set by the user for the I3C_TARGET_READ_MEMORY command and serializes the data into I3cTargetReadMemRequest_t using
    i3cTargetReadMemSerializer if the validation is successful.
    It verifies that the address set by the user does not surpass the end of the memory, the request is not even sent to the Supernova thanks to this validation.

    Arguments
    ---------
    dict: dictionary of metadata that represents the fields for I3cTargetReadMemRequest_t

    Returns
    -------
    requests
        variable of type I3cTargetReadMemRequest_t to later send to the Supernova via USB to request an I3C_TARGET_READ_MEMORY command

    response
        instance of I3cTargetReadMemResponse_t to match the message sent by the Supernova (the response for the command) with the request

    RequestValidatorSuccess
        indicates if the validation was successful or not

    '''

    requests = None
    response = None
    result = None
    # Check memory address value.
    if (metadata["memoryAddr"] is not None):
        # Check read length value.
        if (metadata["length"] is not None) and (metadata["length"] > 0) :
            requests, response = i3cTargetReadMemSerializer(metadata["id"], metadata["memoryAddr"], metadata["length"])
            result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "I3C TARGET READ MEMORY requests success")
        else:
            result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.FAIL, "I3C TARGET READ MEMORY request failed, invalid length input")
    else:
        result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.FAIL, "I3C TARGET READ MEMORY request failed, no memory address input")
    return requests, response, result

#####################################################################
# ------------------------ UART CONTROLLER --------------------------
#####################################################################
    
def uartControllerInitValidator (metadata: dict):
    success, result = validateUartControllerInit(metadata)
    requests = None
    response = None

    if (success):
        requests, response = uartControllerInitSerializer(metadata["id"], metadata["baudRate"], metadata["hardwareHandshake"], metadata["parityMode"], metadata["dataSize"], metadata["stopBitType"])
    
    return requests, response, result
    
def validateUartControllerInit( metadata: dict ):
    result =  SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "UART CONTROLLER INIT requests success")
    success = True

    if (not check_type(metadata["baudRate"],UartControllerBaudRate)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for baudrate value"
        success = False
    if (not check_type(metadata["hardwareHandshake"],bool)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Hardware Handshake value"
        success = False
    if (not check_type(metadata["parityMode"],UartControllerParity)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Parity Mode value"
        success = False
    if (not check_type(metadata["dataSize"],UartControllerDataSize)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for UART data size value"
        success = False
    if (not check_type(metadata["stopBitType"],UartControllerStopBit)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Stop byte configuration value"  
        success = False  

    return success, result

def uartControllerSetParametersValidator(metadata: dict):
    success, result = validateUartControllerSetParameters( metadata)
    requests = None
    response = None

    if (success):
        requests, response = uartControllerSetParametersSerializer(metadata["id"], metadata["baudRate"], metadata["hardwareHandshake"], metadata["parityMode"], metadata["dataSize"], metadata["stopBitType"])

    return requests, response, result


def validateUartControllerSetParameters( metadata: dict ):
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "UART CONTROLLER SET PARAMETERS requests success")
    success = True

    if (not check_type(metadata["baudRate"],UartControllerBaudRate)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for baudrate value"
        success = False
    if (not check_type(metadata["hardwareHandshake"],bool)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Hardware Handshake value"
        success = False
    if (not check_type(metadata["parityMode"],UartControllerParity)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Parity Mode value"
        success = False
    if (not check_type(metadata["dataSize"],UartControllerDataSize)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for UART data size value"
        success = False
    if (not check_type(metadata["stopBitType"],UartControllerStopBit)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for Stop byte configuration value"  
        success = False  

    return success, result

def uartControllerSendMessageValidator(metadata: dict):
    success, result = validateUartSendMessageParameters( metadata )
    requests = None
    response = None
    if (success):
        requests, response = uartControllerSendMessageSerializer(metadata["id"], metadata["data"])
    return requests, response, result

def validateUartSendMessageParameters( metadata: dict ):
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "UART SEND MESSAGE requests success")
    success = True

    if (not check_byte_array(metadata["data"],UART_CONTROLLER_SEND_MAX_PAYLOAD_LENGTH)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: invalid data array"
        success = False

    return success, result

#####################################################################
# ------------------------ SPI CONTROLLER ---------------------------
#####################################################################

def spiControllerInitValidator(metadata: dict) :
    success, result = validateSpiControllerInit(metadata)
    requests, response = None, None

    if success:
        requests, response = spiControllerInitSerializer(metadata["id"], metadata["bitOrder"], metadata["mode"], metadata["dataWidth"], metadata["chipSelect"], metadata["chipSelectPol"], metadata["frequency"])       

    return requests, response, result

def validateSpiControllerInit(metadata: dict):
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SPI CONTROLLER INIT requests success")
    success = True

    if (not check_range(metadata["frequency"],int,SPI_CONTROLLER_MIN_FREQUENCY,SPI_CONTROLLER_MAX_FREQUENCY)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: frequency value out of range"
        success = False
    if (not check_type(metadata["bitOrder"],SpiControllerBitOrder)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for bitOrder value"
        success = False
    if (not check_type(metadata["mode"],SpiControllerMode)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for mode value"
        success = False
    if (not check_type(metadata["dataWidth"],SpiControllerDataWidth)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for dataWidth value"
        success = False
    if (not check_type(metadata["chipSelect"],SpiControllerChipSelect)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for chipSelect value"  
        success = False
    if (not check_type(metadata["chipSelectPol"],SpiControllerChipSelectPolarity)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for chipSelectPol value"  
        success = False

    return success, result

def spiControllerSetParametersValidator(metadata: dict) :
    success, result = validateSpiControllerSetParameters(metadata)
    requests, response = None, None

    if success:
        requests, response = spiControllerSetParametersSerializer(metadata["id"], metadata["bitOrder"], metadata["mode"], metadata["dataWidth"], metadata["chipSelect"], metadata["chipSelectPol"], metadata["frequency"])
    
    return requests, response, result

def validateSpiControllerSetParameters(metadata: dict):
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SPI CONTROLLER SET PARAMETERS requests success")
    success = True

    if (not check_range(metadata["frequency"],int,SPI_CONTROLLER_MIN_FREQUENCY,SPI_CONTROLLER_MAX_FREQUENCY)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: frequency value out of range"
        success = False
    if (not check_type(metadata["bitOrder"],SpiControllerBitOrder)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for bitOrder value"
        success = False
    if (not check_type(metadata["mode"],SpiControllerMode)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for mode value"
        success = False
    if (not check_type(metadata["dataWidth"],SpiControllerDataWidth)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for dataWidth value"
        success = False
    if (not check_type(metadata["chipSelect"],SpiControllerChipSelect)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for chipSelect value"  
        success = False
    if (not check_type(metadata["chipSelectPol"],SpiControllerChipSelectPolarity)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for chipSelectPol value"  
        success = False

    return success, result

def spiControllerTransferValidator(metadata: dict):
    success, result = validateSpiControllerTransfer(metadata)
    requests, response = None, None
    if success:
        requests, response = spiControllerTransferSerializer(metadata["id"], metadata["transferLength"], metadata["payload"])    

    return requests, response, result

def validateSpiControllerTransfer(metadata: dict):
    result = SystemMessage(SystemModules.VALIDATION, RequestValidatorOpcode.SUCCESS, "SPI CONTROLLER TRANSFER requests success")
    success = True

    if (not check_byte_array(metadata["payload"], 1024)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: payload length or data type error"
        success = False
    
    if (not check_type(metadata["payload"], list)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: wrong type for payload value"
        success = False
    
    if (not check_range(metadata["transferLength"],int,1,1024)):
        result.opcode = RequestValidatorOpcode.FAIL
        result.message = "ARGUMENT ERROR: transferLength value out of range"
        success = False

    return success, result
