import pynof

mol = pynof.molecule("""
0 1
O     -5.531670    1.475322    0.000533
C     -6.532573    0.467083    0.094652
C     -5.078524    0.130843    0.119813
H     -7.560396    0.171161    0.124833
H     -4.286469   -0.585918    0.181486
""")

p = pynof.param(mol,"cc-pvdz")
p.autozeros()

p.ipnof = 8

p.RI = True
p.gpu = True

p.orb_method = "Rotations"
p.occ_method = "Softmax"
E,C,n,fmiug0 = pynof.compute_energy(mol,p,hfidr=True,perturb=True)
