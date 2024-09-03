import os
import ctypes
import json


def init_lib(so_file):
    """Initialize the go library to be used in python
    and define the functions available in the library.
    """
    lib = ctypes.CDLL(so_file)
    # Define the functions signature
    lib.UploadFiles.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
    lib.UploadFiles.restype = ctypes.c_char_p
    # Declare the functions available
    funcs = {
        "UploadFiles": lib.UploadFiles,
    }
    return funcs


def encode_ctypes_upload_files(url, api_key, file_paths):
    """Encode the parameters to be used in the UploadFiles function.
    """
    return (
        ctypes.c_char_p(url.encode('utf-8')),
        ctypes.c_char_p(api_key.encode('utf-8')),
        (ctypes.c_char_p * len(file_paths))(*[p.encode('utf-8') for p in file_paths]),
    )

PWD = os.path.dirname(os.path.abspath(__file__))
NAKALA_BATCH_GO_LIB = init_lib(os.path.join(PWD, "nakala_request.so"))


# easy bridges to Python
def process_nkl_files_with_go(url, api_key, file_paths):
    """Process the files with the go library.
    """
    return json.loads(
        NAKALA_BATCH_GO_LIB["UploadFiles"](
            *encode_ctypes_upload_files(url, api_key, file_paths),
            len(file_paths)
        ).decode('utf-8')
    )