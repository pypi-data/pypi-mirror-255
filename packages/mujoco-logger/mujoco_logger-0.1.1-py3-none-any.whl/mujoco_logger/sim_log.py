import json
from enum import Enum

import numpy as np
from numpy import typing as npt

from .convention import muj2pin


class Convention(Enum):
    """
    Enumeration representing different conventions.

    Attributes:
        PIN (int): Pinocchio convention - scalar-last quaternion, world frame linear
        MUJ (int): Mujoco convention - scalar-first quaternion.
    """

    PIN = 1
    MUJ = 2


class SimLog:
    def __init__(self, filename: str, history: dict | None = None) -> None:
        """
        Initialize the SimLog object.

        Args:
            filename (str): The path to the log file.
            history (dict | None, optional): The history dictionary to use.
                If None, the history will be loaded from the file.
        """
        self.__filename = filename

        if history is None:
            with open(self.__filename) as file:
                self.__history = json.load(file)

            for key in self.__history:
                if key.startswith("sensor_") or key.startswith("data_"):
                    self.__history[key] = np.array(self.__history[key])
        else:
            self.__history = history

        # cache pinocchio convention data
        self.__pinpos = None
        self.__pinvel = None

    def __len__(self) -> int:
        """
        Returns the number of entries in the simulation log.

        Returns:
            int: The number of entries in the simulation log.
        """
        return len(self.__history["data_time"])

    def __getitem__(self, key):
        """
        Get the item(s) from the SimLog object using the given key or slice.

        Parameters:
            key (int, slice): The key or slice to retrieve the item(s) from the SimLog object.

        Returns:
            SimLog: A new SimLog object containing the selected item(s).
        """

        if isinstance(key, slice):
            indices = range(*key.indices(self.__len__()))

            copy_history = self.__history.copy()
            for k in copy_history:
                if k.startswith("sensor_") or k.startswith("data_"):
                    copy_history[k] = copy_history[k][indices]

            return SimLog(self.__filename, copy_history)

        copy_history = self.__history.copy()
        for k in copy_history:
            if k.startswith("sensor_") or k.startswith("data_"):
                copy_history[k] = copy_history[k][key]

        return SimLog(self.__filename, copy_history)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    def timestamp(self) -> str:
        """Get the timestamp medatada from the log file.

        Returns:
            str: timestamp when the log was created in ISO format
        """
        return self.__history["timestamp"]

    @property
    def nq(self) -> int:
        """Get the number of generalized coordinates.

        Returns:
            int: generalized coordinates
        """
        return self.__history["nq"]

    @property
    def nv(self) -> int:
        """Get the number of generalized velocities.

        Returns:
            int: generalized velocities
        """
        return self.__history["nv"]

    @property
    def nu(self) -> int:
        """Get the number of control inputs.

        Returns:
            int: control inputs
        """
        return self.__history["nu"]

    def sensor(self, name: str) -> npt.ArrayLike:
        """
        Retrieve the sensor data by name.

        Args:
            name (str): The name of the sensor.

        Returns:
            npt.ArrayLike: The sensor data.

        """
        return self.__history[f"sensor_{name}"]

    def data(self, key: str, convention: Convention = Convention.MUJ) -> npt.ArrayLike:
        """
        Retrieve the data for a given key from the simulation log.

        Args:
            key (str): The key corresponding to the desired data.
            convention (Convention, optional): The convention to use for the data. Defaults to Convention.MUJ.

        Returns:
            npt.ArrayLike: The data corresponding to the given key.

        Raises:
            KeyError: If the key is not found in the simulation log.

        """
        if convention == Convention.MUJ:
            return self.__history[f"data_{key}"]

        # for pinocchio convention we have to apply transformation on qvel and qpos query
        if key not in ["qpos", "qvel"]:
            return self.__history[f"data_{key}"]

        if self.__pinpos is not None and self.__pinvel is not None:
            if key == "qpos":
                return self.__pinpos
            if key == "qvel":
                return self.__pinvel

        # we have to convert one by one
        self.__pinpos = np.zeros_like(self.__history["data_qpos"])
        self.__pinvel = np.zeros_like(self.__history["data_qvel"])

        for i in range(self.__pinpos.shape[0]):
            qi = self.__history["data_qpos"][i]
            vi = self.__history["data_qvel"][i]

            pinpos, pinvel = muj2pin(qi, vi)

            self.__pinpos[i] = pinpos
            self.__pinvel[i] = pinvel

        if key == "qpos":
            return self.__pinpos

        if key == "qvel":
            return self.__pinvel

    @property
    def time(self) -> npt.ArrayLike:
        """
        Get the time array from the simulation log.

        Returns:
            npt.ArrayLike: The time array.
        """
        return self.data("time")

    @property
    def qpin(self) -> npt.ArrayLike:
        """
        Get the joint positions in the pinocchio convention.

        Returns:
            npt.ArrayLike: The joint positions in the pinocchio convention.
        """
        return self.data("qpos", Convention.PIN)

    @property
    def vpin(self) -> npt.ArrayLike:
        """
        Returns the velocity in the pinocchio convention.

        Returns:
            npt.ArrayLike: The velocity in the pinocchio convention.
        """
        return self.data("qvel", Convention.PIN)

    @property
    def dv(self) -> npt.ArrayLike:
        """
        Returns the acceleration.

        Returns:
            npt.ArrayLike: The acceleration.
        """
        return self.data("qacc")

    @property
    def u(self) -> npt.ArrayLike:
        """
        Returns the control input for the simulation.

        Returns:
            npt.ArrayLike: The control input.
        """
        return self.data("ctrl")
