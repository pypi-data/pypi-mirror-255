from .definitions import *
import ctypes

def splitDataUtility(data, maxLength) -> tuple[int, list]:

    """
    This is a private function, used to split large payloads into a collection of payloads that
    fit in the commands structure. The function returns a collection (list) of packets. Each packet
    is composed by a tuple containing the data segment, and a numerical value indicating the remaining
    data after trimming the current packet.

    Arguments
    ---------
    data : list
        List containing all the source data.
    maxLength : int
        Numerical value that represents the length of the data segments.

    Returns
    -------
    tuple
        Two elements tuple, the first one is the number of packets and the second one is the list of packets
        where each packets is a tuple containg a list with data segment and the remaining bytes when trimming that segment
        from the source data.
    """

    # Generate a list of tuples, where each tuple represents a packet. A packet is composed for
    # a list containing the packet data and a number indicating the remainging data.
    packets = []

    # Length of input data
    totalDataLength = len(data)

    # Verify that there is valid data.
    if (totalDataLength > 0) and (maxLength > 0):
        # Calculate the number of packets.
        numberPackets = int(totalDataLength / maxLength)

        # Check if an "uncompleted" packet will be required. If data length is not multiple of maxLength.
        rest = totalDataLength % maxLength
        if (rest != 0):
            numberPackets = numberPackets + 1

        # Generate data packets to send via USB
        for i in range(numberPackets):
            startIndex = i * maxLength
            if i < (numberPackets - 1):
                endIndex = startIndex + maxLength
                remainingDataLength = totalDataLength - (i * maxLength)
            else:
                if (rest == 0):
                    endIndex = startIndex + maxLength
                    remainingDataLength = maxLength
                else:
                    endIndex = startIndex + rest
                    remainingDataLength = rest

            # Generate the segment of data (data slice).
            dataSlice = data[startIndex : endIndex]

            # Add a new packet (tuple) to the list.
            packets.append((remainingDataLength, dataSlice))

    return len(packets), packets

#####################################################################
# ----------------------------- SYSTEM ------------------------------
#####################################################################
def getUsbStringSerializer(id: int, subCommand: GetUsbStringSubCommand) -> tuple[list[GetUsbStringRequest_t], GetUsbStringResponse_t]:
    """
    This function generates and returns a Get USB String command taking the subcommand
    passed as parameter. Just the subcommands bellow are supported:
    2 - Read USB Manufacturer Descriptor String
    3 - Read USB Product Descriptor String
    4 - Read USB Serial Number Descriptor String

    Argument
    --------
    subCommand : int
        Sub-command value.

    Returns
    -------
    ReadFlashDataRequest_t
        Read flash data command structure.
    """
    # Create command instance
    command = GetUsbStringRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = GET_USB_STRING
    command.fields.subCmd = subCommand.value

    return [command], GetUsbStringResponse_t()

def setI3cBusVoltSerializer(id: int, i3cBusVoltage: c_uint16) -> tuple[list[SetI3cBusVoltRequest_t], SetI3cBusVoltResponse_t]:
    """
    This function generates and returns a Set I3C Bus Voltage command
    Argument
    --------
    ldoVolt : c_uint16
        Voltage that wants to be set at the LDO output.

    Returns
    -------
    SetI3cBusVoltRequest_t
        SET_I3C_BUS_VOLTAGE data command structure.
    """
    # Create command instance
    command = SetI3cBusVoltRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = SET_I3C_BUS_VOLTAGE
    command.fields.i3cBusVoltage = i3cBusVoltage

    return [command], SetI3cBusVoltResponse_t()

def resetDeviceSerializer(id: int) -> tuple[list[SysResetDeviceRequest_t], None]:
    """
    This function generates and returns a RESET DEVICE command
    Argument
    --------
    id : int
        Command id

    Returns
    -------
    SysResetDeviceRequest_t
        RESET DEVICE data command structure.
    """
    # Create command instance
    command = SysResetDeviceRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = RESET_DEVICE

    return [command], None

def enterBootModeSerializer(id: int) -> tuple[list[SysEnterBootModeRequest_t], None]:
    """
    This function generates and returns a ENTER BOOT MODE command
    Argument
    --------
    id : int
        Command id

    Returns
    -------
    SysEnterBootModeRequest_t
        ENTER BOOT MODE data command structure.
    """
    # Create command instance
    command = SysEnterBootModeRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = ENTER_BOOT_MODE

    return [command], None

def setI2cSpiUartBusVoltSerializer(id: int, i2cSpiUartBusVolt: c_uint16) -> tuple[list[SetI2cSpiUartBusVoltRequest_t], SetI2cSpiUartBusVoltResponse_t]:
    """
    This function generates and returns a Set I3C Bus Voltage command
    Argument
    --------
    ldoVolt : c_uint16
        Voltage that wants to be set at the LDO output.

    Returns
    -------
    SetI3cBusVoltRequest_t
        SET_I3C_BUS_VOLTAGE data command structure.
    """
    # Create command instance
    command = SetI2cSpiUartBusVoltRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = SET_I2C_SPI_UART_BUS_VOLTAGE
    command.fields.i2cSpiUartBusVolt = i2cSpiUartBusVolt

    return [command], SetI2cSpiUartBusVoltResponse_t()

#####################################################################
# ------------------------------ I2C --------------------------------
#####################################################################

def i2cWriteCommandSerializer(id, cmd, slvAddress, regAddress, length, payload) -> I2cTransferRequest_t:

    """
    This function is used to send the following commands:
        - I2C_WRITE
        - I2C_WRITE_NON_STOP

    It returns the I2cTransferRequest_t command structure ready to be sent to the USB device.

    Arguments
    ---------
    id : in
        Command id.
    cmd: int
        Command code (I2C WRITE or I2C WRITE NO STOP)
    slvAddress : int
        7-bit slave address
    regAddress : list
        List that represents the subaddress/register address. It can contains
        up to 4 bytes.
    length : int
        Remaining data. Not necessary the length of message.
    payload : list
        List containing bytes to transfer.

    Returns
    -------
    I2cTransferRequest_t
        Structure that contains the command to be sent to the USB device.
    """
    # Create command instance
    command = I2cTransferRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = cmd

    # Transfer Length
    command.fields.i2cTransfLength = length

    # Slave address
    command.fields.i2cClientAddress = slvAddress

    # Register address length
    regAddressLength = len(regAddress)
    command.fields.i2cSubAddressLength = regAddressLength

    # Register address
    for i in range(regAddressLength):
        command.fields.i2cSubAddress = c_uint32(command.fields.i2cSubAddress | (regAddress[i]<< i * 8))

    # Payload
    for i in range(len(payload)):
        command.fields.dataToBeSent[i] = payload[i]

    # Return command structure.
    return command



