import pytest
from mock import AsyncMock, Mock, call
from pytest_mock import MockerFixture

from odinprocservcontrol import OdinProcServConfig, OdinProcServControl
from odinprocservcontrol.odinprocserv import builder

# Patch fixtures
ASYNCIO_SLEEP_PATCH = "asyncio.sleep"
ODINPROCSERV_PATCH = "odinprocservcontrol.odinprocserv"


@pytest.fixture
def control():
    config = OdinProcServConfig(
        prefix="BLXXY-EA-ODN",
        process_count=11,
        server_process_name="BLXXY-EA-ODN-01",
        server_delay=3,
        ioc_name="BLXXY-EA-IOC-01",
        ioc_delay=5,
    )
    return OdinProcServControl(config, log_level="DEBUG")


record_mock = None


@pytest.fixture(autouse=True)
def _patch_builder(mocker):
    mocker.patch.object(builder, "longOut")


# Test [start, stop, restart]_processes


@pytest.mark.asyncio
async def test_start_processes_press(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_start_processes", new_callable=AsyncMock)
    await control.start_processes(1)
    control._start_processes.assert_called_once_with()
    control.start.set.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_start_processes_release(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_start_processes", new_callable=AsyncMock)
    await control.start_processes(0)
    control._start_processes.assert_not_called()
    control.start.set.assert_not_called()


@pytest.mark.asyncio
async def test_stop_processes_press(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_stop_processes", new_callable=AsyncMock)
    await control.stop_processes(1)
    control._stop_processes.assert_called_once_with()
    control.stop.set.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_stop_processes_release(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_stop_processes", new_callable=AsyncMock)
    await control.stop_processes(0)
    control._stop_processes.assert_not_called()
    control.stop.set.assert_not_called()


@pytest.mark.asyncio
async def test_restart_processes_press(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_restart_processes", new_callable=AsyncMock)
    await control.restart_processes(1)
    control._restart_processes.assert_called_once_with()
    control.restart.set.assert_called_once_with(0)


@pytest.mark.asyncio
async def test_restart_processes_release(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_restart_processes", new_callable=AsyncMock)
    await control.restart_processes(0)
    control._restart_processes.assert_not_called()
    control.restart.set.assert_not_called()


# Test _[start, stop, restart]_processes


@pytest.mark.asyncio
async def test__start_processes(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    press_mock = mocker.patch.object(control, "_press_buttons", new_callable=AsyncMock)
    sleep_mock = mocker.patch(ASYNCIO_SLEEP_PATCH, new_callable=AsyncMock)
    manager = Mock()
    manager.attach_mock(press_mock, "press_mock")
    manager.attach_mock(sleep_mock, "sleep_mock")
    expected_calls = [
        call.press_mock(
            [
                "BLXXY-EA-ODN-02",
                "BLXXY-EA-ODN-03",
                "BLXXY-EA-ODN-04",
                "BLXXY-EA-ODN-05",
                "BLXXY-EA-ODN-06",
                "BLXXY-EA-ODN-07",
                "BLXXY-EA-ODN-08",
                "BLXXY-EA-ODN-09",
                "BLXXY-EA-ODN-10",
                "BLXXY-EA-ODN-11",
            ],
            "START",
        ),
        call.sleep_mock(3),
        call.press_mock(["BLXXY-EA-ODN-01"], "START"),
        call.sleep_mock(5),
        call.press_mock(["BLXXY-EA-IOC-01"], "START"),
    ]

    await control._start_processes()

    assert expected_calls == manager.method_calls


@pytest.mark.asyncio
async def test__stop_processes(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    mocker.patch.object(control, "_press_buttons", new_callable=AsyncMock)
    expected_call = call(
        [
            "BLXXY-EA-ODN-02",
            "BLXXY-EA-ODN-03",
            "BLXXY-EA-ODN-04",
            "BLXXY-EA-ODN-05",
            "BLXXY-EA-ODN-06",
            "BLXXY-EA-ODN-07",
            "BLXXY-EA-ODN-08",
            "BLXXY-EA-ODN-09",
            "BLXXY-EA-ODN-10",
            "BLXXY-EA-ODN-11",
            "BLXXY-EA-ODN-01",
            "BLXXY-EA-IOC-01",
        ],
        "STOP",
    )

    await control._stop_processes()

    assert expected_call in control._press_buttons.await_args_list


@pytest.mark.asyncio
async def test__restart_processes(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    stop_mock = mocker.patch.object(control, "_stop_processes", new_callable=AsyncMock)
    start_mock = mocker.patch.object(
        control, "_start_processes", new_callable=AsyncMock
    )
    sleep_mock = mocker.patch(ASYNCIO_SLEEP_PATCH, new_callable=AsyncMock)
    manager = Mock()
    manager.attach_mock(stop_mock, "stop_mock")
    manager.attach_mock(start_mock, "start_mock")
    manager.attach_mock(sleep_mock, "sleep_mock")
    expected_calls = [
        call.stop_mock(),
        call.sleep_mock(3),
        call.start_mock(),
    ]

    await control._restart_processes()

    assert expected_calls == manager.method_calls


# Test [start, stop, restart]_processes


@pytest.mark.asyncio
async def test__press_buttons(
    control: OdinProcServControl, mocker: MockerFixture
) -> None:
    caput_mock = mocker.patch(ODINPROCSERV_PATCH + ".caput", new_callable=AsyncMock)
    prefixes = ["A", "B"]
    suffix = "START"

    await control._press_buttons(prefixes, suffix)

    caput_mock.assert_called_once_with(["A:START", "B:START"], 1)


def test_format_process_name():
    format_process_name = OdinProcServControl._format_process_name
    assert format_process_name("BLXXY-EA-EIG1", 1) == "BLXXY-EA-EIG1-01"
    assert format_process_name("BLXXY-EA-EIG1-", 1) == "BLXXY-EA-EIG1-01"
    assert format_process_name("BLXXY-EA-EIG1", 10) == "BLXXY-EA-EIG1-10"
    assert format_process_name("BLXXY-EA-EIG1", 100) == "BLXXY-EA-EIG1-100"
