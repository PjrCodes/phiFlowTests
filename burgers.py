import matplotlib.pyplot as plt
from phi.jax.flow import *

@jit_compile
def step(v, dt=.5):
    v = diffuse.implicit(v, 0.1, dt=dt)
    v = advect.semi_lagrangian(v, v, dt=dt)
    return v

v0 = CenteredGrid(Noise(vector='x,y'), PERIODIC, x=64, y=64, bounds=Box(x=40, y=20))
v_trj = iterate(step, batch(time=100), v0)
plot(v_trj.as_points(), animate='time')
plt.show()
