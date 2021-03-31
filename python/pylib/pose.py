'''
Created 9/4/2013

Author: Walt Johnson
'''
from __future__ import print_function

import numpy as np
from numpy import sin, cos, tan, arccos, arcsin, arctan2, arctan, r_, c_, dot, pi
from tqdm import tqdm
# import pylib.plotTools as pt


def quatInit():
    q = np.zeros(4)
    q[0] = 1.0
    return q


# Quaternion Conjugate: q* = [ w, -x, -y, -z ] of quaterion q = [ w, x, y, z ]
# Rotation in opposite direction.
def quatConj(q):
    qc = np.empty_like(q)
    if len(np.shape(q)) == 1:
        qc[0] = q[0]
        qc[1:4] = -q[1:4]
    else:
        assert np.shape(q)[1] == 4, "Wrong shape of array of quaternions"
        qc[:, 0] = q[:, 0]
        qc[:, 1:4] = -q[:, 1:4]
    return qc


#  * Product of two Quaternions.  Order of q1 and q2 matters (same as applying two successive DCMs)!!!
#  * Concatenates two quaternion rotations into one.
#  * result = q1 * q2
#  * Order of rotation in rotation matrix notation: R(result) = R(q1) * R(q2)
#  * i.e. rotation by q2 followed by rotation by q1
#  * References:
#  *    http://www.mathworks.com/help/aeroblks/quaternionmultiplication.html
#  *    http://physicsforgames.blogspot.com/2010/02/quaternions.html
def mul_Quat_Quat(q1, q2):
    if len(np.shape(q1)) == 1:
        q1 = np.expand_dims(q1, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(q2)) == 1:
        q2 = np.expand_dims(q2, axis=0)
    else:
        array = 1
    n1 = np.shape(q1)[0]
    n2 = np.shape(q2)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions in arrays do not match"

    result = np.empty((max(n1, n2), 4))
    result[:, 0] = q1[:, 0]*q2[:, 0] - q1[:, 1] * \
        q2[:, 1] - q1[:, 2]*q2[:, 2] - q1[:, 3]*q2[:, 3]
    result[:, 1] = q1[:, 0]*q2[:, 1] + q1[:, 1] * \
        q2[:, 0] - q1[:, 2]*q2[:, 3] + q1[:, 3]*q2[:n2, 2]
    result[:, 2] = q1[:, 0]*q2[:, 2] + q1[:, 1] * \
        q2[:, 3] + q1[:, 2]*q2[:, 0] - q1[:, 3]*q2[:n2, 1]
    result[:, 3] = q1[:, 0]*q2[:, 3] - q1[:, 1] * \
        q2[:, 2] + q1[:, 2]*q2[:, 1] + q1[:, 3]*q2[:n2, 0]

    if array == 0:
        result = np.squeeze(result)
    return result


# * Product of two Quaternions.  Order of q1 and q2 matters (same as applying two successive DCMs)!!!
# * Combines two quaternion rotations into one rotation.
# * result = quatConj(q1) * q2
# * Reference: http://www.mathworks.com/help/aeroblks/quaternionmultiplication.html
def mul_ConjQuat_Quat(q1, q2):
    if len(np.shape(q1)) == 1:
        q1 = np.expand_dims(q1, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(q2)) == 1:
        q2 = np.expand_dims(q2, axis=0)
    else:
        array = 1
    n1 = np.shape(q1)[0]
    n2 = np.shape(q2)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions in arrays do not match"

    result = np.empty((max(n1, n2), 4))
    result[:, 0] = q1[:, 0]*q2[:, 0] + q1[:, 1] * \
        q2[:, 1] + q1[:, 2]*q2[:, 2] + q1[:, 3]*q2[:, 3]
    result[:, 1] = q1[:, 0]*q2[:, 1] - q1[:, 1] * \
        q2[:, 0] + q1[:, 2]*q2[:, 3] - q1[:, 3]*q2[:, 2]
    result[:, 2] = q1[:, 0]*q2[:, 2] - q1[:, 1] * \
        q2[:, 3] - q1[:, 2]*q2[:, 0] + q1[:, 3]*q2[:, 1]
    result[:, 3] = q1[:, 0]*q2[:, 3] + q1[:, 1] * \
        q2[:, 2] - q1[:, 2]*q2[:, 1] - q1[:, 3]*q2[:, 0]

    if array == 0:
        result = np.squeeze(result)
    return result


# * Product of two Quaternions.  Order of q1 and q2 matters (same as applying two successive DCMs)!!!
# * Combines two quaternion rotations into one rotation.
# * result = q1 * quatConj(q2)
# * Reference: http://www.mathworks.com/help/aeroblks/quaternionmultiplication.html
def mul_Quat_ConjQuat(q1, q2):
    if len(np.shape(q1)) == 1:
        q1 = np.expand_dims(q1, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(q2)) == 1:
        q2 = np.expand_dims(q2, axis=0)
    else:
        array = 1
    n1 = np.shape(q1)[0]
    n2 = np.shape(q2)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions in arrays do not match"

    result = np.empty((max(n1, n2), 4))
    result[:, 0] = q1[:, 0]*q2[:, 0] + q1[:, 1] * \
        q2[:, 1] + q1[:, 2]*q2[:, 2] + q1[:, 3]*q2[:, 3]
    result[:, 1] = -q1[:, 0]*q2[:, 1] + q1[:, 1] * \
        q2[:, 0] + q1[:, 2]*q2[:, 3] - q1[:, 3]*q2[:, 2]
    result[:, 2] = -q1[:, 0]*q2[:, 2] - q1[:, 1] * \
        q2[:, 3] + q1[:, 2]*q2[:, 0] + q1[:, 3]*q2[:, 1]
    result[:, 3] = -q1[:, 0]*q2[:, 3] + q1[:, 1] * \
        q2[:, 2] - q1[:, 2]*q2[:, 1] + q1[:, 3]*q2[:, 0]

    if array == 0:
        result = np.squeeze(result)
    return result


