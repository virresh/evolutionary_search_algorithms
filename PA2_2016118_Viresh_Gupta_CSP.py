import numpy as np
import sys

# information is stored as a 5xM matrix, each column representing a course
# days 		: 1-5
# time 		: 1-8
# hall 		: 1-N
# course	: 1-M
# professor	: 1-P

DEFAULT_DAYS = 5
DEFAULT_SLOTS = 8
DEFAULT_M = 50
DEFAULT_P = 10
DEFAULT_N = 10

def get_clashes(schedule, cc, debug=False):
	prof_clash = 0
	venue_clash = 0
	prof_set = set()
	hall_set = set()
	for i in range(0, cc):
		for j in range(0, cc):
			if i == j:
				continue
			# because exact comparisions on floats doesn't work well in numpy
			if abs(schedule[0,i] - schedule[0,j]) < 0.1 and abs(schedule[1,i] - schedule[1,j]) < 0.1:
				if abs(schedule[4,i] - schedule[4,j]) < 0.1:
					# print('clashing', i, j)
					prof_set.add(schedule[4,i])
					prof_clash += 1
				if abs(schedule[2,i] - schedule[2,j]) < 0.1:
					hall_set.add(schedule[2,i])
					venue_clash += 1
			if debug:
				print(schedule[3,i], schedule[3,j], i)
	clash_total = prof_clash + venue_clash
	# print(prof_clash, venue_clash)
	return (clash_total, prof_clash, venue_clash, len(prof_set), len(hall_set))

def attach_vals(schedule, current_cr, prof, hall, day, slot):
	counter = 0
	while current_cr < DEFAULT_M:
		schedule[0, current_cr] = day
		schedule[1, current_cr] = slot
		schedule[2, current_cr] = hall
		schedule[4, current_cr] = prof
		clashes = get_clashes(schedule, current_cr+1)
		if clashes[0] == 0:
			counter = 0
			current_cr += 1
			slot = (slot)%DEFAULT_SLOTS + 1
			if slot == 1:
				day = (day)%DEFAULT_DAYS + 1
			hall = (hall)%DEFAULT_N + 1
			prof = (prof)%DEFAULT_P + 1
		elif clashes[3] == DEFAULT_P or clashes[4] == DEFAULT_N and counter != DEFAULT_SLOTS*DEFAULT_DAYS:
			# no prof or hall availaible at the given time slot, skip
			counter+=1
			slot = (slot)%DEFAULT_SLOTS + 1
			if slot == 1:
				day = (day)%DEFAULT_DAYS + 1			
		elif clashes[1] > 0 and counter != DEFAULT_SLOTS*DEFAULT_DAYS:
			# there's a clash with prof availability
			# try the next prof
			prof = (prof)%DEFAULT_P + 1
		elif clashes[2] > 0 and counter != DEFAULT_SLOTS*DEFAULT_DAYS:
			# the venue isn't free 
			# try another venue
			hall = (hall)%DEFAULT_N + 1
		else:
			print('No valid Schedule possible.')
			sys.exit(1)

def main():
	schedule = np.zeros((5, DEFAULT_M))

	for course in range(1, DEFAULT_M+1):
		schedule[3,course-1] = course

	attach_vals(schedule, 0, 1, 1, 1, 1)

	print('Best Suited Schedule: ')
	print(schedule)

if __name__ == '__main__':
	main()
