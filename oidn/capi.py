import ctypes
import os
from oidn.constants import *
import typing
import numpy as np
import importlib
import struct
from typing import Callable

class RawFunctions:
    # Device
    oidnNewDevice = None
    oidnCommitDevice = None
    oidnGetDeviceError = None
    oidnReleaseDevice = None
    oidnRetainDevice = None
    oidnSetDeviceBool = None
    oidnSetDeviceInt = None
    oidnGetDeviceBool = None
    oidnGetDeviceInt = None

    # Filter API
    oidnNewFilter = None
    oidnSetSharedFilterImage = None
    oidnUnsetFilterImage = None
    oidnSetSharedFilterData = None
    oidnUpdateFilterData = None
    oidnUnsetFilterData = None
    oidnSetFilterBool = None
    oidnGetFilterBool = None
    oidnSetFilterInt = None
    oidnGetFilterInt = None
    oidnSetFilterFloat = None
    oidnGetFilterFloat = None
    oidnCommitFilter = None
    oidnExecuteFilter = None
    oidnReleaseFilter = None
    oidnRetainFilter = None


def __init_by_lib(lib: ctypes.CDLL):
    type_map = {
        "i": ctypes.c_int32,
        "l": ctypes.c_long,
        "L": ctypes.c_longlong,
        "z": ctypes.c_size_t,
        "f": ctypes.c_float,
        "d": ctypes.c_double,
        "D": ctypes.c_longdouble,
        "c": ctypes.c_char,
        "s": ctypes.c_char_p,
        "p": ctypes.c_void_p,
        "b": ctypes.c_bool,
        "n": None,
    }

    def get_func(name, argtype, restype):
        f = lib.__getattr__(name)
        f.restype = type_map[restype]
        f.argtypes = [type_map[t] for t in argtype]
        return f

    RawFunctions.oidnNewDevice = get_func("oidnNewDevice", "i", "p")
    RawFunctions.oidnCommitDevice = get_func("oidnCommitDevice", "p", "n")
    RawFunctions.oidnGetDeviceError = get_func("oidnGetDeviceError", "pp", "i")
    RawFunctions.oidnReleaseDevice = get_func("oidnReleaseDevice", "p", "n")
    RawFunctions.oidnRetainDevice = get_func("oidnRetainDevice", "p", "n")
    RawFunctions.oidnSetDeviceBool = get_func("oidnSetDeviceBool", "psb", "n")
    RawFunctions.oidnSetDeviceInt = get_func("oidnSetDeviceInt", "psi", "n")
    RawFunctions.oidnGetDeviceBool = get_func("oidnGetDeviceBool", "ps", "b")
    RawFunctions.oidnGetDeviceInt = get_func("oidnGetDeviceInt", "ps", "i")

    RawFunctions.oidnNewFilter = get_func("oidnNewFilter", "ps", "p")
    RawFunctions.oidnSetSharedFilterImage = get_func(
        "oidnSetSharedFilterImage", "pspizzzzz", "n"
    )
    RawFunctions.oidnUnsetFilterImage = get_func("oidnUnsetFilterImage", "ps", "n")
    RawFunctions.oidnSetSharedFilterData = get_func(
        "oidnSetSharedFilterData", "pspz", "n"
    )
    RawFunctions.oidnUnsetFilterData = get_func("oidnUnsetFilterData", "ps", "n")
    RawFunctions.oidnUpdateFilterData = get_func("oidnUpdateFilterData", "ps", "n")
    RawFunctions.oidnGetFilterBool = get_func("oidnGetFilterBool", "ps", "b")
    RawFunctions.oidnGetFilterFloat = get_func("oidnGetFilterFloat", "ps", "f")
    RawFunctions.oidnGetFilterInt = get_func("oidnGetFilterInt", "ps", "i")
    RawFunctions.oidnSetFilterBool = get_func("oidnSetFilterBool", "psb", "n")
    RawFunctions.oidnSetFilterFloat = get_func("oidnSetFilterFloat", "psf", "n")
    RawFunctions.oidnSetFilterInt = get_func("oidnSetFilterInt", "psi", "n")
    RawFunctions.oidnCommitFilter = get_func("oidnCommitFilter", "p", "n")
    RawFunctions.oidnExecuteFilter = get_func("oidnExecuteFilter", "p", "n")
    RawFunctions.oidnReleaseFilter = get_func("oidnReleaseFilter", "p", "n")
    RawFunctions.oidnRetainFilter = get_func("oidnRetainFilter", "p", "n")

