from enum import Enum
import sys
import platform

system = platform.system()
python_major, python_minor = sys.version_info[:2]

if system == "Windows":
    if (python_major, python_minor) == (3, 12):
        from .win import PyZlBusApi_py312 as zlb
    elif (python_major, python_minor) == (3, 11):
        from .win import PyZlBusApi_py311 as zlb
    else :
        from .win import PyZlBusApi_py310 as zlb
elif system == "Darwin":  # 加载macOS环境下所需的文件
    if (python_major, python_minor) == (3, 12):
        from .linux import libPyZlBusApi_py312 as zlb
    elif (python_major, python_minor) == (3, 11):
        from .linux import libPyZlBusApi_py311 as zlb
    else :
        from .linux import libPyZlBusApi_py310 as zlb
elif system == "Linux":
    if (python_major, python_minor) == (3, 12):
        from .linux import libPyZlBusApi_py312 as zlb
    elif (python_major, python_minor) == (3, 11):
        from .linux import libPyZlBusApi_py311 as zlb
    else :
        from .linux import libPyZlBusApi_py310 as zlb
else:
    raise ValueError(f"Unsupported operating system: {system}")

#====================================================================
# 最低固件版本支持 V00.67.18.000
#====================================================================

class e_CmdError(Enum):
    '''
    指令执行或解码错误
    '''
    ERROR_NONE                        = zlb.e_ERROR_CMU.ERROR_NONE                          # 无错误
    ERROR_PK_LEN                      = zlb.e_ERROR_CMU.ERROR_PK_LEN                        # 包长度错误
    ERROR_TYPE                        = zlb.e_ERROR_CMU.ERROR_TYPE                          # 未知指令类型
    ERROR_PK                          = zlb.e_ERROR_CMU.ERROR_PK                            # 未知包格式
    ERROR_CHECK                       = zlb.e_ERROR_CMU.ERROR_CHECK                         # 校验错误
    ERROR_SUBCMD                      = zlb.e_ERROR_CMU.ERROR_SUBCMD                        # 子指令ID错误
    ERROR_DOT                         = zlb.e_ERROR_CMU.ERROR_DOT                           # DOT ID不匹配
    ERROR_DATA                        = zlb.e_ERROR_CMU.ERROR_DATA                          # 错误数据(or 数据格式)
    ERROR_TRACK                       = zlb.e_ERROR_CMU.ERROR_TRACK                         # 设备ID不匹配    (Dongle 端)
    ERROR_DONGLE                      = zlb.e_ERROR_CMU.ERROR_DONGLE                        # Dongle ID不匹配 (Dongle 端)
    ERROR_RF                          = zlb.e_ERROR_CMU.ERROR_RF                            # 蓝牙ID不匹配
    ERROR_RF_CONN                     = zlb.e_ERROR_CMU.ERROR_RF_CONN                       # 蓝牙未连接不存在该设备)
    ERROR_FACTORY_SET                 = zlb.e_ERROR_CMU.ERROR_FACTORY_SET                   # 厂家设置未打开
    ERROR_RF_MAC                      = zlb.e_ERROR_CMU.ERROR_RF_MAC                        # RF MAC 格式错误
    ERROR_IO                          = zlb.e_ERROR_CMU.ERROR_IO                            # I/O error
    ERROR_FUNC_NOT_INIT               = zlb.e_ERROR_CMU.ERROR_FUNC_NOT_INIT                 # 功能未初始化
    ERROR_FUNC_NOT_CONFIG             = zlb.e_ERROR_CMU.ERROR_FUNC_NOT_CONFIG               # 功能未配置
    ERROR_FUNC_NOT_OPEN               = zlb.e_ERROR_CMU.ERROR_FUNC_NOT_OPEN                 # 功能未开启
    DFU_ERROR_DATA_BLOCK_LEN          = zlb.e_ERROR_CMU.DFU_ERROR_DATA_BLOCK_LEN            # 设置的固件数据块错误
    DFU_ERROR_INVALID_DATAPKT         = zlb.e_ERROR_CMU.DFU_ERROR_INVALID_DATAPKT           # 固件数据无归属，无效数据包
    DFU_ERROR_FIRMWARE_CRC            = zlb.e_ERROR_CMU.DFU_ERROR_FIRMWARE_CRC              # 固件CRC错误
    DFU_ERROR_FIRMWARE_TYPE           = zlb.e_ERROR_CMU.DFU_ERROR_FIRMWARE_TYPE             # 固件版本错误
    DFU_ERROR_FIRMWARE_STORE_FINISH   = zlb.e_ERROR_CMU.DFU_ERROR_FIRMWARE_STORE_FINISH     # 固件未保存完成
    DFU_ERROR_DATA_PACKAGE_INDEX      = zlb.e_ERROR_CMU.DFU_ERROR_DATA_PACKAGE_INDEX        # 流水号不连续
    DFU_ERROR_NO_MEM                  = zlb.e_ERROR_CMU.DFU_ERROR_NO_MEM                    # SRAM 空间不足
    DFU_ERROR_NO_FLASH                = zlb.e_ERROR_CMU.DFU_ERROR_NO_FLASH                  # FLASH 空间不足
    DFU_ERROR_OTA_SETTINGS            = zlb.e_ERROR_CMU.DFU_ERROR_OTA_SETTINGS              # OTA 配置错误
    DFU_ERROR_FIRMWARE_DATA_BLOCK_LEN = zlb.e_ERROR_CMU.DFU_ERROR_FIRMWARE_DATA_BLOCK_LEN   # 固件数据块长度错误
    ERROR_NOKNOW                      = zlb.e_ERROR_CMU.ERROR_NOKNOW                        # 未知错误
    ERROR_NULL                        = zlb.e_ERROR_CMU.ERROR_NULL                          # 传入空指针


class e_UpLoadDataForMat(Enum):
    '''
    上传数据格式
    '''
    UPLOAD_DATA_QUATERNION = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_QUATERNION  # 四元数
    UPLOAD_DATA_RPY        = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_RPY         # 欧拉角
    UPLOAD_DATA_ACC        = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_ACC         # 加速度 g
    UPLOAD_DATA_GYRO       = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_GYRO        # 陀螺仪 °/s
    UPLOAD_DATA_MAG        = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_MAG         # 磁力计uT
    UPLOAD_DATA_LIN_ACC    = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_LIN_ACC     # 线性加速度 g
    UPLOAD_DATA_TEMP       = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_TEMP        # IMU传感器温度
    UPLOAD_DATA_ADCx       = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_ADCx        # adc (手指弯曲传感器)
    UPLOAD_DATA_TIME       = zlb.e_UPLOAD_FORMAT.NEW_UPLOAD_DATA_TIME        # 时间戳


class e_FLOW_FORMAT(Enum):
    '''
    上传数据包流水号格式
    '''
    FLOW_ID_FORMAT_8  = zlb.e_Tk_FLOW_FORMAT.TK_FLOW_ID_FORMAT_8
    FLOW_ID_FORMAT_16  = zlb.e_Tk_FLOW_FORMAT.TK_FLOW_ID_FORMAT_16


class e_ZlbusError(Enum):
    '''
    程序支持返回值状态码
    '''
    TKxx_SUCCESS       = zlb.TKxx_SUCCESS           # 成功           success
    TKxx_ERR_FAILED    = zlb.TKxx_ERR_FAILED        # 失败           failed
    TKxx_ERR_READY     = zlb.TKxx_ERR_READY         # 未准备好       Not ready
    TKxx_ERR_MEM       = zlb.TKxx_ERR_MEM           # 内存不足       Out of memory
    TKxx_ERR_MAX_SIZE  = zlb.TKxx_ERR_MAX_SIZE      # 超限制
    TKxx_ERR_INTERN    = zlb.TKxx_ERR_INTERN        # 内部错误       Internal error
    TKxx_ERR_BUSY      = zlb.TKxx_ERR_BUSY          # 设备或资源繁忙  Device or resource busy
    TKxx_ERR_ALREADY   = zlb.TKxx_ERR_ALREADY       # 操作已在进行中  Operation already in progress
    TKxx_ERR_VAL       = zlb.TKxx_ERR_VAL           # 无效的参数     Invalid argument
    TKxx_ERR_NULL      = zlb.TKxx_ERR_NULL          # 空指针
    TKxx_ERR_TIMEOUT   = zlb.TKxx_ERR_TIMEOUT       # 超时
    TKxx_ERR_NONE      = zlb.TKxx_ERR_NONE          # 无数据等其他错误


class AhrsQuaternion:
    def __init__(self, quat:zlb.pyAhrsQuaternion = None) -> None:
        self.w = 1.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        if quat != None:
            self.copyValue(quat)

    def copyValue(self, quat:zlb.pyAhrsQuaternion = None):
        if quat != None:
            self.w = quat.w
            self.x = quat.x
            self.y = quat.y
            self.z = quat.z


class AhrsEuler:
    def __init__(self, euler:zlb.pyAhrsEuler = None) -> None:
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        if euler != None:
            self.copyValue(euler)

    def copyValue(self, euler:zlb.pyAhrsEuler = None):
        if euler != None:
            self.roll = euler.roll
            self.pitch = euler.pitch
            self.yaw = euler.yaw


class Axis3Float:
    def __init__(self, axis:zlb.pyAxis3Float = None) -> None:
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        if axis != None:
            self.copyValue(axis)

    def copyValue(self, axis:zlb.pyAxis3Float = None):
        if axis != None:
            self.x = axis.x
            self.y = axis.y
            self.z = axis.z

#======================================================================================
# 上报数据结构

