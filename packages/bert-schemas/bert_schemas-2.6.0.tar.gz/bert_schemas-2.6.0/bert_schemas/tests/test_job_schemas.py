import numpy as np
import pytest
from bert_rest_service.schemas.bert_schemas import job as job_schema
from bert_rest_service.schemas.bert_schemas.job import (
    interpolate_1d,
    interpolate_1d_list,
)
from pydantic import ValidationError


def test_interpolate_1d():
    assert interpolate_1d([1, 2, 3], [10, 20, 30], 2) == 20


def test_interpolate_1d_list():
    assert interpolate_1d_list([1, 2, 3], [10, 20, 30], [2, 3]) == [20, 30]


def test_rf_evaporation_cross_validate():
    data = {
        "times_ms": [-3, -4],
        "frequencies_mhz": [2, 1],
        "powers_mw": [2, 3],
        "interpolation": "LINEAR",
    }
    assert job_schema.RfEvaporation.model_validate(data)
    data["times_ms"] = [-3, 4, 5]
    with pytest.raises(ValidationError):
        job_schema.RfEvaporation.model_validate(data)


def test_landscape_interpolation_kind():
    data = {
        "time_ms": 3,
        "potentials_khz": [2, 3],
        "positions_um": [2, 3],
        "spatial_interpolation": "LINEAR",
    }
    landscape = job_schema.Landscape(**data)
    assert landscape.interpolation_kind == "linear"

    data["spatial_interpolation"] = "OFF"
    landscape = job_schema.Landscape(**data)
    assert landscape.interpolation_kind == "zero"


def test_landscape_cross_validate():
    data = {
        "time_ms": 3,
        "potentials_khz": [2, 3],
        "positions_um": [2, 3],
        "spatial_interpolation": "LINEAR",
    }
    assert job_schema.Landscape.model_validate(data)

    data["positions_um"] = [2, 3, 4]
    with pytest.raises(ValidationError):
        data["positions_um"] = [2, 3, 4]
        job_schema.Landscape.model_validate(data)


def test_landscape_get_position_spectrum():
    data = {
        "time_ms": 3,
        "potentials_khz": [2, 3],
        "positions_um": [2, 3],
        "spatial_interpolation": "LINEAR",
    }
    landscape = job_schema.Landscape(**data)
    spectrum = landscape.get_position_spectrum(np.array([6, 3]))
    assert list(spectrum) == [0, 3]


def test_landscape_get_potential():
    data = {
        "time_ms": 3,
        "potentials_khz": [2, 3],
        "positions_um": [2, 3],
        "spatial_interpolation": "LINEAR",
    }
    landscape = job_schema.Landscape(**data)
    res = landscape.get_potential([1.0, 2.0, 3.0])
    assert res == [0.2914965035541314, 1.9804369402077469, 2.772117736811176]


