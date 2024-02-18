from pydantic import BaseModel
from typing import Optional

# =========================================================================== #
#  TIC
# =========================================================================== #
class TAC(BaseModel):
    k: int
    n: int
    timestamp: int
    def getId(self) -> dict:
        return {'k' : self.k, 'n' : self.n}

# =========================================================================== #
#  TIC
# =========================================================================== #
class TIC(BaseModel):
    k: int
    timestamp: int
    pvPlannedDown: bool
    stgPlannedDown: bool
    allPlannedDown: bool
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  MeasuredWeather
# =========================================================================== #
class MeasuredWeather(BaseModel):
    rad_ar: float
    temp_ar: float
    wind_ar: float
    timestamp: int
    storeTimestamp: Optional[int] = None
    def getId(self) -> dict:
        return {'timestamp' : self.timestamp}

# =========================================================================== #
#  MeasuredWeatherTIC
# =========================================================================== #
class MeasuredWeatherTIC(BaseModel):
    k: int
    rad_ar: float
    temp_ar: float
    wind_ar: float
    measuredTimestamp: int
    storeTimestamp: Optional[int] = None
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  OptimizationParameter
# =========================================================================== #
class OptimizationParameter(BaseModel):
    name: str
    value: float
    unit: str
    def getId(self) -> dict:
        return {'name' : self.name}

# =========================================================================== #
#  SAMParameter
# =========================================================================== #
class SAMParameter(BaseModel):
    name: str
    value: float
    unit: str
    def getId(self) -> dict:
        return {'name' : self.name}

# =========================================================================== #
#  ReceivedForecast
# =========================================================================== #
class ReceivedForecast(BaseModel):
    timestamp: int
    rad_ar: float
    temp_ar: float
    wind_ar: float
    storeTimestamp: Optional[int] = None
    def getId(self) -> dict:
        return {'timestamp' : self.timestamp}

# =========================================================================== #
#  SpotEstimatedTIC
# =========================================================================== #
class SpotEstimatedTIC(BaseModel):
    k: int
    spotMwhEUR: float
    estimationK: int
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  SpotPublishedTIC
# =========================================================================== #
class SpotPublishedTIC(BaseModel):
    k: int
    spotMwhEUR: float
    acceptedProgramKwh: float
    publishK: int
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  WeatherEstimateTAC
# =========================================================================== #
class WeatherEstimateTAC(BaseModel):
    k: int
    n: int
    rad_ar: float
    wind_ar: float
    temp_ar: float
    storeTimestamp: Optional[int] = None
    forecastStoreTimestamp: int
    def getId(self) -> dict:
        return {'k' : self.k, 'n': self.n}

# =========================================================================== #
#  WeatherEstimateTIC
# =========================================================================== #
class WeatherEstimateTIC(BaseModel):
    k: int
    rad_ar: float
    wind_ar: float
    temp_ar: float
    storeTimestamp: Optional[int] = None
    forecastStoreTimestamp: int
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  OutputPVForecastedTIC
# =========================================================================== #
class OutputPVForecastedTIC(BaseModel):
    k: int
    outputPVForecasted: float
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  OutputPVForecastedSAMTIC
# =========================================================================== #
class OutputPVForecastedSAMTIC(BaseModel):
    k: int
    outputPVForecasted: float
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  StorageStatusTAC
# =========================================================================== #
class StorageStatusTAC(BaseModel):
    k: int
    n: int
    storageActual: float
    storageInverterRealised: float
    storageActualKwh: float
    storageMax: float
    def getId(self) -> dict:
        return {'k' : self.k, 'n': self.n}

# =========================================================================== #
#  OutputPVMeasuredTAC
# =========================================================================== #
class OutputPVMeasuredTAC(BaseModel):
    k: int
    n: int
    outputPVKwh: float
    def getId(self) -> dict:
        return {'k' : self.k, 'n': self.n}

# =========================================================================== #
#  NuTIC
# =========================================================================== #
class NuTIC(BaseModel):
    k: int
    nuSAM: float
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  OutputPVForecastedTAC
# =========================================================================== #
class OutputPVForecastedTAC(BaseModel):
    k: int
    n: int
    outputPVForecasted: float
    def getId(self) -> dict:
        return {'k' : self.k, 'n': self.n}

# =========================================================================== #
#  ProgramOptLowTAC
# =========================================================================== #
class ProgramOptLowTAC(BaseModel):
    k: int
    n: int
    storageInvSent: float
    pvInvSent: bool
    def getId(self) -> dict:
        return {'k' : self.k, 'n': self.n}

# =========================================================================== #
#  ProgramOptMidTIC
# =========================================================================== #
class ProgramOptMidTIC(BaseModel):
    k: int
    storageStatus: float
    def getId(self) -> dict:
        return {'k' : self.k}

# =========================================================================== #
#  ProgramOptUpTIC
# =========================================================================== #
class ProgramOptUpTIC(BaseModel):
    k: int
    calculatedProgram: float
    def getId(self) -> dict:
        return {'k' : self.k}
    
# =========================================================================== #
#  SOLLog
#  type should be either "INFO" "ERROR" or "WARNING"
# =========================================================================== #
class SOLLog(BaseModel):
    id: Optional[int]
    source: str
    message: str
    details: str
    type: str
    timestamp: Optional[int]