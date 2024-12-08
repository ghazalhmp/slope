import time
import random
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
import attributes
from attributes import *
from attributes import SlipSurface
import slipsurface

class Pso:

    def __init__(self, c1, c2, w, w_damp, func, n_pop, max_iter, n_var, var_size, var_min, var_max):

        # --------------- PSO Parameter ------------------- #

        self.c1 = c1                 # personal learning coefficient
        self.c2 = c2                 # global learning coefficient
        self.w = w                   # inertia weight
        self.w_damp = w_damp         # inertia weight damping ratio
        self.n_pop = n_pop           # population size (swarm size)
        self.max_iter = max_iter     # maximum number of iteration

        # --------------- problem definition --------------- #

        self.func = func             # cost function
        self.n_var = n_var           # number of decision variables
        self.var_size = var_size     # size of decision variables matrix
        self.var_min = var_min       # lower bound of variables
        self.var_max = var_max       # upper bound of variables

        # --------------- Velocity limits ------------------ #

        self.vel_max = 0.1 * (self.var_max - self.var_min)
        self.vel_min = -self.vel_max

        # --------------- initialization  ------------------ #
        self.particles = []
        self.best_costs = []
        self.best_pos = []
        self.global_best_cost = np.inf
        self.global_best_position = -np.inf

    def constriction_coefficient(self):
        phi1 = phi2 = 2.05
        phi = phi1 + phi2
        chi = 2 / (phi - 2 + sqrt((phi ** 2) - 4 * phi))
        self.w = chi
        self.c1 = self.c2 = chi * phi1

    def initialization(self):
        t1 = time.time()
        radius=20
        icc = ImportantCoordinatesCircle(radius)
        valid_circles = icc.get_valid_circles()
        child_number = 0
        while len(self.particles) < self.n_pop:

            particle = Particle()

            # initialize position
            particle.position = [valid_circles[child_number][0], valid_circles[child_number][1]]
            # particle.position = [random.uniform(self.var_min, self.var_max) for _ in range(self.var_size)]

            # initialize velocity
            particle.velocity = [0 for _ in range(self.var_size)]

            # update particle cost function
            particle.cost = self.func(particle.position)

            # update personal best
            particle.best_position = particle.position
            particle.best_cost = particle.cost

            # create particle i-th
            self.particles.append(particle)
            print(f"child {child_number + 1} added")
            print(f"new child position: ", particle.position)
            print(f"new child cost: ", particle.cost)
            child_number += 1

            # update global best
            if particle.best_cost < self.global_best_cost:
                self.global_best_cost = particle.best_cost
                self.global_best_position = particle.best_position

        print("********** result of particle generation **********")
        print("global best cost", self.global_best_cost)
        print("global best pos", self.global_best_position)
        t2 = time.time()
        print("particle generation time: ", round(t2 - t1, 4), "(s)" + "\n")

    def main_loop(self):
        t1 = time.time()

        for it in range(self.max_iter):
            for particle in self.particles:
                p1 = self.w * np.array(particle.velocity)
                r1 = [random.uniform(0, 1) for _ in range(self.var_size)]
                r2 = [random.uniform(0, 1) for _ in range(self.var_size)]
                p2 = self.c1 * (np.array(r1)) * (np.array(particle.best_position) - np.array(particle.position))
                p3 = self.c2 * (np.array(r2)) * (np.array(self.global_best_position) - np.array(particle.position))

                # update velocity
                particle.velocity = np.array(p1) + np.array(p2) + np.array(p3)

                # apply velocity limit
                particle.velocity = np.array([max(vel, self.vel_min) for vel in particle.velocity])
                particle.velocity = np.array([min(vel, self.vel_max) for vel in particle.velocity])

                # update position
                particle.position = np.array(particle.position) + np.array(particle.velocity)

                # velocity mirror effect
                for i in range(len(particle.position)):
                    if particle.position[i] < self.var_min or particle.position[i] > self.var_max:
                        particle.velocity[i] = -particle.velocity[i]

                # apply position limit
                particle.position = np.array([max(pos, self.var_min) for pos in particle.position])
                particle.position = np.array([min(pos, self.var_max) for pos in particle.position])

                # Evaluation
                particle.cost = self.func(particle.position)

                # update personal best
                if particle.cost < particle.best_cost:
                    particle.best_position = particle.position
                    particle.best_cost = particle.cost

                    # update global best
                    if particle.best_cost < self.global_best_cost:
                        self.global_best_cost = particle.best_cost
                        self.global_best_position = particle.best_position
                        print("global_best_cost: ", self.global_best_cost)
                        print("global_best_position: ", self.global_best_position)

            self.best_costs.append(self.global_best_cost)
            self.best_pos.append(self.global_best_position)

            print("iteration", it, ": best cost =", self.best_costs[it])
            print("iteration", it, ": best position =", self.best_pos[it])

            self.w *= self.w_damp

        # --------------- results --------------- #

        t2 = time.time()
        print("Total time of algorithm calculation is:", round(t2 - t1, 4), "(s)")
        plt.plot(self.best_costs)
        plt.xlabel('Iteration')
        plt.ylabel('Best Cost')
        plt.show()

    def run(self, constriction_coefficient=False):
        self.initialization()
        if constriction_coefficient:
            self.constriction_coefficient()
        self.main_loop()


class Particle:

    def __init__(self):
        self.position = []
        self.cost = 0
        self.velocity = []
        self.best_position = 0
        self.best_cost = 0

    def __str__(self):
        return f"position: {self.position} \n" \
               f"cost: {self.cost} \n" \
               f"velocity: {self.velocity} \n" \
               f"best_position: {self.best_position} \n" \
               f"best_cost: {self.best_cost}"


if __name__ == "__main__":
    pso = Pso(1, 1, 1, 1, coast_function, 60, 15, 2, 2, 0, 19)
    pso.run()

