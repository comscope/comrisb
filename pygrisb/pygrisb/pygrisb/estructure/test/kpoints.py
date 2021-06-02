import numpy


def kpoint_plane(fname="k2dvertices.inp"):
    vertices = numpy.ones([3,6], dtype=numpy.int)
    with open(fname, "r") as f:
        '''
provide three vertices which defines a 2d plane, e.g.
-1/2 -1/2 0    # A
 1/2 -1/2 0    # B
-1/2  1/2 0    # C
10 10          # mesh size along AB and AC
D is natually defined by vector addition AD = AB + AC.
        '''
        lines = f.readlines()
        for i, line in enumerate(lines[:3]):
            # split by finger space
            elements = line.split()
            for j, element in enumerate(elements):
                es = element.split("/")
                for k, e in enumerate(es):
                    vertices[i, j*2+k] = int(e)
        # divisions
        line  = lines[3].split()
        nab, nac = int(line[0]), int(line[1])
    # leastr common multiple of the denominators
    lcm = numpy.lcm.reduce(vertices[:, 1::2].reshape(-1))



def make_kline(frsb,outf,lab0,lab1,n0,d0,n1,d1,ndiv):
   # split the path from n0/d0 to n1/d1 into ndiv intervals
   # and printout as fractions with common divisor
   lcm1 = lcm(d1[1],d0[1])
   lcm2 = lcm(d1[2],d0[2])
   lcm3 = lcm(d1[3],d0[3])
   lcm12 = lcm(lcm1,lcm2)
   lcm123 = lcm(lcm12,lcm3)  # Least common divisor of all d0[] and d1[]
   for ic in range(1,4):
      m0[ic] = n0[ic]*ndiv*lcm123/d0[ic]
      m1[ic] = n1[ic]*ndiv*lcm123/d1[ic]
      dm[ic] = (m1[ic]-m0[ic])/ndiv

   if (frsb):
      z1 = "%-10s"% (lab0)   # left-bound formatting of a string
      for ic in range(1,4):
         elem = "%5i"% (m0[ic])
         z1 = z1 + elem

      elem = "%5i  2.0-2.00 2.00  : Generated by make_klist.py "% (lcm123*ndiv)
      z1 = z1 + elem
      outf.write(z1)
      outf.write("\n")

   for il in range(1,ndiv):   #  Loop over intermediate points (between labels)
      z1 = "%10s"% ''         #  Empty 10 pos. at the begin of line
      for ic in range(1,4):
         elem = "%5i"% (m0[ic]+dm[ic]*il)
         z1 = z1 + elem
      elem = "%5i  2.0"% (lcm123*ndiv)
      z1 = z1 + elem
      outf.write(z1)
      outf.write("\n")

   z1 = "%-10s"% (lab1)   # left-bound formatting of a string
   for ic in range(1,4):
      elem = "%5i"% (m1[ic])
      z1 = z1 + elem

   elem = "%5i  2.0"% (lcm123*ndiv)
   z1 = z1 + elem
   outf.write(z1)
   outf.write("\n")
   return

# Declare arrays for numerators ans denominantors:
n1 = array('i',[1,1,1,1])
n0 = array('i',[1,1,1,1])
d1 = array('i',[1,1,1,1])
d0 = array('i',[1,1,1,1])
m0 = array('i',[1,1,1,1])
m1 = array('i',[1,1,1,1])
dm = array('i',[1,1,1,1])
outf = open("KLIST_band","w")  # file to write generated k-list
frsb = True  #  to mark the first block between two labels
frsl = True  #  to mark the first encountered line with label

# Iinquire for input data file and read it in:
data_file = raw_input(' Input file with corner points and Nr of intervals: ')
with open(data_file) as f:
   lines = f.readlines();
   for il in lines:
      thisline = il.split(); # split line into words, ignoring spaces
      if thisline[0].isdigit():
         ndiv = int(thisline[0])  # The first element of line is integer;
         #  assume is is the number of divisions, ignore the rest of line
      else:
         lab1 = thisline[0] # The first element of line is labl;
         #  the tree following must be integer or frac coordinates
         for ic in range(1,4): # to scan elements 2,3,4 of the line
            if ('/' in thisline[ic]):
               fract = thisline[ic].split("/") # extract [n1]./denom.
               n1[ic] = int(fract[0])  # integer numerator
               d1[ic] = int(fract[1])  # integer denominator
            else:
               n1[ic] = int(thisline[ic])  # just the integer number,
               d1[ic] = 1                  # the denominator assumed =1
         if (frsl):
            frsl = False
         else:
            make_kline(frsb,outf,lab0,lab1,n0,d0,n1,d1,ndiv)
            frsb = False

         n0[:] = n1[:]
         d0[:] = d1[:]
         lab0 = lab1

outf.write("END\n")
outf.close()
