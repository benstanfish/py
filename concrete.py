import numpy as np
import materials
from math import abs

# def get_a(bw, Astl, concrete: materials.ConcreteMaterial, steel: materials.RebarMaterial):
#     try:
#         return steel.fy * Astl / (0.85 * concrete.fc * bw)
#     except ZeroDivisionError:
#         return 0

# def get_c_from_a(a, concrete: materials.ConcreteMaterial):
#     try:
#         return a / concrete.b1
#     except ZeroDivisionError:
#         return 0

# def get_c_from_Z(z, d, concrete: materials.ConcreteMaterial, steel: materials.RebarMaterial):
#     try:
#         return d / (1 - z * steel.ey / concrete.ecu)
#     except ZeroDivisionError:
#         return 0

# def get_c_from_d(strain:float , d:float , concrete: materials.ConcreteMaterial):
#     try:
#         return d / (1 - strain / concrete.ecu)
#     except ZeroDivisionError:
#         return 0

# def get_es(c, d, concrete: materials.ConcreteMaterial):
#     try:
#         return concrete.ecu*(1-d/c)
#     except ZeroDivisionError:
#         return 0

# def get_fs(strain: float, steel: materials.RebarMaterial):
#     if abs(strain/steel.ey) < 1:
#         return copysign(strain*steel.Es,strain)
#     else:
#         return copysign(steel.fy,strain)

def geometric_sequence(n, initial, common_ratio):
    return initial * common_ratio ^ (n - 1)

def layerDistances(n, db, cc, h):
    return np.linspace(cc + db/2, h-cc-db/2, n)

def maximumCompression(Ag, layer_areas, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    return (0.85 * concrete.fc) * (Ag - np.sum(layer_areas)) + rebar.fy * np.sum(layer_areas)

def cFromZ(Z, d, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    try:
        return concrete.ecu/(concrete.ecu - Z * rebar.ey)*d
    except ZeroDivisionError:
        return 0
    
def zFromC(c, d, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    if c != 0:
        try:
            return concrete.ecu / rebar.ey * (1 - d / abs(c))
        except:
            return 0
    else:
        # c = 0 is error case; pass 250 which is well past the rupture strain
        return 250

def layerStrain(layer_distance, c, concrete: materials.ConcreteMaterial):
    try:
        return (c - layer_distance)/c * concrete.ecu
    except:
        return 0
    
def layerStress(layer_distance, c, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    strain = layerStrain(layer_distance, c, concrete)
    return min(rebar.fy * np.sign(strain), strain * rebar.Es)

def layerForce(layer_area, layer_distance, c, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    if layer_distance > c:
        return layerStress(layer_distance, c, concrete, rebar) * layer_area
    else:
        return (layerStress(layer_distance, c, concrete, rebar) - 0.85 * concrete.fc) * layer_area
    
def sumLayerForces(layer_areas, layer_distances, c, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    force = 0
    for i in range(layer_areas.shape[0]):
        force += layerForce(layer_areas[i], layer_distances[i], c, concrete, rebar)
    return force

    
def sumLayerMoments(layer_areas, layer_distances, h, c, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    moment = 0
    for i in range(layer_areas.shape[0]):
        moment += layerForce(layer_areas[i], layer_distances[i], c, concrete, rebar) * (h/2 - layer_distances[i])
    return moment

def PMPoints(c, bw, h, layer_distances, layer_areas, concrete: materials.ConcreteMaterial, rebar: materials.RebarMaterial):
    sum_Fs = 0
    sum_Ms = 0
    for i in range(layer_areas.shape[0]):
        sum_Fs += layerForce(layer_areas[i], layer_distances[i], c, concrete, rebar)
        sum_Ms += layerForce(layer_areas[i], layer_distances[i], c, concrete, rebar) * (h/2 - layer_distances[i])
    Cc = 0.85 * bw * (c * concrete.b1) * concrete.fc
    Mc = Cc * (h - (c * concrete.b1))/2
    P = Cc + sum_Fs
    M = Mc + sum_Ms
    return M, P