def NewDevice(device_type: int = DEVICE_TYPE_DEFAULT) -> int:
    """
    Create a new OIDN device

    Args:
        device_type(int) : OIDN_DEVICE_TYPE_XXX
    """
    return RawFunctions.oidnNewDevice(device_type)


def CommitDevice(device_handle: int):
    """
    Batch up multiple changes on the device.

    Args:
        device_handle : Get from NewDevice
    """
    RawFunctions.oidnCommitDevice(device_handle)


def GetDeviceError(device_handle: int) -> tuple[int, str]:
    r"""
    Args:
        device_handle : Get from NewDevice
    Returns:
        tuple of (error_code : int, error_message : str)
    """
    buf = b"\0\0\0\0\0\0\0\0"
    buf_ptr = ctypes.c_char_p(buf)
    err = RawFunctions.oidnGetDeviceError(device_handle, buf_ptr)
    errmsg_ptr = ctypes.c_char_p(struct.unpack("L", buf)[0])
    
    errmsg = ""
    if not (errmsg_ptr.value is None):
        errmsg = errmsg_ptr.value.decode()
    
    msg = [
        "No error occurred.",
        "An unknown error occurred: ",
        "An invalid argument was specified: ",
        "The operation is not allowed: ",
        "No enough memory to execute the operation: ",
        "The hardware (e.g., CPU) is not supported: ",
        "The operation was cancelled by the user: ",
    ]
    return err, msg[err] + errmsg


def ReleaseDevice(device_handle: int):
    r"""
    Args:
        device_handle : Get from NewDevice
    """
    RawFunctions.oidnReleaseDevice(device_handle)


def RetainDevice(device_handle: int):
    r"""
    Args:
        device_handle : Get from NewDevice
    """
    RawFunctions.oidnRetainDevice(device_handle)


def SetDeviceBool(device_handle: int, name: str, value: bool):
    r"""
    These parameters can be set by SetDeviceBool:
        setAffinity (default=True): enables thread affinitization (pinning software threads to hardware threads) if it is necessary for achieving optimal performance
    Args:
        device_handle : Get from NewDevice
        name : parameter name
        value : parameter value(bool type)
    """
    RawFunctions.oidnSetDeviceBool(device_handle, bytes(name, "ascii"), value)
    
def SetDevice1b(device_handle: int, name: str, value: bool):
    r"""
    Alias for SetDeviceBool
    """
    SetDeviceBool(device_handle, name, str)

def SetDeviceInt(device_handle: int, name: str, value: int):
    r"""
    These parameters can be set by SetDevice1b:
        verbose : 0 verbosity level of the console output between 0-4; when set to 0, no output is printed, when set to a higher level more output is printed
        numThreads (default = 0) : maximum number of threads which the library should use; 0 will set it automatically to get the best performance
    Args:
        device_handle : Get from NewDevice
        name : parameter name
        value : parameter value(bool type)
    """
    RawFunctions.oidnSetDeviceInt(device_handle, bytes(name, "ascii"), value)
    
def SetDevice1i(device_handle: int, name: str, value: int):
    r'''
    Alias for SetDeviceInt
    '''
    SetDeviceInt(device_handle, name, value)


def GetDeviceInt(device_handle: int, name: str) -> int:
    r"""
    These parameters can be get by GetDeviceInt:
        version : combined version number (major.minor.patch) with two decimal digits per component
        versionMajor : major version number
        versionMinor : minor version number
        versionPatch : patch version number
        verbose : 0 verbosity level of the console output between 0-4; when set to 0, no output is printed, when set to a higher level more output is printed
    Args:
        device_handle : Get from NewDevice
        name : parameter name
    """
    return RawFunctions.oidnGetDeviceInt(device_handle, bytes(name, "ascii"))

def GetDevice1i(device_handle: int, name: str) -> int:
    r'''
    Alias for GetDeviceInt
    '''
    return GetDeviceInt(device_handle, name)

