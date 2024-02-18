# type: ignore
import warnings
from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    conlist,
    field_validator,
    model_validator,
)
from scipy.interpolate import interp1d
from typing_extensions import TypedDict

from . import projected
from .qpu import QPUBase, QPUName

JobName = Annotated[str, StringConstraints(min_length=1, max_length=50)]

JobNote = Annotated[str, StringConstraints(max_length=500)]


class JobOrigin(str, Enum):
    WEB = "WEB"
    OQTAPI = "OQTAPI"


class JobType(str, Enum):
    BEC = "BEC"
    BARRIER = "BARRIER"
    BRAGG = "BRAGG"
    TRANSISTOR = "TRANSISTOR"
    PAINT_1D = "PAINT_1D"

    def __str__(self):
        return str(self.value)


class ImageType(str, Enum):
    IN_TRAP = "IN_TRAP"
    TIME_OF_FLIGHT = "TIME_OF_FLIGHT"

    def __str__(self):
        return str(self.value)


class OutputJobType(str, Enum):
    IN_TRAP = "IN_TRAP"
    NON_IN_TRAP = "NON_IN_TRAP"

    def __str__(self):
        return str(self.value)


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INCOMPLETE = "INCOMPLETE"

    def __str__(self):
        return str(self.value)


class RfInterpolationType(str, Enum):
    LINEAR = "LINEAR"
    STEP = "STEP"
    OFF = "OFF"
    PREVIOUS = "PREVIOUS"  # assumes value of previous data point

    def __str__(self):
        return str(self.value)


class InterpolationType(str, Enum):
    LINEAR = "LINEAR"
    SMOOTH = "SMOOTH"
    STEP = "STEP"
    OFF = "OFF"
    # native scipy options
    ZERO = "ZERO"  # spline interpolation at zeroth order
    SLINEAR = "SLINEAR"  # spline interpolation at first order
    QUADRATIC = "QUADRATIC"  # spline interpolation at second order
    CUBIC = "CUBIC"  # spline interpolation at third order
    # LINEAR = "LINEAR"         # self explanatory
    NEAREST = "NEAREST"  # assumes value of nearest data point
    PREVIOUS = "PREVIOUS"  # assumes value of previous data point
    NEXT = "NEXT"  # assumes value of next data point

    def __str__(self):
        return str(self.value)


class LaserType(str, Enum):
    TERMINATOR = "TERMINATOR"
    BRAGG = "BRAGG"

    def __str__(self):
        return str(self.value)


class ShapeType(str, Enum):
    GAUSSIAN = "GAUSSIAN"
    LORENTZIAN = "LORENTZIAN"
    SQUARE = "SQUARE"

    def __str__(self):
        return str(self.value)


def interpolation_to_kind(interpolation: InterpolationType) -> str:
    """Method to convert our InterpolationType to something scipy can understand

    Args:
        interpolation (bert_schemas.job.InterpolationType): Primitive job interpolation type

    Returns:
        str: A "kind" string to be used by scipy's interp1d
    """
    interpolation_map = {"OFF": "zero", "STEP": "previous", "SMOOTH": "cubic"}

    return interpolation_map.get(interpolation, interpolation.lower())


def interpolate_1d(
    xs: list[float],
    ys: list[float],
    x: float,
    interpolation: InterpolationType = "LINEAR",
) -> float:
    """Method to interpolate a 1D list of pairs [xs, ys] at the evaluation point x

    Args:
        xs (list[float]): List of x values
        ys (list[float]): List of y values
        x (float): Desired x-coordinate to evaluate the resulting interpolation function
        interpolation (job_schema.InterpolationType, optional): Interpolation style

    Returns:
        float: Interpolation function value at the specified x-coordinate
    """
    f = interp1d(
        xs,
        ys,
        kind=interpolation_to_kind(interpolation),
        bounds_error=False,
        fill_value=(0.0, 0.0),
    )
    return f(x)[()]  # extract value