class UploadIdBase:
    def __init__(self) -> None:
        self.cmdId = 0xFF               # 指令 ID
        self.subCmdId = 0xFF            # 子指令 ID
        self.rfId = 0xFF                # RF ID
        self.icId = 0xFF
        self.dongleId = 0xFF
        self.dotId = 0xFF               # dot ID
        self.flowId = 0                 # 流水号 （0x00 ~ 0xFF or 0x0000 ~ 0xFFFF）

    def baseCopyValue(self, block):
        if block != None:
            self.cmdId = block.getCmdId()
            self.subCmdId = block.getSubCmdId()
            self.rfId = block.getRfId()
            self.icId = block.getIcId()
            self.dongleId = block.getDongleId()
            self.dotId = block.getDotId()
            self.flowId = block.getFlowId()
    
    def getCmdId(self) -> int:
        '''
        指令ID
        '''
        return self.cmdId

    def getSubCmdId(self) -> int:
        '''
        子指令ID
        '''
        return self.subCmdId

    def getRfId(self) -> int:
        return self.rfId

    def getDotId(self) -> int:
        return self.dotId

    def getFlowId(self) -> int:
        '''
        流水号
        '''
        return self.flowId


class ImuDataBlock(UploadIdBase):
    def __init__(self, block:zlb.ImuDataBlock = None) -> None:
        super().__init__()
        self.effectiveDataFormat = 0    # 当前时间有效数据映射位（bit位 1：有效 0：无效）
        self.timeStamp = 0.0            # 时间戳        [单位：ms]
        self.temperature = 25.0         # 温度          [单位：℃]

        self.quat = AhrsQuaternion()    # 四元数
        self.euler = AhrsEuler()        # 欧拉角        [单位：°]
        self.acc = Axis3Float()         # 加速度计      [单位：g]
        self.gyro = Axis3Float()        # 陀螺仪        [单位：°/s]
        self.mag = Axis3Float()         # 磁力计        [单位：uT]
        self.lineAcc = Axis3Float()     # 线性加速度     [单位：g]

        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.ImuDataBlock):
        if block != None:
            self.baseCopyValue(block)
            self.effectiveDataFormat = block.getEffectiveDataFormat()
            self.timeStamp = block.getTimeStamp()
            self.temperature = block.getTemperature()

            self.quat.copyValue(block.getAhrsQuaternion())
            self.euler.copyValue(block.getAhrsEuler())
            self.acc.copyValue(block.getAcc())
            self.gyro.copyValue(block.getGyro())
            self.mag.copyValue(block.getMag())
            self.lineAcc.copyValue(block.getLinAcc())

    def testPrint(self):
        print("ImuDataBlock")

    def getEffectiveDataFormat(self) -> int:
        '''
        当前时间有效数据映射位(bit位 1:有效 0:无效)
        '''
        return self.effectiveDataFormat

    def getTimeStamp(self) -> (bool, float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_TIME.value:
            state = True
        return (state, self.timeStamp)

    def getTemperature(self) -> (bool, float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_TEMP.value:
            state = True
        return (state, self.temperature)
    
    def getAhrsQuaternion(self) -> (bool, AhrsQuaternion):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_QUATERNION.value:
            state = True
        return (state, self.quat)

    def getAhrsEuler(self) -> (bool, AhrsEuler):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_RPY.value:
            state = True
        return (state, self.euler)

    def getAcc(self) -> (bool, Axis3Float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_ACC.value:
            state = True
        return (state, self.acc)

    def getGyro(self) -> (bool, Axis3Float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_GYRO.value:
            state = True
        return (state, self.gyro)

    def getMag(self) -> (bool, Axis3Float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_MAG.value:
            state = True
        return (state, self.mag)

    def getLinAcc(self) -> (bool, Axis3Float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_LIN_ACC.value:
            state = True
        return (state, self.lineAcc)


class UpLoadDeviceStateBlock(UploadIdBase):
    '''
    模块(IC)主动上报
    '''
    def __init__(self, block:zlb.UpLoadDeviceStateBlock = None) -> None:
        super().__init__()
        self.deviceState = 0            # 模块(IC) 状态
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UpLoadDeviceStateBlock):
        if block != None:
            self.baseCopyValue(block)
            self.deviceState = block.getDeviceState()
    
    def testPrint(self):
        print("UpLoadDeviceStateBlock")

    def getDeviceState(self) -> int:
        '''
        模块(IC) 状态
        '''
        return self.deviceState

class BatteryBlock(UploadIdBase):
    def __init__(self, block:zlb.BatteryBlock = None) -> None:
        super().__init__()
        self.mvOk =False
        self.levelOk =False
        self.mv = 0
        self.level = 0

        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.BatteryBlock):
        if block != None:
            self.baseCopyValue(block)
            self.mvOk = block.isAdcMvOk()
            self.levelOk =block.isLevelOk()
            self.mv = block.getAdcMv()
            self.level = block.getLevel()
    
    def testPrint(self):
        print("BatteryBlock")

    def getAdcMv(self) -> (bool, int):
        return (self.mvOk, self.mv)

    def getLevel(self) -> (bool, int):
        return  (self.levelOk, self.level)


class AntValueBlock(UploadIdBase):
    def __init__(self, block:zlb.AntValueBlock = None) -> None:
        super().__init__()
        self.antNums = 0
        self.effectiveDataFormat = 0
        self.timeStamp = 0.0    # 时间戳 [单位：ms]
        self.normalization = False
        self.antValue = []

        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.AntValueBlock):
        if block != None:
            self.baseCopyValue(block)
            self.antNums = block.getAntNums()
            self.effectiveDataFormat = block.getEffectiveDataFormat()
            self.timeStamp = block.getTimeStamp()
            self.normalization = block.isNormalization()
            self.antValue = block.getAntValue()

    def testPrint(self):
        print("AntValueBlock")

    def getEffectiveDataFormat(self) -> int:
        '''
        当前时间有效数据映射位(bit位 1:有效 0:无效)
        '''
        return self.effectiveDataFormat

    def getTimeStamp(self) -> (bool, float):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_TIME.value:
            state = True
        return (state, self.timeStamp)
    
    
    def isNormalization(self):
        return self.isNormalization

    def getAntValue(self) -> (bool, list):
        state = False
        if self.effectiveDataFormat & e_UpLoadDataForMat.UPLOAD_DATA_ADCx.value:
            state = True
        return (state, self.antValue)


#======================================================================================
# 指令结构

class ReplyIdBase:
    def __init__(self) -> None:
        self.cmdId = 0xFF               # 指令 ID
        self.subCmdId = 0xFF            # 子指令 ID
        self.rfId = 0xFF                # RF ID
        self.icId = 0xFF
        self.dongleId = 0xFF
        self.dotId = 0xFF               # dot ID

    def baseCopyValue(self, block):
        if block != None:
            self.cmdId = block.getCmdId()
            self.subCmdId = block.getSubCmdId()
            self.rfId = block.getRfId()
            self.icId = block.getIcId()
            self.dongleId = block.getDongleId()
            self.dotId = block.getDotId()

    def getCmdId(self) -> int:
        '''
        指令ID
        '''
        return self.cmdId

    def getSubCmdId(self) -> int:
        '''
        子指令ID
        '''
        return self.subCmdId

    def getRfId(self) -> int:
        return self.rfId

    def getDotId(self) -> int:
        return self.dotId

class CtrlBaseBlock(ReplyIdBase):
    '''
    指令 -> 回复结构
    '''
    def __init__(self, block:zlb.CtrlBaseBlock = None):
        super().__init__()
        self.error = False
        self.errCode = 0x00
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.CtrlBaseBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.error  = block.isError()
            self.errCode  = block.getErrCode()

    def testPrint(self):
        print("CtrlBaseBlock")

    def isError(self) -> bool:
        return self.error

    def getErrCode(self) -> int:
        return self.errCode


class UploadDataFormatBlock(ReplyIdBase):
    '''
    获取上报数据格式->回复结构
    '''
    def __init__(self, block:zlb.UploadDataFormatBlock = None):
        super().__init__()
        self.uploadDataFormat = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UploadDataFormatBlock):
        if block != None:
            self.baseCopyValue(block)
            self.uploadDataFormat = block.getUploadDataFormat()
    
    def getUploadDataFormat(self) -> int:
        return self.uploadDataFormat


class SamplingHzBlock(ReplyIdBase):
    '''
    获取采样频率->回复结构
    '''
    def __init__(self, block:zlb.SamplingHzBlock = None):
        super().__init__()
        self.samplingHz = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.SamplingHzBlock):
        if block != None:
            self.baseCopyValue(block)
            self.samplingHz = block.getSamplingHz()

    def getSamplingHz(self) -> int:
        return self.samplingHz


class UploadHzBlock(ReplyIdBase):
    '''
    获取上报频率(采样分频表示)->回复结构
    '''
    def __init__(self, block:zlb.UploadHzBlock = None) -> None:
        super().__init__()
        self.uploadHz = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UploadHzBlock):
        if block != None:
            self.baseCopyValue(block)
            self.uploadHz = block.getUploadHz()

    def getUploadHz(self) -> int:
        return self.uploadHz


class FilterMapBlock(ReplyIdBase):
    '''
    获取滤波参数->回复结构
    '''
    def __init__(self, block:zlb.FilterMapBlock = None) -> None:
        super().__init__()
        self.filterMap = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.FilterMapBlock):
        if block != None:
            self.baseCopyValue(block)
            self.filterMap = block.getFilterMap()

    def getFilterMap(self) -> int:
        return self.filterMap


class IcDirBlock(ReplyIdBase):
    '''
    获取模块(IC)安装方向->回复结构
    '''
    def __init__(self, block:zlb.IcDirBlock = None) -> None:
        super().__init__()
        self.icDir = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.IcDirBlock):
        if block != None:
            self.baseCopyValue(block)
            self.icDir = block.getIcDir()

    def getIcDir(self) -> int:
        return self.icDir


class RfNameBlock(ReplyIdBase):
    '''
    获取模块(IC) RF广播名称->回复结构
    '''
    def __init__(self, block:zlb.DevieRfNameBlock = None) -> None:
        super().__init__()
        self.rfName = ''
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DevieRfNameBlock):
        if block != None:
            self.baseCopyValue(block)
            self.rfName = block.getRfName()

    def getRfName(self) -> str:
        return self.rfName