# --------------------------------- PUBLIC FUNCTIONS ---------------------------------- #

def i2cSetParametersSerializer(id, cancelTransfer = 0x00, baudrate = 0x00) -> tuple[list[I2cSetParametersRequest_t], I2cSetParametersResponse_t]:
    """
    This function performs an I2C_SET_PARAMETERS command, sending optional data to
    cancel current I2C transfer and to set baudrate (I2C SCL frequency).

    Arguments
    ---------
    id : in
        Command id.
    cancelTransfer : int
        If 0x10 is passed, then cancel the current I2C transfer.
    baudrate : int
        Numerical value that represents the desired I2C SCL frequency in Hz.

        Returns
    -------
    I2cSetParametersRequest_t
        Structure that contains the command to be sent to the USB device.
    """
    # Create command instance
    command = I2cSetParametersRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I2C_SET_PARAMETERS
    command.fields.anyValue1 = 0x00

    # Validate cancelTransfer value
    if (cancelTransfer == 0x00) or (cancelTransfer == I2cSetParametersSubCommand.I2C_SET_PARAMS_CANCEL_TRANSFER.value):
        command.fields.cancelCurrentI2cTransfer = cancelTransfer

    if baudrate > 0 and baudrate <= 1000000:
        command.fields.setBaudrate = I2cSetParametersSubCommand.I2C_SET_PARAMS_BAUDRATE.value
        command.fields.i2cDivider = ctypes.c_ubyte(int((12000000 / baudrate) - 3))

    # Return command
    return [command], I2cSetParametersResponse_t()

def i2cReadSerializer(id, cmd, slvAddress, length, regAddress = None) -> tuple[list[I2cTransferRequest_t], I2cTransferHighLevelResponse_t]:
    """
    This function is used to send the following commands:
        - I2C_READ
        - I2C_WRITE_AND_READ

    It returns the I2cTransferRequest_t command structure ready to be sent to the USB device.

    Arguments
    ---------
    id : in
        Command id.
    cmd: int
        Command code (I2C READ or I2C WRITE AND READ).
    slvAddress : int
        7-bit slave address
    regAddress : list
        List that represents the subaddress/register address. It can contains
        up to 4 bytes.
    length : int
        Length of data to be read from the USB device.

    Returns
    -------
    I2cTransferRequest_t
        Structure that contains the command to be sent to the USB device.
    """
    # Create command instance
    command = I2cTransferRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = cmd

    # Transfer Length
    command.fields.i2cTransfLength = length

    # Slave address
    command.fields.i2cClientAddress = slvAddress

    # When command is I2C_WRITE_READ, sub-addres/register address is also sent.
    if (cmd == I2C_READ_FROM) and (regAddress != None):
        # Register address length
        regAddressLength = len(regAddress)
        command.fields.i2cSubAddressLength = regAddressLength

        # Register address
        for i in range(regAddressLength):
            command.fields.i2cSubAddress = c_uint32(command.fields.i2cSubAddress | (regAddress[i]<< i * 8))

    # Return command structure.
    return [command], I2cTransferHighLevelResponse_t()

def i2cWriteSerializer(id, cmd, slvAddress, regAddress, payload) -> tuple[list[I2cTransferRequest_t], I2cTransferHighLevelResponse_t]:

    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    # Generate payload chunks.
    nPayloadChunks, payloadChunks = splitDataUtility(payload, I2C_TRANSFER_REQ_PAYLOAD_LENGTH)

    # Send command(s).
    if nPayloadChunks == 0:
        # Build command structure.
        command = i2cWriteCommandSerializer(id, cmd, slvAddress, regAddress, 0, [])
        # Append message to commands list.
        commandsList.append(command)
    else:

        # for each payload chunk... build command and sent message to the USB MESSAGE HANDLER.
        for i in range(nPayloadChunks):
            # Build command structure.
            command = i2cWriteCommandSerializer(id, cmd, slvAddress, regAddress, payloadChunks[i][0], payloadChunks[i][1] )
            # Append message to commands list.
            commandsList.append(command)

    # Return list of commands transfers.
    return commandsList, I2cTransferResponse_t()

#####################################################################
# --------------------------------- I3C -----------------------------
#####################################################################

def i3cInitBusCommandSerializer(id: c_uint16, targetDevicesTable: dict, remainingDevices: c_uint8, startIndex: c_uint8, endIndex: c_uint8 ) -> I3cInitBusRequest_t:
    '''
    This function sends an I3C INIT BUS command to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application.

    targetDevicesTable: dict
        Python dict that contains the Target Device Table information.

    remainingDevices: c_uint8
        The number of targets pending to be sent.

    startIndex: c_uint8
        The starting position of the target devices table.

    endIndex: c_uint8
        The last position of the target devices table whose device is sent inclusive.

    Returns
    -------
    None

    '''

    command = I3cInitBusRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_INIT_BUS

    # Set the number of remaining bytes.
    command.fields.targetCount = remainingDevices

    # Fill the target entries just if there are available devices and the indexes are valid values.
    deviceCount = endIndex - startIndex + 1

    if remainingDevices > 0 and deviceCount > 0 and deviceCount <= I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER:

        for i in range(deviceCount):

            # Retrieves the device from the table
            target = targetDevicesTable[startIndex + i]

            if target != None:
                tableEntry = I3cTargetDeviceEntry_t()
                tableEntry.staticAddress = target["staticAddress"]
                tableEntry.dynamicAddress = target["dynamicAddress"]
                tableEntry.i3cFeatures = target["i3cFeatures"]
                
                # Max IBI Payload
                maxIbiLength = target["maxIbiPayloadLength"]
                tableEntry.maxIbiPayloadSize = maxIbiLength

                # BCR. Create an instance of I3cBcrRegister_t and set the byte value.
                bcr = I3cBcrRegister_t()
                bcr.byte = target["bcr"]
                tableEntry.BCR = bcr

                # DCR
                tableEntry.DCR = target["dcr"]

                # Provisioned ID
                pid = target["pid"]
                tableEntry.PID.data[0:I3C_PID_SIZE] = pid[0:I3C_PID_SIZE]
                
                # Push table entry to command
                command.fields.targetsList[i] = tableEntry

            else:
                pass

    # Return command
    return command