def interpolate_1d_list(
    xs: list[float],
    ys: list[float],
    x_values: list[float],
    interpolation: InterpolationType = "LINEAR",
) -> list[float]:
    """Method to interpolate a 1d list of pairs [xs, ys] at the evaluation points given by x_values

    Args:
        xs (list[float]): List of x values
        ys (list[float]): List of y values
        x_values (list[float]): Desired x-coordinates to evaluate the resulting interpolation function
        interpolation (job_schema.InterpolationType, optional): Interpolation style

    Returns:
        list[float]: Floating point values corresponding to evaluation of the interpolation function
            value at the specified x_values
    """
    f = interp1d(
        xs,
        ys,
        kind=interpolation_to_kind(interpolation),
        bounds_error=False,
        fill_value=(0.0, 0.0),
    )
    return list(f(x_values))


class Image(BaseModel):
    pixels: list[float]
    rows: int
    columns: int
    pixcal: float | None = 1.0
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Point(TypedDict):
    x: float
    y: float


class LineChart(BaseModel):
    points: list[dict[str, float]]
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class RfEvaporation(BaseModel):
    # times_ms upper range can be no larger than end_time_ms of job (80 ms is upper default)
    times_ms: Annotated[
        list[Annotated[int, Field(ge=-2000, le=80)]],
        Field(min_length=1, max_length=20),
    ] = list(range(-1600, 400, 400))
    frequencies_mhz: Annotated[
        list[Annotated[float, Field(ge=0.0, le=25.0)]],
        Field(min_length=1, max_length=20),
    ]
    powers_mw: Annotated[
        list[Annotated[float, Field(ge=0.0, le=1000.0)]],
        Field(min_length=1, max_length=20),
    ]
    interpolation: RfInterpolationType
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    @field_validator("times_ms")
    @classmethod
    def two_values_less_equal_zero(cls, v):
        if not len([elem for elem in v if elem <= 0]) >= 2:
            raise ValueError("At least two values must be <= 0.")
        return v

    @model_validator(mode="after")
    def cross_validate(self) -> "RfEvaporation":
        if not len(self.times_ms) == len(self.frequencies_mhz) == len(self.powers_mw):
            raise ValueError("RfEvaporation data lists must have the same length.")

        if self.times_ms != sorted(self.times_ms):
            warnings.warn(
                "Evaporation times_ms list must be naturally ordered, re-ordering.",
                stacklevel=2,
            )
            self.times_ms, self.frequencies_mhz, self.powers_mw = zip(
                *sorted(
                    zip(
                        self.times_ms,
                        self.frequencies_mhz,
                        self.powers_mw,
                    )
                )
            )
        return self


class Landscape(BaseModel):
    # time_ms upper range can be no larger than end_time_ms of job (80 ms is upper default)
    time_ms: Annotated[float, Field(ge=0.0, le=80.0)] = 0.0
    potentials_khz: Annotated[
        list[Annotated[float, Field(ge=0.0, le=100.0)]],
        Field(min_length=2, max_length=121),
    ] = [0.0, 0.0]
    positions_um: Annotated[
        list[Annotated[float, Field(ge=-60.0, le=60.0)]],
        Field(min_length=2, max_length=121),
    ] = [-1.0, 1.0]
    spatial_interpolation: InterpolationType = InterpolationType.LINEAR

    @computed_field
    @property
    def interpolation_kind(self) -> str:
        if self.spatial_interpolation == InterpolationType.OFF:
            kind = "zero"
        else:
            kind = InterpolationType[self.spatial_interpolation].name.lower()
        return kind

    @model_validator(mode="after")
    def cross_validate(self):
        if not len(self.positions_um) == len(self.potentials_khz):
            raise ValueError("Landscape data lists must have the same length.")

        if self.positions_um != sorted(self.positions_um):
            warnings.warn(
                "Landscape positions_um list must be naturally ordered, re-ordering.",
                stacklevel=2,
            )
            self.positions_um, self.potentials_khz = zip(
                *sorted(zip(self.positions_um, self.potentials_khz))
            )
        return self

    def get_ideal_potential(
        self, time=0.0, positions: list = projected.PROJECTED_SPOTS
    ) -> list[float]:
        """Method to get the ideal potential energy at the specified positions

        Args:
            positions (list, optional): List of positions in microns

        Returns:
            list[float]: Potential energies, in kHz, at the specified positions
        """
        potentials = interpolate_1d_list(
            self.positions_um,
            self.potentials_khz,
            positions,
            self.spatial_interpolation,
        )
        return potentials

    def get_potential(self, positions: list[float]) -> list[float]:
        """Method to calculate the optical potential associated with a Landscape object,
        taking into account the actual implementation of the Oqtant projection system,
        at the given time

        Args:
            positions (list[float]): Positions, in microns, where the potential should be evaluated

        Returns:
            list[float]: Potential energies, in kHz, at the specified positions
        """
        return projected.get_actual_potential(
            self.get_ideal_potential, positions=positions
        )

    def get_position_spectrum(self, positions_um: np.ndarray) -> np.ndarray:
        """Get positional weights over the given positions"""
        spectrum = interpolate_1d_list(
            self.positions_um,
            self.potentials_khz,
            positions_um,
            self.interpolation_kind,
        )
        return np.asarray(spectrum)

    def __lt__(self, other):
        return self.time_ms < other.time_ms


