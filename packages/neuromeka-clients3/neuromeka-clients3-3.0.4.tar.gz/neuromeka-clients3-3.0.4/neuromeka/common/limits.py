# Boundaries for Indy High-level Command
LevelMin = 1
LevelMax = 9
JogLevelMin = 1
JogLevelMax = 3
JogVelLevelDefault = 2
JogAccLevelDefault = 2

JogVelRatioDefault = 15  # %
JogAccRatioDefault = 100  # %
VelRatioMax = 100  # %
VelRatioMin = 1  # %
AccRatioMax = 900  # %
AccRatioMin = 1  # %

JogVelRatioMin = 5  # %
JogVelRatioMax = 25  # %
VelAutoLevelValue = (VelRatioMax - JogVelRatioMax) / (LevelMax - JogLevelMax)  # %
VelManualLevelValue = (JogVelRatioMax - JogVelRatioMin) / (JogLevelMax - JogLevelMin)  # %

TaskDispVelValueDefault = 250  # 250mm/s
TaskDispAccValueDefault = 250  # 250mm/s^2
TaskDispVelValueMax = 1000  # mm/s
TaskRotVelValueMax = 120  # deg/s

if 1:
    # External motor spec.
    # At Hangnam Project
    # Maker : Panasonic
    # Model : MCDLN35BE
    # Max. Speed : 3000 rpm
    # Pitch : 5 mm/rev
    # Physical Gear Ratio : 10
    # Electronic Gear Ratio : 10
    # Electronic Counts : 50000 pulses
    ExternalMotorSpeedMax = 250  # mm/s : 3000rpm -> 50 rev/sec * 5 mm/rev -> 250 mm/s
else:
    # At HQ
    # Maker : Panasonic
    # Model : MCDLN35BE
    # Max. Speed : 3000 rpm
    # Pitch : 10 mm/rev
    # Physical Gear Ratio : 1
    # Electronic Gear Ratio : 1
    # Electronic Counts : 8388608 pulses
    ExternalMotorSpeedMax = 500  # mm/s : 3000rpm -> 50 rev/sec * 10 mm/rev -> 500 mm/s

# JogDispVelValueMin = 50  # mm/s
# JogDispVelValueMax = 250  # mm/s
# JogDispVelValueDefault = 150  # mm/s
# DispVelAutoLevelValue = (DispVelValueMax - JogDispVelValueMax) / (LevelMax - JogLevelMax)  # mm/s
# DispVelManualLevelValue = (JogDispVelValueMax - JogDispVelValueMin) / (JogLevelMax - JogLevelMin)  # mm/s
#
# RotVelValueMax = 120  # deg/s
# RotVelValueMin = 1  # deg/s
# JogRotVelValueMin = 10  # deg/s
# JogRotVelValueMax = 30  # deg/s
# JogRotVelValueDefault = 20  # deg/s
# RotVelAutoValue = (RotVelValueMax - JogRotVelValueMax) / (LevelMax - JogLevelMax)  # deg/s
# RotVelManualValue = (JogDispVelValueMax - JogDispVelValueMin) / (JogLevelMax - JogLevelMin)  # deg/s
