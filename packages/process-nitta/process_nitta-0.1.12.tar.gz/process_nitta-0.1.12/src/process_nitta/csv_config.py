from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class engineStr(str, Enum):
    PYTHON = "python"


class encodingStr(str, Enum):
    Shift_JIS = "shift-jis"
    UTF_8 = "utf-8"


class ColumnStrEnum(str, Enum):
    VOLTAGE = "Voltage"
    FORCE = "Force /N"
    STROKE = "Stroke /mm"
    WAVE_NUMBER = "Wave number /cm$^{-1}$"
    ABSORBANCE = "Absorbance /a.u."
    STRAIN = "Strain $\epsilon$ /-"  # type: ignore
    STRESS = "Stress $\sigma$ /MPa"  # type: ignore
    TEMPERATURE = "Temperature /℃"
    E1 = "$\it E'$ /Pa"  # type: ignore
    E2 = "$\it E''$ /Pa"  # type: ignore
    TAN_DELTA = "tan $\delta$"  # type: ignore
    RAMAN_SHIFT = "Raman Shift /cm$^{-1}$"
    INTENSITY = "Intensity /a.u."
    GAUSSIAN_STRAIN = "Gaussian strain $\it\lambda^2 -1 /\lambda$ /-"  # type: ignore
    TRUE_STRESS = "True stress $\sigma \lambda$ /-"  # type: ignore
    DRAW_RATIO = "Draw ratio $\lambda$ /-"  # type: ignore

    def __str__(self) -> str:
        return super().value


col = ColumnStrEnum


class CSVConfig(BaseModel):
    encoding: encodingStr = encodingStr.Shift_JIS
    sep: str = ","
    header: Optional[int] = None
    names: Optional[List[str]] = None
    usecols: Union[List[int], List[str], None] = None
    dtype: Optional[Dict[str, type]] = None
    skiprows: Optional[List[int]] = None  # 冒頭の行を読み飛ばす動作は許可しない
    skipfooter: int = 0
    nrows: Optional[int] = None
    engine: Optional[engineStr] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def Instron(self) -> "CSVConfig":
        self.header = 51
        self.skipfooter = 3
        self.names = ["EndHeader", "日時(μs)", col.VOLTAGE]
        self.usecols = [col.VOLTAGE]
        self.dtype = {col.VOLTAGE: float}
        self.engine = engineStr.PYTHON
        return self

    def AGIS(self) -> "CSVConfig":
        self.header = 19
        self.names = ["sec", col.FORCE, col.STROKE, "empty"]
        self.usecols = [col.FORCE, col.STROKE]
        self.dtype = {col.FORCE: float, col.STROKE: float}
        return self

    def DMA(self) -> "CSVConfig":
        self.header = 28
        self.names = [
            "TOTAL",
            "BL",
            "No",
            col.TEMPERATURE,
            "FREQ.",
            "OMEGA",
            col.E1,
            col.E2,
            "E*",
            col.TAN_DELTA,
            "ETA'",
            "ETA''",
            "ETA * ",
            "Time",
            "DISP",
            "DISP.1",
            "FORCE",
            "LOAD",
            "C.D",
            "PHASE",
            "STRESS",
            "S.STRESS",
            "N.STRESS",
            "REVL",
            "HUMIDITY ",
            "F/L",
            "Ld",
            "TempB",
            "TempC",
            "J*",
            "J'",
            "J''",
            " W ",
            " TempC",
            "*",
        ]
        self.usecols = [
            col.TEMPERATURE,
            col.E1,
            col.E2,
            col.TAN_DELTA,
        ]
        self.dtype = {
            col.TEMPERATURE: float,
            col.E1: float,
            col.E2: float,
            col.TAN_DELTA: float,
        }
        return self

    def IR_NICOLET(self) -> "CSVConfig":
        self.names = [col.WAVE_NUMBER, col.ABSORBANCE]
        self.usecols = [col.WAVE_NUMBER, col.ABSORBANCE]
        self.dtype = {col.WAVE_NUMBER: float, col.ABSORBANCE: float}
        return self

    def Raman(self) -> "CSVConfig":
        self.sep = "\t"
        self.names = [col.RAMAN_SHIFT, "1", col.INTENSITY]
        self.usecols = [col.RAMAN_SHIFT, col.INTENSITY]
        self.dtype = {col.RAMAN_SHIFT: float, col.INTENSITY: float}
        return self