class OpticalLandscape(BaseModel):
    interpolation: InterpolationType = InterpolationType.LINEAR
    landscapes: Annotated[list[Landscape], Field(min_length=1, max_length=5)]
    model_config = ConfigDict(validate_assignment=True)

    @computed_field
    @property
    def interpolation_kind(self) -> str:
        if self.interpolation == "OFF":
            kind = "zero"
        else:
            kind = InterpolationType[self.interpolation].name.lower()
        return kind

    @model_validator(mode="after")
    def cross_validate(self):
        # ensure the individual Landscape objects are far enough apart in time and naturally (time) ordered
        if len(self.landscapes) > 1:
            if sorted(self.landscapes) != self.landscapes:
                self.landscapes = sorted(
                    self.landscapes, key=lambda landscape: landscape.time_ms
                )

            dts_ms = [
                self.landscapes[i + 1].time_ms - self.landscapes[i].time_ms
                for i in range(len(self.landscapes) - 1)
            ]
            if not all(dt >= 1 for dt in dts_ms):
                raise ValueError(
                    "Constituent Landscape object time_ms values must differ by >= 1 ms"
                )
        return self

    def get_ideal_potential(
        self, time: float, positions: list[float] = projected.PROJECTED_SPOTS
    ) -> list[float]:
        """Method to calculate ideal object potential energy at the specified time and positions

        Args:
            time (float): Time, in ms, at which the potential energy is calculated
            positions (list[float], optional): Positions at which the potential energy is calculated

        Returns:
            list[float]: Potential energies, in kHz, at specified time and positions
        """
        potential = [0.0] * len(positions)
        snaps = self.landscapes if hasattr(self, "landscapes") else self.snapshots

        if len(snaps) < 2:
            return potential
        snap_times = [snap.time_ms for snap in snaps]
        if time >= min(snap_times) and time <= max(snap_times):
            pre = next(snap for snap in reversed(snaps) if snap.time_ms <= time)
            nex = next(snap for snap in snaps if snap.time_ms >= time)
            potential = [
                interpolate_1d(
                    [pre.time_ms, nex.time_ms], [p1, p2], time, self.interpolation
                )
                for p1, p2 in zip(
                    pre.get_ideal_potential(positions=positions),
                    nex.get_ideal_potential(positions=positions),
                )
            ]
        return potential

    def get_potential(
        self, time: float, positions: list = projected.PROJECTED_SPOTS
    ) -> list[float]:
        """Method to calculate the optical potential associated with a Landscape object,
        taking into account the actual implementation of the Oqtant projection system,
        at the given time

        Args:
            time (float): Time, in ms, at which to sample the potential energy
            positions (list[float], optional): Positions, in microns, where the potential should be evaluated

        Returns:
            list[float]: Potential energies, in kHz, at the requested positions and time
        """
        return projected.get_actual_potential(
            self.get_ideal_potential, time=time, positions=positions
        )

    def get_position_spectra(
        self, times_ms: float, positions_um: np.ndarray
    ) -> np.ndarray:
        """Get the position spectrum over the specified positions at the given times"""
        potentials_khz = np.zeros(shape=(len(times_ms), len(positions_um)))
        # construct "current" profile as weighted sum of constituent profiles
        profiles = self.landscapes
        for indx, time_ms in enumerate(times_ms):
            is_active = (
                time_ms >= profiles[0].time_ms and time_ms < profiles[-1].time_ms
            )
            if not is_active:
                potentials_khz[indx] = np.zeros_like(potentials_khz[0])
            else:
                prev_profile = next(
                    profile
                    for profile in reversed(profiles)
                    if profile.time_ms <= time_ms
                )
                next_profile = next(
                    profile for profile in profiles if profile.time_ms > time_ms
                )
                prev_potential = prev_profile.get_position_spectrum(positions_um)
                next_potential = next_profile.get_position_spectrum(positions_um)
                t_prev = prev_profile.time_ms
                t_next = next_profile.time_ms
                prev_weight = (t_next - time_ms) / (t_next - t_prev)
                next_weight = (time_ms - t_prev) / (t_next - t_prev)
                # snapshot landscapes/profiles connected w/ linear interpolation in time
                potentials_khz[indx] = (
                    prev_weight * prev_potential + next_weight * next_potential
                )
        return potentials_khz


