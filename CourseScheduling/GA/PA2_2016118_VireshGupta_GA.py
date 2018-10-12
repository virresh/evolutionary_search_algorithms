import numpy as np
from math import ceil, log10

# A gene can be thought of a 5-tuple (day, time, hall, course, professor)
# days 		: 1-5
# time 		: 1-8
# hall 		: 1-N
# course	: 1-M
# professor	: 1-P
# A chromosome is a combination of M genes (so that every course has a staff)

DEFAULT_M = 50
DEFAULT_P = 10
DEFAULT_N = 10

def get_chromosome(num_days=5, num_slots=8, N=DEFAULT_N, M=DEFAULT_M, P=DEFAULT_P):
	a = np.random.randint(1, num_days+1, M)
	b = np.random.randint(1, num_slots+1, M)
	c = np.random.randint(1, N+1, M)
	# d = np.random.randint(1, M+1, M)
	d = np.random.permutation(M)
	e = np.random.randint(1, P+1, M)
	chromosome = np.vstack((a,b,c,d,e))
	return chromosome

def get_fitness(chromosome, get_clash=False, debug=False, num_days=5, num_slots=8, N=DEFAULT_N, M=DEFAULT_M, P=DEFAULT_P):
	fitness = 0
	free_profs = P - len(np.unique(chromosome[4]))
	free_slots = 0
	s = set()
	for i in range(0, len(chromosome[0])):
		s.add((chromosome[0,i], chromosome[1,i]))
	free_slots = num_days*num_slots - len(s)
	prof_clash = 0
	venue_clash = 0
	course_exceed_max_class = 0
	course_changed_instructor = 0
	for i in range(0, len(chromosome[0])):
		for j in range(0, len(chromosome[0])):
			if i == j:
				continue
			if abs(chromosome[0,i] - chromosome[0,j]) < 0.1 and abs(chromosome[1,i] - chromosome[1,j]) < 0.1:
				# print(' --> ', chromosome[0,i], chromosome[1,i], chromosome[2,i], chromosome[3,i], chromosome[4,i])
				# print(' <-- ', chromosome[0,j], chromosome[1,j], chromosome[2,j], chromosome[3,j], chromosome[4,j])
				# print('')
				# stuff scheduled at same time
				if abs(chromosome[4,i] - chromosome[4,j]) < 0.1:
					prof_clash += 1
				if abs(chromosome[2,i] - chromosome[2,j]) < 0.1:
					venue_clash += 1
				if debug:
					print('here')
			if debug:
				print(chromosome[3,i], chromosome[3,j], i)
			if abs(chromosome[3,i] - chromosome[3,j]) < 0.1:
				if debug:
					print('Course clash !')
				course_exceed_max_class += 1
				if abs(chromosome[4,i] - chromosome[4,i]) > 0.1:
					course_changed_instructor += 1
	CLASH_PENALTY = N*M*P
	NORMALISING_FACTOR = 10**(ceil(log10(CLASH_PENALTY)) )
	clash_total = prof_clash + venue_clash + course_changed_instructor + course_exceed_max_class
	# print(prof_clash, venue_clash, course_exceed_max_class, course_changed_instructor)
	unfitness = free_profs + free_slots + clash_total * CLASH_PENALTY
	fitness = NORMALISING_FACTOR * 1/unfitness
	# print(unfitness)
	if get_clash:
		return (fitness, clash_total)
	return fitness

def select_parents(population, fitness, num_select=10):
	selected = []
	for i in range(num_select):
		most_fit = np.where(fitness == np.max(fitness))
		selected.append(population[most_fit[0][0]])
		fitness[most_fit[0][0]] = -1
	return selected

def do_crossovers(parents, num_offsprings=9):
	offsprings = []
	for i in range(num_offsprings):
		parent1 = parents[i%len(parents)]
		parent2 = parents[(i+1)%len(parents)]
		offspring = np.empty(parents[0].shape)
		cross_point = np.random.randint(1, offspring.shape[1]-1)
		offspring[:, :cross_point] = parent1[:, :cross_point]
		offspring[:, cross_point:] = parent2[:, cross_point:]

		cross_point = np.random.randint(1, offspring.shape[0]-1)
		offspring[:cross_point, :] = parent1[:cross_point, :]
		offspring[cross_point:, :] = parent1[cross_point:, :]
		offsprings.append(offspring)
	return offsprings

def do_mutate(sub_pop, chance=0.5):
	for i in range(len(sub_pop)):
		if np.random.uniform(0,1) < chance:
			sub_pop[i] = get_chromosome()
		elif np.random.uniform(0,1) < chance:
			sub_pop[i][2, :] = np.random.randint(1, DEFAULT_N+1, DEFAULT_M)
			sub_pop[i][3, :] = np.random.permutation(DEFAULT_M)
			sub_pop[i][4, :] = np.random.randint(1, DEFAULT_P+1, DEFAULT_M)

def main():
	num_generations = 20
	population = []
	max_pop = 50
	# generate initial population
	for i in range(15):
		chx = get_chromosome()
		population.append(chx)
	# print(population)
	best_schedule = None

	for generation in range(num_generations):
		print('generation #'+str(generation), 'census', len(population), end=' ')
		fitness = np.empty(len(population))
		# Number of iterations for GA
		# Steps:
		# 	1) Calculate fitness
		#	2) Select most fit parents
		#	3) Generate offsprings via crossover
		# 	4) Induce mutations in offspring
		# 	5) Add new offsprings to the population
		for i in range(len(population)):
			fitness[i] = get_fitness(population[i])
		# print(fitness)
		selected = select_parents(population, fitness)

		child = do_crossovers(selected)

		do_mutate(child)

		if len(population) > max_pop:
			population = selected

		population.extend(child)

		best_fit = 0
		clash_val = 0
		for i in population:
			t = get_fitness(i, get_clash=True)
			if t[0] > best_fit:
				best_fit = t[0]
				clash_val = t[1]
				best_schedule = i
		print('Best of this generation ', best_fit, 'clash val', clash_val)

	print('Best Suited Schedule: ')
	print(best_schedule)
	# get_fitness(best_schedule, debug=True)

if __name__ == '__main__':
	main()
	# parents = [get_chromosome(), get_chromosome()]
	# print(parents)
	# offsprings = do_crossovers(parents, num_offsprings=2)
	# print(offsprings)
	# for offspring in offsprings:
	# 	print(get_fitness(offspring))
