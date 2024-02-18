#include "MPGLGrid.h"

void MPGL_SceneInit(MPGL_Scene *scene)
{
	scene->proj = MPGL_ProjOrtho;
	scene->znear = 5;
	scene->zfar = 15;
	scene->mat_specular[0] = 0.8f;
	scene->mat_specular[1] = 0.8f;
	scene->mat_specular[2] = 0.8f;
	scene->mat_specular[3] = 1.0;
	scene->mat_shininess = 64.0;
	scene->mat_emission[0] = 0.0;
	scene->mat_emission[1] = 0.0;
	scene->mat_emission[2] = 0.0;
	scene->mat_emission[3] = 1.0;
	scene->clear_color[0] = 0.0;
	scene->clear_color[1] = 0.0;
	scene->clear_color[2] = 0.0;
	scene->clear_color[3] = 0.0;
	scene->nlight = 0;
	scene->width = 0;
	scene->height = 0;
}

MPGL_SceneLight *MPGL_SceneLightAdd(MPGL_Scene *scene, float x, float y, float z, float w)
{
	MPGL_SceneLight *light;

	if (scene->nlight >= 8) return NULL;
	light = &(scene->light[(scene->nlight)++]);
	light->position[0] = x;
	light->position[1] = y;
	light->position[2] = z;
	light->position[3] = w;
	light->specular[0] = 0.8f;
	light->specular[1] = 0.8f;
	light->specular[2] = 0.8f;
	light->specular[3] = 1.0;
	light->diffuse[0] = 0.6f;
	light->diffuse[1] = 0.6f;
	light->diffuse[2] = 0.6f;
	light->diffuse[3] = 1.0;
	light->ambient[0] = 0.3f;
	light->ambient[1] = 0.3f;
	light->ambient[2] = 0.3f;
	light->ambient[3] = 1.0;
	return light;
}

void MPGL_SceneSetup(MPGL_Scene *scene)
{
	int i;
	MPGL_SceneLight *light;
	static int gl_light[8] = {GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, GL_LIGHT4,
		GL_LIGHT5, GL_LIGHT6, GL_LIGHT7};

	glEnable(GL_DEPTH_TEST);
	glEnable(GL_CULL_FACE);
	glEnable(GL_NORMALIZE);
	glShadeModel(GL_SMOOTH);
	/* light */
	if (scene->nlight > 0) {
		glEnable(GL_LIGHTING);
		for (i = 0;i < 8;i++) {
			if (i < scene->nlight) {
				glEnable(gl_light[i]);
				light = &(scene->light[i]);
				glLightfv(gl_light[i], GL_POSITION, light->position);
				glLightfv(gl_light[i], GL_SPECULAR, light->specular);
				glLightfv(gl_light[i], GL_DIFFUSE, light->diffuse);
				glLightfv(gl_light[i], GL_AMBIENT, light->ambient);
			}
			else glDisable(gl_light[i]);
		}
	}
	else glDisable(GL_LIGHTING);
	/* material */	
	glEnable(GL_COLOR_MATERIAL);
	glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);
	glMaterialfv(GL_FRONT, GL_SPECULAR, scene->mat_specular);
	glMaterialf(GL_FRONT, GL_SHININESS, scene->mat_shininess);
	glMaterialfv(GL_FRONT, GL_EMISSION, scene->mat_emission);
	/* clear color and depth */
	glClearColor(scene->clear_color[0], scene->clear_color[1], 
	scene->clear_color[2], scene->clear_color[3]);
	glClearDepth(1.0);
}

void MPGL_SceneResize(MPGL_Scene *scene, int width, int height)
{
	double aspect;

	glViewport(0, 0, width, height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	aspect = (float)width / (float)height;
	if (scene->proj == MPGL_ProjFrustum) {
		glFrustum(-aspect, aspect, -1.0, 1.0, scene->znear, scene->zfar);
	}
	else if (scene->proj == MPGL_ProjOrtho) {
		glOrtho(-aspect, aspect, -1.0, 1.0, scene->znear, scene->zfar);
	}
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
	gluLookAt(10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0);
	scene->width = width;
	scene->height = height;
}

void MPGL_SceneFrontText(MPGL_Scene *scene, int x, int y, const char s[], int font_type)
{
	glRasterPos3d(scene->znear-1.0e-6, (2.0*x-scene->width)/scene->height, 2.0*(scene->height-y)/scene->height-1.0);
	MPGL_TextBitmap(s, font_type);
}

/**********************************************************
* for Python
**********************************************************/
#ifdef MP_PYTHON_LIB

static void PyDealloc(MPGL_Scene *self)
{
#ifndef PY3
	self->ob_type->tp_free((PyObject*)self);
#endif
}

static PyObject *PyNew(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	MPGL_Scene *self;

	self = (MPGL_Scene *)type->tp_alloc(type, 0);
	MPGL_SceneInit(self);
	return (PyObject *)self;
}

static PyObject *PyLightAdd(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	float x, y, z, w;
	static char *kwlist[] = { "x", "y", "z", "w", NULL };
	MPGL_SceneLight *light;

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ffff", kwlist, &x, &y, &z, &w)) {
		return NULL;
	}
	light = MPGL_SceneLightAdd(self, x, y, z, w);
	if (light == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "number of lights is maximum");
		return NULL;
	}
	return Py_BuildValue("i", self->nlight - 1);
}