#  * Division of two Quaternions.  Order matters!!!
#  * result = q1 / q2.
#  * Reference: http://www.mathworks.com/help/aeroblks/quaterniondivision.html
def div_Quat_Quat(q1, q2):
    if len(np.shape(q1)) == 1:
        q1 = np.expand_dims(q1, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(q2)) == 1:
        q2 = np.expand_dims(q2, axis=0)
    else:
        array = 1
    n1 = np.shape(q1)[0]
    n2 = np.shape(q2)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions in arrays do not match"

    result = np.empty((max(n1, n2), 4))
    d = 1.0 / (q1[:, 0]*q1[:, 0] + q1[:, 1]*q1[:, 1] +
               q1[:, 2]*q1[:, 2] + q1[:, 3]*q1[:, 3])
    result[:, 0] = q1[:, 0]*q2[:, 0] + q1[:, 1] * \
        q2[:, 1] + q1[:, 2]*q2[:, 2] + q1[:, 3]*q2[:, 3]
    result[:, 1] = q1[:, 0]*q2[:, 1] - q1[:, 1] * \
        q2[:, 0] - q1[:, 2]*q2[:, 3] + q1[:, 3]*q2[:, 2]
    result[:, 2] = q1[:, 0]*q2[:, 2] + q1[:, 1] * \
        q2[:, 3] - q1[:, 2]*q2[:, 0] - q1[:, 3]*q2[:, 1]
    result[:, 3] = q1[:, 0]*q2[:, 3] - q1[:, 1] * \
        q2[:, 2] + q1[:, 2]*q2[:, 1] - q1[:, 3]*q2[:, 0]
    result = result * d
    if array == 0:
        result = np.squeeze(result)
    return result


# Quaternion rotation from vector v1 to vector v2.
# Reference:
def quat_Vec3_Vec3(v1, v2):
    #     Vector3_t w1, w2;

    # Normalize input vectors
    w1 = normalize(v1)
    w2 = normalize(v2)

    qResult = np.zeros(4)
    # q[1:3]
    qResult[1:4] = np.cross(w1, w2)

    # q[0]
    qResult[0] = np.sqrt(np.square(np.dot(w1, w1))) + np.dot(w1, w2)

    # Normalize quaternion
    qResult = qResult / np.linalg.norm(qResult)
    return qResult


# Compute norm of a single vector or each vector in an array
def norm(v, axis=None):
    return np.sqrt(np.sum(v*v, axis=axis))


# Normalize vector or each vector in an array
def normalize(v, axis=None):
    result = np.empty_like(v)
    if len(np.shape(v)) == 1:
        result = v / np.linalg.norm(v)
    else:
        vnorm = np.linalg.norm(v, axis=axis)
        vnorm = np.expand_dims(vnorm, axis=axis)
        result = v / vnorm
    return result


#  * Computationally simple means to apply quaternion rotation to a vector.
#  * Requires quaternion be normalized first.
#  * If quaternion describes current attitude, then rotation is body -> inertial frame.
#  * Equivalent to a DCM.T * vector multiply.
def quatRot(q, v):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(v)) == 1:
        v = np.expand_dims(v, axis=0)
    else:
        array = 1
    n1 = np.shape(q)[0]
    n2 = np.shape(v)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions and vectors in arrays do not match"

    result = np.empty((max(n1, n2), 3))
    t = 2.0 * np.cross(q[:, 1:4], v)
    result = v + (q[:,0] * t.T).T + np.cross(q[:,1:4], t)

    if array == 0:
        result = np.squeeze(result)
    return result


#  * Computationally simple means to apply quaternion conjugate (opposite) rotation to a vector
#  * (18 multiplies, 6 subtracts, 6 adds).  Using a DCM uses (27 multiplies, 12 adds, 6 subtracts).
#  * Requires quaternion be normalized first.
#  * If quaternion describes current attitude, then rotation is inertial -> body frame.
#  * Equivalent to a DCM * vector multiply.
def quatConjRot(q, v):
    qc = quatConj(q)
    return quatRot(qc, v)


#  Find quaternion interpolation between two quaterions.  Blend must be 0 to 1.
#  Reference:  http://physicsforgames.blogspot.com/2010/02/quaternions.html
def quatNLerp(q1, q2, blend):
    if len(np.shape(q1)) == 1:
        q1 = np.expand_dims(q1, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(q2)) == 1:
        q2 = np.expand_dims(q2, axis=0)
    else:
        array = 1
    n1 = np.shape(q1)[0]
    n2 = np.shape(q2)[0]
    assert n1 == n2 or n1 == 1 or n2 == 1, "Number of quaternions in arrays do not match"

    result = np.empty((max(n1, n2), 4))
    dot = q1[:, 0]*q2[:, 0] + q1[:, 1]*q2[:, 1] + \
        q1[:, 2]*q2[:, 2] + q1[:, 3]*q2[:, 3]
    blendI = 1.0 - blend

    ind0 = np.asarray(np.where(dot < 0.0))[0, :]
    ind1 = np.asarray(np.where(dot >= 0.0))[0, :]
    result[ind0, :] = blendI*q1[ind0, :] - blend*q2[ind0, :]
    result[ind1, :] = blendI*q1[ind1, :] + blend*q2[ind1, :]

    result = normalize(result, axis=1)

    if array == 0:
        result = np.squeeze(result)
    return result


#  * This will convert from quaternions to euler angles.  Ensure quaternion is previously normalized.
#  * q(4,1) -> euler[phi;theta;psi] (rad)
#  *
#  * Reference: http://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
def quat2euler(q):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1
    theta = np.empty(shape=(np.shape(q)[0], 3))
    theta[:, 0] = np.arctan2(2.0 * (q[:, 0]*q[:, 1] + q[:, 2]*q[:, 3]),
                             1.0 - 2.0 * (q[:, 1]*q[:, 1] + q[:, 2]*q[:, 2]))
    theta[:, 1] = np.arcsin(2.0 * (q[:, 0]*q[:, 2] - q[:, 3]*q[:, 1]))
    theta[:, 2] = np.arctan2(2.0 * (q[:, 0]*q[:, 3] + q[:, 1]*q[:, 2]),
                             1.0 - 2.0 * (q[:, 2]*q[:, 2] + q[:, 3]*q[:, 3]))

    if array == 0:
        theta = np.squeeze(theta)
    return theta

#  * This will convert from euler angles to quaternion vector
#  * [phi, theta, psi] -> q(4,1)
#  * euler angles in radians


def euler2quat(euler):
    if len(np.shape(euler)) == 1:
        euler = np.expand_dims(euler, axis=0)
        array = 0
    else:
        array = 1
    q = np.zeros((np.shape(euler)[0], 4))

    hphi = euler[:, 0] * 0.5
    hthe = euler[:, 1] * 0.5
    hpsi = euler[:, 2] * 0.5

    shphi = np.sin(hphi)
    chphi = np.cos(hphi)
    shthe = np.sin(hthe)
    chthe = np.cos(hthe)
    shpsi = np.sin(hpsi)
    chpsi = np.cos(hpsi)

    q[:, 0] = chphi * chthe * chpsi + shphi * shthe * shpsi
    q[:, 1] = shphi * chthe * chpsi - chphi * shthe * shpsi
    q[:, 2] = chphi * shthe * chpsi + shphi * chthe * shpsi
    q[:, 3] = chphi * chthe * shpsi - shphi * shthe * chpsi

    if array == 0:
        q = np.squeeze(q)
    return q

