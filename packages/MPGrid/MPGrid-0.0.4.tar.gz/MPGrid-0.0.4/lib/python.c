#ifdef MP_PYTHON_LIB

#include "MPGrid.h"

#if PY_MAJOR_VERSION >= 3
#define PY3
#endif

static void PyGridDealloc(MP_GridData* self)
{
	MP_GridFree(self);
#ifndef PY3
	self->ob_type->tp_free((PyObject*)self);
#endif
}

static PyObject *PyGridNewNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	int nx, ny, nz, ntype;
	int local_coef = FALSE;
	static char *kwlist[] = { "nx", "ny", "nz", "ntype", "local_coef", NULL };
	MP_GridData *self;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iiii|i", kwlist, &nx, &ny, &nz, &ntype, &local_coef)) {
		return NULL;
	}
	self = (MP_GridData *)type->tp_alloc(type, 0);
	if (self != NULL) {
		if (!MP_GridAlloc(self, nx, ny, nz, ntype, local_coef)) {
			Py_DECREF(self);
			return NULL;
		}
	}
	return (PyObject *)self;
}

static PyObject *PyGridReadNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	char *fname;
	int version = 2;
	static char *kwlist[] = { "fname", "version", NULL };
	MP_GridData *self;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|i", kwlist, &fname, &version)) {
		return NULL;
	}
	self = (MP_GridData *)type->tp_alloc(type, 0);
	if (self != NULL) {
		if (!MP_GridRead(self, fname, version)) {
			Py_DECREF(self);
			return NULL;
		}
	}
	return (PyObject *)self;
}

static PyObject *PyGridCopyNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	MP_GridData *grid;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "grid", "pos0", "pos1", NULL };
	MP_GridData *self;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O(iii)(iii)",
		kwlist, &grid, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	self = (MP_GridData *)type->tp_alloc(type, 0);
	if (self != NULL) {
		if (!MP_GridCopy(grid, self, x0, y0, z0, x1, y1, z1)) {
			Py_DECREF(self);
			return NULL;
		}
	}
	return (PyObject *)self;
}

static PyObject *PyGridCloneNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	MP_GridData *grid;
	static char *kwlist[] = { "grid", NULL };
	MP_GridData *self;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &grid)) {
		return NULL;
	}
	self = (MP_GridData *)type->tp_alloc(type, 0);
	if (self != NULL) {
		if (!MP_GridClone(grid, self)) {
			Py_DECREF(self);
			return NULL;
		}
	}
	return (PyObject *)self;
}

static PyMemberDef PyGridMembers[] = {
	{ "ntot", T_INT, offsetof(MP_GridData, ntot), 1, "total number of allocated elements" },
	{ "ntype", T_INT, offsetof(MP_GridData, ntype), 1, "number of type" },
	{ "step", T_INT, offsetof(MP_GridData, step), 1, "step" },
	{ "rand_seed", T_LONG, offsetof(MP_GridData, rand_seed), 0, "seed of random number" },
	{ "local_coef", T_INT, offsetof(MP_GridData, local_coef), 1, "flag of local coefficient mode" },
	{ NULL }  /* Sentinel */
};

static PyObject* PyGridElementFlow(MP_GridData* self, PyObject* args, PyObject* kwds)
{
	int id;
	static char* kwlist[] = { "id", NULL };
	double f[3];

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &id)) {
		return NULL;
	}
	MP_GridElementFlow(self, id, f);
	return Py_BuildValue("ddd", f[0], f[1], f[2]);
}

static PyObject* PyGridMeanFlow(MP_GridData* self, PyObject* args)
{
	return Py_BuildValue("d", MP_GridMeanFlow(self));
}

static PyObject *PyGridSolve(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double dt;
	int nloop;
	static char *kwlist[] = { "dt", "nloop", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "di", kwlist, &dt, &nloop)) {
		return NULL;
	}
	return Py_BuildValue("d", MP_GridSolve(self, dt, nloop));
}

static PyObject *PyGridEstimateDt(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double ratio = 1.0;
	static char *kwlist[] = { "ratio", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "|d", kwlist, &ratio)) {
		return NULL;
	}
	return Py_BuildValue("d", MP_GridEstimateDt(self, ratio));
}