class TofFit(BaseModel):
    gaussian_od: float
    gaussian_sigma_x: float
    gaussian_sigma_y: float
    tf_od: float
    tf_x: float
    tf_y: float
    x_0: float
    y_0: float
    offset: float
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class Barrier(BaseModel):
    # times_ms upper range can be no larger than end_time_ms of job (80 ms is upper default)
    times_ms: Annotated[
        list[Annotated[float, Field(ge=0.0, le=80.0)]],
        Field(min_length=2, max_length=20),
    ] = list(np.arange(1, 12, 1.0))
    positions_um: Annotated[
        list[Annotated[float, Field(ge=-60.0, le=60.0)]],
        Field(min_length=2, max_length=20),
    ] = list(np.arange(1, 12, 1.0))
    heights_khz: Annotated[
        list[Annotated[float, Field(ge=0.0, le=100.0)]],
        Field(min_length=2, max_length=20),
    ] = [10.0] * 11
    widths_um: Annotated[
        list[Annotated[float, Field(ge=0.5, le=50.0)]],
        Field(min_length=2, max_length=20),
    ] = [1.0] * 11
    interpolation: InterpolationType = InterpolationType.LINEAR
    shape: ShapeType = ShapeType.GAUSSIAN
    model_config = ConfigDict(validate_assignment=True)

    @property
    def interpolation_kind(self) -> str:
        if self.interpolation == "OFF":
            kind = "zero"
        else:
            kind = InterpolationType[self.interpolation].name.lower()
        return kind

    @model_validator(mode="after")
    def cross_validate(self):
        if not (
            len(self.times_ms)
            == len(self.positions_um)
            == len(self.heights_khz)
            == len(self.widths_um)
        ):
            raise ValueError("Barrier data lists must have the same length.")

        if self.times_ms != sorted(self.times_ms):
            warnings.warn(
                "Barrier times_ms list must be naturally ordered, re-ordering.",
                stacklevel=2,
            )
            (
                self.times_ms,
                self.positions_um,
                self.heights_khz,
                self.widths_um,
            ) = zip(
                *sorted(
                    zip(
                        self.times_ms,
                        self.positions_um,
                        self.heights_khz,
                        self.widths_um,
                    )
                )
            )
        return self

    @property
    def lifetime(self) -> float:
        """Property to get the lifetime value of a Barrier object

        Returns:
            float: The amount of time, in ms, that the barrier will exist
        """
        return self.death - self.birth

    @property
    def birth(self) -> float:
        """Property to get the (manipulation stage) time that the Barrier object will be created

        Returns:
            float: The time, in ms, at which the barrier will start being projected
        """
        return min(self.times_ms)

    @property
    def death(self) -> float:
        """Property to get the (manipulation stage) time that the Barrier object will cease to exist

        Returns:
            float: The time, in ms, at which the barrier will stop being projected
        """
        return max(self.times_ms)

    def evolve(
        self,
        duration: float,
        position: float = None,
        height: float = None,
        width: float = None,
    ) -> None:
        """Method to evolve the position, height, and/or width of a Barrier object over a duration

        Args:
            duration (float): The time, in ms, over which evolution should take place
            position (float | None, optional): The position, in microns, to evolve to
            height (float | None, optional): The height, in kHz, to evolve to
            width (float | None, optional): The width, in microns, to evolve to
        """
        if position is None:
            position = self.positions_um[-1]
        if height is None:
            height = self.heights_khz[-1]
        if width is None:
            width = self.widths_um[-1]
        self.positions_um.append(position)
        self.heights_khz.append(height)
        self.widths_um.append(width)
        self.times_ms.append(self.times_ms[-1] + duration)

    def is_active(self, time: float) -> bool:
        """Method to determine if a Barrier object is active (exists) at the specified time

        Args:
            time (float): The time, in ms, at which the query is evaluated

        Returns:
            bool: Flag indicating if the barrier exists or not at the specified time
        """
        return time >= self.times_ms[0] and time <= self.times_ms[-1]

    def get_positions(self, times: list[float]) -> list[float]:
        """Method to calculate the Barrier object position at the specified (manipulation stage) times

        Args:
            times (list[float]): The times, in ms, at which positions are calculated

        Returns:
            list[float]: The positions, in microns, at the specified times
        """
        return interpolate_1d_list(
            self.times_ms,
            self.positions_um,
            projected.get_corrected_times(times=times),
            self.interpolation_kind,
        )

    def get_position(self, time: float) -> float:
        """Method to calculate the Barrier object position at the specified (manipulation stage) time

        Args:
            time (float): The time, in ms, at which the position is calculated

        Returns:
            float: The position, in microns, at the specified time
        """
        return self.get_positions(times=[time])[0]

    def get_heights(self, times: list[float]) -> list[float]:
        """Method to calculate the Barrier object heights at the specified list of times

        Args:
            times (list[float]): The times, in ms, at which the heights are calculated

        Returns:
            list[float]: The barrier heights at the specified times
        """
        return interpolate_1d_list(
            self.times_ms,
            self.heights_khz,
            projected.get_corrected_times(times=times),
            self.interpolation_kind,
        )

    def get_height(self, time: float) -> float:
        """Method to get the Barrier object height at the specified time

        Args:
            time (float): The time, in ms, at which the height is calculated

        Returns:
            float: The barrier height at the specified time
        """
        return self.get_heights(times=[time])[0]

    def get_widths(self, times: list[float]) -> list[float]:
        """Method to calculate the Barrier object widths at the specified times

        Args:
            times (list[float]): The times, in ms, at which the heights are calculated

        Returns:
            list[float]: The barrier widths at the specified times
        """
        return interpolate_1d_list(
            self.times_ms,
            self.widths_um,
            projected.get_corrected_times(times=times),
            self.interpolation_kind,
        )

    def get_width(self, time: float) -> float:
        """Method to calculate the Barrier object width at the specified time

        Args:
            times (float): The time, in ms, at which the height is calculated

        Returns:
            float: The barrier width at the specified time
        """
        return self.get_widths(times=[time])[0]

    def get_params(self, time_ms: float) -> dict:
        kind = self.get_interpolation_kind()
        params = {}
        params["position_um"] = interpolate_1d(
            self.times_ms, self.positions_um, time_ms, kind
        )
        params["width_um"] = interpolate_1d(
            self.times_ms, self.widths_um, time_ms, kind
        )
        params["height_khz"] = interpolate_1d(
            self.times_ms, self.heights_khz, time_ms, kind
        )
        return params

    def get_ideal_potential(
        self, time: float = 0.0, positions: list[float] = projected.PROJECTED_SPOTS
    ) -> list[float]:
        """Method to calculate the ideal Barrier object potential energy at the given positions
        and at the specified time without taking into account finite projection system resolution
        to update time of projected light

        Args:
            time (float, optional): The time, in ms, at which the potential is calculated
            positions (list[float], optional): The positions, in microns, at which the potential
                energies are evaluated

        Returns:
            list[float]: The potential energies, in kHz, at the specified positions
        """
        height = self.get_height(time)
        position = self.get_position(time)
        weight = self.get_width(time)
        potential = [0.0] * len(positions)
        if height <= 0 or weight <= 0 or not self.is_active(time):
            return potential
        if self.shape == "SQUARE":  # width = half width
            potential = [
                0 if (p < position - weight or p > position + weight) else height
                for p in positions
            ]
        elif self.shape == "LORENTZIAN":  # width == HWHM (half-width half-max)
            potential = [
                height / (1 + ((p - position) / weight) ** 2) for p in positions
            ]
        elif self.shape == "GAUSSIAN":  # width = sigma (Gaussian width)
            potential = [
                height * np.exp(-((p - position) ** 2) / (2 * weight**2))
                for p in positions
            ]
        return potential

    def get_potential(
        self, time: float, positions: list[float] = projected.PROJECTED_SPOTS
    ) -> list[float]:
        """Method to calculate the optical potential associated with a Barrier object, taking into
        account the actual implementation of the Oqtant projection system

        Args:
            time (float): The time, in ms, at which the potential should be evaluated
            positions (list[float], optional): The positions, in microns, at which the potential should be evaluated

        Returns:
            list[float]: The potential energies, in kHz, at the specified positions
        """
        return projected.get_actual_potential(
            self.get_ideal_potential, time=time, positions=positions
        )

    def evaluate_position_spectrum(
        self, h: float, x0: float, w: float, positions_um: list[float]
    ) -> list[float]:
        if h == 0.0 or w == 0.0:
            return np.zeros_like(positions_um)
        if self.shape == "SQUARE":
            # width = half width (to align more closely with other shapes)
            return np.asarray(
                [0 if (x < x0 - w or x > x0 + w) else h for x in positions_um]
            )
        elif self.shape == ShapeType.LORENTZIAN:
            # width == HWHM (half-width half-max)
            return np.asarray([h / (1 + ((x - x0) / w) ** 2) for x in positions_um])
        elif self.shape == ShapeType.GAUSSIAN:
            # width = sigma (Gaussian width)
            return np.asarray(
                [h * np.exp(-((x - x0) ** 2) / (2 * w**2)) for x in positions_um]
            )

    def get_position_spectrum(
        self, time_ms: float, positions_um: np.ndarray
    ) -> np.ndarray:
        """Get positional weights over the given positions at the specified time"""
        params = self.get_params(time_ms)
        h = params["height_khz"]
        x0 = params["position_um"]
        w = params["width_um"]
        if h > 0 and w > 0 and self.is_active(time_ms):
            return self.evaluate_position_spectrum(h, x0, w, positions_um)
        else:
            return np.zeros(len(positions_um))

    def get_position_spectra(self, times_ms: list, positions_um: list) -> np.ndarray:
        widths = self.get_widths(times_ms)
        heights = self.get_heights(times_ms)
        positions = self.get_positions(times_ms)

        amplitudes = np.zeros(shape=(len(times_ms), len(positions_um)), dtype=float)
        for indx in range(len(times_ms)):
            amplitudes[indx] = self.evaluate_position_spectrum(
                h=heights[indx],
                w=widths[indx],
                x0=positions[indx],
                positions_um=positions_um,
            )
        return amplitudes