class RfPowerBlock(ReplyIdBase):
    '''
    获取模块(IC) RF 功率->回复结构
    '''
    def __init__(self, block:zlb.RfPowerBlock = None) -> None:
        super().__init__()
        self.rfPower = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.RfPowerBlock):
        if block != None:
            self.baseCopyValue(block)
            self.rfPower = block.getRfPower()

    def getRfPower(self) -> int:
        return self.rfPower


class RgbLedgeDataBlock(ReplyIdBase):
    '''
    获取LED交互模式下的 LED 状态->回复结构
    '''
    def __init__(self, block:zlb.RgbDataBlock = None) -> None:
        super().__init__()
        self.mode = 0
        self.color = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.RgbDataBlock):
        if block != None:
            self.baseCopyValue(block)
            self.mode = block.getMode()
            self.color = block.getColor()

    def getMode(self) -> int:
        return self.mode
    
    def getColor(self) -> int:
        return self.color


class UartBaudRateBlock(ReplyIdBase):
    '''
    获取Uart波特率->回复结构
    '''
    def __init__(self, block:zlb.UartBaudRateBlock = None) -> None:
        super().__init__()
        self.baudRate = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UartBaudRateBlock):
        if block != None:
            self.baseCopyValue(block)
            self.baudRate = block.getBaudRate()

    def getBaudRate(self) -> int:
        return self.baudRate


class DeviceMacBlock(ReplyIdBase):
    '''
    获取模块(IC)MAC->回复结构
    '''
    def __init__(self, block:zlb.DeviceMacBlock = None) -> None:
        super().__init__()
        self.macAddr = ''
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DeviceMacBlock):
        if block != None:
            self.baseCopyValue(block)
            self.macAddr = block.getMacAddr()

    def getMacAddr(self) -> str:
        return self.macAddr
    

class DeviceSnFullStrBlock(ReplyIdBase):
    '''
    获取模块(IC)完整SN编码->回复结构
    '''
    def __init__(self, block:zlb.DeviceSnFullStrBlock = None) -> None:
        super().__init__()
        self.snFullStr = ''
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DeviceSnFullStrBlock):
        if block != None:
            self.baseCopyValue(block)
            self.snFullStr = block.getSnFullStr()

    def getSnFullStr(self) -> str:
        return self.snFullStr
    


class BoardVersionBlock(ReplyIdBase):
    '''
    获取模块(IC)硬件版本号->回复结构
    '''
    def __init__(self, block:zlb.DeviceBoardVersionBlock = None) -> None:
        super().__init__()
        self.boardVersion = ''
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DeviceBoardVersionBlock):
        if block != None:
            self.baseCopyValue(block)
            self.boardVersion = block.getBoardVersion()

    def getBoardVersion(self) -> str:
        return self.boardVersion


class FirmwareVersionBlock(ReplyIdBase):
    '''
    获取模块(IC)固件版本号->回复结构
    '''
    def __init__(self, block:zlb.DeviceFirmwareVersionBlock = None) -> None:
        super().__init__()
        self.firmwareVersion = ''
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DeviceFirmwareVersionBlock):
        if block != None:
            self.baseCopyValue(block)
            self.firmwareVersion = block.getFirmwareVersion()

    def getFirmwareVersion(self) -> str:
        return self.firmwareVersion

#-----------------------------------------------------------------------------

class DotIdBlock(ReplyIdBase):
    '''
    获取模块(IC)DotId->回复结构
    '''
    def __init__(self, block:zlb.DotIdBlock = None) -> None:
        super().__init__()
        self.curDotId = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DotIdBlock):
        if block != None:
            self.baseCopyValue(block)
            self.curDotId = block.getCurDotId()

    def getCurDotId(self) -> int:
        return self.curDotId
    

class BleConnIntervalBlock(ReplyIdBase):
    '''
    获取模块(IC) 蓝牙连接间隔 -> 回复结构
    '''
    def __init__(self, block:zlb.BleConnIntervalBlock = None) -> None:
        super().__init__()
        self.bleConnInterval = 100.0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.BleConnIntervalBlock):
        if block != None:
            self.baseCopyValue(block)
            self.bleConnInterval = block.getBleConnInterval()

    def getBleConnInterval(self) -> float:
        return self.bleConnInterval


class AccRangeBlock(ReplyIdBase):
    '''
    获取模块(IC) IMU 加速度计 量程 -> 回复结构
    '''
    def __init__(self, block:zlb.AccRangeBlock = None) -> None:
        super().__init__()
        self.accRange = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.AccRangeBlock):
        if block != None:
            self.baseCopyValue(block)
            self.accRange = block.getAccRange()

    def getAccRange(self) -> int:
        return self.accRange
    

class GyroRangeBlock(ReplyIdBase):
    '''
    获取模块(IC) IMU 陀螺仪 量程 -> 回复结构
    '''
    def __init__(self, block:zlb.GyroRangeBlock = None) -> None:
        super().__init__()
        self.gyroRange = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.GyroRangeBlock):
        if block != None:
            self.baseCopyValue(block)
            self.gyroRange = block.getGyroRange()

    def getGyroRange(self) -> int:
        return self.gyroRange


class MagEllipsoidCalParam:
    def __init__(self, calParam:list = None) -> None:
        self.Kx = 0.0
        self.Ky = 0.0
        self.Kz = 0.0
        self.Ox = 0.0
        self.Oy = 0.0
        self.Oz = 0.0
        if calParam != None:
            self.copyValue(calParam)

    def copyValue(self, calParam:list):
        if calParam != None and len(calParam) == 6:
            self.Kx = calParam[0]
            self.Ky = calParam[1]
            self.Kz = calParam[2]
            self.Ox = calParam[3]
            self.Oy = calParam[4]
            self.Oz = calParam[5]

class MagEllipsoidCalParamBlock(ReplyIdBase):
    '''
    获取模块(IC) 磁力计椭球拟合校准参数 -> 回复结构
    '''
    def __init__(self, block:zlb.MagEllipsoidCalParamBlock = None) -> None:
        super().__init__()
        self.calParam = MagEllipsoidCalParam()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.MagEllipsoidCalParamBlock):
        if block != None:
            self.baseCopyValue(block)
            self.calParam.copyValue(block.getMagEllipsoidCalParam())

    def getMagEllipsoidCalParam(self) -> MagEllipsoidCalParam:
        return self.calParam
    

class FlowIdFormatBlock(ReplyIdBase):
    '''
    获取模块(IC) 上传数据流水号格式->回复结构
    '''
    def __init__(self, block:zlb.FlowIdFormatBlock = None) -> None:
        super().__init__()
        self.flowIdFormat = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.FlowIdFormatBlock):
        if block != None:
            self.baseCopyValue(block)
            self.flowIdFormat = block.getFlowIdFormat()

    def getFlowIdFormat(self) -> int:
        return self.flowIdFormat
    

class EnvMagValueBlock(ReplyIdBase):
    '''
    获取模块(IC) 存储的环境磁场强度范围 -> 回复结构
    '''
    def __init__(self, block:zlb.EnvMagValueBlock = None) -> None:
        super().__init__()
        self.envMagMin = 0.0
        self.envMagMax = 0.0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.EnvMagValueBlock):
        if block != None:
            self.baseCopyValue(block)
            envMag = block.getEnvMagParam()
            if len(envMag) == 2:
                self.envMagMin = envMag[0]
                self.envMagMax = envMag[1]

    def getEnvMagParam(self) -> (float, float):
        return (self.envMagMin, self.envMagMax)


class DataPortBlock(ReplyIdBase):
    '''
    获取模块(IC) 上传数据输出端口->回复结构
    '''
    def __init__(self, block:zlb.DataPortBlock = None) -> None:
        super().__init__()
        self.dataPort = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DataPortBlock):
        if block != None:
            self.baseCopyValue(block)
            self.dataPort = block.getDataOutPort()

    def getDataOutPort(self) -> int:
        return self.dataPort
    

class DataPortMapBlock(ReplyIdBase):
    '''
    获取模块(IC) 上传数据输出端口Map->回复结构
    '''
    def __init__(self, block:zlb.DataPortMapBlock = None):
        super().__init__()
        self.dataPortMap = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DataPortMapBlock):
        if block != None:
            self.baseCopyValue(block)
            self.dataPortMap = block.getDataOutPortMap()

    def getDataOutPortMap(self) -> int:
        return self.dataPortMap
    

class DeviceStateBlock(ReplyIdBase):
    '''
    获取模块(IC) 当前传感器码 -> 回复结构
    '''
    def __init__(self, block:zlb.DeviceStateBlock = None):
        super().__init__()
        self.state = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.DeviceStateBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.state = block.getDeviceState()

    def getDeviceState(self) -> int:
        return self.state


class UserUartIO:
    def __init__(self):
        self.enable = False
        self.txPin = 0xFF
        self.rxPin = 0xFF
        self.baudRate = 0

class UserUartIOBlock(ReplyIdBase):
    '''
    获取模块(IC) UART IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserUartIOBlock = None):
        super().__init__()
        self.io = UserUartIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserUartIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable   = block.isEnable()
            self.io.txPin    = block.getTxPin()
            self.io.rxPin    = block.getRxPin()
            self.io.baudRate = block.getBaudRate()

    def getIo(self) -> UserUartIO:
        return self.io


class UserIicIO:
    def __init__(self):
        self.enable = False
        self.sclPin = 0xFF
        self.sdaPin = 0xFF

class UserIicIOBlock(ReplyIdBase):
    '''
    获取模块(IC) IIC IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserIicIOBlock = None):
        super().__init__()
        self.io = UserIicIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserIicIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.sclPin  = block.getSclPin()
            self.io.sdaPin  = block.getSdaPin()

    def getIo(self) -> UserIicIO:
        return self.io


class UserSpimIO:
    def __init__(self):
        self.enable = False
        self.mode = 0
        self.bitOrder = 0
        self.rate = 0
        self.blockSize = 0
        self.clkPin = 0xFF
        self.misoPin = 0xFF
        self.mosiPin = 0xFF
        self.csnPin = 0xFF


