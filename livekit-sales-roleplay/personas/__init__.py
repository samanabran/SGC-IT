from personas.p1_faisal import PERSONA as P1_FAISAL
from personas.p2_noura import PERSONA as P2_NOURA
from personas.p3_omar import PERSONA as P3_OMAR
from personas.p4_rajesh import PERSONA as P4_RAJESH
from personas.p5_imran import PERSONA as P5_IMRAN
from personas.p6_vikram import PERSONA as P6_VIKRAM
from personas.p7_sarah import PERSONA as P7_SARAH
from personas.p8_michael import PERSONA as P8_MICHAEL
from personas.p9_andrew import PERSONA as P9_ANDREW


PERSONAS = {
    P1_FAISAL["id"]: P1_FAISAL,
    P2_NOURA["id"]: P2_NOURA,
    P3_OMAR["id"]: P3_OMAR,
    P4_RAJESH["id"]: P4_RAJESH,
    P5_IMRAN["id"]: P5_IMRAN,
    P6_VIKRAM["id"]: P6_VIKRAM,
    P7_SARAH["id"]: P7_SARAH,
    P8_MICHAEL["id"]: P8_MICHAEL,
    P9_ANDREW["id"]: P9_ANDREW,
}


def get_persona(persona_id: str):
    return PERSONAS.get(persona_id, P1_FAISAL)
