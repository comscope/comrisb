include ../../../../Makefile.in

# FFLAGS = -O0 -check bound -check pointer -check arg_temp_created \
		-traceback


obj = GPREC.o \
	  GTIME.o \
	  GCONSTANT.o \
	  GMPI.o \
	  GHDF5.o \
	  GPRIMME.o \
	  UTIL.o \
	  CORRORB.o \
	  LOCALSTORE.o \
	  LOCALSTDER.o \
	  BANDSTRU.o \
	  BANDSDER.o \
	  DCSTD.o \
	  fermi.o  \
	  GKERNEL.o  \
	  GKERDER.o


LIB = ../../../lib/libprimme.a
INCLUDE=-I../../../include

all: ${obj} GERR.o
	${PF90} -cpp ${Fmpi_define} -Dreal_version ${FFLAGS} -o CyGErrR GERR.o \
		${obj} ${MKL_LIB} ${LIB}

GPRIMME.o: ../../GPRIMME.f90
	${F90} ${FIX_FORM} ${FFLAGS} -cpp -Dreal_version -c $< $(INCLUDE)

%.o: ../%.f90
	${PF90} ${FREE_FORM} ${FFLAGS} -cpp ${Fmpi_define} -Dreal_version \
            -c $< $(INCLUDE)

%.o: ../../%.f90
	${PF90} ${FREE_FORM} ${FFLAGS} -cpp ${Fmpi_define} ${Fstd_define} \
			-Dreal_version -c $< $(INCLUDE)

clean:
	rm -f *o *mod *out

clean_all:
	rm -f *o *mod *out CyGErrR

install:
	cp CyGErrR ${DESTDIR}