class UserSpimIOBlock(ReplyIdBase):
    '''
    获取模块(IC) SPIM IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserSpimIOBlock = None):
        super().__init__()
        self.io = UserSpimIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserSpimIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.mode  = block.getMode()
            self.io.bitOrder  = block.getBitOrder()
            self.io.rate  = block.getRate()
            self.io.blockSize  = block.getBlockSize()
            self.io.clkPin  = block.getClkPin()
            self.io.misoPin  = block.getMisoPin()
            self.io.mosiPin  = block.getMosiPin()
            self.io.csnPin  = block.getCsnPin()

    def getIo(self) -> UserSpimIO:
        return self.io


class UserSpisIO:   # 当前不支持
    def __init__(self):
        self.enable = False
        self.mode = 0
        self.bitOrder = 0
        self.blockSize = 0
        self.clkPin = 0xFF
        self.misoPin = 0xFF
        self.mosiPin = 0xFF
        self.csnPin = 0xFF
        self.intPin = 0xFF


class UserSpisIOBlock(ReplyIdBase): # 当前不支持
    '''
    获取模块(IC) SPIS IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserSpisIOBlock = None):
        super().__init__()
        self.io = UserSpimIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserSpisIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.mode  = block.getMode()
            self.io.bitOrder  = block.getBitOrder()
            self.io.blockSize  = block.getBlockSize()
            self.io.clkPin  = block.getClkPin()
            self.io.misoPin  = block.getMisoPin()
            self.io.mosiPin  = block.getMosiPin()
            self.io.csnPin  = block.getCsnPin()
            self.io.intPin  = block.getIntPin()

    def getIo(self) -> UserSpimIO:
        return self.io


class UserAntIO:
    def __init__(self):
        self.antEnable = False
        self.ant0Pin = 0xFF
        self.ant1Pin = 0xFF
        self.ant2Pin = 0xFF
        self.ant3Pin = 0xFF
        self.ant4Pin = 0xFF
        self.ant5Pin = 0xFF

class UserAntIOBlock(ReplyIdBase):
    '''
    获取模块(IC) Ant(Adc) IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserAntIOBlock = None):
        super().__init__()
        self.io = UserAntIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserAntIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.antEnable  = block.getAntEnable()
            self.io.ant0Pin  = block.getAnt0Pin()
            self.io.ant1Pin  = block.getAnt1Pin()
            self.io.ant2Pin  = block.getAnt2Pin()
            self.io.ant3Pin  = block.getAnt3Pin()
            self.io.ant4Pin  = block.getAnt4Pin()
            self.io.ant5Pin  = block.getAnt5Pin()

    def getIo(self) -> UserAntIO:
        return self.io


class UserBatteryIO:
    def __init__(self):
        self.enable = False
        self.mode = 0
        self.antPin = 0xFF

class UserBatteryIOBlock(ReplyIdBase):
    '''
    获取模块(IC) 电池 IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserBatteryIOBlock = None):
        super().__init__()
        self.io = UserBatteryIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserBatteryIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.mode  = block.getMode()
            self.io.antPin  = block.getAntPin()

    def getIo(self) -> UserBatteryIO:
        return self.io


class UserBatteryLevelBlock(ReplyIdBase):
    '''
    获取模块(IC) 电池百分电量 -> 回复结构
    '''
    def __init__(self, block:zlb.UserBatteryLevelBlock = None):
        super().__init__()
        self.level = 0
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserBatteryLevelBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.level  = block.getLevel()

    def getLevel(self) -> int:
        return self.level


class UserRgbLedIO:
    def __init__(self):
        self.enable = False
        self.redPinIOMode = 0
        self.redPin = 0xFF
        self.greenPinIOMode = 0
        self.greenPin = 0xFF
        self.bluePinIOMode = 0
        self.bluePin = 0xFF

class UserRgbLedIOBlock(ReplyIdBase):
    '''
    获取模块(IC) RGB LED IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserRgbIOBlock = None):
        super().__init__()
        self.io = UserRgbLedIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserRgbIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.redPinIOMode  = block.getRedPinIOMode()
            self.io.redPin  = block.getRedPin()
            self.io.greenPinIOMode  = block.getGreenPinIOMode()
            self.io.greenPin  = block.getGreenPin()
            self.io.bluePinIOMode  = block.getBluePinIOMode()
            self.io.bluePin  = block.getBluePin()

    def getIo(self) -> UserRgbLedIO:
        return self.io
    

class UserBtnIO:
    def __init__(self):
        self.enable = False
        self.btnPinIOMode = 0
        self.btnPin = 0xFF

class UserBtnIOBlock(ReplyIdBase):
    '''
    获取模块(IC) Btn IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserBtnIOBlock = None):
        super().__init__()
        self.io = UserBtnIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserBtnIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.btnPinIOMode  = block.getBtnPinIOMode()
            self.io.btnPin  = block.getBtnPin()

    def getIo(self) -> UserBtnIO:
        return self.io
    

class UserPowerEnIO:
    def __init__(self):
        self.enable = False
        self.enPinIOMode = 0
        self.enPin = 0xFF

