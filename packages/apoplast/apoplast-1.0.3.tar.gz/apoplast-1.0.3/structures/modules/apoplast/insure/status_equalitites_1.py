
'''
	python3 insurance.py insure/status_equalitites_1.py
'''
import apoplast.insure.equalities as equalities
		

def check_1 ():
	assert (
		equalities.check ([
			[ 1, 1 ],
			[ 9, 9 ],
			[ "0", "0" ]
		]) ==
		True
	)
	
	assert (
		equalities.check ([
			[ 1, 1 ],
			[ 9, 9 ],
			[ "0", "0" ],
			[ 1, 2 ]
		]) ==
		False
	)

	return;
	
checks = {
	'check 1': check_1
}