def i3cTransferCommandSerializer(id: c_uint16, commandDescriptor: I3cTransferCommandDescriptor_t, data) -> I3cTransferRequest_t:

    '''
    This function sends an I3C_TRANSFER command to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    commandDescriptor: I3cTransferCommandDescriptor_t
        Structure that describes the type of I3C transfer requested.

    data: list
        Data to be sent if the transfer is an Private Write or SET command.

    Returns
    -------
    None

    '''

    command = I3cTransferRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_TRANSFER

    # Header
    command.fields.header.requestId = id

    dataLength = commandDescriptor.dataLength

    if (dataLength > 0 and commandDescriptor.readOrWrite == TransferDirection.WRITE.value):
        command.fields.header.hasData = 0x01

    # Descriptor
    command.fields.descriptor = commandDescriptor

    # Data Block
    for i in range(len(data)):
        command.fields.dataBlock[i] = data[i]

    # Return command
    return command

# ------------------------------------------------------------------------------- #
# ==================== USB COMMANDS REQUEST PUBLIC FUNCTIONS ==================== #
#
# Bellow are defined the public functions that are used to build the USB commands
# using the structures defined in usb_commands.py
# ------------------------------------------------------------------------------- #

# I3C CONTROLLER INIT ------------------------------------------------------------------ #

def i3cControllerInitSerializer(id: c_uint16) -> tuple[list[I3cControllerInitRequest_t],I3cControllerInitResponse_t]:
    '''
    This public function is used by the I3C Middleware service to send I3C CONTROLLER INIT command. 

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application.
    '''

    command = I3cControllerInitRequest_t()
 
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_CONTROLLER_INIT

    # Return command
    return [command], I3cControllerInitResponse_t()

# I3C BUS INIT ------------------------------------------------------------------ #

def i3cInitBusSerializer(id: c_uint16, targetDevicesTable: dict = None) -> tuple[list[I3cInitBusRequest_t],I3cInitBusResponse_t]:
    '''
    This public function is used by the I3C Middleware service to send I3C INIT BUS command. This public function
    calls the private __initI3cBus() passing the targetDevicesTable dictionary and indicating which devices are taken into consideration
    from the target devices table.

    This function calls __initI3cBus() more than once when the table contains more than 4 targets.

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application.

    targetDevicesTable: dict
        Python dict that contains the Target Device Table information.
    '''

    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    if targetDevicesTable != None:

        targetsCount = len(targetDevicesTable)

        # Calculate the number of USB transfers required depending of the table size.
        numberPackets = int(targetsCount / I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER)
        rest = targetsCount % I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER
        if (rest != 0):
            numberPackets = numberPackets + 1

        # Target device table is empty.
        if numberPackets == 0:
            command = i3cInitBusCommandSerializer(id, None, 0, 0, 0)
            commandsList.append(command)

        # Target device table is not empty.
        else:
            for i in range(numberPackets):
                    startIndex = i * I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER
                    if i < (numberPackets - 1):
                        endIndex = startIndex + I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER - 1
                        remainingTargetsCount = targetsCount - (i * I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER)
                    else:
                        if (rest == 0):
                            endIndex = startIndex + I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER - 1
                            remainingTargetsCount = I3C_INIT_BUS_MAX_TARGETS_PER_TRANSFER
                        else:
                            endIndex = startIndex + rest - 1
                            remainingTargetsCount = rest

                    command = i3cInitBusCommandSerializer(id, targetDevicesTable, remainingTargetsCount, startIndex, endIndex)
                    commandsList.append(command)

    # There is no devices
    else:
        command = i3cInitBusCommandSerializer(id, None, 0, 0, 0)
        commandsList.append(command)

    # Return list of commands transfers.
    return commandsList, I3cInitBusResponse_t()

# I3C GET TARGET DEVICE TABLE --------------------------------------------------- #

def i3cGetTargetDeviceTableSerializer(id: int) -> tuple[list[I3cGetTargetDeviceTableRequest_t], I3cGetTargetDeviceTableHighLevelResponse_t]:

    # Create command
    command = I3cGetTargetDeviceTableRequest_t()

    # Set endpoint ID and command opcode
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_GET_TARGET_DEVICE_TABLE

    return [command], I3cGetTargetDeviceTableHighLevelResponse_t()

# I3C SET TARGET DEVICE CONFIG -------------------------------------------------- #

def i3cSetTargetDeviceConfigSerializer(id: c_uint16, entries: dict) -> tuple[list[I3cSetTargetDevConfigRequest_t], I3cSetTargetDevConfigResponse_t]:

    # Create command
    command = I3cSetTargetDevConfigRequest_t()

    # Set endpoint ID and command opcode
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_SET_TARGET_DEVICE_CONFIG
    command.fields.numEntries = len(entries)

    for index, item in enumerate(entries.items()):
        '''
        enumerate returns the index of type int and the item of type tuple which
        contains an entry of the dictionary entries.
        '''
        targetDeviceConfigEntry = I3cTargetDeviceConfig_t()
        targetDeviceConfigEntry.targetAddress = item[0]
        targetDeviceConfigEntry.i3cFeatures = item[1]["features"]
        targetDeviceConfigEntry.maxIbiPayloadLength = item[1]["maxIbiPayloadLength"]

        command.fields.targetConfigList[index] = targetDeviceConfigEntry

    return [command], I3cSetTargetDevConfigResponse_t()

# I3C CHANGE DYNAMIC ADDRESS ---------------------------------------------------- #