static PyObject *PyLightPosition(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int id;
	float x, y, z, w;
	static char *kwlist[] = { "id", "x", "y", "z", "w", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iffff", kwlist, &id, &x, &y, &z, &w)) {
		return NULL;
	}
	if (id < 0 || id >= self->nlight) {
		PyErr_SetString(PyExc_ValueError, "invalid id");
		return NULL;
	}
	self->light[id].position[0] = x;
	self->light[id].position[1] = y;
	self->light[id].position[2] = z;
	self->light[id].position[3] = w;
	Py_RETURN_NONE;
}

static PyObject *PyLightSpecular(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int id;
	float r, g, b, a;
	static char *kwlist[] = { "id", "r", "g", "b", "a", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iffff", kwlist, &id, &r, &g, &b, &a)) {
		return NULL;
	}
	if (id < 0 || id >= self->nlight) {
		PyErr_SetString(PyExc_ValueError, "invalid id");
		return NULL;
	}
	self->light[id].specular[0] = r;
	self->light[id].specular[1] = g;
	self->light[id].specular[2] = b;
	self->light[id].specular[3] = a;
	Py_RETURN_NONE;
}

static PyObject *PyLightDiffuse(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int id;
	float r, g, b, a;
	static char *kwlist[] = { "id", "r", "g", "b", "a", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iffff", kwlist, &id, &r, &g, &b, &a)) {
		return NULL;
	}
	if (id < 0 || id >= self->nlight) {
		PyErr_SetString(PyExc_ValueError, "invalid id");
		return NULL;
	}
	self->light[id].diffuse[0] = r;
	self->light[id].diffuse[1] = g;
	self->light[id].diffuse[2] = b;
	self->light[id].diffuse[3] = a;
	Py_RETURN_NONE;
}

static PyObject *PyLightAmbient(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int id;
	float r, g, b, a;
	static char *kwlist[] = { "id", "r", "g", "b", "a", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iffff", kwlist, &id, &r, &g, &b, &a)) {
		return NULL;
	}
	if (id < 0 || id >= self->nlight) {
		PyErr_SetString(PyExc_ValueError, "invalid id");
		return NULL;
	}
	self->light[id].ambient[0] = r;
	self->light[id].ambient[1] = g;
	self->light[id].ambient[2] = b;
	self->light[id].ambient[3] = a;
	Py_RETURN_NONE;
}

static PyObject *PySetup(MPGL_Scene *self, PyObject *args)
{
	MPGL_SceneSetup(self);
	Py_RETURN_NONE;
}

static PyObject *PyResize(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int width, height;
	static char *kwlist[] = { "width", "height", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &width, &height)) {
		return NULL;
	}
	MPGL_SceneResize(self, width, height);
	Py_RETURN_NONE;
}

static PyObject *PyFrontText(MPGL_Scene *self, PyObject *args, PyObject *kwds)
{
	int x, y;
	const char *string;
	int font_type;
	static char *kwlist[] = { "x", "y", "string", "font_type", NULL };

	if (!PyArg_ParseTupleAndKeywords(args, kwds, "iisi", kwlist, &x, &y, &string, &font_type)) {
		return NULL;
	}
	MPGL_SceneFrontText(self, x, y, string, font_type);
	Py_RETURN_NONE;
}

