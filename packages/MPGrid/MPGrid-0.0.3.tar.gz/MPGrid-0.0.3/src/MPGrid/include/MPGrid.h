#ifndef _MPGRID_H
#define _MPGRID_H

#ifdef __cplusplus
extern "C" {
#endif

#ifndef FALSE
#define FALSE 0
#endif
#ifndef TRUE
#define TRUE 1
#endif
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifdef MP_PYTHON_LIB
#ifndef Py_PYTHON_H
#include <Python.h>
#endif
#ifndef Py_STRUCTMEMBER_H
#include <structmember.h>
#endif
#endif
#ifndef _INC_STDIO
#include <stdio.h>
#endif
#ifndef _INC_STDLIB
#include <stdlib.h>
#endif
#ifndef _INC_STRING
#include <string.h>
#endif
#ifndef _INC_MATH
#include <math.h>
#endif
#ifdef WIN32
#pragma warning(disable:4996)
#include <windows.h>
#endif

#ifdef _OPENMP
#include <omp.h>
#endif

/*--------------------------------------------------
	grid typedef and functions
*/
#define MP_GRID_INDEX(d,x,y,z) (x+(y)*d->size[0]+(z)*d->size[0]*d->size[1])
#define MP_GRID_COEF_INDEX(d,i,j) (i+(j)*d->ntype)

enum { MP_GridBoundInsulate, MP_GridBoundPeriodic };
enum { MP_GridInterCond, MP_GridInterTrans };

typedef struct MP_GridData {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	int size[3];
	double element[3];
	int ntot;
	int ntype;
	short *type;
	short *update;
	double *val;
	double *buf;
	double *cx, *cy, *cz;
	int *inter_x, *inter_y, *inter_z;
	double *coef_x, *coef_y, *coef_z;
	double *rhoc;
	int bound[6];
	int step;
	long rand_seed;
	int local_coef;
} MP_GridData;

int MP_GridAlloc(MP_GridData *data, int nx, int ny, int nz, int ntype, int local_coef);
void MP_GridFree(MP_GridData *data);
void MP_GridElementFlow(MP_GridData* data, int id, double f[]);
double MP_GridMeanFlow(MP_GridData *data);
double MP_GridSolve(MP_GridData *data, double dt, int nloop);
double MP_GridEstimateDt(MP_GridData *data, double ratio);
int MP_GridSetInter1(MP_GridData *data, int inter, int i, int j);
int MP_GridSetInter3(MP_GridData *data, int inter[], int i, int j);
int MP_GridSetCoef1(MP_GridData *data, double coef, int i, int j);
int MP_GridSetCoef3(MP_GridData *data, double coef[], int i, int j);
int MP_GridSetInterCoef1(MP_GridData *data, int inter, double coef, int i, int j);
int MP_GridSetInterCoef3(MP_GridData *data, int inter[], double coef[], int i, int j);
void MP_GridRefLocalCoef(MP_GridData *data);
void MP_GridSetLocalCoef1(MP_GridData *data, double lcoef, short type0, short type1);
void MP_GridSetLocalCoef3(MP_GridData *data, double lcoef[], short type0, short type1);
int MP_GridFillType(MP_GridData *data, short type,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridFillUpdate(MP_GridData *data, short update,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridFillVal(MP_GridData *data, double val,
	int x0, int y0, int z0, int x1, int y1, int z1);
void MP_GridGradVal(MP_GridData* data, int dir, double v0, double v1);
int MP_GridFillLocalCoef(MP_GridData *data, double cx, double cy, double cz,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridEllipsoidType(MP_GridData *data, short type,
	int x0, int y0, int z0, int x1, int y1, int z1, double margin);
int MP_GridEllipsoidUpdate(MP_GridData *data, short update,
	int x0, int y0, int z0, int x1, int y1, int z1, double margin);
int MP_GridEllipsoidVal(MP_GridData *data, double val,
	int x0, int y0, int z0, int x1, int y1, int z1, double margin);
int MP_GridCylinderType(MP_GridData *data, short type,
	int x0, int y0, int z0, int x1, int y1, int z1, int dir, double margin);
int MP_GridCylinderUpdate(MP_GridData *data, short update,
	int x0, int y0, int z0, int x1, int y1, int z1, int dir, double margin);
int MP_GridCylinderVal(MP_GridData *data, double val,
	int x0, int y0, int z0, int x1, int y1, int z1, int dir, double margin);
double MP_GridAveVal(MP_GridData *data,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridCountType(MP_GridData *data, short type,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridUniformRandom(MP_GridData *data, short type, int num,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridGaussRandom(MP_GridData *data, short type, int num, double spdis,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridWrite(MP_GridData *data, char *filename, int comp);
int MP_GridRead(MP_GridData *data, char *filename, int version);
int MP_GridCopy(MP_GridData *src, MP_GridData *dst,
	int x0, int y0, int z0, int x1, int y1, int z1);
int MP_GridClone(MP_GridData *src, MP_GridData *dst);

/*--------------------------------------------------
	cg typedef and functions
*/
typedef struct MP_GridCG {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	double *dval;
	double *g;
	double *h;
} MP_GridCG;

int MP_GridCGAlloc(MP_GridCG* cg, MP_GridData* data);
void MP_GridCGFree(MP_GridCG* cg);
double MP_GridCGSolve(MP_GridCG* cg, MP_GridData* data, double dt, int nloop);

/*--------------------------------------------------
	rand functions
*/
float MP_Rand(long *rand_seed);
float MP_RandGauss(long *rand_seed);

#ifdef __cplusplus
}
#endif

#endif /* _MPGRID_H */
