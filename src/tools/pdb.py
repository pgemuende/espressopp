import espresso
from math import sqrt
from espresso import Real3D

def pdbwrite(filename, system, molsize=4, append=False, typenames=None):
  #typenames: a map of typeid to typename to be written, e.g. for water typenames={0:'H', 1:'O'}
  if append:
    file = open(filename, 'a')
    s = "\n"  
  else:    
    file = open(filename,'w')
    s = "REMARK generated by ESPResSo++\n"  
  file.write(s)
  maxParticleID = int(espresso.analysis.MaxPID(system).compute())
  pid    = 0
  addToPid = 0 # if pid begins from 0, then addToPid should be +1
  mol    = 0
  molcnt = 0
  name='FE' # default name, overwritten when typenames map is given
  #following http://deposit.rcsb.org/adit/docs/pdb_atom_format.html#ATOM
  #crystal header
  st = "%-6s%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f %-11s%4d\n"%('CRYST1',system.bc.boxL[0],system.bc.boxL[1],system.bc.boxL[2],90.00,90.00,90,'P 1',1) #boxes are orthorhombic for now
  file.write(st)
  while pid <= maxParticleID:
    if system.storage.particleExists(pid):
      particle = system.storage.getParticle(pid)
      if(pid==0):
        addToPid = 1
      xpos   = particle.pos[0]
      ypos   = particle.pos[1]
      zpos   = particle.pos[2]
      type   = particle.type
      
      if typenames:
	  name=typenames[type]
      #st = "ATOM %6d  FE  UNX F%4d    %8.3f%8.3f%8.3f  0.00  0.00      T%03d\n"%(pid, mol, xpos, ypos, zpos, type)
      #following http://deposit.rcsb.org/adit/docs/pdb_atom_format.html#ATOM
      st = "%-6s%5d %-4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%6.2f%6.2f     T%04d%2s%2s\n"%('ATOM  ',pid+addToPid,name,'','UNX','F',mol%10000,'',xpos,ypos,zpos,0,0,mol%10000,'','')#the additional 'T' in the string is needed to be recognized as string,%10000 to obey the fixed-width format
      file.write(st)
      pid    += 1
      molcnt += 1
      if molcnt == molsize:  
        mol   += 1
        molcnt = 0
    else:
      pid   += 1
  
  file.write('END\n')
  file.close()

def fastwritepdb(filename, system, molsize=1000, append=False, folded=True):
  if append:
    file = open(filename, 'a')
    s = "\n"  
  else:    
    file = open(filename,'w')
    s = "REMARK generated by ESPResSo++\n"  
  file.write(s)
  mol    = 0
  molcnt = 0
  configurations = espresso.analysis.Configurations(system)
  configurations.gather()
  configuration = configurations[0]
  box_x = system.bc.boxL[0]
  box_y = system.bc.boxL[1]
  box_z = system.bc.boxL[2]
  #following http://deposit.rcsb.org/adit/docs/pdb_atom_format.html#ATOM
  #crystal header
  st = "%-6s%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f %-11s%4d\n"%('CRYST1',box_x, box_y, box_z, 90.00, 90.00, 90, 'P 1', 1) #boxes are orthorhombic for now
  file.write(st)
  for pid in configuration:
    if folded:
      pos       = espresso.Real3D(configuration[pid][0], configuration[pid][1], configuration[pid][2])
      foldedpos = system.bc.getFoldedPosition(pos)
      xpos      = foldedpos[0][0]
      ypos      = foldedpos[0][1]
      zpos      = foldedpos[0][2]
    else:
      xpos = configuration[pid][0]
      ypos = configuration[pid][1]
      zpos = configuration[pid][2]    
    st = "%-6s%5d %-4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%6.2f%6.2f     T%04d%2s%2s\n"%('ATOM  ',pid % 100000,'FE','','UNX','F',mol % 10000,'',xpos,ypos,zpos,0,0,mol %1000,'','')
    file.write(st)
    molcnt += 1
    if molcnt == molsize:  
      mol   += 1
      molcnt = 0
  file.write('END\n')
  file.close()