def test_optical_landscape_get_potential():
    data = {
        "landscapes": [
            {
                "time_ms": 3,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
            {
                "time_ms": 4,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
        ]
    }

    landscape = job_schema.OpticalLandscape(**data)

    time = 2.0
    positions = [1.0, 2.2, 3.5]
    potentials = landscape.get_potential(time, positions)

    assert len(potentials) == len(positions)


def test_optical_landscape_cross_validate():
    data = {
        "landscapes": [
            {
                "time_ms": 3,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
            {
                "time_ms": 3,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
        ]
    }
    with pytest.raises(ValidationError):
        job_schema.OpticalLandscape.model_validate(data)

    data["landscapes"][1]["time_ms"] = 4
    assert job_schema.OpticalLandscape.model_validate(data)


def test_optical_landscape_get_position_spectra():
    data = {
        "landscapes": [
            {
                "time_ms": 3,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
            {
                "time_ms": 4,
                "potentials_khz": [2, 3],
                "positions_um": [2, 3],
                "spatial_interpolation": "LINEAR",
            },
        ]
    }

    landscape = job_schema.OpticalLandscape(**data)
    spectrum = landscape.get_position_spectra(np.array([6, 3]), np.array([6, 3]))
    assert all(list(spectrum)[0]) == all([0.0, 0.0])


@pytest.fixture
def barrier_data():
    yield {
        "times_ms": [3, 4],
        "positions_um": [2, 3],
        "heights_khz": [2, 3],
        "widths_um": [2, 3],
        "interpolation": "LINEAR",
    }


def test_barrier_cross_validate(barrier_data):
    assert job_schema.Barrier.model_validate(barrier_data)

    barrier_data["heights_khz"] = [2, 3, 4]
    with pytest.raises(ValidationError):
        job_schema.Barrier.model_validate(barrier_data)


def test_barrier_interpolation_kind(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.interpolation_kind == "linear"

    barrier_data["interpolation"] = "OFF"
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.interpolation_kind == "zero"


def test_barrier_is_active(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.is_active(3)


def test_barrier_get_positions():
    data = {
        "times_ms": [1, 3, 4, 5],
        "positions_um": [0, 2, 3, 6],
        "heights_khz": [2, 3, 4, 5],
        "widths_um": [1, 2, 3, 4],
        "interpolation": "LINEAR",
    }
    barrier = job_schema.Barrier(**data)
    assert list(barrier.get_positions([3, 4])) == [2, 3]


def test_barrier_get_position(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_position(3) == 2


def test_barrier_get_heights(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert list(barrier.get_heights([3, 4])) == [2, 3]


def test_barrier_get_height(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_height(3) == 2


def test_barrier_get_widths(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_widths([3, 4]) == [2.0, 3.0]


def test_barrier_get_width(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_width(3) == 2.0


def test_barrier_get_ideal_potential(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_ideal_potential(3)[0] == 4.1930635165770337e-209


def test_barrier_get_potential(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)
    assert barrier.get_potential(3)[0] == 7.070114771075559e-207


def test_barrier_evaluate_position_spectrum(barrier_data):
    barrier = job_schema.Barrier(**barrier_data)

    spectrum = barrier.evaluate_position_spectrum(1.0, 2.0, 3.0, [6.0, 3.0])
    assert spectrum[0] == 0.41111229050718745


# need Noah input
# def test_barrier_get_position_spectra(barrier_data):
#     barrier = job_schema.Barrier(**barrier_data)
#     spectra = barrier.get_position_spectra([2, 3], [6, 3])
#     assert spectra == np.ndarray([[0.0, 0.0], [0.27067057, 1.76499381]])


def test_pulse_cross_validate():
    pulse_data = {
        "times_ms": [1, 3, 4],
        "intensities_mw_per_cm2": [2, 3, 4],
        "detuning_mhz": 2,
        "interpolation": "LINEAR",
    }
    assert job_schema.Pulse.model_validate(pulse_data)

    pulse_data["times_ms"] = [1, 3, 4, 5]
    with pytest.raises(ValidationError):
        job_schema.Pulse.model_validate(pulse_data)


def test_laser_pulses_overlap():
    laser_data = {
        "type": "TERMINATOR",
        "position_um": 1.0,
        "pulses": [
            {
                "times_ms": [1, 3, 4],
                "intensities_mw_per_cm2": [2, 3, 4],
                "detuning_mhz": 2,
                "interpolation": "LINEAR",
            },
            {
                "times_ms": [1, 3, 4],
                "intensities_mw_per_cm2": [2, 3, 4],
                "detuning_mhz": 2,
                "interpolation": "LINEAR",
            },
        ],
    }

    with pytest.raises(ValidationError):
        job_schema.Laser.model_validate(laser_data)


# need Noah input
# def test_laser_get_intensity_waveform():
#     laser_data = {
#         "type": "TERMINATOR",
#         "position_um": 1.0,
#         "pulses": [
#             {
#                 "times_ms": [1, 3, 4],
#                 "intensities_mw_per_cm2": [2, 3, 4],
#                 "detuning_mhz": 2,
#                 "interpolation": "LINEAR",
#             },
#         ],
#     }
#     laser = job_schema.Laser(**laser_data)
#     waveform = laser.get_intensity_waveform(
#         tstart_ms=1.0, tend_ms=3.0, sample_rate_hz=1.0
#     )
#


def test_input_values_cross_validate():
    input_values = {
        "end_time_ms": 5,
        "image_type": "IN_TRAP",
        "time_of_flight_ms": 2,
        "rf_evaporation": {
            "times_ms": [-3, -4],
            "frequencies_mhz": [2, 1],
            "powers_mw": [2, 3],
            "interpolation": "LINEAR",
        },
        "optical_barriers": [
            {
                "times_ms": [1, 3, 4, 5],
                "positions_um": [0, 2, 3, 6],
                "heights_khz": [2, 3, 4, 5],
                "widths_um": [1, 2, 3, 4],
                "interpolation": "LINEAR",
            }
        ],
        "optical_landscape": {
            "interpolation": "LINEAR",
            "landscapes": [
                {
                    "time_ms": 3,
                    "potentials_khz": [2, 3],
                    "positions_um": [2, 3],
                    "spatial_interpolation": "LINEAR",
                },
                {
                    "time_ms": 4,
                    "potentials_khz": [2, 3],
                    "positions_um": [2, 3],
                    "spatial_interpolation": "LINEAR",
                },
            ],
        },
        "lasers": [
            {
                "type": "TERMINATOR",
                "position_um": 1.0,
                "pulses": [
                    {
                        "times_ms": [1, 3, 4],
                        "intensities_mw_per_cm2": [2, 3, 4],
                        "detuning_mhz": 2,
                        "interpolation": "LINEAR",
                    }
                ],
            }
        ],
    }

    assert job_schema.InputValues.model_validate(input_values)

    with pytest.raises(ValidationError):
        input_values["rf_evaporation"]["times_ms"] = [-3, 6]
        job_schema.InputValues.model_validate(input_values)

    with pytest.raises(ValidationError):
        input_values["optical_barriers"][0]["times_ms"] = [1, 3, 4, 6]
        job_schema.InputValues.model_validate(input_values)

    with pytest.raises(ValidationError):
        input_values["optical_landscape"]["landscapes"][0]["time_ms"] = 6
        job_schema.InputValues.model_validate(input_values)

    with pytest.raises(ValidationError):
        input_values["lasers"][0]["pulses"][0]["times_ms"] = [1, 3, 6]
        job_schema.InputValues.model_validate(input_values)
