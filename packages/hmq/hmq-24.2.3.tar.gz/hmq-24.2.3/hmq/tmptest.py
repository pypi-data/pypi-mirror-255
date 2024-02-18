# %%
import os

os.chdir("/home/ferchault/wrk/hummingqueue/src/user")
import hmq
import numpy as np


# %%
@hmq.task
def dimer_energy(distance: float):
    from pyscf import scf
    from pyscf import gto

    mol = gto.M(atom=f"O 0 0 0; C 0 0 {distance}", basis="cc-pVDZ", verbose=0)
    mf = scf.RHF(mol)
    mf.kernel()
    return mf.e_tot


ds = np.linspace(0.5, 2.0, 1)
for d in ds:
    dimer_energy(d)

tag = dimer_energy.submit(
    tag="tagme",
    ncores=2,
    datacenters="Kassel",
    packages="pyscf,numpy,scipy".split(","),
)
# %%
tag.results


# %%
@hmq.task
def mul(a, b):
    import time

    time.sleep(3)
    return a * b


for i in range(5):
    mul(i, 1)
tag = mul.submit(
    tag="tagme2",
    ncores=1,
    packages="numpy,scipy".split(","),
)
# %%
tag.pull()

# %%
# # %%


@hmq.task
def return_5(value):
    import time

    time.sleep(2)
    return 5


for i in range(300000):
    return_5(i)

tag2 = return_5.submit(tag="test", ncores=1)

# %%
tag2.pull()


# %%
@hmq.task
def sleep(n):
    import time

    time.sleep(1)
    return n


for i in range(10000):
    sleep(2)
tag = sleep.submit(tag="tagme")
# %%
# get results
tag.pull()
# %%
tag.pull()
# %%
tag.to_file("test.hmq")
# %%
tag = hmq.Tag.from_file("test.hmq")
# %%
tag.pull()
# %%
import numpy as np

np.abs(np.random.normal(loc=0, scale=1.48, size=10000)).mean()


# %%
@hmq.task
def test_run():
    import shapely as shp

    return 5


test_run()

tag = test_run.submit()

# %%
tag.pull()
# %%
print(tag.errors[0])


# %%
@hmq.task
def test_run():
    return 5


test_run()

tag = test_run.submit()
# %%
tag.pull()
# %%
tag.results