static PyMethodDef PyMethods[] = {
	{ "light_add", (PyCFunction)PyLightAdd, METH_VARARGS | METH_KEYWORDS,
	"light_add(x, y, z, w) : add light" },
	{ "light_position", (PyCFunction)PyLightPosition, METH_VARARGS | METH_KEYWORDS,
	"light_position(id, x, y, z, w) : set light position" },
	{ "light_specular", (PyCFunction)PyLightSpecular, METH_VARARGS | METH_KEYWORDS,
	"light_specular(id, red, green, blue, alpha) : set light specular" },
	{ "light_diffuse", (PyCFunction)PyLightDiffuse, METH_VARARGS | METH_KEYWORDS,
	"light_diffuse(id, red, green, blue, alpha) : set light diffuse" },
	{ "light_ambient", (PyCFunction)PyLightAmbient, METH_VARARGS | METH_KEYWORDS,
	"light_ambient(id, red, green, blue, alpha) : set light ambient" },
	{ "setup", (PyCFunction)PySetup, METH_NOARGS,
	"setup() : setup scene" },
	{ "resize", (PyCFunction)PyResize, METH_VARARGS | METH_KEYWORDS,
	"resize(width, height) : resize window" },
	{ "front_text", (PyCFunction)PyFrontText, METH_VARARGS | METH_KEYWORDS,
	"front_text(x, y, string, font_type) : draw front text" },
	{ NULL }  /* Sentinel */
};

static PyMemberDef PyMembers[] = {
	{ "proj", T_INT, offsetof(MPGL_Scene, proj), 0, "proj = {0:frustum | 1:ortho} : projection mode" },
	{ "znear", T_DOUBLE, offsetof(MPGL_Scene, znear), 0, "znear = z : znear of viewing volume" },
	{ "zfar", T_DOUBLE, offsetof(MPGL_Scene, zfar), 0, "zfar = z : zfar of viewing volume" },
	{ "mat_shininess", T_FLOAT, offsetof(MPGL_Scene, mat_shininess), 0, "mat_shininess = shininess : material shininess" },
	{ "width", T_INT, offsetof(MPGL_Scene, width), 1, "width : screen width" },
	{ "height", T_INT, offsetof(MPGL_Scene, height), 1, "height : screen height" },
	{ NULL }  /* Sentinel */
};

static PyObject *PyGetMatSpecular(MPGL_Scene *self, void *closure)
{
	return Py_BuildValue("dddd", self->mat_specular[0], self->mat_specular[1],
		self->mat_specular[2], self->mat_specular[3]);
}

static int PySetMatSpecular(MPGL_Scene *self, PyObject *value, void *closure)
{
	float r, g, b, a;

	if (!PyArg_ParseTuple(value, "ffff", &r, &g, &b, &a)) {
		return -1;
	}
	self->mat_specular[0] = r, self->mat_specular[1] = g, self->mat_specular[2] = b, self->mat_specular[3] = a;
	return 0;
}

static PyObject *PyGetMatEmission(MPGL_Scene *self, void *closure)
{
	return Py_BuildValue("dddd", self->mat_emission[0], self->mat_emission[1],
		self->mat_emission[2], self->mat_emission[3]);
}

static int PySetMatEmission(MPGL_Scene *self, PyObject *value, void *closure)
{
	float r, g, b, a;

	if (!PyArg_ParseTuple(value, "ffff", &r, &g, &b, &a)) {
		return -1;
	}
	self->mat_emission[0] = r, self->mat_emission[1] = g, self->mat_emission[2] = b, self->mat_emission[3] = a;
	return 0;
}

static PyObject *PyGetClearColor(MPGL_Scene *self, void *closure)
{
	return Py_BuildValue("dddd", self->clear_color[0], self->clear_color[1],
		self->clear_color[2], self->clear_color[3]);
}

static int PySetClearColor(MPGL_Scene *self, PyObject *value, void *closure)
{
	float r, g, b, a;

	if (!PyArg_ParseTuple(value, "ffff", &r, &g, &b, &a)) {
		return -1;
	}
	self->clear_color[0] = r, self->clear_color[1] = g, self->clear_color[2] = b, self->clear_color[3] = a;
	return 0;
}

static PyGetSetDef PyGetSet[] = {
	{ "mat_specular", (getter)PyGetMatSpecular, (setter)PySetMatSpecular, "mat_specular = (red, green, blue, alpha) : material specular", NULL },
	{ "mat_emission", (getter)PyGetMatEmission, (setter)PySetMatEmission, "mat_emission = (red, green, blue, alpha) : material emission", NULL },
	{ "clear_color", (getter)PyGetClearColor, (setter)PySetClearColor, "clear_color = (red, green, blue, alpha) : clear color", NULL },
	{ NULL }  /* Sentinel */
};

PyTypeObject MPGL_ScenePyType = {
	PyObject_HEAD_INIT(NULL)
#ifndef PY3
	0,							/*ob_size*/
#endif
	"MPGLGrid.scene",			/*tp_name*/
	sizeof(MPGL_Scene),	/*tp_basicsize*/
	0,							/*tp_itemsize*/
	(destructor)PyDealloc,	/*tp_dealloc*/
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
	"scene()",					/* tp_doc */
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