import scipy as sc
import pandas as pd
from fractions import Fraction
def display_format(my_vector,my_decimal):
    return np.round((my_vector).astype(np.cfloat),decimals=my_decimal)
my_dp=Fraction(1,3)
Mat = np.matrix([[0,0,1],
                [Fraction(1,2),0,0],
                [Fraction(1,2),1,0]])
Ex = np.zeros((3,3))
beta = 0.7
A1 = beta*Mat+((1-beta)*Ex)
r = np.matrix([my_dp,my_dp,my_dp])
r = np.transpose(r)
previous_r=r
for i in range(1,100):
    r=A1*r
    print(display_format(r,3))
    if(previous_r==r).all():
        break    
previous_r = r
print("Final : \n", display_format(r,3))
print("Sum" , np.sum(r))