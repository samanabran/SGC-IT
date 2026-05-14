from personas.p1_faisal import PERSONA as P1_FAISAL
from personas.p2_noura import PERSONA as P2_NOURA
from personas.p3_omar import PERSONA as P3_OMAR
from personas.p4_rajesh import PERSONA as P4_RAJESH


PERSONAS = {
    P1_FAISAL["id"]: P1_FAISAL,
    P2_NOURA["id"]: P2_NOURA,
    P3_OMAR["id"]: P3_OMAR,
    P4_RAJESH["id"]: P4_RAJESH,
}


def get_persona(persona_id: str):
    return PERSONAS.get(persona_id, P1_FAISAL)
