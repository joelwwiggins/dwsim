"""
Swarm Optimization

Converted from DWSIM.Math.SwarmOps to Python.
Swarm intelligence optimization algorithms.
"""

import numpy as np
from typing import Callable, Optional
from scipy.optimize import differential_evolution


class SwarmOptimization:
    """Swarm optimization utilities."""

    @staticmethod
    def differential_evolution(f: Callable[[np.ndarray], float],
                             bounds: list,
                             maxiter: int = 100,
                             popsize: int = 15) -> dict:
        """
        Differential evolution optimization.

        Args:
            f: Objective function
            bounds: List of (min, max) tuples for each dimension
            maxiter: Maximum iterations
            popsize: Population size

        Returns:
            Optimization result
        """
        result = differential_evolution(f, bounds, maxiter=maxiter,
                                      popsize=popsize, tol=1e-6)
        return {
            'success': result.success,
            'x': result.x,
            'fun': result.fun,
            'message': result.message,
            'nfev': result.nfev,
            'nit': result.nit
        }

    @staticmethod
    def particle_swarm_optimization(f: Callable[[np.ndarray], float],
                                  bounds: list,
                                  n_particles: int = 30,
                                  maxiter: int = 100) -> dict:
        """
        Basic particle swarm optimization.

        Args:
            f: Objective function
            bounds: List of (min, max) tuples
            n_particles: Number of particles
            maxiter: Maximum iterations

        Returns:
            Optimization result
        """
        # Simple PSO implementation
        n_dims = len(bounds)
        particles = np.random.rand(n_particles, n_dims)
        velocities = np.random.rand(n_particles, n_dims) * 0.1

        # Scale to bounds
        for i in range(n_dims):
            min_val, max_val = bounds[i]
            particles[:, i] = particles[:, i] * (max_val - min_val) + min_val

        personal_best = particles.copy()
        personal_best_fitness = np.array([f(p) for p in particles])
        global_best = personal_best[np.argmin(personal_best_fitness)]
        global_best_fitness = np.min(personal_best_fitness)

        w = 0.7  # Inertia weight
        c1 = 1.4  # Cognitive parameter
        c2 = 1.4  # Social parameter

        for _ in range(maxiter):
            r1, r2 = np.random.rand(2)
            velocities = (w * velocities +
                         c1 * r1 * (personal_best - particles) +
                         c2 * r2 * (global_best - particles))

            particles += velocities

            # Clip to bounds
            for i in range(n_dims):
                min_val, max_val = bounds[i]
                particles[:, i] = np.clip(particles[:, i], min_val, max_val)

            # Update personal bests
            fitness = np.array([f(p) for p in particles])
            better_mask = fitness < personal_best_fitness
            personal_best[better_mask] = particles[better_mask]
            personal_best_fitness[better_mask] = fitness[better_mask]

            # Update global best
            if np.min(fitness) < global_best_fitness:
                global_best = particles[np.argmin(fitness)]
                global_best_fitness = np.min(fitness)

        return {
            'success': True,
            'x': global_best,
            'fun': global_best_fitness,
            'message': 'PSO completed',
            'nfev': maxiter * n_particles,
            'nit': maxiter
        }