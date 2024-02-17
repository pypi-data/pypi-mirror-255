import numpy.typing as npt

from .sim_log import Convention, SimLog


class SimMock:
    def __init__(self, sim_log: SimLog) -> None:
        self.__log = sim_log
        self.__iteration = 0

    @property
    def iteration(self) -> int:
        return self.__iteration

    def __len__(self) -> int:
        return len(self.__log.data("time"))

    def step(self) -> None:
        self.__iteration += 1

    def data(self, key: str, convention: Convention = Convention.MUJ) -> npt.ArrayLike:
        return self.__log.data(key, convention)[self.__iteration]

    def sensor(self, key: str) -> npt.ArrayLike:
        return self.__log.sensor(key)[self.__iteration]

    @property
    def time(self) -> npt.ArrayLike:
        return self.data("time")

    @property
    def qmuj(self) -> npt.ArrayLike:
        return self.data("qpos", Convention.MUJ)

    @property
    def qpin(self) -> npt.ArrayLike:
        return self.data("qpos", Convention.PIN)

    @property
    def vmuj(self) -> npt.ArrayLike:
        return self.data("qvel", Convention.MUJ)

    @property
    def vpin(self) -> npt.ArrayLike:
        return self.data("qvel", Convention.PIN)

    @property
    def dv(self) -> npt.ArrayLike:
        return self.data("qacc")

    @property
    def u(self) -> npt.ArrayLike:
        return self.data("ctrl")
