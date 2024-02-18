def calcForce(mass, acceleration):

    """
    Returns force by taking inputs of mass and acceleration
    """

    return mass*acceleration

def calcAttract(gravityConst, mass_1, mass_2, distance):

    """
    Returns the force of attraction between two bodies
    """

    return gravityConst * mass_1 * mass_2 / (distance * distance)

def calcMomentum(mass, velocity):

    """
    Returns the momentum of a body
    """

    return mass * velocity

def calcElecConsume(rating, hoursUsed):

    """
    Returns the electricity consumed by an appliance
    """

    return rating * hoursUsed

def calcHeatConsume(energy, mass, changeTemp):

    """
    Returns the heat consumed by an object
    """

    return energy / (mass * changeTemp)

def calcReflectAngle(incidenceAngle, normalAngle):

    import math

    """
    Returns the reflection angle made by a mirror
    """

    reflectAngle = normalAngle - incidenceAngle

    if reflectAngle < 0:
        reflectAngle = -reflectAngle

    return reflectAngle