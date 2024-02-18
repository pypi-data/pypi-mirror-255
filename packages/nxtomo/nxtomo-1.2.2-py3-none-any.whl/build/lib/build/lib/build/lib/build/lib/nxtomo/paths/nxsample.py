"""nexus path used to define a `NXsample <https://manual.nexusformat.org/classes/base_classes/NXsample.html>`_"""

from . import nxtransformations


class NEXUS_SAMPLE_PATH:
    NAME = "sample_name"

    ROTATION_ANGLE = "rotation_angle"

    X_TRANSLATION = "x_translation"

    Y_TRANSLATION = "y_translation"

    Z_TRANSLATION = "z_translation"

    ROCKING = "rocking"

    BASE_TILT = "base_tilt"

    N_STEPS_ROCKING = "n_step_rocking"

    N_STEPS_ROTATION = "n_step_rotation"

    NX_TRANSFORMATIONS = None

    NX_TRANSFORMATIONS_PATHS = None


class NEXUS_SAMPLE_PATH_V_1_0(NEXUS_SAMPLE_PATH):
    pass


class NEXUS_SAMPLE_PATH_V_1_1(NEXUS_SAMPLE_PATH_V_1_0):
    NAME = "name"


class NEXUS_SAMPLE_PATH_V_1_2(NEXUS_SAMPLE_PATH_V_1_1):
    pass


class NEXUS_SAMPLE_PATH_V_1_3(NEXUS_SAMPLE_PATH_V_1_2):
    NX_TRANSFORMATIONS = "transformations"

    NX_TRANSFORMATIONS_PATHS = nxtransformations.NEXUS_TRANSFORMATIONS_PATH_V_1_3
