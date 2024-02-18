import cv2
import numpy as np
import vtk


def make_subplot(
    actors, xmin, ymin, xmax, ymax, direction, focal_point, zoom, view_up=[0, 0, 1]
):
    renderer = vtk.vtkRenderer()
    renderer.SetViewport(xmin, ymin, xmax, ymax)
    for actor in actors:
        renderer.AddActor(actor)
    camera = vtk.vtkCamera()
    camera.ParallelProjectionOn()
    position = np.array(focal_point) - np.array(direction)
    camera.SetPosition(*position)
    camera.SetFocalPoint(*focal_point)
    camera.SetViewUp(*view_up)
    renderer.SetActiveCamera(camera)
    renderer.SetBackground(1, 1, 1)
    if zoom is not None:
        renderer.GetActiveCamera().Zoom(zoom)
    return renderer


def render_interactive(subplots, size=(800, 400)):
    win = vtk.vtkRenderWindow()
    for renderer in subplots:
        win.AddRenderer(renderer)
    win.SetSize(size[0], size[1])
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(win)
    iren.Initialize()
    iren.Start()


def render_off_screen(subplots, size=(800, 400), aa_frames=10):
    win = vtk.vtkRenderWindow()
    win.OffScreenRenderingOn()

    for renderer in subplots:
        win.AddRenderer(renderer)

    win.SetMultiSamples(aa_frames)
    win.SetSize(size[0], size[1])
    win.Render()

    img_data = vtk.vtkFloatArray()
    win.GetRGBAPixelData(0, 0, size[0] - 1, size[1] - 1, 1, img_data)
    img_data = vtk.util.numpy_support.vtk_to_numpy(img_data).reshape(size[::-1] + (4,))[
        ::-1
    ]

    return img_data


def plot_to_file(
    surfaces,
    out_fn,
    zoom=None,
    aa_frames=10,
    size=(1728, 1800),
    magnification=1,
    ventral=True,
    lh_actors=[],
    rh_actors=[],
    focal_points=[0, 0, 0],
):
    if surfaces is not None:
        focal_points = surfaces.focal_points
        actors = surfaces.get_actors()
        lh_actors = [actors[0]] + lh_actors
        rh_actors = [actors[1]] + rh_actors
        if zoom is None:
            zoom = surfaces.zoom

    subplots = [
        make_subplot(
            lh_actors,
            0,
            2.0 / 3.0,
            0.5,
            1,
            direction=[800, 0, 0],
            focal_point=focal_points[0],
            zoom=zoom,
        ),
        make_subplot(
            rh_actors,
            0.5,
            2.0 / 3.0,
            1,
            1,
            direction=[-800, 0, 0],
            focal_point=focal_points[1],
            zoom=zoom,
        ),
        make_subplot(
            lh_actors,
            0,
            1.0 / 3.0,
            0.5,
            2.0 / 3.0,
            direction=[-800, 0, 0],
            focal_point=focal_points[0],
            zoom=zoom,
        ),
        make_subplot(
            rh_actors,
            0.5,
            1.0 / 3.0,
            1,
            2.0 / 3.0,
            direction=[800, 0, 0],
            focal_point=focal_points[1],
            zoom=zoom,
        ),
        make_subplot(
            lh_actors,
            0,
            0,
            0.5,
            1.0 / 3.0,
            direction=[0, 0, 800],
            view_up=[-1, 0, 0],
            # focal_point=[-offset, mid[1], mid[2]],
            focal_point=focal_points[0],
            zoom=zoom,
        ),
        make_subplot(
            rh_actors,
            0.5,
            0,
            1,
            1.0 / 3.0,
            direction=[0, 0, 800],
            view_up=[1, 0, 0],
            # focal_point=[offset, mid[1], mid[2]],
            focal_point=focal_points[1],
            zoom=zoom,
        ),
    ]
    # base_fn = out_fn.replace('.png', '')
    # vtk_fn = base_fn + '_vtk.png'
    size = tuple(_ * magnification for _ in size)
    im = render_off_screen(subplots, size=size, aa_frames=aa_frames)

    h = size[1] // 3
    hh, hh_start = int(h * 0.6), int(h * 2.2)
    im_lateral = im[:h]
    im_medial = im[h : h * 2]
    if ventral:
        im_ventral = im[hh_start : hh_start + hh]
        im = np.concatenate([im_lateral, im_ventral, im_medial], axis=0)
    else:
        im = np.concatenate([im_lateral, im_medial], axis=0)

    # shape = tuple(_//magnification for _ in im.shape[:2])
    # print(im.shape, shape)
    # im = cv2.resize(im, shape[::-1], interpolation=cv2.INTER_AREA)
    if out_fn is None:
        return im
    im = np.round(im * 65535).astype(np.uint16)
    cv2.imwrite(out_fn, cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA))


def plot_interactive(actors, focal=None, zoom=0.013, size=(1728, 1800)):
    subplots = [
        make_subplot(
            actors,
            0,
            0,
            1,
            1,
            direction=[800, 0, 0],
            focal_point=([0, 0, 0] if focal is None else focal),
            zoom=zoom,
        ),
    ]
    render_interactive(subplots, size=size)
