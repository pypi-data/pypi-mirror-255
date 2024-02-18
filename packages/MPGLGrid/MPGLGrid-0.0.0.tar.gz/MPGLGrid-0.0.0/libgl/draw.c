#include "MPGLGrid.h"
#include <MPGrid.h>

void MPGL_GridDrawInit(MPGL_GridDrawData *draw)
{
	int i;
	static int range[] = { 0, 0, 0, 10000, 10000, 10000 };

	draw->method = MPGL_DrawMethodQuads;
	draw->kind = MPGL_DrawKindType;
	for (i = 0; i < MPGL_GRID_TYPE_MAX; i++) {
		draw->disp[i] = TRUE;
	}
	for (i = 0; i < 6; i++) {
		draw->range[i] = range[i];
	}
}

static void GridQuads(int dir)
{
	static float d1[][3] = { { -0.5, -0.5, -0.5 },{ -0.5, -0.5, -0.5 },{ -0.5, -0.5, -0.5 },
	{ 0.5, 0.5, 0.5 },{ 0.5, 0.5, 0.5 },{ 0.5, 0.5, 0.5 } };
	static float d2[][3] = { { -0.5, -0.5, 0.5 },{ 0.5, -0.5, -0.5 },{ -0.5, 0.5, -0.5 },
	{ 0.5, -0.5, 0.5 },{ 0.5, 0.5, -0.5 },{ -0.5, 0.5, 0.5 } };
	static float d3[][3] = { { -0.5, 0.5, 0.5 },{ 0.5, -0.5, 0.5 },{ 0.5, 0.5, -0.5 },
	{ 0.5, -0.5, -0.5 },{ -0.5, 0.5, -0.5 },{ -0.5, -0.5, 0.5 } };
	static float d4[][3] = { { -0.5, 0.5, -0.5 },{ -0.5, -0.5, 0.5 },{ 0.5, -0.5, -0.5 },
	{ 0.5, 0.5, -0.5 },{ -0.5, 0.5, 0.5 },{ 0.5, -0.5, 0.5 } };
	static float normals[6][3] = { { -1.0,  0.0,  0.0 },{ 0.0, -1.0, 0.0 },{ 0.0, 0.0, -1.0 },
	{ 1.0, 0.0, 0.0 },{ 0.0, 1.0, 0.0 },{ 0.0, 0.0, 1.0 } };

	glBegin(GL_QUADS);
	glNormal3fv(normals[dir]);
	glVertex3f(d1[dir][0], d1[dir][1], d1[dir][2]);
	glVertex3f(d2[dir][0], d2[dir][1], d2[dir][2]);
	glVertex3f(d3[dir][0], d3[dir][1], d3[dir][2]);
	glVertex3f(d4[dir][0], d4[dir][1], d4[dir][2]);
	glEnd();
}

static void GridCube(void)
{
	static GLfloat vertices[8][3] =
	{
		{ -0.5f, -0.5f,  0.5f },{ 0.5f, -0.5f,  0.5f },{ 0.5f,  0.5f,  0.5f },{ -0.5f,  0.5f,  0.5f },
		{ 0.5f, -0.5f, -0.5f },{ -0.5f, -0.5f, -0.5f },{ -0.5f,  0.5f, -0.5f },{ 0.5f,  0.5f, -0.5f }
	};
	static GLfloat normals[6][3] =
	{
		{ 0.0f,  0.0f,  1.0f },{ 0.0f,  0.0f, -1.0f },{ 1.0f,  0.0f,  0.0f },
		{ -1.0f,  0.0f,  0.0f },{ 0.0f,  1.0f,  0.0f },{ 0.0f, -1.0f,  0.0f }
	};

	glBegin(GL_POLYGON);
	glNormal3fv(normals[0]);
	glVertex3fv(vertices[0]);
	glVertex3fv(vertices[1]);
	glVertex3fv(vertices[2]);
	glVertex3fv(vertices[3]);
	glEnd();
	glBegin(GL_POLYGON);
	glNormal3fv(normals[1]);
	glVertex3fv(vertices[4]);
	glVertex3fv(vertices[5]);
	glVertex3fv(vertices[6]);
	glVertex3fv(vertices[7]);
	glEnd();
	glBegin(GL_POLYGON);
	glNormal3fv(normals[2]);
	glVertex3fv(vertices[1]);
	glVertex3fv(vertices[4]);
	glVertex3fv(vertices[7]);
	glVertex3fv(vertices[2]);
	glEnd();
	glBegin(GL_POLYGON);
	glNormal3fv(normals[3]);
	glVertex3fv(vertices[5]);
	glVertex3fv(vertices[0]);
	glVertex3fv(vertices[3]);
	glVertex3fv(vertices[6]);
	glEnd();
	glBegin(GL_POLYGON);
	glNormal3fv(normals[4]);
	glVertex3fv(vertices[3]);
	glVertex3fv(vertices[2]);
	glVertex3fv(vertices[7]);
	glVertex3fv(vertices[6]);
	glEnd();
	glBegin(GL_POLYGON);
	glNormal3fv(normals[5]);
	glVertex3fv(vertices[1]);
	glVertex3fv(vertices[0]);
	glVertex3fv(vertices[5]);
	glVertex3fv(vertices[4]);
	glEnd();
}