def i3cChangeDynamicAddressSerializer(id: c_uint16, currentAddress: c_uint8, newAddress: c_uint8) -> tuple[list[I3cChangeDynAddrRequest_t], I3cChangeDynAddrResponse_t]:
    '''
    This function sets the command request and response for the SETNEWDAA CCC.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    currentAddress: c_uint8
        Current dynamic address of the target whose address we want to change

    newAddress:
        New dynamic address to assign to the target

    Returns
    -------
    The command and type of response associated to the SETNEWDAA CCC

    '''

    # Create command
    command = I3cChangeDynAddrRequest_t()

    # Set endpoint ID and command opcode
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_CHANGE_DA
    command.fields.currentDynamicAddress = currentAddress
    command.fields.newDynamicAddress = newAddress

    return [command], I3cChangeDynAddrResponse_t()

# I3C CLEAR FEATURE ------------------------------------------------------------- #

def i3cClearFeatureSerializer(id: c_uint16, selector: I3cClearFeatureSelector, targetAddress: c_uint8) -> tuple[list[I3cClearFeatureRequest_t], I3cClearFeatureResponse_t]:

    # Create command
    command = I3cClearFeatureRequest_t()

    # Set endpoint ID and command opcode
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_CLEAR_FEATURE
    command.fields.selector = selector.value
    command.fields.targetAddress = targetAddress

    return [command], I3cClearFeatureResponse_t()

# I3C SET FEATURE --------------------------------------------------------------- #

def i3cSetFeatureSerializer(id: c_uint16, selector: I3cSetFeatureSelector, targetAddress: c_uint8) -> tuple[list[I3cSetFeatureRequest_t],I3cSetFeatureResponse_t]:

    # Create command
    command = I3cSetFeatureRequest_t()

    # Set endpoint ID and command opcode
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_SET_FEATURE
    command.fields.selector = selector.value
    command.fields.targetAddress = targetAddress

    return [command], I3cSetFeatureResponse_t()

# I3C GET CAPABILITIES ---------------------------------------------------------- #

def i3cGetCapabilitySerializer(id: c_uint16) -> tuple[list[I3cGetCapabilitiesRequest_t], I3cGetCapabilitiesResponse_t]:

    '''
    This function retrieves I3C Capability data

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application.

    Returns
    -------
    bytes
        Byte array that contains the response of the USB Device.

    '''

    # Create command

    command = I3cGetCapabilitiesRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_GET_CAPABILITY

    # Return command
    return [command], I3cGetCapabilitiesResponse_t()

# I3C TRANSFER ------------------------------------------------------------------ #

def i3cWriteSerializer(id: c_uint16, targetAddress: c_uint8, mode: TransferMode, pushPullRate: I3cPushPullTransferRate, openDrainRate: I3cOpenDrainTransferRate, regAddress: list, data: list)  -> tuple[list[I3cTransferRequest_t],I3cTransferHighLevelResponse_t]:

    '''
    This function calls the private function __transfer() to send an I3C_TRANSFER with the command descriptor attribute
    set properly according to an I3C Write transfer.
    More than one USB transfers are performed when data length is greater than the payload size.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    targetAddress: c_uint8
        Target address.

    mode: TransferMode
        Transfer mode: I3C SDR, I3C HDR DDR, I2C, etc.

    rate: I3cTransferRate
        Rate/Speed of the transaction.

    regAddress: list
        List that contains the target internal register address where the data is written.

    data : list
        List that contains the data to be written.

    Returns
    -------
    bytes
        bytes that contains the response of the USB Device.

    '''

    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    # Create command descriptor
    commandDescriptor = I3cTransferCommandDescriptor_t()

    commandDescriptor.commandType = I3cCommandType.REGULAR_COMMAND.value
    commandDescriptor.readOrWrite = TransferDirection.WRITE.value
    commandDescriptor.errorHandling = 0x00                                # Not used nowadays.
    commandDescriptor.targetAddress = targetAddress
    commandDescriptor.transferMode = mode.value
    commandDescriptor.transferRate = pushPullRate.value | openDrainRate.value
    commandDescriptor.definingByte = 0x00
    commandDescriptor.CCC = 0x00

    # Data block
    regSize = len(regAddress)
    payload = [regSize] + regAddress + data

    payloadLength = len(payload)
    commandDescriptor.dataLength = payloadLength

    # Generate payload chunks.
    nPayloadChunks, payloadChunks = splitDataUtility(payload, I3C_TRANSFER_REQ_DATA_LENGTH)

    # Send command(s).
    if nPayloadChunks == 0:
        command = i3cTransferCommandSerializer(id, commandDescriptor, [])
        commandsList.append(command)
    else:
        for i in range(nPayloadChunks):
            commandDescriptor.dataLength = payloadChunks[i][0]
            command = i3cTransferCommandSerializer(id, commandDescriptor, payloadChunks[i][1])
            commandsList.append(command)

    # Return list of commands transfers.
    return commandsList, I3cTransferHighLevelResponse_t()

def i3cReadSerializer(id: c_uint16, targetAddress: c_uint8, mode: TransferMode, pushPullRate: I3cPushPullTransferRate, openDrainRate: I3cOpenDrainTransferRate, regAddress: list, length: c_uint16) -> tuple[list[I3cTransferRequest_t],I3cTransferHighLevelResponse_t]:

    '''
    This functions calls the private function __transfer() to send an I3C_TRANSFER with the command descriptor attribute
    set properly according to an I3C Read transaction.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    targetAddress: c_uint8
        Target address.

    mode: TransferMode
        Transfer mode: I3C SDR, I3C HDR DDR, I2C, etc.

    rate: I3cTransferRate
        Rate/Speed of the transaction.

    regAddress: list
        Python list that contains the target internal register address

    '''

    # Create command descriptor
    commandDescriptor = I3cTransferCommandDescriptor_t()

    commandDescriptor.commandType = I3cCommandType.REGULAR_COMMAND.value
    commandDescriptor.readOrWrite = TransferDirection.READ.value
    commandDescriptor.errorHandling = 0x00                                # Not currently used.
    commandDescriptor.targetAddress = targetAddress
    commandDescriptor.transferMode = mode.value
    commandDescriptor.transferRate = pushPullRate.value | openDrainRate.value
    commandDescriptor.definingByte = 0x00
    commandDescriptor.CCC = 0x00

    # Data block
    regAddressSize = len(regAddress)
    payload = [regAddressSize] + regAddress

    commandDescriptor.dataLength = length

    command = i3cTransferCommandSerializer(id, commandDescriptor, payload)

    return [command], I3cTransferHighLevelResponse_t()