class Pulse(BaseModel):
    # times_ms upper range can be no larger than end_time_ms of job (80.0 ms is upper default)
    times_ms: Annotated[
        list[Annotated[float, Field(ge=0.0, le=80.0)]],
        Field(min_length=1, max_length=10),
    ]
    intensities_mw_per_cm2: Annotated[
        list[Annotated[float, Field(ge=0.0, le=1000.0)]],
        Field(min_length=1, max_length=10),
    ]
    detuning_mhz: Annotated[float, Field(ge=-100.0, le=100.0)]
    interpolation: InterpolationType
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def cross_validate(cls, values):
        if not len(values["times_ms"]) == len(values["intensities_mw_per_cm2"]):
            raise ValueError("Pulse data lists must have the same length.")
        return values

    @field_validator("times_ms")
    @classmethod
    def naturally_order_times(cls, v):
        if not v == sorted(v):
            raise ValueError("Pulse times must be naturally ordered.")
        return v

    def __lt__(self, other):
        return min(self.times_ms) < min(other.times_ms)


class Laser(BaseModel):
    type: LaserType
    position_um: float
    pulses: Annotated[list[Pulse], Field(min_length=1, max_length=10)]
    model_config = ConfigDict(validate_assignment=True)

    @field_validator("pulses")
    @classmethod
    def pulses_overlap(cls, v):
        for index, _ in enumerate(v):
            if index < len(v) - 1:
                dt_ms = min(v[index + 1].times_ms) - max(v[index].times_ms)
                if not dt_ms >= 1:
                    raise ValueError(
                        f"Distinct pulses features too close together in time (< 1 ms)"
                    )
        return v

    def get_intensity_waveform(
        self, tstart_ms: float, tend_ms: float, sample_rate_hz: float
    ) -> np.ndarray:
        intensities = []
        time_ms = tstart_ms
        for pulse in self.pulses:
            # pad our intensities list with zeros until the start of the next pulse:
            dt = 1.0 / sample_rate_hz
            dt_ms = dt * 1000.0
            n_zeros = int(
                np.floor(((pulse.times_ms[0] - time_ms) / 1000.0) * sample_rate_hz)
            )
            intensities.extend(np.zeros(n_zeros))
            # jump to start time of pulse and interpolate over it
            time_ms += n_zeros * 1000.0 * dt
            times_ms = np.arange(time_ms, pulse.times_ms[-1], dt_ms)
            style = (
                "zero"
                if pulse.interpolation == "OFF"
                else InterpolationType[pulse.interpolation].name.lower()
            )
            f = interp1d(
                pulse.times_ms,
                pulse.intensities_mw_per_cm2,
                kind=style,
                bounds_error=False,
                fill_value=(0.0, 0.0),
                assume_sorted=True,
                copy=False,
            )
            intensities.extend(f(times_ms))
            # jump current time to the end of the pulse
            time_ms += len(times_ms) * dt_ms
        # extend intensities list to the desired end time
        n_zeros = int(np.floor(((tend_ms - time_ms) / 1000.0) * sample_rate_hz))
        intensities.extend(np.zeros(n_zeros))
        return np.array(intensities)

    @computed_field
    @property
    def detunings(self) -> list[float]:
        return [pulse.detuning_mhz for pulse in self.pulses]

    @computed_field
    @property
    def detuning_triggers(self) -> list[float]:
        trigger_times_ms = [
            pulse.times_ms[-1] for pulse in self.pulses
        ]  # get last pulse
        trigger_times_ms.insert(0, 0)
        return trigger_times_ms[: len(self.pulses)]