class UserPowerEnIOBlock(ReplyIdBase):
    '''
    获取模块(IC) PowerEn IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserPowerEnIOBlock = None):
        super().__init__()
        self.io = UserPowerEnIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserPowerEnIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.enPinIOMode  = block.getEnPinIOMode()
            self.io.enPin  = block.getEnPin()

    def getIo(self) -> UserPowerEnIO:
        return self.io


class UserRfPAEnIO:
    def __init__(self):
        self.enable = False
        self.txEnPinIOMode = 0
        self.txEnPin = 0xFF
        self.rxEnPinIOMode = 0
        self.rxEnPin = 0xFF

class UserRfPAEnIOBlock(ReplyIdBase):
    '''
    获取模块(IC) RfPA IO -> 回复结构
    '''
    def __init__(self, block:zlb.UserRfPAEnIOBlock = None):
        super().__init__()
        self.io = UserRfPAEnIO()
        if block != None:
            self.copyValue(block)

    def copyValue(self, block:zlb.UserRfPAEnIOBlock) -> None:
        if block != None:
            self.baseCopyValue(block)
            self.io.enable  = block.isEnable()
            self.io.txEnPinIOMode  = block.getTxEnPinIOMode()
            self.io.txEnPin  = block.getTxEnPin()
            self.io.rxEnPinIOMode  = block.getRxEnPinIOMode()
            self.io.rxEnPin  = block.getRxEnPin()

    def getIo(self) -> UserRfPAEnIO:
        return self.io

#==========================================================================================
# 用于数据解包

class e_BlockID(Enum):
    '''
    BlockID
    '''
    BlockID_None     = zlb.e_BlockID.BlockID_None
    BlockID_00001000 = zlb.e_BlockID.BlockID_00001000       # getImuDataBlockNote
    BlockID_00001100 = zlb.e_BlockID.BlockID_00001100       # getDeviceStateBlockNote
    BlockID_00001400 = zlb.e_BlockID.BlockID_00001400       # getBatteryBlockNote
    BlockID_00001500 = zlb.e_BlockID.BlockID_00001500       # getAntValueBlockNote

    BlockID_0000D501 = zlb.e_BlockID.BlockID_0000D501       # getUploadDataFormatBlockNote
    BlockID_0000D503 = zlb.e_BlockID.BlockID_0000D503       # getSamplingHzBlockNote
    BlockID_0000D505 = zlb.e_BlockID.BlockID_0000D505       # getUploadHzBlockNote
    BlockID_0000D50B = zlb.e_BlockID.BlockID_0000D50B       # getFilterMapBlockNote
    BlockID_0000D50D = zlb.e_BlockID.BlockID_0000D50D       # getIcDirBlockNote
    BlockID_0000D50F = zlb.e_BlockID.BlockID_0000D50F       # getDevieRfNameBlockNote
    BlockID_0000D511 = zlb.e_BlockID.BlockID_0000D511       # getRfPowerBlockNote
    BlockID_0000D563 = zlb.e_BlockID.BlockID_0000D563       # getRgbLedDataBlockNote
    BlockID_0000D565 = zlb.e_BlockID.BlockID_0000D565       # getUartBaudRateBlockNote
    BlockID_0000D577 = zlb.e_BlockID.BlockID_0000D577       # getDeviceMacBlockNote
    BlockID_0000D579 = zlb.e_BlockID.BlockID_0000D579       # getDeviceSnFullStrBlockNote
    BlockID_0000D57B = zlb.e_BlockID.BlockID_0000D57B       # getDeviceBoardVersionBlockNote
    BlockID_0000D57D = zlb.e_BlockID.BlockID_0000D57D       # getDeviceFirmwareVersionBlockNote

    BlockID_0000D603 = zlb.e_BlockID.BlockID_0000D603       # getDotIdBlockNote
    BlockID_0000D607 = zlb.e_BlockID.BlockID_0000D607       # getBleConnIntervalBlockNote
    BlockID_0000D611 = zlb.e_BlockID.BlockID_0000D611       # getAccRangeBlockNote
    BlockID_0000D613 = zlb.e_BlockID.BlockID_0000D613       # getGyroRangeBlockNote
    BlockID_0000D61B = zlb.e_BlockID.BlockID_0000D61B       # getMagEllipsoidCalParamBlockNote
    BlockID_0000D621 = zlb.e_BlockID.BlockID_0000D621       # getFlowIdFormatBlockNote
    BlockID_0000D627 = zlb.e_BlockID.BlockID_0000D627       # getEnvMagValueBlockNote
    BlockID_0000D631 = zlb.e_BlockID.BlockID_0000D631       # getDataPortBlockNote
    BlockID_0000D633 = zlb.e_BlockID.BlockID_0000D633       # getDataPortMapBlockNote
    BlockID_0000D635 = zlb.e_BlockID.BlockID_0000D635       # getDeviceStateBlockNote
    BlockID_0000D661 = zlb.e_BlockID.BlockID_0000D661       # getUserUartIOBlockNote
    BlockID_0000D663 = zlb.e_BlockID.BlockID_0000D663       # getUserIicIOBlockNote
    BlockID_0000D665 = zlb.e_BlockID.BlockID_0000D665       # getUserSpimIOBlockNote
    BlockID_0000D667 = zlb.e_BlockID.BlockID_0000D667       # getUserSpisIOBlockNote
    BlockID_0000D66B = zlb.e_BlockID.BlockID_0000D66B       # getUserAntIOBlockNote
    BlockID_0000D66D = zlb.e_BlockID.BlockID_0000D66D       # getUserBatteryIOBlockNote
    BlockID_0000D66F = zlb.e_BlockID.BlockID_0000D66F       # getUserBatteryLevelBlockNote
    BlockID_0000D671 = zlb.e_BlockID.BlockID_0000D671       # getUserRgbIOBlockNote
    BlockID_0000D673 = zlb.e_BlockID.BlockID_0000D673       # getUserBtnIOBlockNote
    BlockID_0000D675 = zlb.e_BlockID.BlockID_0000D675       # getUserPowerEnIOBlockNote
    BlockID_0000D679 = zlb.e_BlockID.BlockID_0000D679       # getUserRfPAEnIOBlockNote

    BlockID_OK       = zlb.e_BlockID.BlockID_OK             # getCtrlBaseBlockNote
    BlockID_ERROR    = zlb.e_BlockID.BlockID_ERROR          # getCtrlBaseBlockNote

    
class e_IOPort(Enum):
    eNONE_IO = zlb.e_IOPort.eNONE_IO    # 
    eRF_IO   = zlb.e_IOPort.eRF_IO      # RF 端口
    eUART_IO = zlb.e_IOPort.eUART_IO    # UART 端口
    eUSBD_IO = zlb.e_IOPort.eUSBD_IO    # USBD 端口
    eSPIM_IO = zlb.e_IOPort.eSPIM_IO    # SPIM 端口
    eSPIS_IO = zlb.e_IOPort.eSPIS_IO    # SPIS 端口
    eIIC_IO  = zlb.e_IOPort.eIIC_IO     # IIC 端口


class e_PKT(Enum):
    eNONE_PKT = zlb.e_PKT.eNONE_PKT     # 
    eCTRL_PKT = zlb.e_PKT.eCTRL_PKT     # 指令包
    eDATA_PKT = zlb.e_PKT.eDATA_PKT     # 数据包
    eTX_PKT   = zlb.e_PKT.eTX_PKT       # 数据包（电池，错误状态等）
    eOTA_PKT  = zlb.e_PKT.eOTA_PKT      # OTA包


class ZlBusUnPack:
    def __init__(self, fifoMaxSize: int = 10):
        self.pkt = zlb.ZlBusUnPack(fifoMaxSize)
        self.blockId_method = {
            zlb.e_BlockID.BlockID_None.value     : self.removeHeadDataNote,
            zlb.e_BlockID.BlockID_00001000.value : self.getImuDataBlockNote, 
            zlb.e_BlockID.BlockID_00001100.value : self.getDeviceStateBlockNote, 
            zlb.e_BlockID.BlockID_00001400.value : self.getBatteryBlockNote, 
            zlb.e_BlockID.BlockID_00001500.value : self.getAntValueBlockNote, 
            zlb.e_BlockID.BlockID_0000D501.value : self.getUploadDataFormatBlockNote, 
            zlb.e_BlockID.BlockID_0000D503.value : self.getSamplingHzBlockNote, 
            zlb.e_BlockID.BlockID_0000D505.value : self.getUploadHzBlockNote, 
            zlb.e_BlockID.BlockID_0000D50B.value : self.getFilterMapBlockNote, 
            zlb.e_BlockID.BlockID_0000D50D.value : self.getIcDirBlockNote, 
            zlb.e_BlockID.BlockID_0000D50F.value : self.getDevieRfNameBlockNote, 
            zlb.e_BlockID.BlockID_0000D511.value : self.getRfPowerBlockNote, 
            zlb.e_BlockID.BlockID_0000D563.value : self.getRgbLedDataBlockNote, 
            zlb.e_BlockID.BlockID_0000D565.value : self.getUartBaudRateBlockNote, 
            zlb.e_BlockID.BlockID_0000D577.value : self.getDeviceMacBlockNote, 
            zlb.e_BlockID.BlockID_0000D579.value : self.getDeviceSnFullStrBlockNote, 
            zlb.e_BlockID.BlockID_0000D57B.value : self.getDeviceBoardVersionBlockNote, 
            zlb.e_BlockID.BlockID_0000D57D.value : self.getDeviceFirmwareVersionBlockNote, 
            zlb.e_BlockID.BlockID_0000D603.value : self.getDotIdBlockNote, 
            zlb.e_BlockID.BlockID_0000D607.value : self.getBleConnIntervalBlockNote, 
            zlb.e_BlockID.BlockID_0000D611.value : self.getAccRangeBlockNote, 
            zlb.e_BlockID.BlockID_0000D613.value : self.getGyroRangeBlockNote, 
            zlb.e_BlockID.BlockID_0000D61B.value : self.getMagEllipsoidCalParamBlockNote, 
            zlb.e_BlockID.BlockID_0000D621.value : self.getFlowIdFormatBlockNote, 
            zlb.e_BlockID.BlockID_0000D627.value : self.getEnvMagValueBlockNote, 
            zlb.e_BlockID.BlockID_0000D631.value : self.getDataPortBlockNote, 
            zlb.e_BlockID.BlockID_0000D633.value : self.getDataPortMapBlockNote, 
            zlb.e_BlockID.BlockID_0000D635.value : self.getDeviceStateBlockNote, 
            zlb.e_BlockID.BlockID_0000D661.value : self.getUserUartIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D663.value : self.getUserIicIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D665.value : self.getUserSpimIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D667.value : self.getUserSpisIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D66B.value : self.getUserAntIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D66D.value : self.getUserBatteryIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D66F.value : self.getUserBatteryLevelBlockNote, 
            zlb.e_BlockID.BlockID_0000D671.value : self.getUserRgbIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D673.value : self.getUserBtnIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D675.value : self.getUserPowerEnIOBlockNote, 
            zlb.e_BlockID.BlockID_0000D679.value : self.getUserRfPAEnIOBlockNote, 
            zlb.e_BlockID.BlockID_OK.value       : self.getCtrlBaseBlockNote, 
            zlb.e_BlockID.BlockID_ERROR.value    : self.getCtrlBaseBlockNote, 
        }

    # 获取IO 类型
    def getIoType(self) -> int:
        return self.pkt.getIoType()

    # 获取流水号格式
    def getFlowIdFormat(self) -> int:
        return self.pkt.getFlowIdFormat()
    
    # 手动设置上报数据，流水号格式
    def setFlowIdFormat(self, flowIdFormat:int) -> int:
        return self.pkt.setFlowIdFormat(flowIdFormat & 0xFF)

    # 手动设置上报数据，数据格式
    def setDataFormat(self, dataFormat:int) -> int:
        return self.pkt.setDataFormat(dataFormat & 0xFFFFFFFF)

    # 解码数据输入口
    def decodeDataStreamInput(self, data:bytes) -> int:
        return self.pkt.decodeDataStreamInput(data)

    # 清空数据链表
    def clear(self) -> int:
        return self.pkt.clear()

    def size(self) -> int:
        '''
        数据链表中,节点个数
        '''
        return self.pkt.size()
    
    def count(self) -> int:
        '''
        数据链表中,节点个数
        '''
        return self.pkt.count()

    def length(self) -> int:
        '''
        数据链表中,节点个数
        '''
        return self.pkt.length()

    def getHeadBlockId(self) -> int:
        '''
        从数据链表中，读取头节点 blockId,从而确定ul_getDataNote_Del中 block参数 和 blockSize参数
        '''
        return (self.pkt.getHeadBlockId() & 0xFFFFFFFF)

    def removeHeadDataNote(self) -> None:
        self.pkt.removeHeadDataNote()
        return None

    def getHeadBlockNote(self, blockId: int = None):
        if self.size() > 0:
            if blockId == None:
                blockId = self.getHeadBlockId();

            if blockId in self.blockId_method:
                return self.blockId_method[blockId]()
            else:
                return self.removeHeadDataNote()
        else:
            return None

    def getCtrlBaseBlockNote(self) ->CtrlBaseBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return CtrlBaseBlock(self.pkt.getCtrlBaseBlockNote())
    
    def getImuDataBlockNote(self) ->ImuDataBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return ImuDataBlock(self.pkt.getImuDataBlockNote())

    def getUpLoadDeviceStateBlockNote(self) ->UpLoadDeviceStateBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UpLoadDeviceStateBlock(self.pkt.getUpLoadDeviceStateBlockNote())

    def getBatteryBlockNote(self) ->BatteryBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return BatteryBlock(self.pkt.getBatteryBlockNote())

    def getAntValueBlockNote(self) ->AntValueBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return AntValueBlock(self.pkt.getAntValueBlockNote())
    
    def getUploadDataFormatBlockNote(self) ->UploadDataFormatBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UploadDataFormatBlock(self.pkt.getUploadDataFormatBlockNote())
    
    def getSamplingHzBlockNote(self) ->SamplingHzBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return SamplingHzBlock(self.pkt.getSamplingHzBlockNote())
    
    def getSamplingHzBlockNote(self) ->SamplingHzBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return SamplingHzBlock(self.pkt.getSamplingHzBlockNote())

    def getUploadHzBlockNote(self) ->UploadHzBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UploadHzBlock(self.pkt.getUploadHzBlockNote())
    
    def getFilterMapBlockNote(self) ->FilterMapBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return FilterMapBlock(self.pkt.getFilterMapBlockNote())

    def getIcDirBlockNote(self) ->IcDirBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return IcDirBlock(self.pkt.getIcDirBlockNote())

    def getDevieRfNameBlockNote(self) ->RfNameBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return RfNameBlock(self.pkt.getDevieRfNameBlockNote())
    
    def getRfPowerBlockNote(self) ->RfPowerBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return RfPowerBlock(self.pkt.getRfPowerBlockNote())

    def getRgbLedDataBlockNote(self) ->RgbLedgeDataBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return RgbLedgeDataBlock(self.pkt.getRgbDataBlockNote())
    
    def getUartBaudRateBlockNote(self) ->UartBaudRateBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UartBaudRateBlock(self.pkt.getUartBaudRateBlockNote())

    def getDeviceMacBlockNote(self) ->DeviceMacBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DeviceMacBlock(self.pkt.getDeviceMacBlockNote())
    
    def getDeviceSnFullStrBlockNote(self) ->DeviceSnFullStrBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DeviceSnFullStrBlock(self.pkt.getDeviceSnFullStrBlockNote())
    
    def getDeviceBoardVersionBlockNote(self) ->BoardVersionBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return BoardVersionBlock(self.pkt.getDeviceBoardVersionBlockNote())
    
    def getDeviceFirmwareVersionBlockNote(self) ->FirmwareVersionBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return FirmwareVersionBlock(self.pkt.getDeviceFirmwareVersionBlockNote())
    
    def getDotIdBlockNote(self) ->DotIdBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DotIdBlock(self.pkt.getDotIdBlockNote())
    
    def getBleConnIntervalBlockNote(self) ->BleConnIntervalBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return BleConnIntervalBlock(self.pkt.getBleConnIntervalBlockNote())

    def getAccRangeBlockNote(self) ->AccRangeBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return AccRangeBlock(self.pkt.getAccRangeBlockNote())
    
    def getGyroRangeBlockNote(self) ->GyroRangeBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return GyroRangeBlock(self.pkt.getGyroRangeBlockNote())

    def getMagEllipsoidCalParamBlockNote(self) ->MagEllipsoidCalParamBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return MagEllipsoidCalParamBlock(self.pkt.getMagEllipsoidCalParamBlockNote())

    def getFlowIdFormatBlockNote(self) ->FlowIdFormatBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return FlowIdFormatBlock(self.pkt.getFlowIdFormatBlockNote())
    
    def getEnvMagValueBlockNote(self) ->EnvMagValueBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return EnvMagValueBlock(self.pkt.getEnvMagValueBlockNote())

    def getDataPortBlockNote(self) ->DataPortBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DataPortBlock(self.pkt.getDataPortBlockNote())

    def getDataPortMapBlockNote(self) ->DataPortMapBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DataPortMapBlock(self.pkt.getDataPortMapBlockNote())

    def getDeviceStateBlockNote(self) ->DeviceStateBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return DeviceStateBlock(self.pkt.getDeviceStateBlockNote())

    def getUserUartIOBlockNote(self) ->UserUartIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserUartIOBlock(self.pkt.getUserUartIOBlockNote())

    def getUserIicIOBlockNote(self) ->UserIicIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserIicIOBlock(self.pkt.getUserIicIOBlockNote())

    def getUserSpimIOBlockNote(self) ->UserSpimIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserSpimIOBlock(self.pkt.getUserSpimIOBlockNote())

    def getUserSpisIOBlockNote(self) ->UserSpisIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserSpisIOBlock(self.pkt.getUserSpisIOBlockNote())

    def getUserAntIOBlockNote(self) ->UserAntIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserAntIOBlock(self.pkt.getUserAntIOBlockNote())
    
    def getUserBatteryIOBlockNote(self) ->UserBatteryIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserBatteryIOBlock(self.pkt.getUserBatteryIOBlockNote())

    def getUserBatteryLevelBlockNote(self) ->UserBatteryLevelBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserBatteryLevelBlock(self.pkt.getUserBatteryLevelBlockNote())
    
    def getUserRgbIOBlockNote(self) ->UserRgbLedIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserRgbLedIOBlock(self.pkt.getUserRgbIOBlockNote())

    def getUserBtnIOBlockNote(self) ->UserBtnIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserBtnIOBlock(self.pkt.getUserBtnIOBlockNote())

    def getUserPowerEnIOBlockNote(self) ->UserPowerEnIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserPowerEnIOBlock(self.pkt.getUserPowerEnIOBlockNote())

    def getUserRfPAEnIOBlockNote(self) ->UserRfPAEnIOBlock:
        '''
        : 从数据链表中，读取头节点数据并删除节点（释放内存）
        '''
        return UserRfPAEnIOBlock(self.pkt.getUserRfPAEnIOBlockNote())


#==========================================================================================
# 下行指令集合

def ul_modifyDataFormat(format:int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
    修改上传数据格式
    '''
    return zlb.ul_modifyDataFormat((format & 0xFFFFFFFF), rfId, dotId)


