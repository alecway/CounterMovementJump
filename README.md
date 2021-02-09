# CounterMovementJump
This is a simple script which reads structured data, collected from a force plate, during an athlete's counter-movement jump. It then calculates metrics, and outputs a graph of net force, left and right force, and force asymmetry over time, and highlights the three pre-flight phases of the jump: unweighting, breaking, and propulsive.

Requirements include: pandas, matplotlib, statistics, numpy, and easykinter packages.

Example Output:
	Peak force :  5196.7718540000005 N
	Peak Power :  5173.761035778476 W
	Jump Height :  52.34621916582009 cm
	Unweighting duration : 0.327 s
	Braking duration : 0.185 s
	Propulsive duration : 0.29 s
	Flight duration : 1.998 s
	Peak Pre-Flight Force :  2238.737 N
	Peak Pre-Flight RFD :  11044.921 N/s
	Average Force Development in breaking phase :  7065.551 N/s
	Average Force Development in propulsive phase :  -4338.766 N/s
	Peak Pre-Flight Power :  5173.761035778476 W

