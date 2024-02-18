from ssmdevices.instruments import TektronixMSO64BSpectrogram, TektronixMSO64B
import labbench as lb

scope = TektronixMSO64BSpectrogram()

with scope:
    scope.spectrogram_enabled