def GetDeviceBool(device_handle: int, name: str) -> bool:
    r"""
    These parameters can be get by GetDeviceBool:
        setAffinity (default = True): enables thread affinitization (pinning software threads to hardware threads) if it is necessary for achieving optimal performance
    Args:
        device_handle : Get from NewDevice
        name : parameter name
    """
    return RawFunctions.oidnGetDeviceBool(device_handle, bytes(name, "ascii"))


def GetDevice1b(device_handle: int, name: str) -> bool:
    r'''
    Alias for GetDeviceBool
    '''
    return GetDeviceBool(device_handle, name)


def NewFilter(device_handle: int, type: str) -> int:
    r"""
    Creates a new filter of the specified type (e.g. "RT")

    Args:
        device_handle(int) : Created by NewDevice
        type(str) : e.g. "RT“ or "RTLightmap"
    """
    return RawFunctions.oidnNewFilter(device_handle, bytes(type, "ascii"))


def SetSharedFilterImage(
    filter_handle: int,
    name: str,
    data: np.ndarray,
    format: int,
    width: int,
    height: int,
    byteOffset: int = 0,
    bytePixelStride: int = 0,
    byteRowStride: int = 0,
):
    r"""
    Set filter image, the parameter name cound be:
        color : input beauty image (3 channels, LDR values in [0, 1] or HDR values in [0, +∞), values being interpreted such that, after scaling with the inputScale parameter, a value of 1 corresponds to a luminance level of 100 cd/m²)
        albedo(only support RT filter) : input auxiliary image containing the albedo per pixel (3 channels, values in [0, 1])
        normal(only support RT filter) : input auxiliary image containing the shading normal per pixel (3 channels, world-space or view-space vectors with arbitrary length, values in [-1, 1])
        output : output image (3 channels); can be one of the input images
    Args:
        filter_handle(int): Created by NewFilter
        name(str): color/albedo/normal/output, See document of OIDN.
        data(np.array): data buffer, should be correct in size and dtype; should be c_contiguous when name == 'output'
        format:  Should be oidn.FORMAT_FLOAT3 for image
        width: width in pixel.
        height: height in pixel.
        byteOffset: default to 0
        bytePixel: default to 0
        byteRawStride: default to 0
    """
    desired_dim3 = [0, 1, 2, 3, 4]
    desired_data_shape = (height, width, desired_dim3[format])
    if not data.shape == desired_data_shape:
        raise RuntimeError(f"The shape of the data should be {desired_data_shape}")

    if name == "output" and not data.flags.c_contiguous:
        raise RuntimeError(f"When name == output, the data should be c_contiguous")

    if not data.flags.c_contiguous:
        data = np.ascontiguousarray(data)
    RawFunctions.oidnSetSharedFilterImage(
        filter_handle,
        bytes(name, "ascii"),
        data.__array_interface__["data"][0],
        format,
        width,
        height,
        byteOffset,
        bytePixelStride,
        byteRowStride,
    )
    
def SetSharedFilterImageEx(
    filter_handle: int,
    name: str,
    data: object,
    get_shape : Callable,
    check_c_contiguous: Callable,
    get_array_interface: Callable,
    format: int,
    width: int,
    height: int,
    byteOffset: int = 0,
    bytePixelStride: int = 0,
    byteRowStride: int = 0):
    r'''
    Used internelly. 'data' parameter could be any buffer type, requring get_shape, check_c_contiguous, get_array_interface.
    '''
    desired_dim3 = [0, 1, 2, 3, 4]
    desired_data_shape = (height, width, desired_dim3[format])
    shape = get_shape(data)
    if not shape == desired_data_shape:
        raise RuntimeError(f"The shape of the data should be {desired_data_shape}")

    if name == "output" and not check_c_contiguous(data):
        raise RuntimeError(f"When name == output, the data should be c_contiguous")

    if not check_c_contiguous(data):
        raise RuntimeError(f"Requires C contiguous data for {name}")
        # data = np.ascontiguousarray(data)
        
    RawFunctions.oidnSetSharedFilterImage(
        filter_handle,
        bytes(name, "ascii"),
        get_array_interface(data)["data"][0],
        format,
        width,
        height,
        byteOffset,
        bytePixelStride,
        byteRowStride,
    )


