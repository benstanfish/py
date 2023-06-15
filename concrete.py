"""Library of concrete-related functions based on the ACI 318"""
# Created by Ben Fisher, 2023
# Version 1.0

from math import sqrt, copysign

DIAMS = {
    # Nominal linear diameter of rebar per Appendix A
    3: 0.375,
    4: 0.500,
    5: 0.625,
    6: 0.750,
    7: 0.875,
    8: 1.000,
    9: 1.128,
    10: 1.270,
    11: 1.410,
    14: 1.693,
    18: 2.257
}

AREAS = {
    # Nominal cross-sectional area of rebar per Appendix A
    3: 0.11,
    4: 0.20,
    5: 0.31,
    6: 0.44,
    7: 0.60,
    8: 0.79,
    9: 1.00,
    10: 1.27,
    11: 1.56,
    14: 2.25,
    18: 4.00
}

WEIGHTS = {
    # Nominal linear weight of rebar per Appendix A
    3: 0.376,
    4: 0.668,
    5: 1.043,
    6: 1.503,
    7: 2.044,
    8: 2.67,
    9: 3.4,
    10: 4.303,
    11: 5.313,
    14: 7.65,
    18: 13.6
}

DEFAULT_ES = 29000000.0    # Steel modulus of elasticity (Es) in psi per Sec. 20.2.2.2
DEFAULT_FY = 60000.0       # Default steel yeild strength in psi (Grade 60 bar)
DEFAULT_ECU = -0.003     # Default limit concrete strain. Negative strain == compression.

"""
    Arguments:

    aDist: the "a" distance (in)
    Ag: gross cross-sectional area (in^2)
    Astl: area of steel at a given layer (in^2)
    betaOne: value of beta1 per Table 22.2.2.4.3 (unitless)
    bw: member width (in)
    cDist: the "c" neutral axis distance (in)
    dDist: the "d" distance from compression fiber to steel layer (in)
    ecu: limit concrete compression strain, typically 0.003 (in/in)
    Es: modulus of elasticity of steel (psi)
    fc: 28-day concrete compression strength (psi)
    fy: steel yield strength (psi)
    isSignificantTension: "judgement call" as to whether tension is "significant"
    lam: lightweight concrete factor, lambda (unitless)
    Nu: axial force (lbf), where compression is positive, tension is negative
    strain: steel strain (in/in) at layer "d"
    Vc: concrete shear strength (lbf)
    wc: concrete unit weight (pcf)
"""

def beta1(fc):
    """Calculate the value of beta1 per Table 22.2.2.4.3
    
    fc: 28-day concrete compression strength in psi"""
    # If ksi units are provided, this function converts to psi
    if fc < 10:
        fc *= 1000
    if fc <= 4000:
        return 0.85
    elif fc >= 8000:
        return 0.65
    else:
        return 0.85 - 0.05*(fc - 4000)/1000

def cDist(aDist, betaOne):
    """Returns neutral axis distance c per Eq. (22.2.2.4.1)
    
    aDist: the "a" distance (in)
    betaOne: value of beta1 per Table 22.2.2.4.3 (unitless)"""
    return aDist/betaOne

def aDist(fc, bw, Astl, fy = DEFAULT_FY):
    """Calculates the "a" distance of beam
    
    fc: 28-day concrete compression strength (psi)
    bw: member width (in)
    Astl: area of steel at a given layer (in^2)
    fy: steel yield strength (psi)"""
    # The factor 0.85f'c is the limit concrete stress per Sec. 22.2.2.4.1.
    return  fy * Astl / (0.85 * fc * bw)

def Ec(fc, wc: float = None):
    """Returns concrete elastic modulus (Ec) per Eq. (19.2.2.1.b), unless wc provided, then Eq. (19.2.2.1.a)
    
    fc: 28-day concrete compression strength (psi)
    wc: concrete unit weight (pcf), should be between 90 and 160 pcf
    """
    # Note: wc = 143.959593 pcf makes both equations approximately equal.
    # If ksi units are provided, this function converts to psi
    if fc < 10:
        fc *= 1000
    if wc is None:
        return 57000*sqrt(fc)
    else:
        return (wc**1.5)*33*sqrt(fc)

def ruptureModulus(fc, lam: float = 1):
    """Returns modulus of rupture per Eq. (19.2.3.1). Lambda per Table 19.2.4.2, defaults to lambda = 1 (NWC).

    fc: 28-day concrete compression strength (psi)
    lam: lightweight concrete factor, lambda (unitless)"""
    # If ksi units are provided, this function converts to psi
    if fc < 10:
        fc *= 1000
    return 7.5*lam*sqrt(fc)

def getStrain(dDist, cDist, ecu: float = DEFAULT_ECU):
    """Returns the strain at layer "d" assuming similar triangles. Compression treated as positive.
    
    cDist: the "c" neutral axis distance (in)
    dDist: the "d" distance from compression fiber to steel layer (in)
    ecu = limit concrete strain of 0.003, per Sec. 22.2.2.1"""
    return ecu * (1 - dDist/cDist)

def yieldStrain(fy: float = DEFAULT_FY, Es: float = DEFAULT_ES):
    """Returns the yield strain (ey) for a given steel strength (psi) and elastic modulus (psi)

    fy: steel yield strength (psi)
    Es: modulus of elasticity of steel (psi)"""
    return fy/Es

def steelStress(strain, Es: float = DEFAULT_ES, fy: float = DEFAULT_FY):
    """Returns steel stress (fs) based on the steel strain. Refer to Sec. R20.2.2.1
    
    strain: steel strain (in/in) at layer "d"
    Es: modulus of elasticity of steel (psi)
    fy: steel yield strength (psi)
    """
    # Note that this case applies -ey < fyain < ey. Therefore steel in compression
    # must have a negative sign to get the correct stress sign
    ey = fy/Es
    if abs(strain/ey) < 1:
        return copysign(strain*Es,strain)
    else:
        return copysign(fy,strain)

def getVc(fc: float, bw: float, dDist: float, lam: float = 1):
    """Returns the shear strength Vc (lbf) for nonprestressed 
    members w/o axial forcce per Eq. (22.5.5.1)

    fc: 28-day concrete compression strength (psi)
    bw: member width (in)
    dDist: the "d" distance from compression fiber to steel layer (in)"""
    return 2*lam*sqrt(fc)*bw*dDist

def getVcWithAxial(
    fc: float, bw: float, dDist: float, 
    Nu: float, Ag: float, lam: float = 1, isSignificantTension:bool = False):
    """Returns the shear strength Vc (lbf) for nonprestressed 
    members WITH axial force per Eq. (22.5.6.1) or (22.5.7.1) if 
    
    fc: 28-day concrete compression strength (psi)
    bw: member width (in)
    dDist: the "d" distance from compression fiber to steel layer (in)
    Nu: axial force (lbf), where compression is positive, tension is negative
    Ag: gross cross-sectional area (in^2)"""
    denom = 2000
    if isSignificantTension == True:
        denom = 500
    Vc = 2*(1+Nu/(denom*Ag))*lam*sqrt(fc)*bw*dDist
    return max(Vc,0)


