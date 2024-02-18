def writePrime(FileName = "Data", Start_Number = 0, Range_Numbers = None):

        """
        Assign FileName to change the name of Data File\n
        Assign Start_Number to change the number from which Prime Numbers are checked\n
        Assign Range_Numbers to change the number at which checking Prime Numbers are ended\n
        """

        Prime_File = open(FileName + ".txt", "w+")

        while Start_Number <= Range_Numbers:
            writePrime_Raw(Start_Number, Prime_File)
            Start_Number += 1
        
        Prime_File.close()
         
def writePrime_Raw(Max_Range, Prime_File):

        """
        Function to support other Function [NOT TO USE ALONE]
        """

        init_var = 2

        if (Max_Range == init_var):
            Prime_File.write(str(Max_Range) + "\n")

        else:
            while (init_var < Max_Range):
                if (Max_Range % init_var == 0):
                    break
                elif (init_var + 1 == Max_Range):
                    Prime_File.write(str(Max_Range)+ "\n")
                    break
                if (Max_Range / init_var <= init_var):
                    Prime_File.write(str(Max_Range) + "\n")
                    break
                init_var += 1


def isPrime(Number):
        
        """
        Assign value to Number to check if it is a Prime Number
        Returns True if Prime
        """

        init_var = 2
        
        if (Number == init_var):
            return True
        elif (Number == 1 or Number == 0):
            return False
        elif (Number < 0):
            return False
        else:
            while (init_var < Number):
                if (Number % init_var == 0):
                    return False
                elif (init_var + 1 == Number):
                    return True
                if (Number / init_var <= init_var):
                    return True
                init_var += 1