#  * NE to heading/body frame
#  * This will construct a direction cosine matrix from
#  * the psi angle - rotates from NE to body frame
#  * body = tBL(2,2)*NE


def psiDCM(psi):
    cpsi = cos(psi)  # cos(psi)
    spsi = sin(psi)  # sin(psi)

    DCM = r_[
        c_[cpsi, spsi],
        c_[-spsi, cpsi],
    ]

    return DCM


# * This will extract the psi euler angle from a direction cosine matrix in the
# * standard rotation sequence, for either a 2x2 or 3x3 DCM matrix.
# * [phi][theta][psi] from reference to body frame
# *
# * body = tBL(2,2)*NE
# * body = tBL(3,3)*NED
# *
# * reference: http://en.wikipedia.org/wiki/Rotation_representation_%28mathematics%29
def DCMpsi(A):
    psi = arctan2(A[0, 1], A[0, 0])
    return psi


#  * Reference to body frame - In the 1-2-3 (roll, pitch, yaw) order
#  * This will construct a direction cosine matrix from
#  * euler angles in the standard rotation sequence
#  * [phi][theta][psi] from reference to body frame
#  *
#  * body = tBL(3,3)*NED
#  *
#  * reference: http://en.wikipedia.org/wiki/Rotation_representation_%28mathematics%29
def eulerDCM(euler):
    if len(np.shape(euler)) == 1:
        euler = np.expand_dims(euler, axis=0)
        array = 0
    else:
        array = 1

    DCM = np.empty((np.shape(euler)[0], 3, 3))

    cphi = cos(euler[:, 0])  # cos(phi)
    cthe = cos(euler[:, 1])  # cos(theta)
    cpsi = cos(euler[:, 2])  # cos(psi)

    sphi = sin(euler[:, 0])  # sin(phi)
    sthe = sin(euler[:, 1])  # sin(theta)
    spsi = sin(euler[:, 2])  # sin(psi)

    DCM[:, 0, 0] = cthe * cpsi
    DCM[:, 0, 1] = cthe * spsi
    DCM[:, 0, 2] = -sthe
    DCM[:, 1, 0] = -cphi * spsi + sphi * sthe * cpsi
    DCM[:, 1, 1] = cphi * cpsi + sphi * sthe * spsi
    DCM[:, 1, 2] = sphi * cthe
    DCM[:, 2, 0] = sphi * spsi + cphi * sthe * cpsi
    DCM[:, 2, 1] = -sphi * cpsi + cphi * sthe * spsi
    DCM[:, 2, 2] = cphi * cthe

    if array == 0:
        DCM = np.squeeze(DCM)
    return DCM


#  * This will extract euler angles from a direction cosine matrix in the
#  * standard rotation sequence.
#  * [phi][theta][psi] from reference to body frame
#  *
#  * body = tBL(3,3)*NED
#  *
#  * reference: http://en.wikipedia.org/wiki/Rotation_representation_%28mathematics%29
def DCMeuler(mat):
    if len(np.shape(mat)) == 2:
        mat = np.expand_dims(mat, axis=0)
        array = 0
    else:
        array = 1

    eul = np.empty(shape=(np.shape(mat)[0], 3))

    eul[:, 0] = arctan2(mat[:, 1, 2], mat[:, 2, 2])
    eul[:, 1] = arcsin(-mat[:, 0, 2])
    eul[:, 2] = arctan2(mat[:, 0, 1], mat[:, 0, 0])

    if array == 0:
        eul = np.squeeze(eul)
    return eul


def DCMeulerToPsi(A, phi, the):
    psi = arctan2(A[0, 1]/cos(the), A[0, 0]/cos(the))
    return r_[phi, the, psi]


# /*
#  * This will construct a direction cosine matrix from
#  * quaternions in the standard rotation sequence
#  * [phi][theta][psi] from reference to body frame
#  *
#  * body = tBL(3,3)*NED
#  * q(4,1)
#  *
#  * Reference: http://en.wikipedia.org/wiki/Rotation_representation_%28mathematics%29
#  */
def quatDCM(q):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1

    DCM = np.empty(shape=(np.shape(q)[0], 3, 3))

    DCM[:, 0, 0] = 1.0 - 2.0 * (q[:, 2]**2 + q[:, 3]**2)
    DCM[:, 0, 1] = 2.0 * (q[:, 1]*q[:, 2] + q[:, 0]*q[:, 3])
    DCM[:, 0, 2] = 2.0 * (q[:, 1]*q[:, 3] - q[:, 0]*q[:, 2])
    DCM[:, 1, 0] = 2.0 * (q[:, 1]*q[:, 2] - q[:, 0]*q[:, 3])
    DCM[:, 1, 1] = 1.0 - 2.0 * (q[:, 1]**2 + q[:, 3]**2)
    DCM[:, 1, 2] = 2.0 * (q[:, 2]*q[:, 3] + q[:, 0]*q[:, 1])
    DCM[:, 2, 0] = 2.0 * (q[:, 1]*q[:, 3] + q[:, 0]*q[:, 2])
    DCM[:, 2, 1] = 2.0 * (q[:, 2]*q[:, 3] - q[:, 0]*q[:, 1])
    DCM[:, 2, 2] = 1.0 - 2.0 * (q[:, 1]**2 + q[:, 2]**2)

    if array == 0:
        DCM = np.squeeze(DCM)
    return DCM


#  * This will construct quaternions from a direction cosine
#  * matrix in the standard rotation sequence.
#  * [phi][theta][psi] from reference to body frame
#  *
#  * body = tBL(3,3)*NED
#  * q(4,1)
#  *
#  * Reference: http://en.wikipedia.org/wiki/Rotation_representation_%28mathematics%29
def DCMquat(mat):
    if len(np.shape(mat)) == 2:
        mat = np.expand_dims(mat, axis=0)
        array = 0
    else:
        array = 1

    q = np.empty(shape=(np.shape(mat)[0], 4))
    q_sq4 = np.empty_like(q)

    q_sq4[:, 0] = 1 + mat[:, 0, 0] + mat[:, 1, 1] + mat[:, 2, 2]
    q_sq4[:, 1] = 1 + mat[:, 0, 0] - mat[:, 1, 1] - mat[:, 2, 2]
    q_sq4[:, 2] = 1 - mat[:, 0, 0] + mat[:, 1, 1] - mat[:, 2, 2]
    q_sq4[:, 3] = 1 - mat[:, 0, 0] - mat[:, 1, 1] + mat[:, 2, 2]

    for i in range(0, np.shape(mat)[0]):
        ind = np.argmax(q_sq4[i, :])
        q[i, ind] = 0.5 * np.sqrt(q_sq4[i, ind])
        d = 0.25 / q[i, ind]
        if ind == 0:
            q[i, 1] = d * (mat[i, 1, 2] - mat[i, 2, 1])
            q[i, 2] = d * (mat[i, 2, 0] - mat[i, 0, 2])
            q[i, 3] = d * (mat[i, 0, 1] - mat[i, 1, 0])
        elif ind == 1:
            q[i, 0] = d * (mat[i, 1, 2] - mat[i, 2, 1])
            q[i, 2] = d * (mat[i, 1, 0] + mat[i, 0, 1])
            q[i, 3] = d * (mat[i, 0, 2] + mat[i, 2, 0])
        elif ind == 2:
            q[i, 0] = d * (mat[i, 2, 0] - mat[i, 0, 2])
            q[i, 1] = d * (mat[i, 1, 0] + mat[i, 0, 1])
            q[i, 3] = d * (mat[i, 2, 1] + mat[i, 1, 2])
        else:
            q[i, 0] = d * (mat[i, 0, 1] - mat[i, 1, 0])
            q[i, 1] = d * (mat[i, 0, 2] + mat[i, 2, 0])
            q[i, 2] = d * (mat[i, 2, 1] + mat[i, 1, 2])

    ind = q[:, 0] < 0
    q[ind, :] = -q[ind, :]

    if array == 0:
        q = np.squeeze(q)
    return q


