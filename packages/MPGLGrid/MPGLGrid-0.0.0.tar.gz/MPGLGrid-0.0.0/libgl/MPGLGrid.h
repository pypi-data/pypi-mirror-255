#ifndef _MPGLGRID_H
#define _MPGLGRID_H

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

#ifndef _MPGRID_H
#include <MPGrid.h>
#endif

#include <GL/gl.h>
#include <GL/glu.h>

#ifdef MP_PYTHON_LIB
#if PY_MAJOR_VERSION >= 3
#define PY3
#endif
#endif

/*--------------------------------------------------
  text functions
*/
enum { MPGL_TextHelvetica10, MPGL_TextHelvetica12, MPGL_TextHelvetica18 };

void MPGL_TextBitmap(const char s[], int font_type);

/*--------------------------------------------------
  colormap typedef and functions
*/
#define MPGL_COLORMAP_MAX 16

enum { MPGL_ColormapStep, MPGL_ColormapGrad };

typedef struct MPGL_Colormap {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	int mode;
	char title[32];
	int nstep;
	float step_color[MPGL_COLORMAP_MAX][3];
	char label[MPGL_COLORMAP_MAX][32];
	int ngrad;
	float grad_color[MPGL_COLORMAP_MAX][3];
	int nscale;
	double range[2];
	float size[2];
	int font_type;
	float font_color[3];
} MPGL_Colormap;

#ifdef MP_PYTHON_LIB
extern PyTypeObject MPGL_ColormapPyType;
#endif

void MPGL_ColormapInit(MPGL_Colormap *colormap);
void MPGL_ColormapColor(MPGL_Colormap *colormap);
void MPGL_ColormapGrayscale(MPGL_Colormap *colormap);
void MPGL_ColormapStepColor(MPGL_Colormap *colormap, int id, float color[]);
void MPGL_ColormapGradColor(MPGL_Colormap *colormap, double value, float color[]);
void MPGL_ColormapDraw(MPGL_Colormap *colormap);

/*--------------------------------------------------
  scene typedef and functions
*/
enum { MPGL_ProjFrustum, MPGL_ProjOrtho };

typedef struct MPGL_SceneLight {
	float position[4];
	float specular[4];
	float diffuse[4];
	float ambient[4];
} MPGL_SceneLight;

typedef struct MPGL_Scene {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	int proj;
	double znear, zfar;
	float lookat[9];
	float mat_specular[4];
	float mat_shininess;
	float mat_emission[4];
	float clear_color[4];
	int nlight;
	MPGL_SceneLight light[8];
	int width, height;
} MPGL_Scene;

#ifdef MP_PYTHON_LIB
extern PyTypeObject MPGL_ScenePyType;
#endif

void MPGL_SceneInit(MPGL_Scene *scene);
MPGL_SceneLight *MPGL_SceneLightAdd(MPGL_Scene *scene, float x, float y, float z, float w);
void MPGL_SceneSetup(MPGL_Scene *scene);
void MPGL_SceneResize(MPGL_Scene *scene, int width, int height);
void MPGL_SceneFrontText(MPGL_Scene *scene, int x, int y, const char s[], int font_type);

/*--------------------------------------------------
model typedef and functions
*/
enum { MPGL_ModelModeRotate, MPGL_ModelModeTranslate, MPGL_ModelModeZoom };

typedef struct MPGL_Model {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	float mat[4][4];
	float center[3];
	float scale;
	float mat_inv[4][4];
	float init_dir[6];
	float region[6];
	int button_down;
	int button_x, button_y;
	int button_mode;
} MPGL_Model;

#ifdef MP_PYTHON_LIB
extern PyTypeObject MPGL_ModelPyType;
#endif

void MPGL_ModelInit(MPGL_Model *model, float init_dir[], float region[]);
void MPGL_ModelReset(MPGL_Model *model);
void MPGL_ModelFit(MPGL_Model *model);
void MPGL_ModelZoom(MPGL_Model *model, float s);
void MPGL_ModelTranslateZ(MPGL_Model *model, float mz);
void MPGL_ModelTranslateY(MPGL_Model *model, float my);
void MPGL_ModelTranslateX(MPGL_Model *model, float mx);
void MPGL_ModelRotateZ(MPGL_Model *model, float az);
void MPGL_ModelRotateY(MPGL_Model *model, float ay);
void MPGL_ModelRotateX(MPGL_Model *model, float ax);
void MPGL_ModelInverse(MPGL_Model *model);
void MPGL_ModelSetDirection(MPGL_Model *model, float dir[6]);
void MPGL_ModelGetDirection(MPGL_Model *model, float dir[6]);
void MPGL_ModelSetAngle(MPGL_Model *model, float angle[3]);
void MPGL_ModelGetAngle(MPGL_Model *model, float angle[3]);
void MPGL_ModelTransform(MPGL_Model *model);
void MPGL_ModelButton(MPGL_Model *model, int x, int y, int down);
int MPGL_ModelMotion(MPGL_Model *model, MPGL_Scene *scene, int x, int y, int ctrl);

/*--------------------------------------------------
  grid functions
*/
#define MPGL_GRID_TYPE_MAX 256

#define MPGL_GRID_QUADS_LIST0 101
#define MPGL_GRID_QUADS_LIST1 102
#define MPGL_GRID_QUADS_LIST2 103
#define MPGL_GRID_QUADS_LIST3 104
#define MPGL_GRID_QUADS_LIST4 105
#define MPGL_GRID_QUADS_LIST5 106
#define MPGL_GRID_CUBE_LIST 107
#define MPGL_GRID_CYLINDER_LIST 108

enum { MPGL_DrawMethodQuads, MPGL_DrawMethodCubes };
enum { MPGL_DrawKindType, MPGL_DrawKindUpdate, MPGL_DrawKindVal, MPGL_DrawKindCx, MPGL_DrawKindCy, MPGL_DrawKindCz };

typedef struct MPGL_GridDrawData {
#ifdef MP_PYTHON_LIB
	PyObject_HEAD
#endif
	int method;
	int kind;
	int disp[MPGL_GRID_TYPE_MAX];
	int range[6];
} MPGL_GridDrawData;

#ifdef MP_PYTHON_LIB
extern PyTypeObject MPGL_GridDrawDataPyType;
#endif

void MPGL_GridDrawInit(MPGL_GridDrawData *draw);
void MPGL_GridDrawList(void);
void MPGL_GridDrawColormapRange(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap);
void MPGL_GridDraw(MPGL_GridDrawData *draw, MP_GridData *data, MPGL_Colormap *colormap);
void MPGL_GridDrawAxis(int size[]);
void MPGL_GridDrawRegion(MPGL_GridDrawData *draw, MP_GridData *data, float region[]);

#ifdef __cplusplus
}
#endif

#endif /* _MPGLGRID_H */