def i3cSendCccSerializer(id: c_uint16, cmdType: c_uint8, isReadOrWrite: c_uint8, targetAddress: c_uint8, mode: TransferMode, pushPullRate: I3cPushPullTransferRate, openDrainRate: I3cOpenDrainTransferRate, defByte: c_uint8, ccc: c_uint8, length: c_uint16, data: list) :
    '''
    This functions calls the private function __transfer() to send an I3C_TRANSFER with the command descriptor attribute
    set properly according to an I3C CCC transaction.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    cmdType: c_uint8
        Integer used to differenciate between CCC with or without defining byte

    isReadOrWrite: c_uint8
        Integer that indicates wheter the CCC performs a read or write operation

    targetAddress: c_uint8
        Target address.

    mode: TransferMode
        Transfer mode: I3C SDR, I3C HDR DDR, I2C, etc.

    rate: I3cTransferRate
        Rate/Speed of the transaction.

    defByte: c_uint8
        Defining byte in case cmdType indicates the command includes one

    ccc: c_uint8
        Code to send

    length: c_uint16
        Length of the data to be written or retrieved

    data : list
        List that contains the data to be written.

    '''

    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    # Create command descriptor
    commandDescriptor = I3cTransferCommandDescriptor_t()

    commandDescriptor.commandType = cmdType.value
    commandDescriptor.readOrWrite = isReadOrWrite.value
    commandDescriptor.errorHandling = 0x00 # Not used actually.
    commandDescriptor.targetAddress = targetAddress
    commandDescriptor.transferMode = mode.value
    commandDescriptor.transferRate = pushPullRate.value | openDrainRate.value
    commandDescriptor.definingByte = defByte
    commandDescriptor.CCC = ccc.value

    # Data block

    if isReadOrWrite == TransferDirection.READ:
        commandDescriptor.dataLength = length
        command = i3cTransferCommandSerializer(id, commandDescriptor, [])
        commandsList.append(command)
    else:
        dataLen = len(data)
        commandDescriptor.dataLength = dataLen

        # Generate payload chunks.
        nPayloadChunks, payloadChunks = splitDataUtility(data, I3C_TRANSFER_REQ_DATA_LENGTH)

        # Send command(s)
        if nPayloadChunks == 0:
            command = i3cTransferCommandSerializer(id, commandDescriptor, [])
            commandsList.append(command)
        else:
            for i in range(nPayloadChunks):
                commandDescriptor.dataLength = payloadChunks[i][0]
                command = i3cTransferCommandSerializer(id, commandDescriptor, payloadChunks[i][1])
                commandsList.append(command)

    # Get response instance from CCC_RESPONSE_INSTANCE dictionary.
    response =  CCC_RESPONSE_INSTANCE[ccc]()

    # Return list of commands transfers.
    return commandsList, response

def i3cTargetResetSerializer(id: c_uint16, isReadOrWrite: TransferDirection, targetAddress: c_uint8, pushPullRate: I3cPushPullTransferRate, openDrainRate: I3cOpenDrainTransferRate, defByte: I3cTargetResetDefByte) -> tuple[list[I3cTransferRequest_t], I3cTransferHighLevelResponse_t]:

    '''
    This functions calls the private function __transfer() to send an TARGET_RESET with the command descriptor attribute
    set properly according to an I3C TARGET RESET transaction.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    isReadOrWrite: c_uint8
        Integer that indicates wheter the CCC performs a read or write operation

    targetAddress: c_uint8
        Target address.

    rate: I3cTransferRate
        Rate/Speed of the transaction.

    defByte: c_uint8
        Defining byte for RSTACT CCC

    '''

    # Create command descriptor
    commandDescriptor = I3cTransferCommandDescriptor_t()

    commandDescriptor.commandType = I3cCommandType.TARGET_RESET_PATTERN.value
    commandDescriptor.readOrWrite = isReadOrWrite.value
    commandDescriptor.errorHandling = 0x00                                # Not currently used.
    commandDescriptor.targetAddress = targetAddress
    commandDescriptor.transferRate = pushPullRate.value | openDrainRate.value
    commandDescriptor.definingByte = defByte.value

    command = i3cTransferCommandSerializer(id, commandDescriptor, [])

    return [command], I3cTransferHighLevelResponse_t()