static PyObject *PyGridGetType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int x, y, z, id;
	static char *kwlist[] = { "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)", kwlist, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		return Py_BuildValue("i", self->type[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
}

static PyObject *PyGridSetType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int x, y, z, id;
	static char *kwlist[] = { "type", "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)", kwlist, &type, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		if (type >= 0 && type < self->ntype) {
			self->type[id] = type;
		}
		else {
			PyErr_SetString(PyExc_ValueError, "invalid type");
			return NULL;
		}
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridFillType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "type", "pos0", "pos1", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)", kwlist, &type, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	if (type >= 0 && type < self->ntype) {
		count = MP_GridFillType(self, type, x0, y0, z0, x1, y1, z1);
		return Py_BuildValue("i", count);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid type");
		return NULL;
	}
}

static PyObject *PyGridEllipsoidType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int x0, y0, z0, x1, y1, z1;
	double margin = 0.33;
	static char *kwlist[] = { "type", "pos0", "pos1", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)|d", kwlist, &type, &x0, &y0, &z0, &x1, &y1, &z1, &margin)) {
		return NULL;
	}
	if (type >= 0 && type < self->ntype) {
		count = MP_GridEllipsoidType(self, type, x0, y0, z0, x1, y1, z1, margin);
		return Py_BuildValue("i", count);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid type");
		return NULL;
	}
}

static PyObject *PyGridCylinderType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int x0, y0, z0, x1, y1, z1;
	int dir;
	double margin = 0.33;
	static char *kwlist[] = { "type", "pos0", "pos1", "dir", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)i|d", kwlist, &type, &x0, &y0, &z0, &x1, &y1, &z1, &dir, &margin)) {
		return NULL;
	}
	if (type >= 0 && type < self->ntype) {
		count = MP_GridCylinderType(self, type, x0, y0, z0, x1, y1, z1, dir, margin);
		return Py_BuildValue("i", count);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid type");
		return NULL;
	}
}

