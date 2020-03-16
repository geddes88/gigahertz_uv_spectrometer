from numpy import *

def FNR(D,P3):
	#function used by SunZen
	return ((D/P3)-int(D/P3))*P3

def sunzen(Yr,DofY,Hr,Mn,Sc,Lat,Lon):
	# SS 2015
	# translated from IDL to python
	
	# DS Sept 2009
	# take out of the utilites pro file, make stand alone

	# DS May 2004
	# Take out NZST and replace with varible timezone,so the
	# Sunzen program can be used for any location
	
	# Calculate Solar Zenith Angle (Z) and Azimuth (Z1) from Input
	# REM ARITHMETIC BY DR R.L.MCKENZIE - REPORT PEL # 641 (IE: BLAME HIM)
	# REM Changes made Aug 1999 by ISB to make it equivalent to the most recent
	# REM version of SunZen
	# REM 1: Line 8516 Comment out the last part of the equation (note: currently
	# REM    not sure if this is correct or not.
	# REM 2: Line 8561 Change L4 <= P2 to L4 < P2 - Found to cause a problem at
	# REM    Low latitude stations
	# Note - this code needs to convert UTC to NZST

	# convert all date/times to integer values
	Yr=int(Yr)
	DofY=int(DofY)
	Hr=int(Hr)
	Mn=int(Mn)
	Sc=round(Sc)
	H2=Hr+12. #UTC to NZST
	#H2=Hr #JR reinstated
	
	P0=2.*arctan(1.)
	P1=4.*arctan(1.)
	P2=6.*arctan(1.)
	P3=8.*arctan(1.)
	X=.016751
	C9=P3/360.
	L1=Lat*C9
	
	I=int((Yr-1901)/4)
	J=(Yr-1901) % 4
	E1=1461*I+365*J+DofY+364 #- ((Date.Year - 1901) \ 100)
	S2=Sc+50.5+(Yr-1980)
	I1=E1
	F1=H2/24.+Mn/1440.+S2/86400.9
	F2=I1/36525.+F1/36525.
	R1=279.697*C9
	R2=502.322
	R3=((I1-29200)*.985647)*C9
	R4=.985647*F1*C9
	L3=4.88163+5.94986+FNR(R3,P3)+FNR(R4,P3)
	L3=FNR(L3,P3)
	R5=358.475*C9
	R6=502.298
	R7=((I1-29200)*.9856)*C9
	R8=.9856*F1*C9
	A1=6.25658+5.92588+FNR(R7,P3)+FNR(R8,P3)
	A1=FNR(A1,P3)
	F=(2.*X-(X*X*X)/4.)*sin(A1)+(5./4.)*X*X*sin(2.*A1)
	F=F+(13./12.)*X*X*X*sin(3.*A1)
	E9=(23.4523-.0130125*F2)*C9
	L4=L3+F
	X1=sin(E9)*sin(L4)
	D=P0
	if X1 != 1.:
		D=arctan(X1/sqrt(1.0-X1*X1))
	X2=cos(E9)*tan(L4)
	if ((L4 > P0) and (L4 <= P3)): 
		t1=-1 
	else: 
		t1=0
	if ((L4 > P0) and (L4 < P2)):
		t2=-1
	else:
		t2=0

	A=arctan(X2)-P3*t1-P1*t2
	if L4 > P3:
		t1=-1 
	else:
		t1=0
	Q=L3-A+P3*t1
	H=((H2+Mn/60.+Sc/3600.)*15+Lon)*C9+Q
	Z=sin(L1)*sin(D)+cos(L1)*cos(D)*cos(H)
	if Z >= 1:
		Z=0
	if Z < 1: 
		Z=arctan(Z/sqrt(1-Z*Z))
		Z=(P0-Z)/C9

	A1=-cos(D)*sin(H)
	A2=sin(D)*cos(L1)-cos(H)*cos(D)*sin(L1)
	Z1=arctan(A1/A2)
	if A2 < 0.:
		Z1=Z1+P1
	if Z1 < 0.:
		Z1=Z1+P3
	Z1=Z1/C9 #Z = SOLAR ZENITH ANGLE , Z1 = SOLAR AZIMUTH
	return Z, Z1
