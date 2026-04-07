from __future__ import annotations

import importlib
import sys
import types
from typing import Any, cast

from qtpy import API_NAME, QtCore, QtGui, QtNetwork, QtWidgets
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtNetwork import *
from qtpy.QtWidgets import *

pyqtSignal = QtCore.Signal
pyqtSlot = QtCore.Slot
pyqtProperty = QtCore.Property


def _resolve_sip():
    binding_sip: Any
    try:
        module_name = "PyQt6.sip" if API_NAME == "pyqt6" else "PyQt5.sip"
        binding_sip = importlib.import_module(module_name)
    except Exception:
        binding_sip = types.SimpleNamespace()

    if not hasattr(binding_sip, "transferback"):
        binding_sip.transferback = lambda obj: None
    return binding_sip


def _install_pyqt_aliases():
    qtcore_any = cast(Any, QtCore)
    qtcore_any.pyqtSignal = pyqtSignal
    qtcore_any.pyqtSlot = pyqtSlot
    qtcore_any.pyqtProperty = pyqtProperty
    try:
        qobject_type = getattr(qtcore_any, "QObject", None)
        if qobject_type is None:
            raise AttributeError
        pyqt_bound_signal = type(qobject_type().destroyed)
    except Exception:
        pyqt_bound_signal = object
    qtcore_any.pyqtBoundSignal = pyqt_bound_signal

    sip = _resolve_sip()

    package = types.ModuleType("PyQt5")
    package.__path__ = []
    package_any = cast(Any, package)
    package_any.QtCore = QtCore
    package_any.QtGui = QtGui
    package_any.QtNetwork = QtNetwork
    package_any.QtWidgets = QtWidgets
    package_any.sip = sip

    sys.modules["PyQt5"] = package
    sys.modules["PyQt5.QtCore"] = QtCore
    sys.modules["PyQt5.QtGui"] = QtGui
    sys.modules["PyQt5.QtNetwork"] = QtNetwork
    sys.modules["PyQt5.QtWidgets"] = QtWidgets

    sip_module = types.ModuleType("PyQt5.sip")
    sip_module_any = cast(Any, sip_module)
    sip_module_any.transferback = sip.transferback
    if hasattr(sip, "isdeleted"):
        sip_module_any.isdeleted = sip.isdeleted
    sys.modules["PyQt5.sip"] = sip_module

    return sip_module


pyqtBoundSignal: Any = object


sip = _install_pyqt_aliases()