#  * This will construct the cross-product matrix Wx(3,3)
#  * such that cross(x, y) = Wx * y
#  * p, q, r (rad/sec)
def eulerWx(x):
    if len(np.shape(x)) == 1:
        x = np.expand_dims(x, axis=0)
        array = 0
    else:
        array = 1

    mat = np.empty(shape=(np.shape(x)[0], 3, 3))

    # Row 1
    mat[:, 0, 0] = 0.0
    mat[:, 0, 1] = -x[:, 2]
    mat[:, 0, 2] = x[:, 1]
    # Row 2
    mat[:, 1, 0] = x[:, 2]
    mat[:, 1, 1] = 0.0
    mat[:, 1, 2] = -x[:, 0]
    # Row 3
    mat[:, 2, 0] = -x[:, 1]
    mat[:, 2, 1] = x[:, 0]
    mat[:, 2, 2] = 0.0

    if array == 0:
        mat = np.squeeze(mat)
    return mat


#  * This will construct the quaternion omega matrix
#  * W(4,4)
#  * p, q, r (rad/sec)
def quatW(omega):
    if len(np.shape(omega)) == 1:
        omega = np.expand_dims(omega, axis=0)
        array = 0
    else:
        array = 1

    mat = np.empty(shape=(np.shape(omega)[0], 4, 4))
    p = omega[:, 0] * 0.5
    q = omega[:, 1] * 0.5
    r = omega[:, 2] * 0.5

    # Row 1
    mat[:, 0, 0] = 0.0
    mat[:, 0, 1] = -p
    mat[:, 0, 2] = -q
    mat[:, 0, 3] = -r
    # Row 2
    mat[:, 1, 0] = p
    mat[:, 1, 1] = 0.0
    mat[:, 1, 2] = r
    mat[:, 1, 3] = -q
    # Row 3
    mat[:, 2, 0] = q
    mat[:, 2, 1] = -r
    mat[:, 2, 2] = 0.0
    mat[:, 2, 3] = p
    # Row 4
    mat[:, 3, 0] = r
    mat[:, 3, 1] = q
    mat[:, 3, 2] = -p
    mat[:, 3, 3] = 0.0

    if array == 0:
        mat = np.squeeze(mat)
    return mat


# * Convert quaternion to rotation axis
def quatRotAxis(q):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1

    axis = normalize(q[:, 1:4], axis=1)

    if array == 0:
        axis = np.squeeze(axis)
    return axis


# * Convert quaternion to rotation vector
def quatRotVec(q):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1
    rv = np.zeros(shape=(np.shape(q)[0], 3))

    theta = np.arccos(q[:, 0]) * 2.0
    sin_half_theta = np.sqrt(1.0 - q[:, 0] * q[:, 0])
    ind1 = np.asarray(np.where(np.fabs(theta) > 1e-6))[0, :]
    ind0 = np.asarray(np.where(np.fabs(theta) <= 1e-6))[0, :]
    rv[ind1, :] = q[ind1, 1:4] * (theta[ind1] / sin_half_theta[ind1])[:, None]
    rv[ind0, :] = q[ind0, 1:4] * 2.0

    if array == 0:
        rv = np.squeeze(rv)
    return rv


#  *  Compute the derivative of the Euler_t angle psi with respect
#  * to the quaternion Q.  The result is a row vector
#  *
#  * d(psi)/d(q0)
#  * d(psi)/d(q1)
#  * d(psi)/d(q2)
#  * d(psi)/d(q3)
def dpsi_dq(q):
    if len(np.shape(q)) == 1:
        q = np.expand_dims(q, axis=0)
        array = 0
    else:
        array = 1
    dq = np.zeros(shape=(np.shape(q)[0], 4))

    t1 = 1.0 - 2.0 * (q[:, 2]*q[:, 2] + q[:, 3]*q[:, 2])
    t2 = 2.0 * (q[:, 1]*q[:, 2] + q[:, 0]*q[:, 3])
    err = 2.0 / (t1*t1 + t2*t2)

    dq[:, 0] = err * (q[:, 3]*t1)
    dq[:, 1] = err * (q[:, 2]*t1)
    dq[:, 2] = err * (q[:, 1]*t1 + 2.0 * q[:, 2]*t2)
    dq[:, 3] = err * (q[:, 0]*t1 + 2.0 * q[:, 3]*t2)

    if array == 0:
        dq = np.squeeze(dq)

    return dq


#  Find Earth Centered Earth Fixed coordinate from LLA
#
#  lla[0] = latitude (decimal degree)
#  lla[1] = longitude (decimal degree)
#  lla[2] = msl altitude (m)
def lla2ecef(lla_deg):
    # Earth first eccentricity: e = sqrt((R^2-b^2)/R^2);
    e = 0.08181919084262
    # double R, b, Rn, Smu, Cmu, Sl, Cl;

    # Earth equatorial and polar radii (from flattening, f = 1/298.257223563;
    R = 6378137.0         # m
    # Earth polar radius b = R * (1-f)
    b = 6356752.31424518

    if len(np.shape(lla_deg)) == 1:
        lla_deg = np.expand_dims(lla_deg, axis=0)
        array = 0
    else:
        array = 1
    LLA = np.copy(lla_deg)
    LLA[:, 0:2] = np.radians(LLA[:, 0:2])

    Smu = sin(LLA[:, 0])
    Cmu = cos(LLA[:, 0])
    Sl = sin(LLA[:, 1])
    Cl = cos(LLA[:, 1])

    # Radius of curvature at a surface point:
    Rn = R / np.sqrt(1 - e**2 * Smu**2)

    Pe = np.empty(np.shape(LLA))
    Pe[:, 0] = (Rn + LLA[:, 2]) * Cmu * Cl
    Pe[:, 1] = (Rn + LLA[:, 2]) * Cmu * Sl
    Pe[:, 2] = (Rn * (b/R)**2 + LLA[:, 2]) * Smu

    if array == 0:
        Pe = np.squeeze(Pe)
    return Pe