class NonPlotOutput(BaseModel):
    mot_fluorescence_image: Image
    tof_image: Image
    tof_fit_image: Image
    tof_fit: TofFit
    tof_x_slice: LineChart
    tof_y_slice: LineChart
    total_mot_atom_number: int
    tof_atom_number: int
    thermal_atom_number: int
    condensed_atom_number: int
    temperature_nk: int
    model_config = ConfigDict(
        from_attributes=True, validate_assignment=True, extra="forbid"
    )


class PlotOutput(BaseModel):
    it_plot: Image
    model_config = ConfigDict(
        from_attributes=True, validate_assignment=True, extra="forbid"
    )


class Output(BaseModel):
    input_id: int | None = None
    values: PlotOutput | NonPlotOutput
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class JobOutput(Output):
    ...


class BecOutput(Output):
    values: NonPlotOutput


class BarrierOutput(Output):
    values: NonPlotOutput | PlotOutput


class InputValues(BaseModel):
    end_time_ms: Annotated[int, Field(ge=0, le=80)]
    image_type: ImageType
    time_of_flight_ms: Annotated[int, Field(ge=2, le=20)]
    rf_evaporation: RfEvaporation
    optical_barriers: (
        Annotated[list[Barrier], Field(min_length=1, max_length=5)] | None
    ) = None
    optical_landscape: OpticalLandscape | None = None
    lasers: Annotated[list[Laser], Field(min_length=1, max_length=1)] | None = None

    @model_validator(mode="after")
    def cross_validate(self):
        if list(
            filter(
                lambda time_ms: time_ms > self.end_time_ms,
                self.rf_evaporation.times_ms,
            )
        ):
            raise ValueError(
                "rf_evaporation.times_ms max values cannot exceed end_time_ms"
            )
        if self.optical_barriers:
            for index, optical_barrier in enumerate(self.optical_barriers):
                if list(
                    filter(
                        lambda time_ms: time_ms > self.end_time_ms,
                        optical_barrier.times_ms,
                    )
                ):
                    raise ValueError(
                        f"optical_barriers[{index}].times_ms max values cannot exceed end_time_ms"
                    )
        if self.optical_landscape:
            for index, landscape in enumerate(self.optical_landscape.landscapes):
                if landscape.time_ms > self.end_time_ms:
                    raise ValueError(
                        f"optical_landscape.landscapes[{index}].time_ms max value cannot exceed end_time_ms"
                    )
        if self.lasers:
            for laser_index, laser in enumerate(self.lasers):
                for pulse_index, pulse in enumerate(laser.pulses):
                    if list(
                        filter(
                            lambda time_ms: time_ms > self.end_time_ms,
                            pulse.times_ms,
                        )
                    ):
                        raise ValueError(
                            f"lasers[{laser_index}].pulses[{pulse_index}].times_ms max values cannot exceed end_time_ms"
                        )
        return self