static void Cylinder(unsigned int list, unsigned int res)
{
	GLUquadricObj *quadObj = gluNewQuadric();

	gluQuadricDrawStyle(quadObj, GLU_FILL);
	gluQuadricOrientation(quadObj, GLU_OUTSIDE);
	gluQuadricNormals(quadObj, GLU_SMOOTH);
	if (glIsList(list) == GL_TRUE) glDeleteLists(list, 1);
	glNewList(list, GL_COMPILE);
	gluCylinder(quadObj, 1.0, 1.0, 1.0, res, res);
	glTranslatef(0.0, 0.0, 1.0);
	gluDisk(quadObj, 0.0, 1.0, res, res);
	glTranslatef(0.0, 0.0, -1.0);
	glRotatef(180, 1, 0, 0);
	gluDisk(quadObj, 0.0, 1.0, res, res);
	glEndList();
	gluDeleteQuadric(quadObj);
}

void MPGL_GridDrawList(void)
{
	if (glIsList(MPGL_GRID_QUADS_LIST0) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST0, 1);
	if (glIsList(MPGL_GRID_QUADS_LIST1) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST1, 1);
	if (glIsList(MPGL_GRID_QUADS_LIST2) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST2, 1);
	if (glIsList(MPGL_GRID_QUADS_LIST3) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST3, 1);
	if (glIsList(MPGL_GRID_QUADS_LIST4) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST4, 1);
	if (glIsList(MPGL_GRID_QUADS_LIST5) == GL_TRUE) glDeleteLists(MPGL_GRID_QUADS_LIST5, 1);
	if (glIsList(MPGL_GRID_CUBE_LIST) == GL_TRUE) glDeleteLists(MPGL_GRID_CUBE_LIST, 1);
	glNewList(MPGL_GRID_QUADS_LIST0, GL_COMPILE);
	GridQuads(0);
	glEndList();
	glNewList(MPGL_GRID_QUADS_LIST1, GL_COMPILE);
	GridQuads(1);
	glEndList();
	glNewList(MPGL_GRID_QUADS_LIST2, GL_COMPILE);
	GridQuads(2);
	glEndList();
	glNewList(MPGL_GRID_QUADS_LIST3, GL_COMPILE);
	GridQuads(3);
	glEndList();
	glNewList(MPGL_GRID_QUADS_LIST4, GL_COMPILE);
	GridQuads(4);
	glEndList();
	glNewList(MPGL_GRID_QUADS_LIST5, GL_COMPILE);
	GridQuads(5);
	glEndList();
	glNewList(MPGL_GRID_CUBE_LIST, GL_COMPILE);
	GridCube();
	glEndList();
	Cylinder(MPGL_GRID_CYLINDER_LIST, 32);
}

/*static void GridColor(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	if (draw->kind == MPGL_DrawKindType) MPGL_ColormapStepColor(colormap, data->type[id], color);
	else if (draw->kind == MPGL_DrawKindUpdate) MPGL_ColormapStepColor(colormap, data->update[id], color);
	else if (draw->kind == MPGL_DrawKindVal) MPGL_ColormapGradColor(colormap, data->val[id], color);
	glColor3fv(color);
}*/

static void TypeColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapStepColor(colormap, data->type[id], color);
	glColor3fv(color);
}

static void UpdateColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapStepColor(colormap, data->update[id], color);
	glColor3fv(color);
}

static void ValColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapGradColor(colormap, data->val[id], color);
	glColor3fv(color);
}

static void CxColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapGradColor(colormap, data->cx[id], color);
	glColor3fv(color);
}

static void CyColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapGradColor(colormap, data->cy[id], color);
	glColor3fv(color);
}

