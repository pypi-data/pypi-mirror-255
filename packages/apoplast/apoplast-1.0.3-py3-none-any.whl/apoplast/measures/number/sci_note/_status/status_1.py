

'''
	python3 insurance.py measures/number/sci_note/_status/status_1.py
'''

import apoplast.measures.number.sci_note as sci_note

from fractions import Fraction

def equal (s1, s2):
	assert (s1 == s2), [ s1, s2 ]

	return;

def status_1 ():	
	assert (sci_note.calc ('9999999') == [ "9.999", "e+6" ]), sci_note.calc ('9999999')

	s_note = sci_note.calc (Fraction (4, 3))
	assert (s_note == [ "1.333", "e+0" ]), s_note
	
	s_note = sci_note.calc ('5.0057')
	assert (s_note == [ "5.005", "e+0" ]), s_note
	
	s_note = sci_note.calc ('5000.0057')
	assert (s_note == [ "5.000", "e+3" ]), s_note


	#assert (sci_note.calc (        '-1') == [  "-1.000", "e+0" ]), sci_note.calc (        '-1')
	#assert (sci_note.calc ('1/10000' ) == [ "0.001", "e-3" ]), sci_note.calc ('1/10000' )
	
	
	#
	#	-infinity < s <= -1
	#
	assert (sci_note.calc (         '-1') == [   "-1.000", "e+0" ])	
	assert (sci_note.calc (       '-999') == [ "-999.000", "e+0" ])	
	
	assert (sci_note.calc (      '-1000') == [   "-1.000", "e+3" ])
	assert (sci_note.calc (    '-100000') == [ "-100.000", "e+3" ])
	assert (sci_note.calc (    '-999999') == [ "-999.999", "e+3" ])
	
	#
	#	-1 < s < zero
	#
	equal (sci_note.calc ('-1/10000000'), [ "-100.000", "e-9" ])
	equal (sci_note.calc ('-1/1000000'), [ "-1.000", "e-6" ])
	equal (sci_note.calc ('-1/100000'), [ "-10.000", "e-6" ])

	#
	#	zero
	#
	assert (sci_note.calc ('0') == [ "0.000", "e+0" ])
	
	#
	#	zero < s < 1
	#
	assert (.1e-3 == 100e-6)
	assert (1/10000 == 100e-6)

	equal (sci_note.calc ('1/10000000'), [ "100.000", "e-9" ])
	equal (sci_note.calc ('1/1000000'), [ "1.000", "e-6" ])
	equal (sci_note.calc ('1/100000'), [ "10.000", "e-6" ])

	equal (sci_note.calc ('999999/1000000000' ), [ "999.999", "e-6" ])
	assert (sci_note.calc (   '999/1000000' ) == [ "999.000", "e-6" ]),sci_note.calc (   '9/10000' )
	assert (sci_note.calc (   '9/10000' ) == [ "900.000", "e-6" ])	
	assert (sci_note.calc (   '1/10000' ) == [ "100.000", "e-6" ])
	
	assert (sci_note.calc (   '1/1000'  ) == [   "1.000", "e-3" ])
	assert (sci_note.calc (   '1/100'   ) == [  "10.000", "e-3" ])
	assert (sci_note.calc (   '1/10'    ) == [ "100.000", "e-3" ])
	assert (sci_note.calc (   '1/2'     ) == [ "500.000", "e-3" ]), sci_note.calc ('1/2')
	assert (sci_note.calc ( '999/1000') == [ "999.000", "e-3" ]), sci_note.calc ('1/2')
	assert (sci_note.calc ('999999/1000000') == [ "999.999", "e-3" ])
	
	#
	#	no rounding occurs
	#
	assert (sci_note.calc ('9999999/10000000') == [ "999.999", "e-3" ])


	#
	#	1 <= s <= infinity
	#
	assert (sci_note.calc (         '1') == [   "1.000", "e+0" ])	
	assert (sci_note.calc (       '999') == [ "999.000", "e+0" ])	
	
	assert (sci_note.calc (      '1000') == [   "1.000", "e+3" ])
	assert (sci_note.calc (    '100000') == [ "100.000", "e+3" ])
	assert (sci_note.calc (    '999999') == [ "999.999", "e+3" ])
	
	assert (sci_note.calc (   '1000000') == [   "1.000", "e+6" ])	
	assert (sci_note.calc (  '10000000') == [  "10.000", "e+6" ])
	assert (sci_note.calc ( '100000000') == [ "100.000", "e+6" ])
	assert (sci_note.calc ( '999999999') == [ "999.999", "e+6" ])
	
	assert (sci_note.calc ('1000000000') == [   "1.000", "e+9" ])
	
	
	
	
	
checks = {
	"status 1": status_1
}