#!/usr/bin/env python

###########################################################################
#                                                                         #
#  Example script for LJ simulation with Langevin Thermostat              #
#                                                                         #
###########################################################################

import espresso
import MPI
import math
import logging

from espresso import Real3D, Int3D

# Input values for system

N      = 10
cutoff = 2.5
skin   = 0.3

def calcNumberCells(size, nodes, cutoff):
    ncells = 1
    while size / (ncells * nodes) >= cutoff:
       ncells = ncells + 1
    return ncells - 1

system = espresso.System()

system.rng  = espresso.esutil.RNG()

SIZE = float(N)
box  = Real3D(SIZE)

system.bc = espresso.bc.OrthorhombicBC(system.rng, box)

system.skin = skin

comm = MPI.COMM_WORLD

nodeGrid = Int3D(1, 1, comm.size)
cellGrid = Int3D(1, 1, 1)

for i in range(3):
   cellGrid[i] = calcNumberCells(SIZE, nodeGrid[i], cutoff)

print 'NodeGrid = %s' % (nodeGrid,)
print 'CellGrid = %s' % (cellGrid,)

system.storage = espresso.storage.DomainDecomposition(system, comm, nodeGrid, cellGrid)

pid = 0

for i in range(N):
  for j in range(N):
    for k in range(N):

      m = (i + 2*j + 3*k) % 11
      r = 0.45 + m * 0.01
      x = (i + r) / N * SIZE
      y = (j + r) / N * SIZE
      z = (k + r) / N * SIZE

      system.storage.addParticle(pid, Real3D(x, y, z))

      # not yet: dd.setVelocity(id, (1.0, 0.0, 0.0))
      pid = pid + 1

system.storage.resortParticles()

integrator = espresso.integrator.VelocityVerlet(system)

print 'integrator.dt = %g, will be set to 0.005' % integrator.dt

integrator.dt = 0.005

print 'integrator.dt = %g, is now '%integrator.dt

# now build Verlet List
# ATTENTION: you have to add the skin explicitly here

vl = espresso.VerletList(system, cutoff = cutoff + system.skin)

potLJ = espresso.interaction.LennardJones(1.0, 1.0, cutoff = cutoff)

# ATTENTION: auto shift was enabled

print "potLJ, shift = %g"%potLJ.shift

interLJ = espresso.interaction.VerletListLennardJones(vl)

interLJ.setPotential(type1 = 0, type2 = 0, potential = potLJ)

# Todo

system.addInteraction(interLJ)

temp = espresso.analysis.Temperature(system)

temperature = temp.compute()
kineticEnergy = 0.5 * temperature * (3 * N * N * N)
potentialEnergy = interLJ.computeEnergy()
print 'Start: tot energy = %10.6f pot = %10.6f kin = %10.f temp = %10.6f'%(kineticEnergy + potentialEnergy,
           potentialEnergy, kineticEnergy, temperature)

nsteps = 20

for i in range(20):
   integrator.run(nsteps)
   temperature = temp.compute()
   kineticEnergy = 0.5 * temperature * (3 * N * N * N)
   potentialEnergy = interLJ.computeEnergy()
   print 'Step %6d: tot energy = %10.6f pot = %10.6f kin = %10.6f temp = %f'%(nsteps*(i+1), 
        kineticEnergy + potentialEnergy, potentialEnergy, kineticEnergy, temperature)

# logging.getLogger("Langevin").setLevel(logging.INFO)

langevin = espresso.integrator.Langevin(system)

integrator.langevin = langevin

langevin.gamma = 1.0
langevin.temperature = 4.0

print 'Heat up to t = ', langevin.temperature

for i in range(20):
   integrator.run(nsteps)
   temperature = temp.compute()
   kineticEnergy = 0.5 * temperature * (3 * N * N * N)
   potentialEnergy = interLJ.computeEnergy()
   print 'Step %6d: tot energy = %10.6f pot = %10.6f kin = %10.6f temp = %f'%(nsteps*(i+1), 
        kineticEnergy + potentialEnergy, potentialEnergy, kineticEnergy, temperature)

langevin.temperature = 0.5

print 'Cool down to t = ', langevin.temperature

for i in range(40):
   integrator.run(nsteps)
   temperature = temp.compute()
   kineticEnergy = 0.5 * temperature * (3 * N * N * N)
   potentialEnergy = interLJ.computeEnergy()
   print 'Step %6d: tot energy = %10.6f pot = %10.6f kin = %10.6f temp = %f'%(nsteps*(i+1),
        kineticEnergy + potentialEnergy, potentialEnergy, kineticEnergy, temperature)