static void CzColor(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z)
{
	int id = MP_GRID_INDEX(data, x, y, z);
	float color[3];

	MPGL_ColormapGradColor(colormap, data->cz[id], color);
	glColor3fv(color);
}

static void GridDispRange(MPGL_GridDrawData *draw, MP_GridData *data, int range[])
{
	int i;

	for (i = 0; i < 6; i++) {
		range[i] = draw->range[i];
	}
	for (i = 0;i < 3;i++) {
		if (range[i] < 0 || range[i] >= data->size[i]) range[i] = 0;
		if (range[i+3] < 0 || range[i+3] >= data->size[i]) range[i+3] = data->size[i] - 1;
	}
}

static void GridQuadsDraw(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	int x, y, z;
	int range[6];
	void (*color_func)(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z);

	if (draw->kind == MPGL_DrawKindType) color_func = TypeColor;
	else if (draw->kind == MPGL_DrawKindUpdate) color_func = UpdateColor;
	else if (draw->kind == MPGL_DrawKindVal) color_func = ValColor;
	else if (draw->kind == MPGL_DrawKindCx && data->local_coef) color_func = CxColor;
	else if (draw->kind == MPGL_DrawKindCy && data->local_coef) color_func = CyColor;
	else if (draw->kind == MPGL_DrawKindCz && data->local_coef) color_func = CzColor;
	else return;
	GridDispRange(draw, data, range);
	x = range[0];
	for (z = range[2];z <= range[5];z++) {
		for (y = range[1];y <= range[4];y++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST0);
			glPopMatrix();
		}
	}
	y = range[1];
	for (z = range[2];z <= range[5];z++) {
		for (x = range[0];x <= range[3];x++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST1);
			glPopMatrix();
		}
	}
	z = range[2];
	for (y = range[1];y <= range[4];y++) {
		for (x = range[0];x <= range[3];x++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST2);
			glPopMatrix();
		}
	}
	x = range[3];
	for (z = range[2];z <= range[5];z++) {
		for (y = range[1];y <= range[4];y++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST3);
			glPopMatrix();
		}
	}
	y = range[4];
	for (z = range[2];z <= range[5];z++) {
		for (x = range[0];x <= range[3];x++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST4);
			glPopMatrix();
		}
	}
	z = range[5];
	for (y = range[1];y <= range[4];y++) {
		for (x = range[0];x <= range[3];x++) {
			(color_func)(data, colormap, x, y, z);
			glPushMatrix();
			glTranslatef((float)x, (float)y, (float)z);
			glCallList(MPGL_GRID_QUADS_LIST5);
			glPopMatrix();
		}
	}
}

static void ValMinMax(MP_GridData *data, int x, int y, int z, double *min, double *max)
{
	int id = MP_GRID_INDEX(data, x, y, z);

	if (data->val[id] < *min) *min = data->val[id];
	if (data->val[id] > *max) *max = data->val[id];
}

static void CxMinMax(MP_GridData *data, int x, int y, int z, double *min, double *max)
{
	int id = MP_GRID_INDEX(data, x, y, z);

	if (data->cx[id] < *min) *min = data->cx[id];
	if (data->cx[id] > *max) *max = data->cx[id];
}

static void CyMinMax(MP_GridData *data, int x, int y, int z, double *min, double *max)
{
	int id = MP_GRID_INDEX(data, x, y, z);

	if (data->cy[id] < *min) *min = data->cy[id];
	if (data->cy[id] > *max) *max = data->cy[id];
}

static void CzMinMax(MP_GridData *data, int x, int y, int z, double *min, double *max)
{
	int id = MP_GRID_INDEX(data, x, y, z);

	if (data->cz[id] < *min) *min = data->cz[id];
	if (data->cz[id] > *max) *max = data->cz[id];
}

