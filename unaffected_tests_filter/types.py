from __future__ import annotations

from typing import NewType, Union

NotTestSrcPathStr = NewType("NotTestSrcPathStr", str)
TestSrcPathStr = NewType("TestSrcPathStr", str)
SrcPathStr = Union[NotTestSrcPathStr, TestSrcPathStr]
ChecksumStr = NewType("ChecksumStr", str)
