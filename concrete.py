import materials
from math import sqrt, copysign

def get_a(bw, Astl, concrete: materials.ConcreteMaterial,
          steel: materials.SteelMaterial):
    try:
        return steel.fy * Astl / (0.85 * concrete.fc * bw)
    except ZeroDivisionError:
        return 0

def get_c(a, concrete: materials.ConcreteMaterial):
    try:
        return a / concrete.b1
    except ZeroDivisionError:
        return 0

def get_es(c,d,concrete: materials.ConcreteMaterial):
    try:
        return concrete.ecu*(1-d/c)
    except ZeroDivisionError:
        return 0

def get_fs(strain: float, steel: materials.SteelMaterial):
    if abs(strain/steel.ey) < 1:
        return copysign(strain*steel.Es,strain)
    else:
        return copysign(steel.fy,strain)

def get_Vc(bw, d, concrete: materials.ConcreteMaterial):
    return 2 * concrete.lam * sqrt(concrete.fc) * bw * d

def get_Vc_with_axial(bw, d, Nu, Ag, concrete: materials.ConcreteMaterial,
                      isSignificantTension: bool = False):
    # Eq. (22.5.6.1) or (22.5.7.1)
    denominator = 2000
    if isSignificantTension == True:
        denominator = 500
    return max((1 + Nu/(denominator * Ag)) * get_Vc(bw, d, concrete),0)

def get_Av_s(Vu, Vc, d, steel: materials.SteelMaterial,
             isSeisShear: bool = False):
    try:
        phiV = 0.75
        if isSeisShear == True:
            phiV = 0.6
        return (Vu - phiV * Vc) / (phiV * steel.fy * d)
    except ZeroDivisionError:
        return 0