def pqrwrite(filename, system, molsize=4, append=False):
  if append:
    file = open(filename, 'a')
    s = "\n"  
  else:    
    file = open(filename,'w')
    s = "REMARK generated by ESPResSo++\n"  
  file.write(s)
  maxParticleID = int(espresso.analysis.MaxPID(system).compute())
  pid    = 0
  addToPid = 0 # if pid begins from 0, then addToPid should be +1
  mol    = 0
  molcnt = 0
  #following http://deposit.rcsb.org/adit/docs/pdb_atom_format.html#ATOM
  #crystal header
  st = "%-6s%9.3f%9.3f%9.3f%7.2f%7.2f%7.2f %-11s%4d\n"%('CRYST1',system.bc.boxL[0],system.bc.boxL[1],system.bc.boxL[2],90.00,90.00,90,'P 1',1) #boxes are orthorhombic for now
  file.write(st)
  while pid <= maxParticleID:
    if system.storage.particleExists(pid):
      particle = system.storage.getParticle(pid)
      if(pid==0):
        addToPid = 1
      xpos   = particle.pos[0]
      ypos   = particle.pos[1]
      zpos   = particle.pos[2]
      type   = particle.type
      q      = particle.q
      radius = particle.radius
      #st = "ATOM %6d  FE  UNX F%4d    %8.3f%8.3f%8.3f  0.00  0.00      T%03d\n"%(pid, mol, xpos, ypos, zpos, type)
      #following http://deposit.rcsb.org/adit/docs/pdb_atom_format.html#ATOM
      st = "%-6s%5d %-4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%8.3f%8.3f\n"%('ATOM  ',pid+addToPid,'FE','','UNX','F',mol%10000,'',xpos,ypos,zpos,q,radius)
  
      # ATOM      1  N   ALA     1      46.457  12.189  21.556  0.1414 1.8240
  
      file.write(st)
      pid    += 1
      molcnt += 1
      if molcnt == molsize:  
        mol   += 1
        molcnt = 0
    else:
      pid   += 1
  
  file.write('END\n')
  file.close()

def psfwrite(filename, system, maxdist=None, molsize=4, typenames=None):
  file = open(filename,'w')
  maxParticleID = int(espresso.analysis.MaxPID(system).compute())
  nParticles    = int(espresso.analysis.NPart(system).compute())
  file.write("PSF CMAP\n")
  st = "\n%8d !NATOM\n" % nParticles
  file.write(st)
  
  pid    = 0
  addToPid = 0 # if pid begins from 0, then addToPid should be +1
  mol    = 0
  molcnt = 0
  name='FE' # default name, overwritten when typenames map is given
  while pid <= maxParticleID:
    if system.storage.particleExists(pid):
      particle = system.storage.getParticle(pid)
      if(pid==0):
        addToPid = 1
      xpos   = particle.pos[0]
      ypos   = particle.pos[1]
      zpos   = particle.pos[2]
      type   = particle.type
      if typenames:
	  name=typenames[type]
      st = "%8d T%03d %4d UNX  %2s   %2s                    \n" % (pid+addToPid, type, mol, name, name)
      file.write(st)
      pid    += 1
      molcnt += 1
      if molcnt == molsize:
        mol   += 1
        molcnt = 0
    else:
      pid += 1

  bond = []
  nInteractions = system.getNumberOfInteractions()
  for i in range(nInteractions):
      if system.getInteraction(i).bondType() == espresso.interaction.Pair:
        try:
           
          FixedPairList = system.getInteraction(i).getFixedPairList().getBonds()
          j = 0
          while j < len(FixedPairList):
              fplb = FixedPairList[j]
              k = 0
              while k < len(fplb):
                if maxdist != None:
                  pid1 = fplb[k][0]
                  pid2 = fplb[k][1]
                  p1 = system.storage.getParticle(pid1)
                  p2 = system.storage.getParticle(pid2)
                  x1 = p1.pos[0]
                  y1 = p1.pos[1]
                  z1 = p1.pos[2]
                  x2 = p2.pos[0]
                  y2 = p2.pos[1]
                  z2 = p2.pos[2]
                  xx = (x1-x2) * (x1-x2)
                  yy = (y1-y2) * (y1-y2)
                  zz = (z1-z2) * (z1-z2)
                  d = sqrt( xx + yy + zz )
                  if (d <= maxdist):
                    bond.append(fplb[k])
                else:
                  bond.append(fplb[k])
                k += 1
                
              j += 1
              
        except:
          pass
              
  bond.sort()

  file.write("\n%8d !NBOND:\n" % (len(bond)))
  i = 0
  while i < len(bond):
    file.write("%8d%8d" % (bond[i][0]+addToPid, bond[i][1]+addToPid) ) #pid_count_translate[bond[i][1]]
    if ( ((i+1) % 4) == 0 and (i != 0) ) or i == len(bond)-1 :
      file.write("\n")
    i += 1

  file.write('END\n')
  file.close()
  
  
  
  """
  NOT finished yet - working on that see lammps.write how to do this!
   
  bonds     = []
  angles    = []
  dihedrals = [] 
  nInteractions = system.getNumberOfInteractions()
  for i in range(nInteractions):
      bT = system.getInteraction.bondType
      if   bT == espresso.interaction.Pair:
             bl = system.getInteraction(i).getFixedPairList().getBonds
             for j in range(len(bl)):
               bonds.extend(bl[j])
      elif bT == espresso.interaction.Angle:
             an = system.getInteraction(i).getFixedTripleList().getTriples
             for j in range(len(an)):
               angles.extend(an[j])
      elif bT == espresso.interaction.Dihedral:
             di = system.getInteraction(i).getFixedQuadrupleList().getQuadruples
             for j in range(len(di)):
               dihedrals.extend(di[j])
  
  nbonds     = len(bonds)
  nangles    = len(angles)
  ndihedrals = len(dihedrals)
"""
  