class Input(BaseModel):
    job_id: int | None = None
    run: int | None = None
    values: InputValues
    output: Output | None = None
    notes: JobNote | None = None
    model_config = ConfigDict(validate_assignment=True)


class InputWithoutOutput(Input):
    output: Output = Field(exclude=True)


class JobBase(BaseModel):
    name: JobName
    origin: JobOrigin | None = None
    status: JobStatus = JobStatus.PENDING
    display: bool = True
    time_start: datetime | None = None
    time_complete: datetime | None = None
    qpu_name: QPUName = QPUName.UNDEFINED
    inputs: conlist(
        Input,
        min_length=1,
        max_length=30,
    )

    @computed_field
    @property
    def job_type(self) -> JobType:
        input_values = self.inputs[0].values
        if input_values.optical_landscape:
            return JobType.PAINT_1D
        elif (
            input_values.optical_barriers
            or input_values.image_type == ImageType.IN_TRAP
        ):
            return JobType.BARRIER
        else:
            return JobType.BEC

    @computed_field
    @property
    def input_count(self) -> int:
        return len(self.inputs)

    @model_validator(mode="after")
    def run(self):
        for i, _ in enumerate(self.inputs):
            if not self.inputs[i].run:
                self.inputs[i].run = i + 1
        return self

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