def UnsetFilterImage(filter_handle: int, name: str):
    r"""
    Remove filter image, name could be color | albedo | normal | output
    Args:
        filter_handle : handle of fitler, get from NewFitler
        name : image name
    """
    RawFunctions.oidnUnsetFilterImage(filter_handle, bytes(name, "ascii"))
    
def RemoveFilterImage(filter_handle: int, name: str):
    r'''
    Alias for UnsetFilterImage
    '''
    UnsetFilterImage(filter_handle, name)

def SetSharedFilterData(filter_handle: int, name: str, data: np.array):
    r"""
    Set filter data, the name could be:
        weights : trained model weights blob
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
        data : numpy array with dtype != object
    """
    if not data.flags.c_contiguous:
        data = np.ascontiguousarray(data)
    RawFunctions.oidnSetSharedFilterData(
        filter_handle,
        bytes(name, "ascii"),
        data.__array_interface__["data"][0],
        data.itemsize * data.size,
    )


def UpdateFilterData(filter_handle: int, name: str):
    r"""
    Just notify the filter that the contents of its data has been changed, name can be weight.

    Args:
        fitler_handle : Get from NewFilter
        name : parameter name
    """
    RawFunctions.oidnUpdateFilterData(filter_handle, bytes(name, "ascii"))


def UnsetFilterData(filter_handle: int, name: str):
    r"""
    Remove the filter data, name can be weight.

    Args:
        fitler_handle : Get from NewFilter
        name : name of the data
    """
    RawFunctions.oidnUnsetFilterData(filter_handle, bytes(name, "ascii"))
    
def RemoveFilterData(filter_handle: int, name: str):
    r'''
    Alias for UnsetFilterData
    '''
    UnsetFilterData(filter_handle, name)    

def GetFilterInt(filter_handle: int, name: str) -> int:
    r"""
    Get filter parameter (type int), the name could be:
        maxMemoryMB (default=3000) : approximate maximum scratch memory to use in megabytes (actual memory usage may be higher); limiting memory usage may cause slower denoising due to internally splitting the image into overlapping tiles
        alignment : when manually denoising in tiles, the tile size and offsets should be multiples of this amount of pixels to avoid artifacts; when denoising HDR images inputScale must be set by the user to avoid seam artifacts
        overlap : when manually denoising in tiles, the tiles should overlap by this amount of pixels
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
    """
    return RawFunctions.oidnGetFilterInt(filter_handle, bytes(name, "ascii"))

def GetFilter1i(filter_handle: int, name: str) -> int:
    r"""
    Alias for GetFilterInt
    """
    return GetFilterInt(filter_handle, name)


def GetFilterBool(filter_handle: int, name: str) -> bool:
    r"""
    Get filter parameter (type bool), the name could be:
        hdr (default = False, only support RT) : whether the main input image is HDR
        srgb (default = False, only support RT) : whether the main input image is encoded with the sRGB (or 2.2 gamma) curve (LDR only) or is linear; the output will be encoded with the same curve
        cleanAux (default = False, only support RT) : whether the auxiliary feature (albedo, normal) images are noise-free; recommended for highest quality but should not be enabled for noisy auxiliary images to avoid residual noise
        directional (default = False, only support RTLightmap) : whether the input contains normalized coefficients (in [-1, 1]) of a directional lightmap (e.g. normalized L1 or higher spherical harmonics band with the L0 band divided out); if the range of the coefficients is different from [-1, 1], the inputScale parameter can be used to adjust the range without changing the stored values
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
    """
    return RawFunctions.oidnGetFilterBool(filter_handle, bytes(name, "ascii"))

def GetFilter1b(filter_handle: bool, name: str) -> bool:
    r'''
    Alias for GEtFilterBool
    '''
    return GetFilterBool(filter_handle, name)

def GetFilterFloat(filter_handle: int, name: str) -> float:
    r"""
    Get filter parameter (type float), the name could be:
        inputScale (default=nan) : scales values in the main input image before filtering, without scaling the output too, which can be used to map color or auxiliary feature values to the expected range, e.g. for mapping HDR values to physical units (which affects the quality of the output but not the range of the output values); if set to NaN, the scale is computed implicitly for HDR images or set to 1 otherwise
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
    """
    return RawFunctions.oidnGetFilterFloat(filter_handle, bytes(name, "ascii"))

