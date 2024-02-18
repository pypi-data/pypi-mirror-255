# Copyright 2024 Infleqtion
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from collections.abc import Callable

import numpy as np

"""A module that captures the features, and limitations, of optical objects
implemented by the Oqtant hardware projection system.
"""

RESOLUTION = 2.2  # 1/e^2 diameter of projection system, microns
POSITION_STEP = 1.0  # grid step between projected spots, microns
POSITION_MIN = -60.0  # minimum position of projected light, microns
POSITION_MAX = 60  # maximum position of projected light, microns
PROJECTED_SPOTS = np.arange(POSITION_MIN, POSITION_MAX + 1.0, POSITION_STEP)
UPDATE_PERIOD = 0.1  # milliseconds between updates of projected light
ENERGY_MIN = 0.0  # minimum projected energy shift at any position, kHz
ENERGY_MAX = 100  # maximum projected energy shift at any position, kHz


def get_corrected_times(times: list[float]) -> list[float]:
    """Method to calculate the effective times realized by the projection system,
    which only updates optical features periodically

    Args:
        times (list[float]): Time, in ms, to be corrected

    Returns:
        list[float]: The corrected times
    """
    times_corrected = (
        np.floor((1000.0 * np.asarray(times)) / (1000.0 * UPDATE_PERIOD))
        * UPDATE_PERIOD
    )
    return list(times_corrected)


def get_corrected_time(time: float) -> float:
    """Method to calculate the effective time realized by the projection system,
    which only updates optical features periodically

    Args:
        time (float): Time, in ms, to be corrected

    Returns:
        float: The corrected time
    """
    return get_corrected_times(times=[time])[0]


def get_potential_from_weights(weights: list, positions: list[float]) -> list[float]:
    """Method to calculate projected potential based on given weights (intensities)
    applied to each projected spot

    Args:
        weights: height of each Gaussian spot

    Returns:
        list[float]: Calculated total optical potential at the given positions
    """
    if len(weights) != len(PROJECTED_SPOTS):
        raise ValueError(f"number of weights values must equal {len(PROJECTED_SPOTS)}")

    potential = np.zeros_like(positions)
    for indx, spot in enumerate(PROJECTED_SPOTS):
        potential += gaussian(
            xs=positions,
            amp=weights[indx],
            center=spot,
            sigma=RESOLUTION / 4.0,
            offset=0.0,
        )
    return list(potential)


def get_corrected_projection_weights(
    get_ideal_potential: Callable[[float], list], time: float = 0
) -> np.ndarray:
    """Method to calculate weights for each horizontal "spot" projected onto the atom ensemble to
    attempt to achieve the passed optical object's "ideal" potential energy profile.
    Implements first-order corrections for anamolous contributions from nearby spots,
    inter-integer barrier centers, etc

    Args:
        get_ideal_potential (Callable[[float], list]): Method for the optical object or any class
            that supports optical objects that calculates the specified "ideal" or "requested"
            potential energy profile
        time (float, optional): Time at which to correct

    Returns:
        np.ndarray[float]: Calculated (optical intensity) contribution for each projected spot
            (diffraction frequency) used by the projection systems
    """
    bin_size = 10  # index range of local scaling window
    positions_fine = np.arange(
        POSITION_MIN - POSITION_STEP / 2,
        POSITION_MAX + POSITION_STEP / 2,
        POSITION_STEP / bin_size,
    )

    # determine the ideal potential energy at each projected spot
    potential_ideal = np.asarray(
        get_ideal_potential(time=time, positions=positions_fine)
    )
    potential_ideal_course = np.asarray(
        get_ideal_potential(time=time, positions=PROJECTED_SPOTS)
    )

    # calculate the optical field that would result from raw object data
    potential_raw = get_potential_from_weights(
        weights=potential_ideal_course, positions=positions_fine
    )
    # bin them up and find the local maximum
    potential_ideal_binned = np.asarray(potential_ideal).reshape(
        int(len(list(potential_raw)) / bin_size), bin_size
    )
    potential_raw_binned = np.asarray(potential_raw).reshape(
        int(len(list(potential_raw)) / bin_size), bin_size
    )
    # scale local optical potential to get close to the ideal value
    maxes_ideal = np.asarray([np.max(x) for x in potential_ideal_binned])
    maxes_raw = np.asarray([np.max(x) for x in potential_raw_binned])
    scalings = np.divide(
        maxes_ideal,
        maxes_raw,
        where=maxes_raw != 0.0,
        out=np.zeros_like(maxes_ideal),
    )
    return list(np.multiply(scalings, potential_ideal_course))


def get_actual_potential(
    get_ideal_potential: Callable[[float], list],
    time: float = 0.0,
    positions: list = PROJECTED_SPOTS,
) -> list[float]:
    """Method to calculate the "actual" potential energy vs position for optical
    objects/fields as realized by the Oqtant projection system. Includes effects,
    and first-order corrections for, finite time updates and finite optical
    resolution/optical objects being projected as sums of gaussians and energetic
    clipping of optical potentials at 100 kHz

    Args:
        get_ideal_potential (Callable[[float], list]): Object method for request/ideal potential
        time (float, optional): Time to evaluate ideal potential
        positions (list[float], optional): Positions to evaluate the actual potential at

    Returns:
        list[float]: Expected actual potential energy at the request positions
    """
    weights = get_corrected_projection_weights(
        get_ideal_potential, time=get_corrected_time(time)
    )

    corrected_potential = get_potential_from_weights(
        weights=weights,
        positions=positions,
    )
    return list(np.clip(np.asarray(corrected_potential), ENERGY_MIN, ENERGY_MAX))


def gaussian(
    xs: np.ndarray,
    amp: float = 1.0,
    center: float = 0.0,
    sigma: float = 1.0,
    offset: float = 0.0,
) -> np.ndarray:
    """Method that evaluates a standard gaussian form over the given input points

    Args:
        xs (numpy.ndarray): Positions where the gaussian should be evaluated
        amp (float, optional): Gaussian amplitude
        center (float, optional): Gaussian center
        sigma (float, optional): Gaussian width
        offset (float, optional): Gaussian dc offset

    Returns:
        np.ndarray: Gaussian function evaluated over the input points
    """
    return amp * np.exp(-((xs - center) ** 2) / (2 * sigma**2)) + offset
