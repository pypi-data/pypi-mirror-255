from .courses import courses

def calculate_hours():
	return sum(course.duration for course in courses)