static PyObject *PyGridGetUpdate(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int x, y, z, id;
	static char *kwlist[] = { "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)", kwlist, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		return Py_BuildValue("i", self->update[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
}

static PyObject *PyGridSetUpdate(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short update;
	int x, y, z, id;
	static char *kwlist[] = { "update", "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)", kwlist, &update, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		self->update[id] = update;
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridFillUpdate(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short update;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "update", "pos0", "pos1", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)", kwlist, &update, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	count = MP_GridFillUpdate(self, update, x0, y0, z0, x1, y1, z1);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridEllipsoidUpdate(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short update;
	int x0, y0, z0, x1, y1, z1;
	double margin = 0.33;
	static char *kwlist[] = { "update", "pos0", "pos1", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)|d", kwlist, &update, &x0, &y0, &z0, &x1, &y1, &z1, &margin)) {
		return NULL;
	}
	count = MP_GridEllipsoidUpdate(self, update, x0, y0, z0, x1, y1, z1, margin);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridCylinderUpdate(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short update;
	int x0, y0, z0, x1, y1, z1;
	int dir;
	double margin = 0.33;
	static char *kwlist[] = { "update", "pos0", "pos1", "dir", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)i|d", kwlist, &update, &x0, &y0, &z0, &x1, &y1, &z1, &dir, &margin)) {
		return NULL;
	}
	count = MP_GridCylinderUpdate(self, update, x0, y0, z0, x1, y1, z1, dir, margin);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridGetVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int x, y, z, id;
	static char *kwlist[] = { "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)", kwlist, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		return Py_BuildValue("d", self->val[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
}

static PyObject *PyGridSetVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double val;
	int x, y, z, id;
	static char *kwlist[] = { "val", "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "d(iii)", kwlist, &val, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		self->val[id] = val;
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridFillVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double val;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "val", "pos0", "pos1", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "d(iii)(iii)", kwlist, &val, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	count = MP_GridFillVal(self, val, x0, y0, z0, x1, y1, z1);
	return Py_BuildValue("i", count);
}

static PyObject* PyGridGradVal(MP_GridData* self, PyObject* args, PyObject* kwds)
{
	int dir;
	double v0, v1;
	static char* kwlist[] = { "dir", "v0", "v1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "idd", kwlist, &dir, &v0, &v1)) {
		return NULL;
	}
	MP_GridGradVal(self, dir, v0, v1);
	Py_RETURN_NONE;
}

static PyObject *PyGridEllipsoidVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double val;
	int x0, y0, z0, x1, y1, z1;
	double margin = 0.33;
	static char *kwlist[] = { "val", "pos0", "pos1", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "d(iii)(iii)|d", kwlist, &val, &x0, &y0, &z0, &x1, &y1, &z1, &margin)) {
		return NULL;
	}
	count = MP_GridEllipsoidVal(self, val, x0, y0, z0, x1, y1, z1, margin);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridCylinderVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double val;
	int x0, y0, z0, x1, y1, z1;
	int dir;
	double margin = 0.33;
	static char *kwlist[] = { "val", "pos0", "pos1", "dir", "margin", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "d(iii)(iii)i|d", kwlist, &val, &x0, &y0, &z0, &x1, &y1, &z1, &dir, &margin)) {
		return NULL;
	}
	count = MP_GridCylinderVal(self, val, x0, y0, z0, x1, y1, z1, dir, margin);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridGetLocalCoef(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int x, y, z, id;
	static char *kwlist[] = { "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)", kwlist, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		return Py_BuildValue("(ddd)", self->cx[id], self->cy[id], self->cz[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
}

static PyObject *PyGridSetLocalCoef(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double cx, cy, cz;
	int x, y, z, id;
	static char *kwlist[] = { "lcoef", "pos", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(ddd)(iii)", kwlist,
		&cx, &cy, &cz, &x, &y, &z)) {
		return NULL;
	}
	id = MP_GRID_INDEX(self, x, y, z);
	if (id >= 0 && id < self->ntot) {
		self->cx[id] = cx;
		self->cy[id] = cy;
		self->cz[id] = cz;
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid pos");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridFillLocalCoef(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double cx, cy, cz;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "lcoef", "pos0", "pos1", NULL };
	int count;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(ddd)(iii)(iii)", kwlist,
		&cx, &cy, &cz, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	count = MP_GridFillLocalCoef(self, cx, cy, cz, x0, y0, z0, x1, y1, z1);
	return Py_BuildValue("i", count);
}

static PyObject *PyGridGetInter(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int i, j, id;
	static char *kwlist[] = { "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &i, &j)) {
		return NULL;
	}
	id = MP_GRID_COEF_INDEX(self, i, j);
	if (id >= 0 && id < self->ntype*self->ntype) {
		return Py_BuildValue("iii", self->inter_x[id], self->inter_y[id], self->inter_z[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
}

static PyObject *PyGridSetInter1(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int inter;
	int i, j;
	static char *kwlist[] = { "inter", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iii", kwlist, &inter, &i, &j)) {
		return NULL;
	}
	if (MP_GridSetInter1(self, inter, i, j) < 0) {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridSetInter3(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int inter[3];
	int i, j;
	static char *kwlist[] = { "inter", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)ii", kwlist, &(inter[0]), &(inter[1]), &(inter[2]), &i, &j)) {
		return NULL;
	}
	if (MP_GridSetInter3(self, inter, i, j) < 0){
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridGetCoef(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int i, j, id;
	static char *kwlist[] = { "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &i, &j)) {
		return NULL;
	}
	id = MP_GRID_COEF_INDEX(self, i, j);
	if (id >= 0 && id < self->ntype*self->ntype) {
		return Py_BuildValue("ddd", self->coef_x[id], self->coef_y[id], self->coef_z[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
}

static PyObject *PyGridSetCoef1(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double coef;
	int i, j;
	static char *kwlist[] = { "coef", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "dii", kwlist, &coef, &i, &j)) {
		return NULL;
	}
	if (MP_GridSetCoef1(self, coef, i, j) < 0) {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridSetCoef3(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double coef[3];
	int i, j;
	static char *kwlist[] = { "coef", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(ddd)ii", kwlist, &(coef[0]), &(coef[1]), &(coef[2]), &i, &j)) {
		return NULL;
	}
	if (MP_GridSetCoef3(self, coef, i, j) < 0) {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridGetInterCoef(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int i, j, id;
	static char *kwlist[] = { "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &i, &j)) {
		return NULL;
	}
	id = MP_GRID_COEF_INDEX(self, i, j);
	if (id >= 0 && id < self->ntype*self->ntype) {
		return Py_BuildValue("(iii)(ddd)", self->inter_x[id], self->inter_y[id], self->inter_z[id],
			self->coef_x[id], self->coef_y[id], self->coef_z[id]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
}

static PyObject *PyGridSetInterCoef1(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int inter;
	double coef;
	int i, j;
	static char *kwlist[] = { "inter", "coef", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "idii", kwlist, &inter, &coef, &i, &j)) {
		return NULL;
	}
	if (MP_GridSetInterCoef1(self, inter, coef, i, j) < 0) {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridSetInterCoef3(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int inter[3];
	double coef[3];
	int i, j;
	static char *kwlist[] = { "inter", "coef", "i", "j", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)(ddd)ii", kwlist,
		&(inter[0]), &(inter[1]), &(inter[2]), &(coef[0]), &(coef[1]), &(coef[2]), &i, &j)) {
		return NULL;
	}
	if (MP_GridSetInterCoef3(self, inter, coef, i, j) < 0) {
		PyErr_SetString(PyExc_ValueError, "invalid i, j");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridRefLocalCoef(MP_GridData *self, PyObject *args)
{
	MP_GridRefLocalCoef(self);
	Py_RETURN_NONE;
}

static PyObject *PyGridSetLocalCoef1(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double lcoef;
	short type0, type1;
	static char *kwlist[] = { "lcoef", "type0", "type1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "dhh", kwlist, &lcoef, &type0, &type1)) {
		return NULL;
	}
	MP_GridSetLocalCoef1(self, lcoef, type0, type1);
	Py_RETURN_NONE;
}

static PyObject *PyGridSetLocalCoef3(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double lcoef[3];
	short type0, type1;
	static char *kwlist[] = { "lcoef", "type0", "type1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(ddd)hh", kwlist,
		&(lcoef[0]), &(lcoef[1]), &(lcoef[2]), &type0, &type1)) {
		return NULL;
	}
	MP_GridSetLocalCoef3(self, lcoef, type0, type1);
	Py_RETURN_NONE;
}

static PyObject *PyGridGetRhoc(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int i;
	static char *kwlist[] = { "i", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &i)) {
		return NULL;
	}
	if (i >= 0 && i < self->ntype) {
		return Py_BuildValue("d", self->rhoc[i]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid i");
		return NULL;
	}
}

static PyObject *PyGridSetRhoc(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	double rhoc;
	int i;
	static char *kwlist[] = { "rhoc", "i", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "di", kwlist, &rhoc, &i)) {
		return NULL;
	}
	if (i >= 0 && i < self->ntype) {
		self->rhoc[i] = rhoc;
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid i");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject *PyGridAveVal(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "pos0", "pos1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)(iii)", kwlist, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	return Py_BuildValue("d", MP_GridAveVal(self, x0, y0, z0, x1, y1, z1));
}

static PyObject *PyGridCountType(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "type", "pos0", "pos1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "h(iii)(iii)", kwlist, &type, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	return Py_BuildValue("i",
		MP_GridCountType(self, type, x0, y0, z0, x1, y1, z1));
}

static PyObject *PyGridUniformRandom(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int num;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "type", "num", "pos0", "pos1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "hi(iii)(iii)", kwlist, &type, &num, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	return Py_BuildValue("i",
		MP_GridUniformRandom(self, type, num, x0, y0, z0, x1, y1, z1));
}

static PyObject *PyGridGaussRandom(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	short type;
	int num;
	double spdis;
	int x0, y0, z0, x1, y1, z1;
	static char *kwlist[] = { "type", "num", "spdis", "pos0", "pos1", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "hid(iii)(iii)", kwlist, &type, &num, &spdis, &x0, &y0, &z0, &x1, &y1, &z1)) {
		return NULL;
	}
	return Py_BuildValue("i",
		MP_GridGaussRandom(self, type, num, spdis, x0, y0, z0, x1, y1, z1));
}

static PyObject *PyGridWrite(MP_GridData *self, PyObject *args, PyObject *kwds)
{
	char *fname;
	int comp;
	static char *kwlist[] = { "fname", "comp", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "si", kwlist, &fname, &comp)) {
		return NULL;
	}
	if (!MP_GridWrite(self, fname, comp)) {
		PyErr_SetString(PyExc_ValueError, "write failure");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef PyGridMethods[] = {
	{ "element_flow", (PyCFunction)PyGridElementFlow, METH_VARARGS | METH_KEYWORDS,
	"element_fow(id) : return flow of an element" },
	{ "mean_flow", (PyCFunction)PyGridMeanFlow, METH_NOARGS,
	"mean_flow() : return mean flow of elements" },
	{ "solve", (PyCFunction)PyGridSolve, METH_VARARGS | METH_KEYWORDS,
	"solve(dt, nloop) : solve" },
	{ "estimate_dt", (PyCFunction)PyGridEstimateDt, METH_VARARGS | METH_KEYWORDS,
	"estimate_dt([ratio=1.0]) : estimate dt" },
	{ "get_type", (PyCFunction)PyGridGetType, METH_VARARGS | METH_KEYWORDS,
	"get_type((x, y, z)) : get type" },
	{ "set_type", (PyCFunction)PyGridSetType, METH_VARARGS | METH_KEYWORDS,
	"set_type(type, (x, y, z)) : set type" },
	{ "fill_type", (PyCFunction)PyGridFillType, METH_VARARGS | METH_KEYWORDS,
	"fill_type(type, (x0, y0, z0), (x1, y1, z1)) : fill type"},
	{ "ellipsoid_type", (PyCFunction)PyGridEllipsoidType, METH_VARARGS | METH_KEYWORDS,
	"ellipsoid_type(type, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill type in ellipsoid shape" },
	{ "cylinder_type", (PyCFunction)PyGridCylinderType, METH_VARARGS | METH_KEYWORDS,
	"cylinder_type(type, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill type in cylinder shape" },
	{ "get_update", (PyCFunction)PyGridGetUpdate, METH_VARARGS | METH_KEYWORDS,
	"get_update((x, y, z)) : get update" },
	{ "set_update", (PyCFunction)PyGridSetUpdate, METH_VARARGS | METH_KEYWORDS,
	"set_update(update, (x, y, z)) : set update" },
	{ "fill_update", (PyCFunction)PyGridFillUpdate, METH_VARARGS | METH_KEYWORDS,
	"fill_update(update, (x0, y0, z0), (x1, y1, z1)) : fill update" },
	{ "ellipsoid_update", (PyCFunction)PyGridEllipsoidUpdate, METH_VARARGS | METH_KEYWORDS,
	"ellipsoid_update(update, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill update in ellipsoid shape" },
	{ "cylinder_update", (PyCFunction)PyGridCylinderUpdate, METH_VARARGS | METH_KEYWORDS,
	"cylinder_update(update, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill update in cylinder shape" },
	{ "get_val", (PyCFunction)PyGridGetVal, METH_VARARGS | METH_KEYWORDS,
	"get_val((x, y, z)) : get value" },
	{ "set_val", (PyCFunction)PyGridSetVal, METH_VARARGS | METH_KEYWORDS,
	"set_val(val, (x, y, z)) : set value" },
	{ "fill_val", (PyCFunction)PyGridFillVal, METH_VARARGS | METH_KEYWORDS,
	"fill_val(val, (x0, y0, z0), (x1, y1, z1)) : fill value" },
	{ "grad_val", (PyCFunction)PyGridGradVal, METH_VARARGS | METH_KEYWORDS,
	"grad_val(val, v0, v1) : fill gradation value" },
	{ "ellipsoid_val", (PyCFunction)PyGridEllipsoidVal, METH_VARARGS | METH_KEYWORDS,
	"ellipsoid_val(val, (x0, y0, z0), (x1, y1, z1), [margin=0.33]) : fill value in ellipsoid shape" },
	{ "cylinder_val", (PyCFunction)PyGridCylinderVal, METH_VARARGS | METH_KEYWORDS,
	"cylinder_val(val, (x0, y0, z0), (x1, y1, z1), dir, [margin=0.33]) : fill value in cylinder shape" },
	{ "get_local_coef", (PyCFunction)PyGridGetLocalCoef, METH_VARARGS | METH_KEYWORDS,
	"get_local_coef((x, y, z)) : get local coefficient" },
	{ "set_local_coef", (PyCFunction)PyGridSetLocalCoef, METH_VARARGS | METH_KEYWORDS,
	"set_local_coef((cx, cy, cz), (x, y, z)) : set local coefficient" },
	{ "fill_local_coef", (PyCFunction)PyGridFillLocalCoef, METH_VARARGS | METH_KEYWORDS,
	"fill_local_coef((cx, cy, cz), (x0, y0, z0), (x1, y1, z1)) : fill value" },
	{ "get_inter", (PyCFunction)PyGridGetInter, METH_VARARGS | METH_KEYWORDS,
	"get_inter(i, j) : get interface type" },
	{ "set_inter1", (PyCFunction)PyGridSetInter1, METH_VARARGS | METH_KEYWORDS,
	"set_inter1(inter, i, j) : set interface type" },
	{ "set_inter3", (PyCFunction)PyGridSetInter3, METH_VARARGS | METH_KEYWORDS,
	"set_inter3((inter_x, inter_y, inter_z), i, j) : set interface type" },
	{ "get_coef", (PyCFunction)PyGridGetCoef, METH_VARARGS | METH_KEYWORDS,
	"get_coef(i, j) : get coefficient" },
	{ "set_coef1", (PyCFunction)PyGridSetCoef1, METH_VARARGS | METH_KEYWORDS,
	"set_coef1(coef, i, j) : set coefficient" },
	{ "set_coef3", (PyCFunction)PyGridSetCoef3, METH_VARARGS | METH_KEYWORDS,
	"set_coef3((coef_x, coef_y, coef_z), i, j) : set coefficient" },
	{ "get_inter_coef", (PyCFunction)PyGridGetInterCoef, METH_VARARGS | METH_KEYWORDS,
	"get_inter_coef(i, j) : get interface type and coefficient" },
	{ "set_inter_coef1", (PyCFunction)PyGridSetInterCoef1, METH_VARARGS | METH_KEYWORDS,
	"set_inter_coef1(inter, coef, i, j) : set interface type and coefficient" },
	{ "set_inter_coef3", (PyCFunction)PyGridSetInterCoef3, METH_VARARGS | METH_KEYWORDS,
	"set_inter_coef3((inter_x, inter_y, inter_z), (coef_x, coef_y, coef_z), i, j) : set interface type and coefficient" },
	{ "ref_local_coef", (PyCFunction)PyGridRefLocalCoef, METH_NOARGS,
	"ref_local_coef() : reflect local coefficient with coefficient table" },
	{ "set_local_coef1", (PyCFunction)PyGridSetLocalCoef1, METH_VARARGS | METH_KEYWORDS,
	"set_local_coef1(c, type0, type1) : set local coefficient by type" },
	{ "set_local_coef3", (PyCFunction)PyGridSetLocalCoef3, METH_VARARGS | METH_KEYWORDS,
	"set_local_coef3((cx, cy, cz), type0, type1) : set local coefficient by type" },
	{ "get_rhoc", (PyCFunction)PyGridGetRhoc, METH_VARARGS | METH_KEYWORDS,
	"get_rhoc(i) : get coefficient, rhoc x c" },
	{ "set_rhoc", (PyCFunction)PyGridSetRhoc, METH_VARARGS | METH_KEYWORDS,
	"set_rhoc(rhoc, i) : set coefficient, rhoc x c" },
	{ "ave_val", (PyCFunction)PyGridAveVal, METH_VARARGS | METH_KEYWORDS,
	"ave_val((x0, y0, z0), (x1, y1, z1)) : average values of region" },
	{ "count_type", (PyCFunction)PyGridCountType, METH_VARARGS | METH_KEYWORDS,
	"count_type(type, (x0, y0, z0), (x1, y1, z1)) : count type in region" },
	{ "uniform_random", (PyCFunction)PyGridUniformRandom, METH_VARARGS | METH_KEYWORDS,
	"uniform_random(type, num, (x0, y0, z0), (x1, y1, z1)) : set type by uniform random" },
	{ "gauss_random", (PyCFunction)PyGridGaussRandom, METH_VARARGS | METH_KEYWORDS,
	"gauss_random(type, num, spdis, (x0, y0, z0), (x1, y1, z1)) : set type by gauss random" },
	{ "write", (PyCFunction)PyGridWrite, METH_VARARGS | METH_KEYWORDS,
	"write(fname, comp) : write grid" },
	{ NULL }  /* Sentinel */
};

static PyObject *PyGridGetSize(MP_GridData *self, void *closure)
{
	return Py_BuildValue("iii", self->size[0], self->size[1], self->size[2]);
}

static PyObject *PyGridGetElement(MP_GridData *self, void *closure)
{
	return Py_BuildValue("ddd", self->element[0], self->element[1], self->element[2]);
}

static int PyGridSetElement(MP_GridData *self, PyObject *value, void *closure)
{
	double ex, ey, ez;

	if (!PyArg_ParseTuple(value, "ddd", &ex, &ey, &ez)) {
		return -1;
	}
	self->element[0] = ex;
	self->element[1] = ey;
	self->element[2] = ez;
	return 0;
}

static PyObject *PyGridGetBound(MP_GridData *self, void *closure)
{
	return Py_BuildValue("iiiiii", self->bound[0], self->bound[1], self->bound[2],
		self->bound[3], self->bound[4], self->bound[5]);
}

static int PyGridSetBound(MP_GridData *self, PyObject *value, void *closure)
{
	int xl, yl, zl, xu, yu, zu;

	if (!PyArg_ParseTuple(value, "iiiiii", &xl, &yl, &zl, &xu, &yu, &zu)) {
		return -1;
	}
	self->bound[0] = xl;
	self->bound[1] = yl;
	self->bound[2] = zl;
	self->bound[3] = xu;
	self->bound[4] = yu;
	self->bound[5] = zu;
	return 0;
}

static PyGetSetDef PyGridGetSet[] = {
	{ "size", (getter)PyGridGetSize, NULL, "size = (nx, ny, nz)", NULL },
	{ "element", (getter)PyGridGetElement, (setter)PyGridSetElement, "element = (ex, ey, ez)", NULL },
	{ "bound", (getter)PyGridGetBound, (setter)PyGridSetBound, "bound = (xl, yl, zl, xu, yu , zu)", NULL },
	{ NULL }  /* Sentinel */
};

static PyTypeObject PyGridNewType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGrid.new",				/*tp_name*/
	sizeof(MP_GridData),		/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyGridDealloc,	/*tp_dealloc*/
	0,							/*tp_print*/
	0,							/*tp_getattr*/
	0,							/*tp_setattr*/
	0,							/*tp_compare*/
	0,							/*tp_repr*/
	0,							/*tp_as_number*/
	0,							/*tp_as_sequence*/
	0,							/*tp_as_mapping*/
	0,							/*tp_hash */
	0,							/*tp_call*/
	0,							/*tp_str*/
	0,							/*tp_getattro*/
	0,							/*tp_setattro*/
	0,							/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags*/
	"new(nx, ny, nz, ntype, [local_coef=FALSE])",	/* tp_doc */
	0,							/* tp_traverse */
	0,							/* tp_clear */
	0,							/* tp_richcompare */
	0,							/* tp_weaklistoffset */
	0,							/* tp_iter */
	0,							/* tp_iternext */
	PyGridMethods,				/* tp_methods */
	PyGridMembers,				/* tp_members */
	PyGridGetSet,				/* tp_getset */
	0,							/* tp_base */
	0,							/* tp_dict */
	0,							/* tp_descr_get */
	0,							/* tp_descr_set */
	0,							/* tp_dictoffset */
	0,							/* tp_init */
	0,							/* tp_alloc */
	PyGridNewNew,				/* tp_new */
};

static PyTypeObject PyGridReadType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGrid.read",				/*tp_name*/
	sizeof(MP_GridData),		/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyGridDealloc,	/*tp_dealloc*/
	0,							/*tp_print*/
	0,							/*tp_getattr*/
	0,							/*tp_setattr*/
	0,							/*tp_compare*/
	0,							/*tp_repr*/
	0,							/*tp_as_number*/
	0,							/*tp_as_sequence*/
	0,							/*tp_as_mapping*/
	0,							/*tp_hash */
	0,							/*tp_call*/
	0,							/*tp_str*/
	0,							/*tp_getattro*/
	0,							/*tp_setattro*/
	0,							/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags*/
	"read(fname, [version=2])",	/* tp_doc */
	0,							/* tp_traverse */
	0,							/* tp_clear */
	0,							/* tp_richcompare */
	0,							/* tp_weaklistoffset */
	0,							/* tp_iter */
	0,							/* tp_iternext */
	PyGridMethods,				/* tp_methods */
	PyGridMembers,				/* tp_members */
	PyGridGetSet,				/* tp_getset */
	0,							/* tp_base */
	0,							/* tp_dict */
	0,							/* tp_descr_get */
	0,							/* tp_descr_set */
	0,							/* tp_dictoffset */
	0,							/* tp_init */
	0,							/* tp_alloc */
	PyGridReadNew,				/* tp_new */
};

static PyTypeObject PyGridCopyType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGrid.copy",				/*tp_name*/
	sizeof(MP_GridData),		/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyGridDealloc,	/*tp_dealloc*/
	0,							/*tp_print*/
	0,							/*tp_getattr*/
	0,							/*tp_setattr*/
	0,							/*tp_compare*/
	0,							/*tp_repr*/
	0,							/*tp_as_number*/
	0,							/*tp_as_sequence*/
	0,							/*tp_as_mapping*/
	0,							/*tp_hash */
	0,							/*tp_call*/
	0,							/*tp_str*/
	0,							/*tp_getattro*/
	0,							/*tp_setattro*/
	0,							/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags*/
	"copy(grid, (x0, y0, z0), (x1, y1, z1))",		/* tp_doc */
	0,							/* tp_traverse */
	0,							/* tp_clear */
	0,							/* tp_richcompare */
	0,							/* tp_weaklistoffset */
	0,							/* tp_iter */
	0,							/* tp_iternext */
	PyGridMethods,				/* tp_methods */
	PyGridMembers,				/* tp_members */
	PyGridGetSet,				/* tp_getset */
	0,							/* tp_base */
	0,							/* tp_dict */
	0,							/* tp_descr_get */
	0,							/* tp_descr_set */
	0,							/* tp_dictoffset */
	0,							/* tp_init */
	0,							/* tp_alloc */
	PyGridCopyNew,				/* tp_new */
};

static PyTypeObject PyGridCloneType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGrid.clone",				/*tp_name*/
	sizeof(MP_GridData),		/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyGridDealloc,	/*tp_dealloc*/
	0,							/*tp_print*/
	0,							/*tp_getattr*/
	0,							/*tp_setattr*/
	0,							/*tp_compare*/
	0,							/*tp_repr*/
	0,							/*tp_as_number*/
	0,							/*tp_as_sequence*/
	0,							/*tp_as_mapping*/
	0,							/*tp_hash */
	0,							/*tp_call*/
	0,							/*tp_str*/
	0,							/*tp_getattro*/
	0,							/*tp_setattro*/
	0,							/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/*tp_flags*/
	"clone(grid)",				/* tp_doc */
	0,							/* tp_traverse */
	0,							/* tp_clear */
	0,							/* tp_richcompare */
	0,							/* tp_weaklistoffset */
	0,							/* tp_iter */
	0,							/* tp_iternext */
	PyGridMethods,				/* tp_methods */
	PyGridMembers,				/* tp_members */
	PyGridGetSet,				/* tp_getset */
	0,							/* tp_base */
	0,							/* tp_dict */
	0,							/* tp_descr_get */
	0,							/* tp_descr_set */
	0,							/* tp_dictoffset */
	0,							/* tp_init */
	0,							/* tp_alloc */
	PyGridCloneNew,				/* tp_new */
};

static PyMethodDef MPGridPyMethods[] = {
	{ NULL }  /* Sentinel */
};

#ifdef PY3
static struct PyModuleDef MPGridPyModule = {
	PyModuleDef_HEAD_INIT,
	"MPGrid",
	NULL,
	-1,
	MPGridPyMethods,
};
#endif

#ifndef PY3
PyMODINIT_FUNC initMPGrid(void)
#else
PyMODINIT_FUNC PyInit_MPGrid(void)
#endif
{
	PyObject *m;

#ifndef PY3
	if (PyType_Ready(&PyGridNewType) < 0) return;
	if (PyType_Ready(&PyGridReadType) < 0) return;
	if (PyType_Ready(&PyGridCopyType) < 0) return;
	if (PyType_Ready(&PyGridCloneType) < 0) return;
	m = Py_InitModule3("MPGrid", MPGridPyMethods, "MPGrid extention");
	if (m == NULL) return;
#else
	if (PyType_Ready(&PyGridNewType) < 0) return NULL;
	if (PyType_Ready(&PyGridReadType) < 0) return NULL;
	if (PyType_Ready(&PyGridCopyType) < 0) return NULL;
	if (PyType_Ready(&PyGridCloneType) < 0) return NULL;
	m = PyModule_Create(&MPGridPyModule);
	if (m == NULL) return NULL;
#endif
	Py_INCREF(&PyGridNewType);
	PyModule_AddObject(m, "new", (PyObject *)&PyGridNewType);
	Py_INCREF(&PyGridReadType);
	PyModule_AddObject(m, "read", (PyObject *)&PyGridReadType);
	Py_INCREF(&PyGridCopyType);
	PyModule_AddObject(m, "copy", (PyObject *)&PyGridCopyType);
	Py_INCREF(&PyGridCloneType);
	PyModule_AddObject(m, "clone", (PyObject *)&PyGridCloneType);
	PyModule_AddIntConstant(m, "BoundInsulate", MP_GridBoundInsulate);
	PyModule_AddIntConstant(m, "BoundPeriodic", MP_GridBoundPeriodic);
	PyModule_AddIntConstant(m, "InterCond", MP_GridInterCond);
	PyModule_AddIntConstant(m, "InterTrans", MP_GridInterTrans);
#ifdef PY3
	return m;
#endif
}

#endif /* MP_PYTHON_LIB */
