import re

time_pattern = '([\d]{0,2}[\.:]?[\d]{1,2})\s?(pm|p\.m\.|am|a\.m\.|nn|noon)'

test = {
	1: 'lunch at 7.30pm',
	2: '6.20 p.m. tomorrow',
	3: 'at 12nn later',
	4: '3',
	5: '12',
	6: '21:30 am'
}

try:
	for (k,v) in test.items():
		if k in [4,5]: #negative test case
			print('Test {}: {}'.format(k, re.search(time_pattern v)))
		else:
			print('Test {}: {}'.format(k, ''.join([x for x in re.search(time_pattern, v).group(0).split()])

	print('Success!')
except:
	print('Test {}: Failed'.format(k))