# * Coordinate transformation from ECEF coordinates to latitude/longitude/altitude (deg,deg,m)
def ecef2lla(Pe, Niter=5):

    # Earth equatorial radius
    R = 6378137.0
    # Earth polar radius b = R * (1-f)
    b = 6356752.31424518
    # Earth first eccentricity
    e = 0.08181919084262    # e = sqrt((R^2-b^2)/R^2);
    e2 = e**2
    # Earth flattening
    f = 0.0033528106647474805

    if len(np.shape(Pe)) == 1:
        Pe = np.expand_dims(Pe, axis=0)
        array = 0
    else:
        array = 1
    LLA = np.empty(np.shape(Pe))

    # Longitude
    LLA[:, 1] = arctan2(Pe[:, 1], Pe[:, 0])

    # Latitude computation using Bowring's method
    s = np.sqrt(Pe[:, 0]**2 + Pe[:, 1]**2)
    beta = arctan2(Pe[:, 2], (1.0-f)*s)  # reduced latitude, initial guess

    B = e2 * R
    A = e2 * R / (1.0 - f)
    for i in range(0, Niter):
        # iterative latitude computation
        LLA[:, 0] = arctan2(Pe[:, 2]+A*sin(beta)**3, s-B*cos(beta)**3)
        beta = arctan((1-f) * tan(LLA[:, 0]))

    # Radius of curvature in the vertical prime
    sin_lat = sin(LLA[:, 0])
    Rn = R / np.sqrt(1.0 - e2 * sin_lat**2)

    # Altitude above planetary ellipsoid
    LLA[:, 2] = s * cos(LLA[:, 0]) + (Pe[:, 2] + e2 *
                                      Rn * sin_lat) * sin_lat - Rn

    # Convert to degrees
    LLA[:, 0:2] = np.degrees(LLA[:, 0:2])

    if array == 0:
        LLA = np.squeeze(LLA)
    return LLA


#  Find NED (north, east, down) from lla_ref_deg to lla_deg
#
#  lla_ref_deg[0] = reference latitude (decimal degree)
#  lla_ref_deg[1] = reference longitude (decimal degree)
#  lla_ref_deg[2] = reference msl altitude (m)
#  lla_deg[0] = latitude (decimal degree)
#  lla_deg[1] = longitude (decimal degree)
#  lla_deg[2] = msl altitude (m)
def lla2ned(lla_ref_deg, lla_deg):
    # Earth equatorial radius
    R = 6378137.0
    # Earth first eccentricity
    e = 0.08181919084262    # e = sqrt((R^2-b^2)/R^2);
    e2 = e**2

    if len(np.shape(lla_deg)) == 1:
        lla_deg = np.expand_dims(lla_deg, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(lla_ref_deg)) == 1:
        lla_ref_deg = np.expand_dims(lla_ref_deg, axis=0)

    lla = np.copy(lla_deg)
    lla_ref = np.copy(lla_ref_deg)
    # Convert deg to rad
    lla[:, 0:2] = np.radians(lla[:, 0:2])
    lla_ref[:, 0:2] = np.radians(lla_ref_deg[:, 0:2])

    Pn = np.empty(np.shape(lla))

    deltaLLA = lla - lla_ref
    # radius of curvature in the prime vertical:
    sin_lat_ref = sin(lla_ref[:, 0])
    Rn = R / np.sqrt(1.0 - e2 * sin_lat_ref**2)
    # radius of curvature in the meridian
    Rm = Rn * (1.0 - e2) / (1.0 - e2 * sin_lat_ref**2)
    Pn[:, 0] = deltaLLA[:, 0] * Rm
    Pn[:, 1] = deltaLLA[:, 1] * Rn * cos(lla_ref[:, 0])
    Pn[:, 2] = -deltaLLA[:, 2]

    if array == 0:
        Pn = np.squeeze(Pn)
    return Pn


#  Find LLA (degrees, m) from NED (north, east, down) from lla_ref_deg to lla_deg
#
#  lla_ref_deg[0] = reference latitude (decimal degree)
#  lla_ref_deg[1] = reference longitude (decimal degree)
#  lla_ref_deg[2] = reference msl altitude (m)
#  Pn[0] = position North (m)
#  Pn[1] = position East (m)
#  Pn[2] = position Down (m)
def ned2lla(lla_ref_deg, Pn):
    # Earth equatorial radius
    R = 6378137.0
    # Earth first eccentricity
    e = 0.08181919084262    # e = sqrt((R^2-b^2)/R^2);
    e2 = e**2

    if len(np.shape(Pn)) == 1:
        Pn = np.expand_dims(Pn, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(lla_ref_deg)) == 1:
        lla_ref_deg = np.expand_dims(lla_ref_deg, axis=0)

    lla_ref = np.copy(lla_ref_deg)
    # Convert deg to rad
    lla_ref[:, 0:2] = np.radians(lla_ref_deg[:, 0:2])

    lla = np.empty(np.shape(Pn))

    # radius of curvature in the prime vertical:
    sin_lat_ref = sin(lla_ref[:, 0])
    Rn = R / np.sqrt(1.0 - e2 * sin_lat_ref**2)
    # radius of curvature in the meridian
    Rm = Rn * (1.0 - e2) / (1.0 - e2 * sin_lat_ref**2)

    lla[:, 0] = lla_ref[:, 0] + Pn[:, 0] / Rm
    lla[:, 1] = lla_ref[:, 1] + Pn[:, 1] / (Rn * cos(lla_ref[:, 0]))
    lla[:, 2] = lla_ref[:, 2] - Pn[:, 2]

    # Convert lat/lon to degrees
    lla[:, 0:2] = np.degrees(lla[:, 0:2])
    if array == 0:
        lla = np.squeeze(lla)
    return lla