def i3cTransferSerializer(metadata: dict):

    # Private Write or Private Read.
    if (metadata["commandType"] == I3cCommandType.REGULAR_COMMAND):

        if (metadata["isReadOrWrite"] == TransferDirection.WRITE):
            return i3cWriteSerializer(metadata["id"], metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["registerAddress"], metadata["data"])

        elif (metadata["isReadOrWrite"] == TransferDirection.READ):
            return i3cReadSerializer(metadata["id"], metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["registerAddress"], metadata["length"])

    # Target Reset
    elif (metadata["commandType"] == I3cCommandType.TARGET_RESET_PATTERN):
        return i3cTargetResetSerializer(metadata["id"], metadata["isReadOrWrite"], metadata["targetAddress"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["defByte"])

    # CCC
    else:
        return i3cSendCccSerializer(metadata["id"], metadata["commandType"], metadata["isReadOrWrite"],  metadata["targetAddress"], metadata["mode"], metadata["pushPullRate"], metadata["openDrainRate"], metadata["defByte"], metadata["ccc"], metadata["length"], metadata["data"])

# I3C TARGET INIT ------------------------------------------------------------------ #

def i3cTargetInitSerializer(id: c_uint16, memoryLayout: I3cTargetMemoryLayout_t, uSecondsWaitIbi: c_uint8, maxRdLength: c_uint16, maxWrLength: c_uint16, i3cFeatures: c_uint8) -> tuple[list[I3cTargetInitRequest_t],I3cTargetInitResponse_t]:
    '''
    This public function is used by the I3C Middleware service to send I3C TARGET INIT command.

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application

    memoryLayout: I3cTargetMemoryLayout_t
                  Layout of the memory of the Supernova as an I3C target

    uSecondsWaitIbi: c_uint8
                     Micro Seconds to allow an In-Band Interrupt (IBI) to drive SDA low when the controller is not doing so

    maxRdLength: c_uint16
                 Maximum read length (in bytes) of the Supernova

    maxWrLength: c_uint16
                 Maximum write length (in bytes) of the Supernova

    i3cFeatures: c_uint8
                 Variable that holds the configuration flags of the Supernova in target mode
    '''

    command = I3cTargetInitRequest_t()

    # Create I3cTargetFeatures_t variable
    targetFeatures = I3cTargetFeatures_t()
    targetFeatures.i3cOffline = ((i3cFeatures & I3C_OFFLINE_MASK) >> I3C_OFFLINE_SHIFT)
    targetFeatures.partNOrandom = ((i3cFeatures & PART_NO_RANDOM_MASK) >> PART_NO_RANDOM_SHIFT)
    targetFeatures.ddrOk = ((i3cFeatures & DDR_OK_MASK) >> DDR_OK_SHIFT)
    targetFeatures.ignoreTE0TE1Errors = ((i3cFeatures & IGNORE_ERRORS_MASK) >> IGNORE_ERRORS_SHIFT)
    targetFeatures.matchStartStop = ((i3cFeatures & MATCH_START_STOP_MASK) >> MATCH_START_STOP_SHIFT)
    targetFeatures.alwaysNack = ((i3cFeatures & ALWAYS_NACK_MASK) >> ALWAYS_NACK_SHIFT)

    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_TARGET_INIT
    command.fields.memoryLayout = memoryLayout.value
    command.fields.uSecondsToWaitForIbi = uSecondsWaitIbi
    command.fields.maxReadLength = maxRdLength
    command.fields.maxWriteLength = maxWrLength
    command.fields.targetFeatures= targetFeatures
    
    # Return command
    return [command], I3cTargetInitResponse_t()

def i3cTargetSetConfSerializer(id: c_uint16, uSecondWaitIbi: c_uint8, maxRdLength: c_uint16, maxWrLength: c_uint16, i3cFeatures: c_uint8) -> tuple[list[I3cTargetSetConfRequest_t],I3cTargetSetConfResponse_t]:
    '''
    This public function is used by the I3C Middleware service to send I3C TARGET SET CONFIGURATION command.

    Arguments
    ---------
    id: c_uint16
        Integer that identifies the USB command requested by the USB host application.

    uSecondWaitIbi: c_uint8
                    Micro seconds to allow an In-Band Interrupt (IBI) to drive SDA low when the controller is not doing so

    maxRdLength: c_uint16
                 Maximum read length (in bytes) of the Supernova

    maxWrLength: c_uint16
                 Maximum write length (in bytes) of the Supernova

    i3cFeatures: I3cTargetFeatures_t
                 Variable that holds the configuration flags of the Supernova in target mode
    '''

    command = I3cTargetSetConfRequest_t()

    # Create I3cTargetFeatures_t variable
    targetFeatures = I3cTargetFeatures_t()
    targetFeatures.i3cOffline = ((i3cFeatures & I3C_OFFLINE_MASK) >> I3C_OFFLINE_SHIFT)
    targetFeatures.partNOrandom = ((i3cFeatures & PART_NO_RANDOM_MASK) >> PART_NO_RANDOM_SHIFT)
    targetFeatures.ddrOk = ((i3cFeatures & DDR_OK_MASK) >> DDR_OK_SHIFT)
    targetFeatures.ignoreTE0TE1Errors = ((i3cFeatures & IGNORE_ERRORS_MASK) >> IGNORE_ERRORS_SHIFT)
    targetFeatures.matchStartStop = ((i3cFeatures & MATCH_START_STOP_MASK) >> MATCH_START_STOP_SHIFT)
    targetFeatures.alwaysNack = ((i3cFeatures & ALWAYS_NACK_MASK) >> ALWAYS_NACK_SHIFT)

    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_TARGET_SET_CONFIGURATION
    command.fields.uSecondsToWaitForIbi = uSecondWaitIbi
    command.fields.maxReadLength = maxRdLength
    command.fields.maxWriteLength = maxWrLength
    command.fields.targetFeatures= targetFeatures

    # Return command
    return [command], I3cTargetSetConfResponse_t()

def i3cTargetWriteMemCommandSerializer(id: c_uint16, memAddress: c_uint16, length: c_uint8, data: list) -> I3cTargetWriteMemRequest_t:
    '''
    This function sends an I3C_TARGET_WRITE_MEM command to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    memAddress: c_uint16
        Address of the memory with MSB indicating if the user intended to surpass the memory range

    length:
        length of the data to be sent in the command request

    data: list
        Data to be sent.

    Returns
    -------
    variable of type I3cTargetWriteMemRequest_t that represents the command request

    '''

    command = I3cTargetWriteMemRequest_t()

    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_TARGET_WRITE_MEMORY
    command.fields.memoryAddress = memAddress
    command.fields.length = length

    # Data Block
    for i in range(len(data)):
        command.fields.dataBlock[i] = data[i]

    # Return command
    return command

def i3cTargetWriteMemSerializer(id: c_uint16, memoryAddr: c_uint16, data: list) -> tuple[list[I3cTargetWriteMemRequest_t],I3cTargetWriteMemResponse_t]:
    '''
    This function calls the private function i3cTargetWriteMemCommandSerializer to send an I3C_TARGET_WRITE_MEM
    More than one USB transfers are performed when data length is greater than the payload size.
    If the user tries to surpass the end of the memory, the firmware is notified with the MSB of the memoryAddress field set so that it knows the response should indicate an error.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    memoryAddr: c_uint16
        Address of the memory to start writing

    data : list
        List that contains the data to be written.

    Returns
    -------
    bytes
        bytes that contains the response of the USB Device.

    '''
    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    payload = data
    length = len(payload)

    # Data block
    
    # Generate payload chunks
    nPayloadChunks, payloadChunks = splitDataUtility(payload, I3C_TARGET_WRITE_MEM_REQ_DATA_LENGTH)

    # Send command(s)
    for i in range(nPayloadChunks):
        length = payloadChunks[i][0]
        command = i3cTargetWriteMemCommandSerializer(id, memoryAddr, length, payloadChunks[i][1])
        commandsList.append(command)

    # Return list of commands transfers.
    return commandsList, I3cTargetWriteMemResponse_t()

def i3cTargetReadMemSerializer(id: c_uint16, memoryAddr: c_uint16, length: c_uint16) -> tuple[list[I3cTargetReadMemRequest_t],I3cTargetReadMemHighLevelResponse_t]:
    '''
    This function sends an I3C_TARGET_READ_MEM command to the USB HID device.
    The firmware handles the error caused when the user tries to surpass the end of the memory, it is not indicated in the request generated in this function.
    The firmware realizes the error when (length > I3C_TARGET_MEMORY_LENGTH - memoryAddr).

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    memoryAddr: c_uint16
        Address of the memory to start reading

    length: c_uint16
        Length of the data to be read

    Returns
    -------
    bytes
        bytes that contains the response of the USB Device.

    '''

    command = I3cTargetReadMemRequest_t()

    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = I3C_TARGET_READ_MEMORY
    command.fields.memoryAddress = memoryAddr
    command.fields.length = length

    # Return command
    return [command], I3cTargetReadMemHighLevelResponse_t()

#####################################################################
# ------------------------ UART CONTROLLER --------------------------
#####################################################################

def uartControllerInitSerializer(id: int, baudrate: UartControllerBaudRate, hardwareHandshake:bool, parityMode:UartControllerParity, dataSize:UartControllerDataSize, stopBit: UartControllerStopBit) -> tuple[list[UartControllerSetParamsRequest_t], UartControllerSetParamsResponse_t]:

    '''
    This function creates the associated command for the INIT command to send to the USB HID device. 

    Arguments
    ---------
    id : int
        It is a 2-bytes integer that represents the transfer id. The range allowed is [0, 65535].

    baudrate : UartControllerBaudRate
        This parameter represents the UART TX and RX frequency from the options provided by the UartControllerBaudRate enum.
        The frequency goes from 600bps to up to 115200bps.

    hardwareHandshake : bool 
        This parameter represents a boolean flag to enable or disable this option.
    
    parityMode: UartControllerParity
        This parameter represents the different parity modes available in the UartControllerParity enum.
        The parity modes are: none, even or odd.
    
    dataSize: UartControllerDataSize
        This parameter represents the different data sizes available in the UartControllerDataSize enum.
        The data sizes are either 7 or 8.

    stopBit: UartControllerStopBit
        This parameter represent the different stop bit configuration available in the UartControllerStopBit enum.
        The stop bit can be of size 1 or 2.

    Returns
    -------
    tuple
        Command list with the command to be sent to the USB device and the response instance.

    '''

    # Create command descriptor
    command = UartControllerInitRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = UART_CONTROLLER_INIT
    command.fields.baudRate = baudrate.value
    command.fields.hardwareHandshake = hardwareHandshake
    command.fields.parityMode = parityMode.value
    command.fields.dataSize = dataSize.value
    command.fields.stopBitType = stopBit.value

    return [command], UartControllerInitResponse_t()


def uartControllerSetParametersSerializer(id: int, baudrate: UartControllerBaudRate, hardwareHandshake:bool, parityMode:UartControllerParity, dataSize:UartControllerDataSize, stopBit: UartControllerStopBit) -> tuple[list[UartControllerSetParamsRequest_t], UartControllerSetParamsResponse_t]:

    '''
    This function creates the associated command for the SET PARAMETERS command to send to the USB HID device. 

    Arguments
    ---------
    id : int
        It is a 2-bytes integer that represents the transfer id. The range allowed is [0, 65535].

    baudrate : UartControllerBaudRate
        This parameter represents the UART TX and RX frequency from the options provided by the UartControllerBaudRate enum.
        The frequency goes from 600bps to up to 115200bps.

    hardwareHandshake : bool 
        This parameter represents a boolean flag to enable or disable this option.
    
    parityMode: UartControllerParity
        This parameter represents the different parity modes available in the UartControllerParity enum.
        The parity modes are: none, even or odd.
    
    dataSize: UartControllerDataSize
        This parameter represents the different data sizes available in the UartControllerDataSize enum.
        The data sizes are either 7 or 8.

    stopBit: UartControllerStopBit
        This parameter represent the different stop bit configuration available in the UartControllerStopBit enum.
        The stop bit can be of size 1 or 2.

    Returns
    -------
    tuple
        Command list with the command to be sent to the USB device and the response instance.

    '''

    # Create command descriptor
    command = UartControllerSetParamsRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = UART_CONTROLLER_SET_PARAMETERS
    command.fields.baudRate = baudrate.value
    command.fields.hardwareHandshake = hardwareHandshake
    command.fields.parityMode = parityMode.value
    command.fields.dataSize = dataSize.value
    command.fields.stopBitType = stopBit.value

    return [command], UartControllerSetParamsResponse_t()

def uartControllerSendMessageSerializer(id: c_uint16, payload: list) -> tuple[list[UartControllerSendRequest_t], UartControllerSendResponse_t]:
    '''
    Divides the transaction into multiple commands packages to send to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    payload: list
        Data to be sent.

    Returns
    -------
    tuple
        Command list with the command to be sent to the USB device and the response instance.

    '''
    
    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    # Generate payload chunks.
    nPayloadChunks, payloadChunks = splitDataUtility(payload, UART_CONTROLLER_SEND_REQ_COMMAND_PAYLOAD_LENGTH)
    # Send command(s).
    if nPayloadChunks == 0:
        command = uartSendCommandSerializer(id)
        commandsList.append(command)
    else:
        for i in range(nPayloadChunks):
            command = uartSendCommandSerializer(id, payloadChunks[i])
            commandsList.append(command)
    # Return list of commands transfers.
    return commandsList, UartControllerSendResponse_t()

def uartSendCommandSerializer(id: c_uint16, payloadChunk = (0,[])) -> UartControllerSendResponse_t:
    '''
    This function creates the commands packages to send to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    payloadChunk: tuple
        Data to be sent and the remaining length. By default it is (0,[]) for the
        case when the payload is empty.

    Returns
    -------
    Command to append
    
    '''
    command = UartControllerSendRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = UART_CONTROLLER_SEND
    command.fields.payloadLength = payloadChunk[0]

    # Load Payload
    for i in range(len(payloadChunk[1])):
        command.fields.payload[i] = payloadChunk[1][i]

    # Return command
    return command

#####################################################################
# ------------------------ SPI CONTROLLER ---------------------------
#####################################################################

def spiControllerInitSerializer(id: c_uint16,
                                 bitOrder: SpiControllerBitOrder,
                                 mode: SpiControllerMode,
                                 dataWidth: SpiControllerDataWidth,
                                 chipSelect: SpiControllerChipSelect,
                                 chipSelectPol: SpiControllerChipSelectPolarity,
                                 frequency: c_uint32) -> tuple[list[SpiControllerInitRequest_t], SpiControllerInitResponse_t]:
    """
    This function performs a SPI_CONTROLLER_INIT command, sending configuration data to
    initialize the SPI controller.
    
    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    bitOrder: SpiControllerBitOrder
        Sets the bit's order of the transfer. It could be MSB or LSB first.

    mode: SpiControllerMode
        Sets the transfer mode: Mode 0, Mode 1, Mode 2 or Mode 3.

    dataWidth: SpiControllerDataWidth
        Sets the data width of the transfer. It could be 8 or 16 bits.

    chipSelect: SpiControllerChipSelect
        Sets the chip select to be used: Chip Select 0, Chip Select 1, Chip Select 2 or Chip Select 3.

    chipSelectPol : SpiControllerChipSelectPolarity
        Sets the chip select polarity: Active Low or Active High.

    frequency : c_uint32
        Value of frequency to be set in the SPI controller expressed in Hz.

    Returns
    -------
    tuple
        Command list with the commands to be sent to the USB device and the response instance.
    """
    # Create command instance
    command = SpiControllerInitRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = SPI_CONTROLLER_INIT
    command.fields.bitOrder = bitOrder.value
    command.fields.mode = mode.value
    command.fields.dataWidth = dataWidth.value
    command.fields.chipSelect = chipSelect.value
    command.fields.chipSelectPol = chipSelectPol.value
    command.fields.frequency = frequency

    return [command], SpiControllerInitResponse_t()

def spiControllerSetParametersSerializer(id: c_uint16,
                                         bitOrder: SpiControllerBitOrder,
                                         mode: SpiControllerMode,
                                         dataWidth: SpiControllerDataWidth,
                                         chipSelect: SpiControllerChipSelect,
                                         chipSelectPol: SpiControllerChipSelectPolarity,
                                         frequency: c_uint32) -> tuple[list[SpiControllerSetParameterRequest_t], SpiControllerSetParameterResponse_t]:
    """
    This function performs a SPI_CONTROLLER_SET_PARAMETERS command, sending optional data to
    set bit order, mode, data width, chip select, chip select polarity and clock frequency.
    
    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    bitOrder: SpiControllerBitOrder
        Sets the bit's order of the transfer. It could be MSB or LSB first.

    mode: SpiControllerMode
        Sets the transfer mode: Mode 0, Mode 1, Mode 2 or Mode 3.

    dataWidth: SpiControllerDataWidth
        Sets the data width of the transfer. It could be 8 or 16 bits.

    chipSelect: SpiControllerChipSelect
        Sets the chip select to be used: Chip Select 0, Chip Select 1, Chip Select 2 or Chip Select 3.

    chipSelectPol : SpiControllerChipSelectPolarity
        Sets the chip select polarity: Active Low or Active High.

    frequency : c_uint32
        Value of frequency to be set in the SPI controller expressed in Hz.

    Returns
    -------
    tuple
        Command list with the commands to be sent to the USB device and the response instance.
    """
    # Create command instance
    command = SpiControllerSetParameterRequest_t()

    # Fill command fields.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = SPI_CONTROLLER_SET_PARAMETERS
    command.fields.bitOrder = bitOrder.value
    command.fields.mode = mode.value
    command.fields.dataWidth = dataWidth.value
    command.fields.chipSelect = chipSelect.value
    command.fields.chipSelectPol = chipSelectPol.value
    command.fields.frequency = frequency

    # Return command
    return [command], SpiControllerSetParameterResponse_t()

def spiControllerTransferSerializer(id: c_uint16,
                                    transferLength: c_uint16,
                                    payload: list) -> tuple[list[SpiControllerTransferRequest_t], SpiControllerTransferResponse_t]:
    """
    This function performs a SPI_CONTROLLER_TRANSFER command, sending data to
    the SPI controller.

    Arguments
    ---------
    id : c_uint16
        An integer number that identifies the transfer.

    transferLength : c_uint16
        Length of the transfer.
    
    payload : list
        List that contains the data to be sent.
    
    Returns
    -------
    tuple
        Command list with the commands to be sent to the USB device and the response instance.
    """
    # List returned. It contains the bunch of commands to send to the USB device.
    commandsList = []

    # Generate payload chunks.
    nPayloadChunks, payloadChunks = splitDataUtility(payload, SPI_CONTROLLER_TRANSFER_REQUEST_PAYLOAD_LENGTH)

    # Send command(s).
    if nPayloadChunks == 0:
        command = spiControllerTransferCommandSerializer(id, transferLength)
        commandsList.append(command)
    else:
        for i in range(nPayloadChunks):
            command = spiControllerTransferCommandSerializer(id, transferLength, payloadChunks[i])
            commandsList.append(command)

    # Return list of commands transfers.
    return commandsList, SpiControllerTransferHighLevelResponse_t()

def spiControllerTransferCommandSerializer(id: c_uint16, transferLength, payloadChunk=(0,[])) -> SpiControllerTransferRequest_t:
    """
    This function creates the commands packages to send to the USB HID device.

    Arguments
    ---------
    id: c_uint16
        ID that identifies the transaction.

    transferLength: c_uint16
        Total length of the transfer. Includes the length of the sent payload and the received if it's needed.

    payloadChunk: tuple
        Data to be sent and the remaining length. Default value is (0,[]) for the empty data case.

    Returns
    -------
    Command to append
    """
    command = SpiControllerTransferRequest_t()

    # Set endpoint ID and command opcode.
    command.fields.endpointId = ENDPOINT_ID
    command.fields.id = id
    command.fields.cmd = SPI_CONTROLLER_TRANSFER
    command.fields.payloadLength = payloadChunk[0]
    command.fields.transferLength = transferLength

    # Load Payload
    for i in range(len(payloadChunk[1])):
        command.fields.payload[i] = payloadChunk[1][i]

    # Return command
    return command
