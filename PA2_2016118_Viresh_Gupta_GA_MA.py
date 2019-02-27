import argparse
import numpy as np
from math import ceil, log10

# A gene can be thought of a 5-tuple (day, time, hall, course, professor)
# days 		: 1-5
# time 		: 1-8
# hall 		: 1-N
# course	: 1-M
# professor	: 1-P
# A chromosome is a combination of M genes (so that every course has a staff)

DEFAULT_DAYS = 5
DEFAULT_SLOTS = 8
DEFAULT_M = 50
DEFAULT_P = 10
DEFAULT_N = 10

use_memetic = False

def get_chromosome(num_days=DEFAULT_DAYS, num_slots=DEFAULT_SLOTS, N=DEFAULT_N, M=DEFAULT_M, P=DEFAULT_P):
	a = np.random.randint(1, num_days+1, M)
	b = np.random.randint(1, num_slots+1, M)
	c = np.random.randint(1, N+1, M)
	# d = np.random.randint(1, M+1, M)
	d = np.random.permutation(M) + 1
	e = np.random.randint(1, P+1, M)
	chromosome = np.vstack((a,b,c,d,e))
	return chromosome

def get_fitness(chromosome, get_clash=False, debug=False, num_days=DEFAULT_DAYS, num_slots=DEFAULT_SLOTS, N=DEFAULT_N, M=DEFAULT_M, P=DEFAULT_P):
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
	fitness = NORMALISING_FACTOR * 1/unfitness if unfitness != 0 else NORMALISING_FACTOR
	# print(unfitness)
	if get_clash:
		return (fitness, clash_total)
	return fitness

def select_parents(population, fitness, num_select=10):
	selected = []
	for i in range(num_select):
		most_fit = np.where(fitness == np.max(fitness))
		chx = population[most_fit[0][0]]
		if use_memetic:
			# do a hill climbing on the nearby chromosomes of the selected parent
			for k in range(6):
				if k%2==0:
					chx2 = chx.copy()
					chx2[0, :] = np.random.permutation(chx2[0, :])
					chx2[1, :] = np.random.permutation(chx2[1, :])
					chx2[2, :] = np.random.permutation(chx2[2, :])
					chx2[3, :] = np.random.permutation(chx2[3, :])
					chx2[4, :] = np.random.permutation(chx2[4, :])
				else:
					chx2 = chx.copy()
					chx2 = mutate(chx2)
				if get_fitness(chx) < get_fitness(chx2):
					chx = chx2
					break
		selected.append(chx)
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

def mutate(chromosome, chanceA=0.5, chanceB=0.5):
	if np.random.uniform(0,1) < chanceA:
		chromosome = get_chromosome()
	elif np.random.uniform(0,1) < chanceB:
		chromosome[2, :] = np.random.randint(1, DEFAULT_N+1, DEFAULT_M)
		chromosome[3, :] = np.random.permutation(DEFAULT_M) + 1
		chromosome[4, :] = np.random.randint(1, DEFAULT_P+1, DEFAULT_M)
	return chromosome

def do_mutate(sub_pop, chance=0.5):
	for i in range(len(sub_pop)):
		sub_pop[i] = mutate(sub_pop[i], chanceA=chance, chanceB=chance)

def main(itrs=20):
	num_generations = itrs
	population = []
	max_pop = 50
	# generate initial population
	for i in range(15):
		chx = get_chromosome()
		population.append(chx)

	best_schedule = None

	for generation in range(num_generations):
		print('generation #'+str(generation), 'census', len(population), end=' ')
		fitness = np.empty(len(population))

		# Steps:
		# 	1) Calculate fitness
		for i in range(len(population)):
			fitness[i] = get_fitness(population[i])
		
		#	2) Select most fit parents
		selected = select_parents(population, fitness)

		#	3) Generate offsprings via crossover
		child = do_crossovers(selected)

		# 	4) Induce mutations in offspring
		do_mutate(child)

		if len(population) > max_pop:
			population = selected

		# 	5) Add new offsprings to the population
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
	parser = argparse.ArgumentParser()
	parser.add_argument("--ma", help='Whether to use memetic algorithm or simple GA', action='store_true')
	parser.add_argument("-i", "--iterations", help='Number of generations to consider', type=int, default=20)
	args = parser.parse_args()
	use_memetic = args.ma
	main(args.iterations)
