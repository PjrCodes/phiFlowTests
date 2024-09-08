"""Karman Vortex Street
Air flow around a static cylinder.
Vortices start appearing after a couple of hundred steps.
"""

from phi.torch import flow
from tqdm import trange
from matplotlib import pyplot as plt
from procGen import procGen


rect_set = procGen.generate_buildings(procGen.Size(100, 100), density=0.8, limit_count=10)

WORLD_WIDTH = 100
WORLD_HEIGHT = 100

SPEED_X = 10
SPEED_Y = -10

SPEEDS = flow.tensor([SPEED_X, SPEED_Y])

velocity = flow.StaggeredGrid(
    SPEEDS,
    flow.ZERO_GRADIENT,
    x=WORLD_WIDTH,
    y=WORLD_HEIGHT,
    bounds=flow.Box(x=WORLD_WIDTH, y=WORLD_HEIGHT),
)


cuboid_list = []
for start, end in rect_set:
    cuboid_list.append(flow.Box(flow.vec(x=start.x, y=start.y), flow.vec(x=end.x, y=end.y)))

# make all of them obstacles

obstacle_list = []
for cuboid in cuboid_list:
    obstacle_list.append(flow.Obstacle(cuboid))

BOUNDARY_BOX = flow.Box(x=(-1 * flow.INF, 0.5), y=None)
BOUNDARY_MASK = flow.StaggeredGrid(
    BOUNDARY_BOX, velocity.extrapolation, velocity.bounds, velocity.resolution
)

pressure = None


@flow.math.jit_compile
def step(v, p):
    v = flow.advect.semi_lagrangian(v, v, 1.0)
    v = v * (1 - BOUNDARY_MASK) + BOUNDARY_MASK * (
        SPEED_X,
        SPEED_Y,
    )  # make sure you dont simulat OOB
    v, p = flow.fluid.make_incompressible(
        v, obstacle_list, flow.Solve("auto", 1e-5, x0=p)
    )  # make it do the boundary thign
    return v, p


traj, _ = flow.iterate(step, flow.batch(time=100), velocity, pressure, range=trange)
anim = flow.plot(
    [traj.curl(), *cuboid_list[::-1]],
    animate="time",
    size=(6, 6),
    frame_time=10,
    overlay="list",
    # plt_params={"cmap":"coolwarm"},
)

plt.show()