#  Find Delta LLA of NED (north, east, down) from LLAref
#
#  lla_ref_deg[0] = reference latitude (decimal degree)
#  lla_ref_deg[1] = reference longitude (decimal degree)
#  lla_ref_deg[2] = reference msl altitude (m)
#  Pn[0] = position North (m)
#  Pn[1] = position East (m)
#  Pn[2] = position Down (m)
def ned2DeltaLla(lla_ref_deg, Pn):
    # Earth equatorial radius
    R = 6378137.0
    # Earth first eccentricity
    e = 0.08181919084262    # e = sqrt((R^2-b^2)/R^2);
    e2 = e**2

    if len(np.shape(Pn)) == 1:
        Pn = np.expand_dims(Pn, axis=0)
        array = 0
    else:
        array = 1
    if len(np.shape(lla_ref_deg)) == 1:
        lla_ref_deg = np.expand_dims(lla_ref_deg, axis=0)

    lla_ref = np.copy(lla_ref_deg)
    # Convert deg to rad
    lla_ref[:, 0:2] = np.radians(lla_ref_deg[:, 0:2])

    deltaLLA = np.empty(np.shape(Pn))

    # radius of curvature in the prime vertical:
    sin_lat_ref = sin(lla_ref[:, 0])
    Rn = R / np.sqrt(1.0 - e2 * sin_lat_ref**2)
    # radius of curvature in the meridian
    Rm = Rn * (1.0 - e2) / (1.0 - e2 * sin_lat_ref**2)

    deltaLLA[:, 0] = Pn[:, 0] / Rm
    deltaLLA[:, 1] = Pn[:, 1] / (Rn * cos(lla_ref[:, 0]))
    deltaLLA[:, 2] = -Pn[:, 2]

    # Convert delta lat/lon to degrees
    deltaLLA[:, 0:2] = np.degrees(deltaLLA[:, 0:2])
    if array == 0:
        deltaLLA = np.squeeze(deltaLLA)
    return deltaLLA


# Compute rotation matrix from NED to ECEF at given latitude/longitude
def rotmat_ned2ecef(latlon):
    if len(np.shape(latlon)) == 1:
        latlon = np.expand_dims(latlon, axis=0)
        array = 0
    else:
        array = 1

    Smu = sin(latlon[:, 0])
    Cmu = cos(latlon[:, 0])
    Sl = sin(latlon[:, 1])
    Cl = cos(latlon[:, 1])

    R = np.empty(shape=(np.shape(latlon)[0], 3, 3))
    R[:, 0, 0] = -Smu * Cl
    R[:, 0, 1] = -Sl
    R[:, 0, 2] = -Cmu * Cl
    R[:, 1, 0] = -Smu * Sl
    R[:, 1, 1] = Cl
    R[:, 1, 2] = -Cmu * Sl
    R[:, 2, 0] = Cmu
    R[:, 2, 1] = 0.0
    R[:, 2, 2] = -Smu

    if array == 0:
        R = np.squeeze(R)
    return R


# Compute rotation matrix from ECEF to NED at given latitude/longitude
def rotmat_ecef2ned(latlon):
    if len(np.shape(latlon)) == 1:
        latlon = np.expand_dims(latlon, axis=0)
        array = 0
    else:
        array = 1

    Smu = sin(latlon[:, 0])
    Cmu = cos(latlon[:, 0])
    Sl = sin(latlon[:, 1])
    Cl = cos(latlon[:, 1])

    R = np.empty(shape=(np.shape(latlon)[0], 3, 3))
    R[:, 0, 0] = -Smu * Cl
    R[:, 0, 1] = -Smu * Sl
    R[:, 0, 2] = Cmu
    R[:, 1, 0] = -Sl
    R[:, 1, 1] = Cl
    R[:, 1, 2] = 0.0
    R[:, 2, 0] = -Cmu * Cl
    R[:, 2, 1] = -Cmu * Sl
    R[:, 2, 2] = -Smu

    if array == 0:
        R = np.squeeze(R)
    return R


# Convert body attitude in Euler angles relative to ENU frame
# to body attitude in Euler angles relative to NED frame
def enu2nedEuler(eul_e2b):
    q_n2e = euler2quat(np.array([pi, 0, pi/2]))
    q_e2b = euler2quat(eul_e2b)
    q_n2b = mul_Quat_Quat(q_e2b, q_n2e)
    eul_n2b = quat2euler(q_n2b)
    return eul_n2b


#  Compute body atitude as Euler angles (pitch and heading with zero roll)
#  given body X unit vector NED cordinates
#  TODO: this function needs a better name
def nedEuler(ned):
    if len(np.shape(ned)) == 1:
        ned = np.expand_dims(ned, axis=0)
        array = 0
    else:
        array = 1

    euler = np.empty(shape=(np.shape(ned)[0], 3))
    euler[:, 2] = arctan2(ned[:, 1], ned[:, 0])
    euler[:, 1] = arctan2(-ned[:, 2], np.sqrt(ned[:, 0]**2 + ned[:, 1]**2))
    euler[:, 0] = 0

    if array == 0:
        euler = np.squeeze(euler)
    return euler


#  Compute coordinates of a body X unit vector in NED
#  given body attitude in NED as Euler angles
#  TODO: this function needs a better name
def eulerNed(euler):
    if len(np.shape(euler)) == 1:
        euler = np.expand_dims(euler, axis=0)
        array = 0
    else:
        array = 1
    e0 = np.array([1., 0., 0.])
    q  = euler2quat(euler)
    e0n = quatRot(q, e0)
    if array == 0:
        e0n = np.squeeze(e0n)
    return e0n


# Rotate theta eulers from body to inertial frame by ins eulers, in order: phi, theta, psi
def eulerRotateBodyToInertial2(e, rot):
    eResult = np.zeros(np.shape(e))

    Ai = eulerDCM(rot)                  # use estimate

    for i in range(0, np.shape(eResult)[0]):
        # Create DCMs (rotation matrices)
        At = eulerDCM(e[i, :])

        # Apply INS Rotation to Desired Target vector
        AiAt = dot(Ai, At)               # Apply rotation
        eResult[i, :] = DCMeuler(AiAt)            # Pull out new eulers

    return eResult

# Rotate theta eulers from inertial to body frame by ins eulers, in order: psi, theta, phi


def eulerRotateInertialToBody2(e, rot):
    eResult = np.zeros(np.shape(e))

    Ai = eulerDCM(rot)                  # use estimate

    for i in range(0, np.shape(eResult)[0]):
        # Create DCMs (rotation matrices)
        At = eulerDCM(e[i, :])

        # Apply INS Rotation to Desired Target vector
        AiAt = dot(Ai.T, At)             # Apply rotation
        eResult[i, :] = DCMeuler(AiAt)            # Pull out new eulers

    return eResult

# Rotate vector from inertial to body frame by euler angles, in order: psi, theta, phi


def vectorRotateInertialToBody(vIn, eRot):
    vResult = np.zeros(np.shape(vIn))

    for i in range(0, np.shape(vResult)[0]):
        # Create DCM (rotation matrix)
        DCM = eulerDCM(eRot[i, :])
        # Apply rotation to vector
        vResult[i, :] = np.dot(DCM, vIn[i, :])

    return vResult