def ul_getDataFormat(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
    获取上传数据格式
    '''
    return zlb.ul_getDataFormat(rfId, dotId)


class e_SampleHz(Enum):
    TK_Sample_200HZ = zlb.e_SampleHz.TK_Sample_200HZ
    TK_Sample_240HZ = zlb.e_SampleHz.TK_Sample_240HZ
    TK_Sample_250HZ = zlb.e_SampleHz.TK_Sample_250HZ


def ul_modifySampleHz(sampleHz:int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
    修改采样频率
    ul_modifySampleHz(e_SampleHz.TK_Sample_250HZ.value).hex(" ")
    '''
    return zlb.ul_modifySampleHz((sampleHz & 0xFFFF), rfId, dotId)

def ul_getSampleHz(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
    获取采样频率
    '''
    return zlb.ul_getSampleHz(rfId, dotId)

class e_UploadHz(Enum):
    TK_Sample_200HZ_DIVx_UPLOAD_1HZ   = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_1HZ
    TK_Sample_200HZ_DIVx_UPLOAD_5HZ   = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_5HZ
    TK_Sample_200HZ_DIVx_UPLOAD_10HZ  = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_10HZ
    TK_Sample_200HZ_DIVx_UPLOAD_20HZ  = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_20HZ
    TK_Sample_200HZ_DIVx_UPLOAD_25HZ  = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_25HZ
    TK_Sample_200HZ_DIVx_UPLOAD_50HZ  = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_50HZ
    TK_Sample_200HZ_DIVx_UPLOAD_100HZ = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_100HZ
    TK_Sample_200HZ_DIVx_UPLOAD_200HZ = zlb.e_UploadHz.TK_Sample_200HZ_DIVx_UPLOAD_200HZ

    TK_Sample_240HZ_DIVx_UPLOAD_1HZ   = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_1HZ
    TK_Sample_240HZ_DIVx_UPLOAD_5HZ   = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_5HZ
    TK_Sample_240HZ_DIVx_UPLOAD_10HZ  = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_10HZ
    TK_Sample_240HZ_DIVx_UPLOAD_20HZ  = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_20HZ
    TK_Sample_240HZ_DIVx_UPLOAD_25HZ  = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_25HZ
    TK_Sample_240HZ_DIVx_UPLOAD_30HZ  = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_30HZ
    TK_Sample_240HZ_DIVx_UPLOAD_60HZ  = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_60HZ
    TK_Sample_240HZ_DIVx_UPLOAD_120HZ = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_120HZ
    TK_Sample_240HZ_DIVx_UPLOAD_240HZ = zlb.e_UploadHz.TK_Sample_240HZ_DIVx_UPLOAD_240HZ

    TK_Sample_250HZ_DIVx_UPLOAD_1HZ   = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_1HZ
    TK_Sample_250HZ_DIVx_UPLOAD_5HZ   = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_5HZ
    TK_Sample_250HZ_DIVx_UPLOAD_10HZ  = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_10HZ
    TK_Sample_250HZ_DIVx_UPLOAD_25HZ  = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_25HZ
    TK_Sample_250HZ_DIVx_UPLOAD_50HZ  = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_50HZ
    TK_Sample_250HZ_DIVx_UPLOAD_250HZ = zlb.e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_250HZ

def ul_modifyUploadHz(SampleDiv:int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
    修改 SampleDiv: 采样率的分配系数
    ul_modifyUploadHz(e_UploadHz.TK_Sample_250HZ_DIVx_UPLOAD_50HZ.value).hex(" ")
    '''
    return zlb.ul_modifyUploadHz((SampleDiv & 0xFFFF), rfId, dotId)

def ul_getUploadHz(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     获取数据上传频率
    '''
    return zlb.ul_getUploadHz(rfId, dotId)

def ul_startMagnetometerCalibration(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     启动磁力计校准
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x06
     启动磁力计校准后, 挥动Sensor,空中走8字形,持续时长约20s(秒)
    '''
    return zlb.ul_startMagnetometerCalibration(rfId, dotId)


class e_FiterParam(Enum):
    TK_StaticFiter          = zlb.e_FiterParam.TK_StaticFiter            # 静态滤波
    TK_SixAxisDataFiter     = zlb.e_FiterParam.TK_SixAxisDataFiter       # 6轴模式
    TK_MagDataFlexibleFiter = zlb.e_FiterParam.TK_MagDataFlexibleFiter   # 灵活磁场变换
    TK_MagDataFixedFiter    = zlb.e_FiterParam.TK_MagDataFixedFiter      # 抗磁干扰
    TK_ZeroOffsetFiter      = zlb.e_FiterParam.TK_ZeroOffsetFiter        # 零点滤波


def ul_configDataFilter(dataFilter: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     配置滤波参数
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x08
    '''
    return zlb.ul_configDataFilter((dataFilter & 0xFFFF), rfId, dotId)

def ul_clearDataFilter(dataFilter: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     清除滤波参数
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x0A
    '''
    return zlb.ul_clearDataFilter((dataFilter & 0xFFFF), rfId, dotId)

def ul_getDataFilter(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     获取滤波参数
     blockId = BlockID_0000D50B
     cmdId = 0xD5, subCmdId = 0x0B
    '''
    return zlb.ul_getDataFilter(rfId, dotId)


class e_Convention(Enum):
    TK_NED_0 = zlb.e_Convention.TK_NED_0
    TK_NED_1 = zlb.e_Convention.TK_NED_1
    TK_NED_2 = zlb.e_Convention.TK_NED_2
    TK_NED_3 = zlb.e_Convention.TK_NED_3
    TK_ENU_0 = zlb.e_Convention.TK_ENU_0
    TK_ENU_1 = zlb.e_Convention.TK_ENU_1
    TK_ENU_2 = zlb.e_Convention.TK_ENU_2
    TK_ENU_3 = zlb.e_Convention.TK_ENU_3


def ul_modifyIcConvention(convention: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改IC安装方向
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x0C
    '''
    return zlb.ul_modifyIcConvention(convention & 0xFF, rfId, dotId)

def ul_getIcConvention(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取IC安装方向
     blockId = BlockID_0000D50D
     cmdId = 0xD5, subCmdId = 0x0D
    '''
    return zlb.ul_getIcConvention(rfId, dotId)


def ul_modifyIcAdvName(userName: str, sensorName: str, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改IC RF 广播名称
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x0E
     userName:    用户名 (字符串),长度范围4~8
     sensorName: 传感器名 (字符串),固定长度4
    '''
    if userName == None or sensorName == None:
        return bytes()

    userNameLen = len(userName)
    sensorNameLen = len(sensorName)

    if (userNameLen >= 4) and (userNameLen <= 8) and (sensorNameLen == 4):
        return zlb.ul_modifyIcAdvName(userName, sensorName, rfId, dotId)
    else :
        return bytes()

def ul_getIcAdvName(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取IC RF 广播名称
     blockId = BlockID_0000D50F
     cmdId = 0xD5, subCmdId = 0x0F
    '''
    return zlb.ul_getIcAdvName(rfId, dotId)


class e_RfPower(Enum):
    TK_N8dBm = zlb.e_RfPower.TK_N8dBm
    TK_N4dBm = zlb.e_RfPower.TK_N4dBm
    TK_P0dBm = zlb.e_RfPower.TK_P0dBm
    TK_P3dBm = zlb.e_RfPower.TK_P3dBm
    TK_P4dBm = zlb.e_RfPower.TK_P4dBm
    TK_P8dBm = zlb.e_RfPower.TK_P8dBm
    TK_P10dBm = zlb.e_RfPower.TK_P10dBm

def ul_modifyIcRfPower(powerdBm: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改IC RF Power
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x10
    '''
    return zlb.ul_modifyIcRfPower(powerdBm & 0xFF, rfId, dotId)

def ul_getIcRfPower(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取IC RF Power
     blockId = BlockID_0000D511
     cmdId = 0xD5, subCmdId = 0x11
    '''
    return zlb.ul_getIcRfPower(rfId, dotId)

def ul_disconnectIcRf(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     断开RF连接
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x12
    '''
    return zlb.ul_disconnectIcRf(rfId, dotId)

def ul_enableDataOutPut(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     上报数据使能输出
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x14
    '''
    return zlb.ul_enableDataOutPut(rfId, dotId)

def ul_disEnableDataOutPut(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     上报数据禁止输出
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x15
    '''
    return zlb.ul_disEnableDataOutPut(rfId, dotId)

class e_LedColor(Enum): # RGB 点灯颜色
    TK_LED_RED    = zlb.e_LedColor.TK_LED_RED
    TK_LED_GREEN  = zlb.e_LedColor.TK_LED_GREEN
    TK_LED_BLUE   = zlb.e_LedColor.TK_LED_BLUE
    TK_LED_YELLOW = zlb.e_LedColor.TK_LED_YELLOW
    TK_LED_PUEPLE = zlb.e_LedColor.TK_LED_PUEPLE
    TK_LED_CYAN   = zlb.e_LedColor.TK_LED_CYAN
    TK_LED_WHITE  = zlb.e_LedColor.TK_LED_WHITE

class e_LedMode(Enum):  # RGB 点灯模式
    TK_LED_MODE_LIGHT          = zlb.e_LedMode.TK_LED_MODE_LIGHT             # 常亮
    TK_LED_MODE_BREATHE        = zlb.e_LedMode.TK_LED_MODE_BREATHE           # 呼吸灯
    TK_LED_MODE_FLICKER_LOW    = zlb.e_LedMode.TK_LED_MODE_FLICKER_LOW       # 低频闪烁
    TK_LED_MODE_FLICKER_MEDIUM = zlb.e_LedMode.TK_LED_MODE_FLICKER_MEDIUM    # 中频闪烁
    TK_LED_MODE_FLICKER_HIGH   = zlb.e_LedMode.TK_LED_MODE_FLICKER_HIGH      # 高频闪烁

def ul_enterLedInteraction(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启LED交互
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x60
    '''
    return zlb.ul_enterLedInteraction(rfId, dotId)

def ul_exitLedInteraction(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     退出LED交互
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x61
    '''
    return zlb.ul_exitLedInteraction(rfId, dotId)

def ul_modifyLedInteractionColor(ledColor:int, ledMode:int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改 LED 交互模式下，灯颜色与点灯模式
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x62
    '''
    return zlb.ul_modifyLedInteractionColor(ledColor & 0xFF, ledMode & 0xFF, rfId, dotId)

def ul_getLedInteractionColor(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 LED 交互模式下，灯颜色与点灯模式
     blockId = BlockID_0000D563
     cmdId = 0xD5, subCmdId = 0x63
    '''
    return zlb.ul_getLedInteractionColor(rfId, dotId)

class e_BaudRate(Enum): # 串口波特率
    TK_BaudRate_115200 = zlb.e_BaudRate.TK_BaudRate_115200
    TK_BaudRate_128000 = zlb.e_BaudRate.TK_BaudRate_128000
    TK_BaudRate_256000 = zlb.e_BaudRate.TK_BaudRate_256000
    TK_BaudRate_460800 = zlb.e_BaudRate.TK_BaudRate_460800
    TK_BaudRate_512000 = zlb.e_BaudRate.TK_BaudRate_512000
    TK_BaudRate_750000 = zlb.e_BaudRate.TK_BaudRate_750000
    TK_BaudRate_921300 = zlb.e_BaudRate.TK_BaudRate_921300

def ul_modifyUartBaudRate(baudRate: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改串口波特率
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x64
    '''
    return zlb.ul_modifyUartBaudRate(baudRate, rfId, dotId)

def ul_getUartBaudRate(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取串口波特率
     blockId = BlockID_0000D565
     cmdId = 0xD5, subCmdId = 0x65
    '''
    return zlb.ul_getUartBaudRate(rfId, dotId)

def ul_imuStaticCalibrationInit(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     初始化 IMU N面静态校准参数
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x6E
    '''
    return zlb.ul_imuStaticCalibrationInit(rfId, dotId)

def ul_imuStaticCalibration(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     IMU N面静态校准
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x6E
    '''
    return zlb.ul_imuStaticCalibration(rfId, dotId)

def ul_imuStaticCalibrationExit(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     退出 IMU N面静态校准(计算校准参数)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x6E
    '''
    return zlb.ul_imuStaticCalibrationExit(rfId, dotId)

def ul_clearStaticCalibrationParam(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     取消N面静态校准参数(计算校准参数)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x6F
    '''
    return zlb.ul_clearStaticCalibrationParam(rfId, dotId)

def ul_getMacAddressStr(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 MAC ADDRESS 字符串
     blockId = BlockID_0000D577
     cmdId = 0xD5, subCmdId = 0x77
    '''
    return zlb.ul_getMacAddressStr(rfId, dotId)

def ul_getDeviceSnStr(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 完整设备SN编号 字符串
     blockId = BlockID_0000D579
     cmdId = 0xD5, subCmdId = 0x79
    '''
    return zlb.ul_getDeviceSnStr(rfId, dotId)

def ul_getBoardVesionStr(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 硬件版本号
     blockId = BlockID_0000D57B
     cmdId = 0xD5, subCmdId = 0x7B
    '''
    return zlb.ul_getBoardVesionStr(rfId, dotId)

def ul_getFirmwareVesionStr(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 固件版本号
     blockId = BlockID_0000D57D
     cmdId = 0xD5, subCmdId = 0x7D
    '''
    return zlb.ul_getFirmwareVesionStr(rfId, dotId)

def ul_deviceShutdown(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     设备关机
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x7E
    '''
    return zlb.ul_deviceShutdown(rfId, dotId)

def ul_restoreFactorySettings(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     恢复出厂设置
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD5, subCmdId = 0x7F
    '''
    return zlb.ul_restoreFactorySettings(rfId, dotId)

#-------------------------------------------------------

def hl_modifyDotId(configDotId: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改DotID (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x02
    '''
    return zlb.hl_modifyDotId(configDotId & 0xFF, rfId, dotId)

def hl_getDotId(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     获取DotID (高级设置)
     blockId = BlockID_0000D603
     cmdId = 0xD6, subCmdId = 0x03
    '''
    return zlb.hl_getDotId(rfId, dotId)

def hl_modifyRfConnInterval(connInterval: float, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改Rf ConnInterval (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x06
     connInterval: 1.25ms 的倍数
    '''
    return zlb.hl_modifyRfConnInterval(connInterval, rfId, dotId)

def hl_getRfConnInterval(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     获取Rf ConnInterval (高级设置)
     blockId = BlockID_0000D607
     cmdId = 0xD6, subCmdId = 0x07
    '''
    return zlb.hl_getRfConnInterval(rfId, dotId)


class e_AccRange(Enum):
    TK_ACC_RANGE_2G  = zlb.e_AccRange.TK_ACC_RANGE_2G
    TK_ACC_RANGE_4G  = zlb.e_AccRange.TK_ACC_RANGE_4G
    TK_ACC_RANGE_8G  = zlb.e_AccRange.TK_ACC_RANGE_8G
    TK_ACC_RANGE_16G = zlb.e_AccRange.TK_ACC_RANGE_16G

def hl_modifyAccRange(accRange: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改accRange (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x10
    '''
    return zlb.hl_modifyAccRange(accRange & 0xFF, rfId, dotId)

def hl_getAccRange(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取accRange (高级设置)
     blockId = BlockID_0000D611
     cmdId = 0xD6, subCmdId = 0x11
    '''
    return zlb.hl_getAccRange(rfId, dotId)


class e_GyroRange(Enum):
    TK_GYRO_RANGE_250DPS  = zlb.e_GyroRange.TK_GYRO_RANGE_250DPS
    TK_GYRO_RANGE_500DPS  = zlb.e_GyroRange.TK_GYRO_RANGE_500DPS
    TK_GYRO_RANGE_1000DPS = zlb.e_GyroRange.TK_GYRO_RANGE_1000DPS
    TK_GYRO_RANGE_2000DPS = zlb.e_GyroRange.TK_GYRO_RANGE_2000DPS

def hl_modifyGyroRange(gyroRange: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改GyroRange (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x12
    '''
    return zlb.hl_modifyGyroRange(gyroRange & 0xFF, rfId, dotId)

def hl_getGyroRange(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取GyroRange (高级设置)
     blockId = BlockID_0000D613
     cmdId = 0xD6, subCmdId = 0x13
    '''
    return zlb.hl_getGyroRange(rfId, dotId)

def hl_modifyMagCalParam_Ex(calParam: MagEllipsoidCalParam, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     修改 磁力计 椭球拟合 校准参数 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x1A
    '''
    zlCalParam = [calParam.Kx, calParam.Ky, calParam.Kz, calParam.Ox, calParam.Oy, calParam.Oz]
    return zlb.hl_modifyMagCalParam_Ex(zlCalParam, rfId, dotId)

def hl_getMagCalParam_Ex(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 磁力计 椭球拟合 校准参数 (高级设置)
     blockId = BlockID_0000D61B
     cmdId = 0xD6, subCmdId = 0x1B
    '''
    return zlb.hl_getMagCalParam_Ex(rfId, dotId)

def hl_configFlowFormat(flowFormat: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     配置 流水号格式 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x20
    '''
    return zlb.hl_configFlowFormat(flowFormat & 0xFF, rfId, dotId)

def hl_getFlowFormat(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 流水号格式 (高级设置)
     blockId = BlockID_0000D621
     cmdId = 0xD6, subCmdId = 0x21
    '''
    return zlb.hl_getFlowFormat(rfId, dotId)

def hl_resetFlowNums(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     重置 流水号 (重新从0开始) (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x22
    '''
    return zlb.hl_resetFlowNums(rfId, dotId)


class e_DataOutPort(Enum):
    TK_NONE_PORT = 0
    TK_RF_PORT   = zlb.e_DataOutPort.TK_RF_PORT
    TK_UART_PORT = zlb.e_DataOutPort.TK_UART_PORT
    TK_USB_PORT  = zlb.e_DataOutPort.TK_USB_PORT        # 不支持，保留位
    TK_SPIM_PORT = zlb.e_DataOutPort.TK_SPIM_PORT
    TK_SPIS_PORT = zlb.e_DataOutPort.TK_SPIS_PORT       # 不支持，保留位

def hl_configOutDataPort(outDataPort: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     配置 数据输出接口 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x30
    '''
    return zlb.hl_configOutDataPort(outDataPort & 0xFFFF, rfId, dotId)

def hl_getOutDataPort(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 数据输出接口 (高级设置)
     blockId = BlockID_0000D631
     cmdId = 0xD6, subCmdId = 0x31
    '''
    return zlb.hl_getOutDataPort(rfId, dotId)

def hl_checkOutDataPort(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     检查 数据输出接口 (高级设置)
     blockId = BlockID_0000D633
     cmdId = 0xD6, subCmdId = 0x33
    '''
    return zlb.hl_checkOutDataPort(rfId, dotId)

def hl_swapUserUartTrxPin(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     交换 Uart Trx Pin (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x60
    '''
    return zlb.hl_swapUserUartTrxPin(rfId, dotId)

def hl_getUserUartIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 Uart IO (高级设置)
     blockId = BlockID_0000D661
     cmdId = 0xD6, subCmdId = 0x61
    '''
    return zlb.hl_getUserUartIO(rfId, dotId)

def hl_getUserIicIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 Iic IO (高级设置)
     blockId = BlockID_0000D663
     cmdId = 0xD6, subCmdId = 0x63
    '''
    return zlb.hl_getUserIicIO(rfId, dotId)

def hl_enableUserSpim(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 SPIM (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x64
    '''
    return zlb.hl_enableUserSpim(rfId, dotId)

def hl_disEnableUserSpim(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 SPIM (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x64
    '''
    return zlb.hl_disEnableUserSpim(rfId, dotId)

def hl_getUserSpimIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 SPIM IO (高级设置)
     blockId = BlockID_0000D665
     cmdId = 0xD6, subCmdId = 0x65
    '''
    return zlb.hl_getUserSpimIO(rfId, dotId)

def hl_enableUserSpis(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 SPIS (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x66
    '''
    return zlb.hl_enableUserSpis(rfId, dotId)

def hl_disEnableUserSpis(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 SPIS (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x66
    '''
    return zlb.hl_disEnableUserSpis(rfId, dotId)

def hl_getUserSpisIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 SPIS IO (高级设置)
     blockId = BlockID_0000D667
     cmdId = 0xD6, subCmdId = 0x67
    '''
    return zlb.hl_getUserSpisIO(rfId, dotId)


class e_AntEn(Enum):
    TK_ANT0_ENABLE   = zlb.e_AntEn.TK_ANT0_ENABLE
    TK_ANT1_ENABLE   = zlb.e_AntEn.TK_ANT1_ENABLE
    TK_ANT2_ENABLE   = zlb.e_AntEn.TK_ANT2_ENABLE
    TK_ANT3_ENABLE   = zlb.e_AntEn.TK_ANT3_ENABLE
    TK_ANT4_ENABLE   = zlb.e_AntEn.TK_ANT4_ENABLE
    TK_ANT5_ENABLE   = zlb.e_AntEn.TK_ANT5_ENABLE


def hl_configUserAnt(antEnableMap: int, rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 or 关闭 ANT 端口 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x6A
    '''
    return zlb.hl_configUserAnt(antEnableMap & 0xFF, rfId, dotId)

def hl_getUserAntIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 ANT IO (高级设置)
     blockId = BlockID_0000D66B
     cmdId = 0xD6, subCmdId = 0x6B
    '''
    return zlb.hl_getUserAntIO(rfId, dotId)

def hl_enableUserBattery(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 Battery (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x6C
    '''
    return zlb.hl_enableUserBattery(rfId, dotId)

def hl_disEnableUserBattery(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 Battery (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x6C
    '''
    return zlb.hl_disEnableUserBattery(rfId, dotId)

def hl_getUserBatteryIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 Battery IO (高级设置)
     blockId = BlockID_0000D66D
     cmdId = 0xD6, subCmdId = 0x6D
    '''
    return zlb.hl_getUserBatteryIO(rfId, dotId)

def hl_getUserBatteryLevel(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 电池电量 (高级设置)
     blockId = BlockID_0000D66F
     cmdId = 0xD6, subCmdId = 0x6F
    '''
    return zlb.hl_getUserBatteryLevel(rfId, dotId)

def hl_enableUserRgbLed(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 RgbLed (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x70
    '''
    return zlb.hl_enableUserRgbLed(rfId, dotId)

def hl_disEnableUserRgbLed(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 RgbLed (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x70
    '''
    return zlb.hl_disEnableUserRgbLed(rfId, dotId)

def hl_getUserRgbLedIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 RgbLed IO (高级设置)
     blockId = BlockID_0000D671
     cmdId = 0xD6, subCmdId = 0x71
    '''
    return zlb.hl_getUserRgbLedIO(rfId, dotId)

def hl_enableUserBtn(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 按钮 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x72
    '''
    return zlb.hl_enableUserBtn(rfId, dotId)

def hl_disEnableUserBtn(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 按钮 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x72
    '''
    return zlb.hl_disEnableUserBtn(rfId, dotId)

def hl_getUserBtnIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 Btn IO (高级设置)
     blockId = BlockID_0000D673
     cmdId = 0xD6, subCmdId = 0x73
    '''
    return zlb.hl_getUserBtnIO(rfId, dotId)


def hl_enableUserPowerEn(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 电源管理 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x74
    '''
    return zlb.hl_enableUserPowerEn(rfId, dotId)

def hl_disEnableUserPowerEn(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 电源管理 (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x74
    '''
    return zlb.hl_disEnableUserPowerEn(rfId, dotId)

def hl_getUserPowerEnIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 PowerEn IO (高级设置)
     blockId = BlockID_0000D675
     cmdId = 0xD6, subCmdId = 0x75
    '''
    return zlb.hl_getUserPowerEnIO(rfId, dotId)

def hl_enableUserRf(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 RF (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x76

     Rf: 仅支持开启，不支持关闭
    '''
    return zlb.hl_enableUserRf(rfId, dotId)

def hl_enableUserRfPa(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     开启 RfPa (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x78
    '''
    return zlb.hl_enableUserRfPa(rfId, dotId)

def hl_disEnableUserRfPa(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     关闭 RfPa (高级设置)
     blockId = BlockID_OK or BlockID_ERROR
     cmdId = 0xD6, subCmdId = 0x78
    '''
    return zlb.hl_disEnableUserRfPa(rfId, dotId)

def hl_getUserRfPaIO(rfId = 0x3F, dotId = 0xFF) -> bytes:
    '''
     读取 RfPa IO (高级设置)
     blockId = BlockID_0000D679
     cmdId = 0xD6, subCmdId = 0x79
    '''
    return zlb.hl_getUserRfPaIO(rfId, dotId)