static void GridQuadsColormapRange(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	int x, y, z;
	int range[6];
	double min = 1.0e32;
	double max = -1.0e32;
	void (*minmax_func)(MP_GridData *data, int x, int y, int z, double *min, double *max);

	if (draw->kind == MPGL_DrawKindVal) minmax_func = ValMinMax;
	else if (draw->kind == MPGL_DrawKindCx && data->local_coef) minmax_func = CxMinMax;
	else if (draw->kind == MPGL_DrawKindCy && data->local_coef) minmax_func = CyMinMax;
	else if (draw->kind == MPGL_DrawKindCz && data->local_coef) minmax_func = CzMinMax;
	else return;
	GridDispRange(draw, data, range);
	x = range[0];
	for (z = range[2]; z <= range[5]; z++) {
		for (y = range[1]; y <= range[4]; y++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	y = range[1];
	for (z = range[2]; z <= range[5]; z++) {
		for (x = range[0]; x <= range[3]; x++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	z = range[2];
	for (y = range[1]; y <= range[4]; y++) {
		for (x = range[0]; x <= range[3]; x++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	x = range[3];
	for (z = range[2]; z <= range[5]; z++) {
		for (y = range[1]; y <= range[4]; y++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	y = range[4];
	for (z = range[2]; z <= range[5]; z++) {
		for (x = range[0]; x <= range[3]; x++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	z = range[5];
	for (y = range[1]; y <= range[4]; y++) {
		for (x = range[0]; x <= range[3]; x++) {
			(minmax_func)(data, x, y, z, &min, &max);
		}
	}
	colormap->range[0] = min;
	colormap->range[1] = max;
}

static void GridCubesDraw(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	int id;
	int x, y, z;
	int range[6];
	void (*color_func)(MP_GridData *data, MPGL_Colormap *colormap, int x, int y, int z);

	if (draw->kind == MPGL_DrawKindType) color_func = TypeColor;
	else if (draw->kind == MPGL_DrawKindUpdate) color_func = UpdateColor;
	else if (draw->kind == MPGL_DrawKindVal) color_func = ValColor;
	else if (draw->kind == MPGL_DrawKindCx && data->local_coef) color_func = CxColor;
	else if (draw->kind == MPGL_DrawKindCy && data->local_coef) color_func = CyColor;
	else if (draw->kind == MPGL_DrawKindCz && data->local_coef) color_func = CzColor;
	else return;
	GridDispRange(draw, data, range);
	for (z = range[2]; z <= range[5]; z++) {
		for (y = range[1]; y <= range[4]; y++) {
			for (x = range[0]; x <= range[3]; x++) {
				id = MP_GRID_INDEX(data, x, y, z);
				if (draw->disp[data->type[id]]) {
					(color_func)(data, colormap, x, y, z);
					glPushMatrix();
					glTranslatef((float)x, (float)y, (float)z);
					glCallList(MPGL_GRID_CUBE_LIST);
					glPopMatrix();
				}
			}
		}
	}
}

static void GridCubesColormapRange(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	int id;
	int x, y, z;
	int range[6];
	double min = 1.0e32;
	double max = -1.0e32;
	void (*minmax_func)(MP_GridData *data, int x, int y, int z, double *min, double *max);

	if (draw->kind == MPGL_DrawKindVal) minmax_func = ValMinMax;
	else if (draw->kind == MPGL_DrawKindCx && data->local_coef) minmax_func = CxMinMax;
	else if (draw->kind == MPGL_DrawKindCy && data->local_coef) minmax_func = CyMinMax;
	else if (draw->kind == MPGL_DrawKindCz && data->local_coef) minmax_func = CzMinMax;
	else return;
	GridDispRange(draw, data, range);
	for (z = range[2]; z <= range[5]; z++) {
		for (y = range[1]; y <= range[4]; y++) {
			for (x = range[0]; x <= range[3]; x++) {
				id = MP_GRID_INDEX(data, x, y, z);
				if (draw->disp[data->type[id]]) {
					(minmax_func)(data, x, y, z, &min, &max);
				}
			}
		}
	}
	colormap->range[0] = min;
	colormap->range[1] = max;
}

void MPGL_GridDrawColormapRange(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	if (draw->method == MPGL_DrawMethodQuads) GridQuadsColormapRange(draw, data, colormap);
	else if (draw->method == MPGL_DrawMethodCubes) GridCubesColormapRange(draw, data, colormap);
}

static void ElementScale(MP_GridData *data, float scale[])
{
	int i;
	double min = data->element[0];

	for (i = 1; i < 3; i++) {
		if (data->element[i] < min) min = data->element[i];
	}
	for (i = 0; i < 3; i++) {
		scale[i] = (float)(data->element[i] / min);
	}
}

void MPGL_GridDraw(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap)
{
	int i;
	float scale[3];

	if (draw->kind == MPGL_DrawKindType) {
		colormap->mode = MPGL_ColormapStep;
		sprintf(colormap->title, "Type");
		colormap->nstep = data->ntype;
		for (i = 0;i < data->ntype;i++) {
			sprintf(colormap->label[i], "%d", i);
		}
	}
	else if (draw->kind == MPGL_DrawKindUpdate) {
		colormap->mode = MPGL_ColormapStep;
		sprintf(colormap->title, "Update");
		colormap->nstep = 2;
		sprintf(colormap->label[0], "F");
		sprintf(colormap->label[1], "T");
	}
	else if (draw->kind == MPGL_DrawKindVal) {
		colormap->mode = MPGL_ColormapGrad;
		sprintf(colormap->title, "Value");
	}
	else if (draw->kind == MPGL_DrawKindCx) {
		colormap->mode = MPGL_ColormapGrad;
		sprintf(colormap->title, "Cx");
	}
	else if (draw->kind == MPGL_DrawKindCy) {
		colormap->mode = MPGL_ColormapGrad;
		sprintf(colormap->title, "Cy");
	}
	else if (draw->kind == MPGL_DrawKindCz) {
		colormap->mode = MPGL_ColormapGrad;
		sprintf(colormap->title, "Cz");
	}
	ElementScale(data, scale);
	glPushMatrix();
	glScalef(scale[0], scale[1], scale[2]);
	if (draw->method == MPGL_DrawMethodQuads) GridQuadsDraw(draw, data, colormap);
	else if (draw->method == MPGL_DrawMethodCubes) GridCubesDraw(draw, data, colormap);
	glPopMatrix();
}

void MPGL_GridDrawAxis(int size[])
{
	glPushMatrix();
	glRotatef(90.0f, 0.0f, 1.0f, 0.0f);
	glScalef(0.5f, 0.5f, (float)size[0]);
	glColor3f(1.0f, 0.0f, 0.0f);
	glCallList(MPGL_GRID_CYLINDER_LIST);
	glPopMatrix();
	glPushMatrix();
	glRotatef(-90.0f, 1.0f, 0.0f, 0.0f);
	glScalef(0.5f, 0.5f, (float)size[1]);
	glColor3f(0.0f, 1.0f, 0.0f);
	glCallList(MPGL_GRID_CYLINDER_LIST);
	glPopMatrix();
	glPushMatrix();
	glScalef(0.5f, 0.5f, (float)size[2]);
	glColor3f(0.0f, 0.0f, 1.0f);
	glCallList(MPGL_GRID_CYLINDER_LIST);
	glPopMatrix();
}

void MPGL_GridDrawRegion(MPGL_GridDrawData *draw, MP_GridData *data, float region[])
{
	int i;
	int range[6];
	float scale[3];

	GridDispRange(draw, data, range);
	ElementScale(data, scale);
	for (i = 0; i < 3; i++) {
		region[i] = (range[i] - 0.5f) * scale[i];
		region[i + 3] = (range[i + 3] + 0.5f) * scale[i];
	}
}

/**********************************************************
* for Python
**********************************************************/
#ifdef MP_PYTHON_LIB

static void PyDealloc(MPGL_GridDrawData *self)
{
#ifndef PY3
	self->ob_type->tp_free((PyObject*)self);
#endif
}

static PyObject *PyNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	MPGL_GridDrawData *self;

	self = (MPGL_GridDrawData *)type->tp_alloc(type, 0);
	MPGL_GridDrawInit(self);
	return (PyObject *)self;
}

static PyObject *PyGridDrawList(MPGL_GridDrawData *self, PyObject *args)
{
	MPGL_GridDrawList();
	Py_RETURN_NONE;
}

static PyObject *PyGridDrawColormapRange(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	MP_GridData *data;
	MPGL_Colormap *cmp;
	static char *kwlist[] = { "grid", "cmp", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO!", kwlist, &data, &MPGL_ColormapPyType, &cmp)) {
		return NULL;
	}
	MPGL_GridDrawColormapRange(self, data, cmp);
	Py_RETURN_NONE;
}

static PyObject *PyGridDraw(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	MP_GridData *data;
	MPGL_Colormap *cmp;
	static char *kwlist[] = { "grid", "cmp", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO!", kwlist, &data, &MPGL_ColormapPyType, &cmp)) {
		return NULL;
	}
	MPGL_GridDraw(self, data, cmp);
	Py_RETURN_NONE;
}

static PyObject *PyGridDrawAxis(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	int sx, sy, sz;
	static char *kwlist[] = { "size", NULL };
	int size[3];

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "(iii)", kwlist, &sx, &sy, &sz)) {
		return NULL;
	}
	size[0] = sx, size[1] = sy, size[2] = sz;
	MPGL_GridDrawAxis(size);
	Py_RETURN_NONE;
}

static PyObject *PyGridDrawRegion(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	MP_GridData *data;
	static char *kwlist[] = { "grid", NULL };
	float region[6];

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &data)) {
		return NULL;
	}
	MPGL_GridDrawRegion(self, data, region);
	return Py_BuildValue("dddddd", region[0], region[1], region[2],
		region[3], region[4], region[5]);
}

static PyObject *PyGridDrawGetDisp(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	int type;
	static char *kwlist[] = { "type", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &type)) {
		return NULL;
	}
	if (type >= 0 && type < MPGL_GRID_TYPE_MAX) {
		return Py_BuildValue("i", self->disp[type]);
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid type");
		return NULL;
	}
}

static PyObject *PyGridDrawSetDisp(MPGL_GridDrawData *self, PyObject *args, PyObject *kwds)
{
	int type, disp;
	static char *kwlist[] = { "type", "disp", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &type, &disp)) {
		return NULL;
	}
	if (type >= 0 && type < MPGL_GRID_TYPE_MAX) {
		self->disp[type] = disp;
	}
	else {
		PyErr_SetString(PyExc_ValueError, "invalid type");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyMethodDef PyMethods[] = {
	{ "list", (PyCFunction)PyGridDrawList, METH_NOARGS,
	"list() : set render list" },
	{ "cmp_range", (PyCFunction)PyGridDrawColormapRange, METH_VARARGS | METH_KEYWORDS,
	"cmp_range(grid, cmp) : set colormap range" },
	{ "draw", (PyCFunction)PyGridDraw, METH_VARARGS | METH_KEYWORDS,
	"draw(grid, cmp) : draw grid data" },
	{ "draw_axis", (PyCFunction)PyGridDrawAxis, METH_VARARGS | METH_KEYWORDS,
	"draw_axis(grid) : draw axis" },
	{ "region", (PyCFunction)PyGridDrawRegion, METH_VARARGS | METH_KEYWORDS,
	"region(grid) : return draw region" },
	{ "get_disp", (PyCFunction)PyGridDrawGetDisp, METH_VARARGS | METH_KEYWORDS,
	"get_disp(type) : get display flag" },
	{ "set_disp", (PyCFunction)PyGridDrawSetDisp, METH_VARARGS | METH_KEYWORDS,
	"set_disp(type, disp) : set display flag, 0:non-display 1:display" },
	{ NULL }  /* Sentinel */
};

static PyMemberDef PyMembers[] = {
	{ "method", T_INT, offsetof(MPGL_GridDrawData, method), 0, "draw method, 0:quads 1:cubes" },
	{ "kind", T_INT, offsetof(MPGL_GridDrawData, kind), 0, "draw kind, 0:type 1:update 2:val" },
	{ NULL }  /* Sentinel */
};

static PyObject *PyGetRange(MPGL_GridDrawData *self, void *closure)
{
	return Py_BuildValue("iiiiii", self->range[0], self->range[1], self->range[2],
		self->range[3], self->range[4], self->range[5]);
}

static int PySetRange(MPGL_GridDrawData *self, PyObject *value, void *closure)
{
	int x0, y0, z0, x1, y1, z1;

	if (!PyArg_ParseTuple(value, "iiiiii", &x0, &y0, &z0, &x1, &y1, &z1)) {
		return -1;
	}
	self->range[0] = x0, self->range[1] = y0, self->range[2] = z0;
	self->range[3] = x1, self->range[4] = y1, self->range[5] = z1;
	return 0;
}

static PyGetSetDef PyGetSet[] = {
	{ "range", (getter)PyGetRange, (setter)PySetRange, "range = (x0, y0, z0, x1, y1, z1)", NULL },
	{ NULL }  /* Sentinel */
};

PyTypeObject MPGL_GridDrawDataPyType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGLGrid.draw",			/*tp_name*/
	sizeof(MPGL_GridDrawData),	/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyDealloc,		/*tp_dealloc*/
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
	"draw()",					/* tp_doc */
	0,							/* tp_traverse */
	0,							/* tp_clear */
	0,							/* tp_richcompare */
	0,							/* tp_weaklistoffset */
	0,							/* tp_iter */
	0,							/* tp_iternext */
	PyMethods,					/* tp_methods */
	PyMembers,					/* tp_members */
	PyGetSet,					/* tp_getset */
	0,							/* tp_base */
	0,							/* tp_dict */
	0,							/* tp_descr_get */
	0,							/* tp_descr_set */
	0,							/* tp_dictoffset */
	0,							/* tp_init */
	0,							/* tp_alloc */
	PyNew,						/* tp_new */
};

#endif /* MP_PYTHON_LIB */