# Rotate vector from body to inertial frame by euler angles, in order: phi, theta, psi


def vectorRotateBodyToInertial(vIn, eRot):
    vResult = np.zeros(np.shape(vIn))

    for i in range(0, np.shape(vResult)[0]):
        # Create DCM (rotation matrix)
        DCM = eulerDCM(eRot[i, :])
        # Apply rotation to vector
        vResult[i, :] = np.dot(DCM.T, vIn[i, :])

    return vResult

# Rotate vector from inertial to body frame by euler angles, in order: psi, theta, phi


def vectorRotateInertialToBody2(vIn, eRot):
    vResult = np.zeros(np.shape(vIn))

    # Create DCM (rotation matrix)
    DCM = eulerDCM(eRot)

    for i in range(0, np.shape(vResult)[0]):
        # Apply rotation to vector
        vResult[i, :] = np.dot(DCM, vIn[i, :])

    return vResult

# Rotate vector from body to inertial frame by euler angles, in order: phi, theta, psi


def vectorRotateBodyToInertial2(vIn, eRot):
    vResult = np.zeros(np.shape(vIn))

    # Create DCM (rotation matrix)
    DCM = eulerDCM(eRot)

    for i in range(0, np.shape(vResult)[0]):
        # Apply rotation to vector
        vResult[i, :] = np.dot(DCM.T, vIn[i, :])

    return vResult


# Find euler angles of a vector (no roll)
def vectorEuler(v):
    psi = np.arctan2(v[1], v[0])
    dcm = psiDCM(psi)
    v2 = np.dot(dcm, v[0:2])
    theta = np.arctan2(-v[2], v2[0])
    result = r_[0., theta, psi]
#     print("v:", v, " v2:", v2, " e:", result * 180/pi)
    return result


def vectorQuat(v):
    return euler2quat(vectorEuler(v))


def unwrapAngle(angle):

    twoPi = pi*2

    for i in range(0, np.shape(angle)[0]):
        while angle[i] < -pi:
            angle[i] += twoPi
        while angle[i] > pi:
            angle[i] -= twoPi

    return angle


# Non-accelerated gravity used to determine attitude
def accellToEuler(acc):
    euler = np.zeros(np.shape(acc))

    euler[:, 0] = np.arctan2(-acc[:, 1], -acc[:, 2])
    euler[:, 1] = np.arctan2(acc[:, 0], np.sqrt(
        acc[:, 1]*acc[:, 1] + acc[:, 2]*acc[:, 2]))
    return euler


def acc2AttAndBias(acc):
    att = np.zeros(np.shape(acc))
    bias = np.zeros(np.shape(acc))

#     pe = pt.cPlot()

    for i in range(0, 4):
        att = accellToEuler(acc-bias)

        gIF = np.r_[0, 0, -9.80665]
        for i in range(0, np.shape(bias)[0]):
            # Create DCM (rotation matrix)
            DCM = eulerDCM(att[i, :])
            # Apply rotation to vector: inertial -> body
            g = np.dot(DCM, gIF)
            bias[i, :] = acc[i, :] - g

#         pe.plot3Axes(1, range(0,np.shape(bias)[0]), bias, 'Bias', 'm/s^2')

    return [att, bias]

# THIS FUNCTION SHALL BE DELETED
# qmat_matrix = np.array([[[1.0, 0, 0, 0],
#                          [0, -1.0, 0, 0],
#                          [0, 0, -1.0, 0],
#                          [0, 0, 0, -1.0]],
#                         [[0, 1.0, 0, 0],
#                          [1.0, 0, 0, 0],
#                          [0, 0, 0, 1.0],
#                          [0, 0, -1.0, 0]],
#                         [[0, 0, 1.0, 0],
#                          [0, 0, 0, -1.0],
#                          [1.0, 0, 0, 0],
#                          [0, 1.0, 0, 0]],
#                         [[0, 0, 0, 1.0],
#                          [0, 0, 1.0, 0],
#                          [0, -1.0, 0, 0],
#                          [1.0, 0, 0, 0]]])
# def qmult(q1, q2):
#     if q1.shape[0] == 1 and q2.shape[0] == 1:
#         dots = np.empty_like(q2)
#         for i in range(q2.shape[0]):
#             dots[i, :] = qmat_matrix.dot(q2.T).squeeze().dot(q1.T).T
#     elif q1.shape[0] == 1 and q2.shape[0] != 1:
#         dots = np.empty_like(q2)
#         for i in range(q2.shape[0]):
#             dots[i, :] = qmat_matrix.dot(q2[i, :].T).squeeze().dot(q1.T).T
#     elif q1.shape[0] != 1 and q2.shape[0] == 1:
#         dots = np.empty_like(q2)
#         for i in range(q2.shape[0]):
#             dots[i, :] = qmat_matrix.dot(q2.T).squeeze().dot(q1[i,:].T).T
#     elif q1.shape[0] == q2.shape[0]:
#         dots = np.empty_like(q2)
#         for i in range(q2.shape[0]):
#             dots[i, :] = qmat_matrix.dot(q2[i,:].T).squeeze().dot(q1[i, :].T).T
#     else:
#         raise Exception("Incompatible quaternion arrays -- cannot multiply")

#     # print qmat_matrix.dot(q2.T).squeeze()
#     # print np.tensordot(qmat_matrix.T, q2, axes=[0,1]).T.squeeze()
#     # dots = np.empty((2,4,4))
#     # for i in range(q1.shape[0]):
#     #      dots[i,:] = qmat_matrix.dot(q2[i,:].T)
#     # tensordots = np.tensordot(qmat_matrix.T, q2, axes=[0,1]).T
#     # dots = np.empty_like(q1)
#     # for i in range(q1.shape[0]):
#     #      dots[i,:] = qmat_matrix.dot(q2[i,:].T).squeeze().dot(q1[i,:].T).T
#     # tensordots = np.tensordot(q1, np.tensordot(qmat_matrix.T, q2, axes=[0,1]), axes=1).T
#     # print "dots = ", dots, "\ntensordots = ", tensordots
#     # print "diff = ", dots - tensordots

#     # return np.tensordot(q1, np.tensordot(q2.T, qmat_matrix.T, axes=[0,1]).T, axes=1)[0].T
#     return dots


def qlog(q):
    q *= np.sign(q[:, 0])[:, None]
    norm_v = norm(q[:, 1:], axis=1)
    out = np.empty((len(q), 3))
    idx = norm_v > 1e-4
    out[~idx] = 2.0 * np.sign(q[~idx, 0, None]) * q[~idx, 1:]
    out[idx] = (2.0 * np.arctan2(norm_v[idx, None], q[idx, 0, None])
                ) * q[idx, 1:]/norm_v[idx, None]
    return out


