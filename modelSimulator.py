import streamlit as st
import tensorflow as tf
import numpy as np


# """
# # Stress Intensity Factor Calculator (Proof of Concept)

# """


def KP(model, a, b, w, l0, l1):
    inputs = np.array([[a / b, w / b, l0 / b, l1 / b]])
    outputs = model.predict(inputs)
    kop = (outputs * l1 * (a ** 0.5) / b / w / w)
    return kop if np.isfinite(kop) else 0.0


def emp2(a, b, w, L, P):
    F = 1.85 - 3.38*(a/b) + 13.24*pow(a/b, 2) - 23.26*pow(a/b, 3) + 16.8*pow(a/b, 4)
    y = (pow(b, 2) * w / 2 + pow(w, 2) / 4 * (b + w / 6)) / (b * w + pow(w, 2) / 4)
    I = (w*pow(b, 3)/12 + pow(y-b/2, 2)*b*w + pow(w, 4)/288 + pow(w/6+b-y, 2)*pow(w, 2)/4)
    sigma = P * L * y / I
    return sigma * (pow(a, 0.5) * 3.14159) * F


def pad(n, width, z='0'):
    return (str(z) * (width - len(str(n))) + str(n))


def getDisplayValues(a, b, w, l0, l1, P, K_o, record_num):
    result = {"success": False}
    
    print(type(a), type(b), type(w), type(l0), type(l1), type(P), type(K_o))
    try:
        K_o = float(K_o)
        str_output = ("a={:.3f}, b={:.3f}, w={:.3f}, L0={:.3f}, L1={:.3f}, P={:.3f}, KI={:.3f}".format(a, b, w, l0, l1, P, K_o))
        
        result["str_output"] = str_output
        result["empirical"] = '{:.3f}'.format(emp2(a, b, w, l1, P))
        result["ki_value"] = '{:.3f}'.format(K_o)
        
        if (0.1 <= a/b <= 0.8 and 1.0 <= w/b <= 3.0 and
            0.1 <= l0/b <= 0.4 and 2.0 <= l1/b <= 5.0):
            result["type"] = ":) Interpolation"
        else:
            result["type"] = ":( Extrapolation"
        
        result["success"] = True
        return result
    except:
        print("invalid input!")
        return result