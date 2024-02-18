#include "MPGrid.h"

int MP_GridCGAlloc(MP_GridCG* cg, MP_GridData* data)
{
	int i;
	int ntot = data->ntot;

	cg->dval = (double*)malloc(ntot * sizeof(double));
	cg->g = (double*)malloc(ntot * sizeof(double));
	cg->h = (double*)malloc(ntot * sizeof(double));
	if (cg->dval == NULL || cg->g == NULL || cg->h == NULL) return FALSE;
	for (i = 0; i < ntot; i++) {
		cg->dval[i] = 0.0;
		cg->g[i] = 0.0;
		cg->h[i] = 0.0;
	}
	return TRUE;
}

void MP_GridCGFree(MP_GridCG* cg)
{
	free(cg->dval);
	free(cg->g);
	free(cg->h);
}

static double GridCGFunc(MP_GridData* data)
{
	return MP_GridMeanFlow(data);
}

static void GridCGDFunc(MP_GridCG* cg, MP_GridData* data)
{
	int i;
	double f[3];

#ifdef _OPENMP
#pragma omp parallel for private(f)
#endif
	for (i = 0; i < data->ntot; i++) {
		if (data->update[i]) {
			MP_GridElementFlow(data, i, f);
			cg->dval[i] = -(f[0] + f[1] + f[2]);
		}
		else {
			cg->dval[i] = 0.0;
		}
	}
}

static double GridCGLineFunc(MP_GridCG* cg, MP_GridData* data, double dt)
{
	int i;

	for (i = 0; i < data->ntot; i++) {
		if (data->update[i]) {
			data->val[i] = data->buf[i] + dt * cg->dval[i];
		}
	}
	return GridCGFunc(data);
}

static void GridCGSection(MP_GridCG* cg, MP_GridData *data, double dt[], double e[])
{
	double fac = 1.0 + (sqrt(5.0) - 1.0) / 2.0;
	double dt_tmp, e_tmp, dt_lim;
	double r, q;

	e[0] = GridCGLineFunc(cg, data, dt[0]);
	e[1] = GridCGLineFunc(cg, data, dt[1]);
	if (e[1] > e[0]) {
		dt_tmp = dt[0], dt[0] = dt[1], dt[1] = dt_tmp;
		e_tmp = e[0], e[0] = e[1], e[1] = e_tmp;
	}
	dt[2] = dt[1] + fac * (dt[1] - dt[0]);
	e[2] = GridCGLineFunc(cg, data, dt[2]);
	while (TRUE) {
		r = (dt[1] - dt[0]) * (e[1] - e[2]);
		q = (dt[1] - dt[2]) * (e[1] - e[0]);
		if (r - q == 0.0) {
			dt_tmp = dt[1] - 0.5 * ((dt[1] - dt[0]) * r - (dt[1] - dt[2]) * q) / (1.0e-32);
		}
		else {
			dt_tmp = dt[1] - 0.5 * ((dt[1] - dt[0]) * r - (dt[1] - dt[2]) * q) / (r - q);
		}
		dt_lim = dt[2] + 100.0 * (dt[2] - dt[1]);
		if ((dt[0] - dt_tmp) * (dt_tmp - dt[1]) > 0.0) {
			e_tmp = GridCGLineFunc(cg, data, dt_tmp);
			if (e_tmp < e[1]) {
				dt[2] = dt[1], dt[1] = dt_tmp;
				e[2] = e[1], e[1] = e_tmp;
				break;
			}
			dt_tmp = dt[2] + fac * (dt[2] - dt[1]);
			e_tmp = GridCGLineFunc(cg, data, dt_tmp);
		}
		else if ((dt[1] - dt_tmp) * (dt_tmp - dt[2]) > 0.0) {
			e_tmp = GridCGLineFunc(cg, data, dt_tmp);
			if (e_tmp < e[2]) {
				dt[0] = dt[1], dt[1] = dt_tmp;
				e[0] = e[1], e[1] = e_tmp;
				break;
			}
			dt_tmp = dt[2] + fac * (dt[2] - dt[1]);
			e_tmp = GridCGLineFunc(cg, data, dt_tmp);
		}
		//		else if ((dt[2]-dt_tmp)*(dt_tmp-dt_lim) > 0.0) {
		//			e_tmp = GridCGLineFunc(dt_tmp);
		//			if (e_tmp < e[2]) {
		//				dt[1] = dt[2], dt[2] = dt_tmp, dt_tmp = dt[2]+fac*(dt[2]-dt[1]);
		//				e[1] = e[2], e[2] = e_tmp, e_tmp = GridCGLineFunc(dt_tmp);
		//			}
		//		}
		//		else if ((dt_tmp-dt_lim)*(dt_lim-dt[2]) >= 0.0) {
		//			dt_tmp = dt_lim;
		//			e_tmp = GridCGLineFunc(dt_tmp);
		//		}
		else {
			dt_tmp = dt[2] + fac * (dt[2] - dt[1]);
			e_tmp = GridCGLineFunc(cg, data, dt_tmp);
		}
		dt[0] = dt[1], dt[1] = dt[2], dt[2] = dt_tmp;
		e[0] = e[1], e[1] = e[2], e[2] = e_tmp;
		if (e[2] > e[1]) break;
	}
	if (dt[0] > dt[2]) {
		dt_tmp = dt[0], dt[0] = dt[2], dt[2] = dt_tmp;
		e_tmp = e[0], e[0] = e[2], e[2] = e_tmp;
	}
}

