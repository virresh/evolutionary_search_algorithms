import numpy as np
from math import ceil, log10

# A gene can be thought of a 5-tuple (day, time, hall, course, professor)
# days 		: 1-5
# time 		: 1-8
# hall 		: 1-N
# course	: 1-M
# professor	: 1-P
# A chromosome is a combination of M genes (so that every course has a staff)

def get_chromosome(num_days=5, num_slots=8, N=5, M=10, P=20):
	a = np.random.randint(1, num_days, M)
	b = np.random.randint(1, num_slots, M)
	c = np.random.randint(1, N, M)
	d = np.random.permutation(M)
	e = np.random.randint(1, P, M)
	chromosome = np.vstack((a,b,c,d,e))
	return chromosome

def get_fitness(chromosome, num_days=5, num_slots=8, N=5, M=10, P=20):
	fitness = 0
	# for i in range(1, P+1):		
	free_profs = P - len(np.unique(chromosome[4]))
	free_slots = 0
	s = set()
	for i in range(0, len(chromosome[0])):
		# print(chromosome[0][i], chromosome[1][i])
		s.add((chromosome[0][i], chromosome[1][i]))
	# print(s)
	free_slots = num_days*num_slots - len(s)
	prof_clash = 0
	venue_clash = 0
	course_exceed_max_class = 0
	course_changed_instructor = 0
	for i in range(0, len(chromosome[0])):
		for j in range(0, len(chromosome[0])):
			if chromosome[0][i] == chromosome[0][j] and chromosome[1][i] == chromosome[1][j]:
				# stuff scheduled at same time
				if chromosome[4][i] == chromosome[4][j]:
					prof_clash += 1
				if chromosome[2][i] == chromosome[2][j]:
					venue_clash += 1
			if chromosome[3][i] == chromosome[3][j]:
				course_exceed_max_class += 1
				if chromosome[4][i] != chromosome[4][i]:
					course_changed_instructor += 1
	CLASH_PENALTY = N*M*P
	NORMALISING_FACTOR = 10**(ceil(log10(CLASH_PENALTY)) + 3)
	clash_total = prof_clash + venue_clash + course_changed_instructor + course_exceed_max_class
	unfitness = free_profs + free_slots + clash_total * CLASH_PENALTY

	return NORMALISING_FACTOR * 1/unfitness

def select_parents(population, fitness, num_select=5):
	selected = np.empty((population[0].shape[1], num_select))
	for i in range(num_select):
		most_fit = np.where(fitness == np.max(fitness))[0][0]
		selected[i,:] = population[most_fit, :]
		fitness[i] = -1
	return selected


def main():
	num_generations = 1
	population = []
	# generate initial population
	for i in range(50):
		chx = get_chromosome()
		population.append(chx)

	for generation in range(num_generations):
		fitness = np.empty(population.shape[1])
		# Number of iterations for GA
		# Steps:
		# 	1) Calculate fitness
		#	2) Select most fit parents
		#	3) Generate offsprings via crossover
		# 	4) Induce mutations in offspring
		# 	5) Add new offsprings to the population
		for i in range(len(population)):
			fitness[i] = get_fitness(population[i])
		print(select_parents(population, fitness))

if __name__ == '__main__':
	main()
