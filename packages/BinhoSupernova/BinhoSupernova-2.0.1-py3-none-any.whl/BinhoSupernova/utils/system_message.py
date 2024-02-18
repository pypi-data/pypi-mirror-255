from enum import Enum

class SystemModules(Enum):
    '''
    This enum represents the available system modules.
    '''
    SYSTEM = 0
    VALIDATION = 1

class SystemOpcode(Enum):
    '''
    This enum represents the system module opcodes.
    '''
    OK                          = 0x00
    OPEN_CONNECTION_FAIL        = 0x01
    OPEN_CONNECTION_REQUIRED    = 0x02
    CLOSE_CONNECTION_REQUEST    = 0x03
    INVALID_CALLBACK_SIGNATURE  = 0x04
    UNEXPECTED_DISCONNECTION    = 0x05
    CONFIGURATION_ERROR         = 0x06
    # TODO: Add as many system message opcodes as needed.

class RequestValidatorOpcode(Enum):
    '''
    This enum represents the validator module opcodes.
    '''
    SUCCESS = 0x00
    FAIL    = 0x01

# dictionary that associates the module to its opcodes 
ModuleOpcodes = {
    SystemModules.SYSTEM: SystemOpcode,
    SystemModules.VALIDATION: RequestValidatorOpcode,
}

class SystemMessage:
    '''
    This class represents a system message.
    '''
    def __init__(self, module: SystemModules, opcode, message) -> None:
        self.module = module
        self.opcode = opcode
        self.message = message

    def toDictionary(self) -> dict:
        return {
            "module" : self.module.value,
            "opcode": self.opcode.value,
            "message" : self.message
        }

    def __str__(self) -> str:
        return str(self.toDictionary())