static double GridCGGolden(MP_GridCG* cg, MP_GridData* data, double dt1, double dt2, double tol)
{
	double tau = (sqrt(5.0) - 1.0) / 2.0;
	double dt11 = dt2 - tau * (dt2 - dt1);
	double e1 = GridCGLineFunc(cg, data, dt11);
	double dt22 = dt1 + tau * (dt2 - dt1);
	double e2 = GridCGLineFunc(cg, data, dt22);

	while (TRUE) {
		if (e2 > e1) {
			if (fabs(e2 - e1) < tol) {
				return dt11;
			}
			dt2 = dt22;
			dt22 = dt11;
			dt11 = dt1 + (1.0 - tau) * (dt2 - dt1);
			e2 = e1;
			e1 = GridCGLineFunc(cg, data, dt11);
		}
		else {
			if (fabs(e2 - e1) < tol) {
				return dt22;
			}
			dt1 = dt11;
			dt11 = dt22;
			dt22 = dt2 - (1.0 - tau) * (dt2 - dt1);
			e1 = e2;
			e2 = GridCGLineFunc(cg, data, dt22);
		}
	}
}

static double GridCGLineMinimize(MP_GridCG* cg, MP_GridData* data, double dt)
{
	int i;
	double dtt[3], e[3];
	double dt_min, e_min;

	dtt[0] = 0.0, dtt[1] = dt;
	for (i = 0; i < data->ntot; i++) {
		data->buf[i] = data->val[i];
	}
	GridCGSection(cg, data, dtt, e);
	//fprintf(stderr, "dtt %e %e %e\n", dtt[0], dtt[1], dtt[2]);
	dt_min = GridCGGolden(cg, data, dtt[0], dtt[2], dt*1.0e-6);
	e_min = GridCGLineFunc(cg, data, dt_min);
	//fprintf(stderr, "min %e %e\n", dt_min, e_min);
	return e_min;
}

double MP_GridCGSolve(MP_GridCG *cg, MP_GridData *data, double dt, int nloop)
{
	int i;
	double e1, e2;
	double dgg, gg, gam;
	int n = 0;

	e1 = GridCGFunc(data);
	GridCGDFunc(cg, data);
	for (i = 0; i < data->ntot; i++) {
		cg->g[i] = -cg->dval[i];
		cg->dval[i] = cg->h[i] = cg->g[i];
	}
	while (TRUE) {
		e2 = GridCGLineMinimize(cg, data, dt);
		//fprintf(stderr, "%e\n", e2);
		if (++n >= nloop) {
			return e2;
		}
		else {
			e1 = e2;
		}
		GridCGDFunc(cg, data);
		dgg = 0.0;
		gg = 0.0;
		for (i = 0; i < data->ntot; i++) {
			if (data->update[i]) {
				gg += cg->g[i] * cg->g[i];
				dgg += (cg->dval[i] + cg->g[i]) * cg->dval[i];
			}
		}
	    if (gg == 0.0) return 0.0;
		gam = dgg / gg;
		for (i = 0; i < data->ntot; i++) {
			cg->g[i] = -cg->dval[i];
			cg->dval[i] = cg->h[i] = cg->g[i] + gam * cg->h[i];
		}
	}
}