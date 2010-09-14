#!/usr/bin/env python

###########################################################################
#                                                                         #
#  Example script for LJ simulation with or without Langevin thermostat   #
#                                                                         #
###########################################################################

import sys
import time
start_time = time.clock()
import espresso
import MPI
import logging
import lammps_file
from espresso import Real3D, Int3D

# read coordinates and box size
x, y, z, Lx, Ly, Lz = lammps_file.read('data.lj')

num_particles = len(x)
density = num_particles / (Lx * Ly * Lz)
size = (Lx, Ly, Lz)
rc = 2.5
skin = 0.3
nvt = True
print "number of particles = ", num_particles
print "density = ", density

# compute the number of cells on each node
def calcNumberCells(size, nodes, rc):
    ncells = 1
    while size / (ncells * nodes) >= (rc + skin):
       ncells = ncells + 1
    return ncells - 1

system = espresso.System()
system.rng  = espresso.esutil.RNG()
system.bc = espresso.bc.OrthorhombicBC(system.rng, size)
system.skin = skin
comm = MPI.COMM_WORLD

nodeGrid = Int3D(1, 1, comm.size)
cellGrid = Int3D(
    calcNumberCells(size[0], nodeGrid[0], rc),
    calcNumberCells(size[1], nodeGrid[1], rc),
    calcNumberCells(size[2], nodeGrid[2], rc)
    )

print 'NodeGrid = %s' % (nodeGrid,)
print 'CellGrid = %s' % (cellGrid,)

system.storage = espresso.storage.DomainDecomposition(system, comm, nodeGrid, cellGrid)

if 0:
  pid = 0
  N = 0
  for i in range(N):
    for j in range(N):
      for k in range(N):
	m = (i + 2*j + 3*k) % 11
	r = 0.45 + m * 0.01
	x = (i + r) / N * size[0]
	y = (j + r) / N * size[1]
	z = (k + r) / N * size[2]
	x = 1.0 * i
	y = 1.0 * j
	z = 1.0 * k
	system.storage.addParticle(pid, Real3D(x, y, z))
	# not yet: dd.setVelocity(id, (1.0, 0.0, 0.0))
	pid = pid + 1

# add particles to the system
for pid in range(num_particles):
  system.storage.addParticle(pid + 1, Real3D(x[pid], y[pid], z[pid]))

# assign particles to processors then cells
system.storage.decompose()

# all particles interact via a LJ interaction (use Verlet lists)
vl = espresso.VerletList(system, cutoff=rc+system.skin)
potLJ = espresso.interaction.LennardJones(epsilon=1.0, sigma=1.0, cutoff=rc, shift=False)
interLJ = espresso.interaction.VerletListLennardJones(vl)
interLJ.setPotential(type1=0, type2=0, potential=potLJ)
system.addInteraction(interLJ)

# setup integrator
integrator = espresso.integrator.VelocityVerlet(system)
integrator.dt = 0.001

if(nvt):
  langevin = espresso.integrator.Langevin(system)
  integrator.langevin = langevin
  langevin.gamma = 1.0
  langevin.temperature = 1.0

# analysis
temperature = espresso.analysis.Temperature(system)
pressure = espresso.analysis.Pressure(system)
pressureTensor = espresso.analysis.PressureTensor(system)

T = temperature.compute()
P = pressure.compute()
Pij = pressureTensor.compute()
Ek = 0.5 * T * (3 * num_particles)
Ep = interLJ.computeEnergy()
sys.stdout.write(' step     T        P        Pxy       etotal     epotential    ekinetic\n')
sys.stdout.write('%5d %8.4f %10.5f %8.5f %12.3f %12.3f %12.3f\n' % (0, T, P, Pij[3], Ek + Ep, Ep, Ek))

integrator.run(10000)

T = temperature.compute()
P = pressure.compute()
Pij = pressureTensor.compute()
Ek = 0.5 * T * (3 * num_particles)
Ep = interLJ.computeEnergy()
sys.stdout.write('%5d %8.4f %10.5f %8.5f %12.3f %12.3f %12.3f\n' % (10000, T, P, Pij[3], Ek + Ep, Ep, Ek))
print "CPU time =", time.clock() - start_time, "s"
sys.exit()

nsteps = 10
intervals = 20
for i in range(1, intervals + 1):
  integrator.run(10)
  step = nsteps * i
  T = temperature.compute()
  P = pressure.compute()
  Pij = pressureTensor.compute()
  Ek = 0.5 * T * (3 * num_particles)
  Ep = interLJ.computeEnergy()
  sys.stdout.write('%5d %8.4f %10.5f %8.5f %12.3f %12.3f %12.3f\n' % (step, T, P, Pij[3], Ek + Ep, Ep, Ek))
