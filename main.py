"""Karman Vortex Street
Air flow around a static cylinder.
Vortices start appearing after a couple of hundred steps.
"""

from phi.torch import flow
from tqdm import trange
from matplotlib import pyplot as plt

WORLD_WIDTH = 64
WORLD_HEIGHT = 64

SPEED_X = 10
SPEED_Y = 0
SPEED_X2 = -10
SPEED_Y2 = 0

SPEEDS = flow.tensor([SPEED_X, SPEED_Y])

velocity = flow.StaggeredGrid(
    SPEEDS,
    flow.ZERO_GRADIENT,
    x=WORLD_WIDTH,
    y=WORLD_HEIGHT,
    bounds=flow.Box(x=WORLD_WIDTH, y=WORLD_HEIGHT),
)


CUBOID_1 = flow.Box(flow.vec(x=15, y=32), flow.vec(x=20, y=42))
CUBOID_2 = flow.Box(flow.vec(x=15, y=50), flow.vec(x=30, y=60))
CUBOID_3 = flow.Box(flow.vec(x=10, y=10), flow.vec(x=20, y=20))

# CUTU = flow.geom.Cuboid(flow.vec(x=15, y=32), x=5, y=10)
# CUTD = flow.geom.Cuboid(flow.vec(x=15, y=50), x=15, y=10)

OBSTACLE_CUBOID_1 = flow.Obstacle(CUBOID_1)
OBSTACLE_CUBOID_2 = flow.Obstacle(CUBOID_2)
OBSTACLE_CUBOID_3 = flow.Obstacle(CUBOID_3)

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
        v, [OBSTACLE_CUBOID_1, OBSTACLE_CUBOID_2, OBSTACLE_CUBOID_3], flow.Solve("auto", 1e-5, x0=p)
    )  # make it do the boundary thign
    return v, p


traj, _ = flow.iterate(step, flow.batch(time=100), velocity, pressure, range=trange)
anim = flow.plot(
    [traj.curl(), CUBOID_3, CUBOID_2, CUBOID_1],
    animate="time",
    size=(6, 6),
    frame_time=10,
    overlay="list",
    # plt_params={"cmap":"coolwarm"},
)

plt.show()
