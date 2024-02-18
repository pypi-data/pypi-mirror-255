class Course:
	def __init__(self, name, duration, link):
		self.name=name
		self.duration=duration
		self.link=link
		
	def __repr__(self):
		return f"{self.name} - {self.duration} - {self.link}"
		
	
courses=[
	Course("Ethical Hackaing Certified Associate", 60, "https://certjoin.com/certifications/ethicalhackingcertifiedassociate/"),
	Course("Certified Ethical Hacker", 20, "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/"),
	Course("eJPT v2", 30, "https://security.ine.com/certifications/ejpt-certification/")
]

def list_courses():
	for course in courses:
		print(course)
	
def search_course_by_name(name):
	for course in courses:
		if course.name == name :
			print(course)
		else: 	return None 
