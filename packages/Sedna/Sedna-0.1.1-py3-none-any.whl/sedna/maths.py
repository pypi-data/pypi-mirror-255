def factors(Number):
    """
    Returns the factors of a number
    """
    all_factors = []
    for init in range(1, (Number + 1)):
        if (Number % init == 0):
            all_factors.append(init)

    return all_factors

def permutation(HeadNumber, BaseNumber):

    """
    Returns the permutation of the inputs
    """

    Product = 1
    Products = 0
    init = HeadNumber

    if (BaseNumber == 0):
        return Product

    while init >= 1:
        Product *= init
        Products += 1

        if (Products == BaseNumber):
            break

        init -= 1

    return Product

def combination(HeadNumber, BaseNumber):

    """
    Returns the combination of the inputs
    """

    Value = permutation(HeadNumber, BaseNumber)

    for number in range(1, BaseNumber + 1):
        Value /= number
    
    return Value

def factorial(Number):
    
    """
    Returns the factorial of the input
    """

    Value = 1

    for number in range(1, Number + 1):
        Value *= number

    return Value

def mean(Numbers):
    
    """
    Returns the mean of an array of values
    """

    Sum = 0
    Number_Elements = 0
    
    try:

        for Element in Numbers:
            Sum += Element
            Number_Elements += 1

        Mean = Sum / Number_Elements
    
        return Mean

    except TypeError:

        print("ERROR: Please assign an array instead of integer!")

        return -1
    
def median(Numbers):

    """
    Returns the median of an array of values
    """

    import math

    try:

        Numbers.sort()

        number_elements = 0
        
        for Element in Numbers:
            number_elements += 1

        Median_Element = (number_elements + 1) / 2

        if (Median_Element % 2 == 0):
            return Numbers[int(Median_Element - 1)]
        
        else:
            FirstElement = Numbers[math.floor(Median_Element - 1)]
            SecondElement = Numbers[math.ceil(Median_Element - 1)]

            FinalElement = (FirstElement + SecondElement) / 2

            return FinalElement
        
    except AttributeError:

        print("ERROR: Please assign an array instead of an integer!")

        return -1
    
def mode(Numbers):

    """
    Returns the mode of an array of values\n
    Returns only one mode of the bi/tri modal data
    """

    try:
        Numbers.sort()
        i = 0
        ModeElement = None
        tempElement = None
        times = 0
        tempTimes = 0

        while i < len(Numbers):
            
            if (ModeElement == None):
                ModeElement = Numbers[i]
                times += 1
            elif (ModeElement == Numbers[i]):
                times += 1
            elif (ModeElement != Numbers[i] and tempElement == Numbers[i]):
                tempElement = Numbers[i]
                tempTimes += 1
            elif (ModeElement != Numbers[i] and tempElement != Numbers[i]):
                tempElement = Numbers [i]
                tempTimes = 1

            if (tempTimes > times):
                ModeElement = tempElement
                times = tempTimes
                tempTimes = 0
                tempElement = None

            i += 1

        return ModeElement

    except AttributeError:
        print("ERROR: Please assign an array instead of an integer!")
        return -1
    
def dataRange(Numbers):
    
    """
    Returns the range of input data
    """

    try:

        MinElement, MaxElement = Numbers[0], Numbers[0]

        for Element in Numbers:

            MinElement = Element if Element < MinElement else MinElement
            MaxElement = Element if Element > MaxElement else MaxElement

        return MaxElement - MinElement
    
    except AttributeError:

        print("ERROR: Please assign an array instead of an integer!")
        return -1

def percentage(value, total):

    """
    Returns the percentage of value
    """

    return value / total * 100

def randomRange(Min, Max):
    import random
    
    """
    Returns a random number between inputs
    """

    return random.randrange(Min, Max)