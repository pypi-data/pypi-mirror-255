# Copyright (c) 2021 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# Imports
#
import binascii
from typing import Union


#
# Classes
#

# Wrapper for utility functions
class Utils:
    # Decode data to specified encoding
    @staticmethod
    def Decode(data: Union[str, bytes],
               encoding: str = "utf-8") -> str:
        if isinstance(data, str):
            return data
        if isinstance(data, bytes):
            return data.decode(encoding)
        raise TypeError("Invalid data type")

    # Encode data to specified encoding
    @staticmethod
    def Encode(data: Union[str, bytes],
               encoding: str = "utf-8") -> bytes:
        if isinstance(data, str):
            return data.encode(encoding)
        if isinstance(data, bytes):
            return data
        raise TypeError("Invalid data type")

    # Convert data to string
    @staticmethod
    def DataToString(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            return data
        if isinstance(data, bytes):
            return Utils.BytesToHexStr(data)
        raise TypeError("Invalid data type")

    # Convert bytes to hex string
    @staticmethod
    def BytesToHexStr(data: bytes) -> str:
        return Utils.Decode(binascii.hexlify(data))