def GetFilter1f(filter_handle: int, name: str) -> float:
    r'''
    Alias for GetFilterFloat
    '''
    return GetFilterFloat(filter_handle, name)

def SetFilterBool(filter_handle: int, name: str, value: bool):
    r"""
    Get filter parameter (type bool), the name could be:
        hdr (default = False, only support RT) : whether the main input image is HDR
        srgb (default = False, only support RT) : whether the main input image is encoded with the sRGB (or 2.2 gamma) curve (LDR only) or is linear; the output will be encoded with the same curve
        cleanAux (default = False, only support RT) : whether the auxiliary feature (albedo, normal) images are noise-free; recommended for highest quality but should not be enabled for noisy auxiliary images to avoid residual noise
        directional (default = False, only support RTLightmap) : whether the input contains normalized coefficients (in [-1, 1]) of a directional lightmap (e.g. normalized L1 or higher spherical harmonics band with the L0 band divided out); if the range of the coefficients is different from [-1, 1], the inputScale parameter can be used to adjust the range without changing the stored values
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
        value : value of the parameter
    """
    RawFunctions.oidnSetFilterBool(filter_handle, bytes(name, "ascii"), value)

def SetFilter1b(filter_handle: int, name: str, value: bool):
    r'''
    Alias for SetFilterBool
    '''
    SetFilterBool(filter_handle, name, value)


def SetFilterInt(filter_handle: int, name: str, value: int):
    r"""
    Get filter parameter (type int), the name could be:
        maxMemoryMB (default=3000) : approximate maximum scratch memory to use in megabytes (actual memory usage may be higher); limiting memory usage may cause slower denoising due to internally splitting the image into overlapping tiles
        alignment : when manually denoising in tiles, the tile size and offsets should be multiples of this amount of pixels to avoid artifacts; when denoising HDR images inputScale must be set by the user to avoid seam artifacts
        overlap : when manually denoising in tiles, the tiles should overlap by this amount of pixels
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
        value : value of the parameter
    """
    RawFunctions.oidnSetFilterInt(filter_handle, bytes(name, "ascii"), value)


def SetFilter1i(filter_handle: int, name: str, value: int):
    r'''
    Alias for SetFilterInt
    '''
    SetFilterInt(filter_handle, name, value)

def SetFilterFloat(filter_handle: int, name: str, value: float):
    r"""
    Get filter parameter (type float), the name could be:
        inputScale (default=nan) : scales values in the main input image before filtering, without scaling the output too, which can be used to map color or auxiliary feature values to the expected range, e.g. for mapping HDR values to physical units (which affects the quality of the output but not the range of the output values); if set to NaN, the scale is computed implicitly for HDR images or set to 1 otherwise
    Args:
        filter_handle : Get from NewFilter
        name : name of the parameter
        value : value of the parameter
    """
    RawFunctions.oidnSetFilterFloat(filter_handle, bytes(name, "ascii"), value)
    
def SetFilter1f(filter_handle: int, name : str, value: float):
    r'''
    Alias for SetFilterFloat
    '''
    SetFilterFloat(filter_handle, name, value)

def CommitFilter(filter_handle: int):
    r"""
    Batch up multiple changes for the filter

    Args:
        filter_handle : Get from NewFilter
    """
    RawFunctions.oidnCommitFilter(filter_handle)


def ExecuteFilter(filter_handle: int):
    r"""
    Execute the filter. Remember CommitFilter to ensure all your parameters notified.

    Args:
        filter_handle : Get from NewFilter
    """
    RawFunctions.oidnExecuteFilter(filter_handle)


def ReleaseFilter(filter_handle: int):
    r"""
    Release the filter

    Args:
        filter_handle : Get from NewFilter
    """
    RawFunctions.oidnReleaseFilter(filter_handle)


def RetainFilter(filter_handle: int):
    r"""
    Release the filter

    Args:
        filter_handle : Get from NewFilter
    """
    RawFunctions.oidnRetainFilter(filter_handle)
