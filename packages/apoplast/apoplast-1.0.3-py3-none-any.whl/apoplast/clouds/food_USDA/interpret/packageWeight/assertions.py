


def make (measures):
	assert ("mass" in measures)
	assert ("per package" in measures ["mass"])
	assert ("grams" in measures ["mass"]["per package"])
	assert ("fraction string" in measures ["mass"]["per package"]["grams"])
	assert ("decimal string" in measures ["mass"]["per package"]["grams"])

	assert ("volume" in measures)
	assert ("per package" in measures ["volume"])
	assert ("liters" in measures ["volume"]["per package"])
	assert ("fraction string" in measures ["volume"]["per package"]["liters"])
	assert ("decimal string" in measures ["volume"]["per package"]["liters"])