# needed for post fixtures
class JobPost(JobBase):
    inputs: conlist(
        Input,
        min_length=1,
        max_length=30,
    )


class JobCreate(JobBase):
    pass


class ResponseInput(BaseModel):
    job_id: int | None = None
    run: int | None = None
    values: InputValues
    output: JobOutput | None = None
    notes: JobNote | None = None
    model_config = ConfigDict(from_attributes=True)


class JobResponse(JobBase):
    external_id: UUID
    qpu: QPUBase | None = None
    time_submit: datetime
    inputs: list[ResponseInput]
    failed_inputs: list[int] = []


class JobInputsResponse(JobResponse):
    qpu_name: QPUName = QPUName.UNDEFINED
    inputs: list[InputWithoutOutput]


class PaginatedJobsResponse(JobBase):
    external_id: UUID
    time_submit: datetime
    time_start: datetime | None = None
    time_complete: datetime | None = None
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class Job(JobBase):
    job_id: UUID


class ExternalId(BaseModel):
    id: UUID


class UpdateJobDisplay(BaseModel):
    job_external_id: UUID
    display: bool = True
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class JobCreateResponse(BaseModel):
    job_id: UUID
    queue_position: int
    est_time: int | str


class JobExternalIdsList(BaseModel):
    external_ids: list[UUID]
