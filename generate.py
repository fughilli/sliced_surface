from matplotlib import pyplot, cm
import math
import numpy
import ezdxf
from typing import NamedTuple


def PlotSurface(function, dimensions):
    xs = numpy.linspace(0, dimensions[0], num=100)
    ys = numpy.linspace(0, dimensions[1], num=100)

    x_grid, y_grid = numpy.meshgrid(xs, ys)
    zs = function(x_grid, y_grid)

    fig, ax = pyplot.subplots(subplot_kw={"projection": "3d"})
    ax.plot_surface(x_grid,
                    y_grid,
                    zs,
                    cmap=cm.coolwarm,
                    linewidth=0,
                    antialiased=True)
    pyplot.show()


def GenerateSerialCode(serial, x_start, bit_width, depth):
    if serial == 0:
        return []

    bits = math.floor(math.log(serial, 2) + 1)
    x = x_start
    points = []
    for i in range(bits):
        bit_depth = (depth / 4) if ((1 << i) & serial) == 0 else depth
        points += [(x, 0), (x, bit_depth)]
        x += bit_width / 2
        points += [(x, bit_depth), (x, 0)]
        x += bit_width / 2
    return points


class Point(NamedTuple):
    x: float
    y: float


class Slice(object):
    def __init__(self, origin, points, serial):
        self.spline_points = numpy.array(points) + origin
        self.box_points = numpy.array([points[0], (points[0].x, 0)] +
                                      GenerateSerialCode(serial, 25.4, 10, 5) +
                                      [(points[-1].x, 0), points[-1]]) + origin

    def Export(msp, tesselate=False):
        pass


def GenerateSlice(origin, xs, y, function, offset, serial):
    ys = function(xs, y) + offset
    spline_points = (numpy.stack((xs, ys), axis=-1) + origin)
    box_points_raw = ([(xs[0], ys[0]),
                       (xs[0], 0)] + GenerateSerialCode(serial, 25.4, 10, 5) +
                      [(xs[-1], 0), (xs[-1], ys[-1])])
    box_points = (numpy.array(box_points_raw) + origin)

    return spline_points, box_points


def AddSlice(msp, offset, spline_points, box_points, tesselate=False):
    if tesselate:
        total_points = numpy.concatenate((spline_points, box_points[::-1][1:]))
        print(len(total_points))
        last_p = total_points[0]
        for p in total_points[1:]:
            msp.add_line(last_p, p)
            last_p = p
    else:
        msp.add_open_spline(spline_points, degree=3)
        msp.add_polyline2d(box_points)
        for i in range(4):
            msp.add_circle(
                numpy.array(
                    (base_thickness / 2 +
                     ((width - base_thickness) * i / 3), base_thickness / 2)) +
                offset, (3. / 8 * inches + 0.5) / 2)


inches = 25.4
feet = 12 * inches

stock_thickness = 0.75 * inches
dimensions = numpy.array((4 * feet, 2.5 * feet))
slices = int(math.ceil(dimensions[1] / (stock_thickness * 2)))
print("num_slices=", slices)
width, height = dimensions
thickness = 6 * inches
base_thickness = 1.5 * inches
wave_thickness = thickness - base_thickness

distance = lambda x, y, origin: numpy.sqrt((x - origin[0])**2 +
                                           (y - origin[1])**2)
wave = lambda x, y, origin, period, falloff: (numpy.cos(
    distance(x, y, origin) / period) / (1 + distance(x, y, origin) * falloff))
surface = lambda x, y: ((wave(x, y, (width / 4, height / 4), 60, 0.002) + wave(
    x, y,
    (width * 3 / 4, height * 3 / 4), 40, 0.005) + 2) / 4 * wave_thickness)

if __name__ == '__main__':
    #PlotSurface(surface, dimensions)

    doc = ezdxf.new(dxfversion='R2010')
    doc.layers.new('ENTITIES', dxfattribs={'color': 2})
    msp = doc.modelspace()

    xs = numpy.linspace(0, dimensions[0], num=10)
    ys = numpy.linspace(0, dimensions[1], num=slices)
    for i, y in enumerate(ys):
        offset = (0, (thickness + 1 * inches) * i)
        AddSlice(msp,
                 offset,
                 *GenerateSlice(offset, xs, y, surface, base_thickness, i + 1),
                 tesselate=False)
    doc.saveas('outputs/total.dxf')

    xs = numpy.linspace(0, dimensions[0], num=100)
    ys = numpy.linspace(0, dimensions[1], num=slices)
    for i, y in enumerate(ys):
        doc = ezdxf.new(dxfversion='R2010')
        doc.layers.new('ENTITIES', dxfattribs={'color': 2})
        msp = doc.modelspace()
        AddSlice(msp, (0, 0),
                 *GenerateSlice((0, 0), xs, y, surface, base_thickness, i + 1),
                 tesselate=True)
        doc.saveas('outputs/slice_{:d}.dxf'.format(i))