def qexp(v):
    out = np.empty((len(v), 4))
    norm_v = norm(v, axis=1)
    idx = norm_v > 1e-4
    out[~idx, 0] = 1
    out[~idx, 1:] = v[~idx, :]
    out[idx] = np.cos(norm_v[idx, None]/2.0)
    out[idx, 1:] = np.sin(norm_v[idx, None]/2.0) * v[idx, :]/norm_v[idx, None]
    return out

# Attitude quaternion resulting from q1 followed by rotation due to rotation vector v


def qboxplus(q, v):
    return mul_Quat_Quat(qexp(v), q)

# Rotation from attitude q1 to q2 in terms of rotation vector


def qboxminus(q1, q2):
    return qlog(mul_Quat_Quat(q1, quatConj(q2)))

# Implementation of "Mean of Sigma Points" from Integrating Generic Sensor Fusion Algorithms with
# Sound State Representations through Encapsulation of Manifolds by Hertzberg et. al.
# https://arxiv.org/pdf/1107.1119.pdf p.13


def meanOfQuat(q):
    n = float(q.shape[0])
    mu = q[None, 0, :]
    prev_mu = None
    iter = 0
    while prev_mu is None or norm(qboxminus(mu, prev_mu)) > 1e-3:
        iter += 1
        prev_mu = mu
        mu = qboxplus(mu, np.sum(qboxminus(q, mu), axis=0)[None, :]/n)
    assert np.abs(1.0 - norm(mu)) <= 1e03
    return mu


def meanOfQuatArray(q):
    assert q.shape[2] == 4
    mu = np.empty((q.shape[0], 4))
    for i in tqdm(range(q.shape[0])):
        mu[None, i, :] = meanOfQuat(q[i, :, :])
    return mu


# def salemUtLla():
#     return np.r_[ 40.0557114, -111.6585476, 1426.77 ]    # // (deg,deg,m) Lat,Lon,Height above sea level (not HAE, height above ellipsoid)
#
# def salemUtMagDecInc():
#     return np.r_[ 0.20303997, 1.141736219 ]    # (rad) Declination: 11.6333333 deg or 11 deg 38', Inclination: -65.4166667 deg or 65 deg 25'

if __name__ == '__main__':
    q = np.random.random((5000, 4))
    q = normalize(q, axis=1)
    y = np.random.random((5000, 3))

    q1 = q[0:2, :]
    q2 = q[2:4, :]
    q3 = mul_Quat_Quat(q2, q1)
    q0 = q[0, :]

    qq = quatNLerp(q1, q2, 0.5)

    # Test quat-to-DCM conversions
    R = quatDCM(q1)
    quat = DCMquat(R)
    assert np.sqrt(np.sum(np.square(q1 - quat))) < 1e-8

    # Test cross-product matrix,
    # see https://ajcr.net/Basic-guide-to-einsum/ for einsum() usage
    u = np.cross(y[0:2, :], y[1:3, :])
    # v = np.einsum('...ij,...j', eulerWx(y[0:2,:]), y[1:3,:])
    v = np.einsum('ijk,ik->ij', eulerWx(y[0:2, :]), y[1:3, :])
    assert np.sqrt(np.sum(np.square(u - v))) < 1e-8

    # Test quaternion to rotation vector conversion
    a = quatRotAxis(q[0:5, :])
    rv = quatRotVec(q[0:5, :])

    # Test quat-to-Euler conversions
    print("q =", q0)
    eul = quat2euler(q0)
    print("eul =", eul)
    quat = euler2quat(eul)
    print("q restored =", quat)
    print("q inverse", quatConj(q0))
    assert np.sqrt(np.sum(np.square(q0 - quat))) < 1e-8
    print("q array =", q1)
    eul = quat2euler(q1)
    print("eul array =", eul)
    quat = euler2quat(eul)
    print("q array restored =", quat)
    print("q array inverse", quatConj(q1))
    assert np.sqrt(np.sum(np.square(q1 - quat))) < 1e-8

    # Test quaternion multiplication with inverse
    quat0 = mul_Quat_Quat(quatConj(q1), q2)
    quat1 = mul_ConjQuat_Quat(q1, q2)
    assert np.sqrt(np.sum(np.square(quat0 - quat1))) < 1e-8
    quat0 = mul_Quat_Quat(q1, quatConj(q2))
    quat1 = mul_Quat_ConjQuat(q1, q2)
    assert np.sqrt(np.sum(np.square(quat0 - quat1))) < 1e-8
    print("q2 =", q2)
    print("q3 = q2*q1; q3*inv(q1) = ", mul_Quat_Quat(q3, quatConj(q1)))
    assert np.sqrt(
        np.sum(np.square(mul_Quat_Quat(q3, quatConj(q1)) - q2))) < 1e-8

    dq1 = dpsi_dq(q1)

    # Test ECEF-to-LLA transformations
    xe0 = y[0:5, :]*100000
    ind1 = xe0 >= 0
    ind0 = xe0 < 0
    np.clip(xe0[ind1], 10000, 1e10)
    np.clip(xe0[ind0], -1e10, -10000)
    lla_deg = ecef2lla(xe0, 100)
    xe1 = lla2ecef(lla_deg)
    assert np.sqrt(np.sum(np.square(xe0 - xe1))) < 1e-4

    # Test NED-to-LLA transformations
    lla_ref = np.array([40.0, 117.0, 10.0])
    lla = np.array([[40.1, 117.1, 20.0], [40.2, 117.2, 0.0]])
    ned1 = lla2ned(lla_ref, lla)
    lla1 = ned2lla(lla_ref, ned1)
    assert np.sqrt(np.sum(np.square(lla - lla1))) < 1e-4

    # Test attitude in ENU to attitude in NED
    eul_e2b = np.radians(np.array([[90.0, 0.0, 180.0], [0.0, 45.0, -90.0]]))
    eul_n2b = enu2nedEuler(eul_e2b)
    un = eulerNed(eul_n2b)

    # Test rotation matrix from Euler angles
    R = eulerDCM(eul_n2b)
    R1 = eulerDCM(eul_n2b[0, :])
    R2 = eulerDCM(eul_n2b[1, :])
    assert np.sqrt(np.sum(np.square(R[0, :, :] - R1))) < 1e-8
    assert np.sqrt(np.sum(np.square(R[1, :, :] - R2))) < 1e-8

    # Find the mean Quaternion
    mu = meanOfQuat(q)
    qarr = np.random.random((5000, 25, 4))
    qarr = normalize(qarr, axis=2)
    mu = meanOfQuatArray(qarr)
    print(mu)

    pass
