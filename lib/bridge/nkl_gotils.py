import os
import ctypes
import json
import platform


def init_lib() -> dict:
    """Initialize the go library to be used in python
    and define the functions available in the library.

    :return: the functions available in the library
    :rtype: dict
    """
    system = platform.system()
    lib_ext = ""

    if system == "Linux":
        lib_ext = ".so"
    elif system == "Darwin":  # macOS
        lib_ext = ".dylib"
    else:
        raise f"Unsupported OS: {system}"

    so_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"nakala_request{lib_ext}"
    )
    lib = ctypes.CDLL(so_file)
    # Define the functions signature
    lib.UploadFiles.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
    lib.UploadFiles.restype = ctypes.c_char_p
    # Declare the functions available
    return {
        "UploadFiles": lib.UploadFiles,
    }


def encode_ctypes_upload_files(url: str,
                               api_key: str,
                               file_paths: list[str]) -> tuple:
    """Encode the parameters to be used in the UploadFiles function.

    :param url: the url of the Nakala API
    :type url: str
    :param api_key: the api key to use the Nakala API
    :type api_key: str
    :param file_paths: the paths to the files to upload
    :type file_paths: list[str]
    :return: the encoded parameters
    :rtype: tuple
    """
    return (
        ctypes.c_char_p(url.encode('utf-8')),
        ctypes.c_char_p(api_key.encode('utf-8')),
        (ctypes.c_char_p * len(file_paths))(*[p.encode('utf-8') for p in file_paths]),
    )


NAKALA_BATCH_GO_LIB = init_lib()


# easy bridges to Python
def process_nkl_files_with_go(url: str,
                              api_key: str,
                              file_paths: list[str]) -> dict:
    """Process the files with the go library.

    :param url: the url of the Nakala API
    :type url: str
    :param api_key: the api key to use the Nakala API
    :type api_key: str
    :param file_paths: the paths to the files to upload
    :type file_paths: list[str]
    :return: the response from the go library
    :rtype: dict
    """
    return json.loads(
        NAKALA_BATCH_GO_LIB["UploadFiles"](
            *encode_ctypes_upload_files(url, api_key, file_paths),
            len(file_paths)
        ).decode('utf-8')
    )
