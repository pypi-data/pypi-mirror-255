from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True, kw_only=True)
class Rotation:
    R: list[list[float]]

    @staticmethod
    def zero() -> Rotation:
        return Rotation(R=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])

    @staticmethod
    def from_euler(omega: float, phi: float, kappa: float) -> Rotation:
        Rx = np.array([[1, 0, 0], [0, np.cos(omega), -np.sin(omega)], [0, np.sin(omega), np.cos(omega)]])
        Ry = np.array([[np.cos(phi), 0, np.sin(phi)], [0, 1, 0], [-np.sin(phi), 0, np.cos(phi)]])
        Rz = np.array([[np.cos(kappa), -np.sin(kappa), 0], [np.sin(kappa), np.cos(kappa), 0], [0, 0, 1]])
        return Rotation(R=(Rz @ Ry @ Rx).tolist())

    @staticmethod
    def from_rvec(rvec) -> Rotation:
        return Rotation(R=cv2.Rodrigues(rvec)[0].tolist())

    def __mul__(self, other) -> Rotation:
        return Rotation(R=np.dot(self.R, other.R).tolist())

    @property
    def T(self) -> Rotation:
        return Rotation(R=np.array(self.R).T.tolist())

    @property
    def euler(self) -> tuple[float, float, float]:
        return (
            np.arctan2(self.R[2][1], self.R[2][2]),
            np.arctan2(-self.R[2][0], np.sqrt(self.R[2][1]**2 + self.R[2][2]**2)),
            np.arctan2(self.R[1][0], self.R[0][0]),
        )

    @property
    def total_angle(self) -> float:
        # https://en.wikipedia.org/wiki/Rotation_matrix#Determining_the_angle
        trace = np.trace(self.R)
        return 0 if np.isclose(trace, 3) else np.arccos((trace - 1) / 2)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        omega, phi, kappa = np.round(np.rad2deg(self.euler), 2)
        return f'{omega:6.1f} {phi:6.1f} {kappa:6.1f}'
