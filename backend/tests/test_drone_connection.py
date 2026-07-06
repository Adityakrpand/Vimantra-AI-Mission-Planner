from collections.abc import AsyncIterator
import asyncio

import pytest

from app.services.drone_connection import (
    DroneConnectionService,
    DroneConnectionTimeoutError,
)


class FakeConnectionState:
    def __init__(self, is_connected: bool) -> None:
        self.is_connected = is_connected


class FakeCoreTelemetry:
    def __init__(self, states: list[FakeConnectionState]) -> None:
        self._states = states

    async def connection_state(self) -> AsyncIterator[FakeConnectionState]:
        for state in self._states:
            yield state


class FakeDroneSystem:
    def __init__(self, states: list[FakeConnectionState]) -> None:
        self.core = FakeCoreTelemetry(states)
        self.connected_to: str | None = None

    async def connect(self, system_address: str | None = None) -> None:
        self.connected_to = system_address


class HangingDroneSystem(FakeDroneSystem):
    async def connect(self, system_address: str | None = None) -> None:
        self.connected_to = system_address
        await asyncio.Event().wait()


@pytest.mark.anyio
async def test_connect_updates_status_when_mavsdk_reports_connected() -> None:
    fake_system = FakeDroneSystem([FakeConnectionState(False), FakeConnectionState(True)])
    service = DroneConnectionService(system_factory=lambda: fake_system)

    status = await service.connect("udp://:14540", timeout_seconds=1)

    assert fake_system.connected_to == "udp://:14540"
    assert status.connected is True
    assert status.system_address == "udp://:14540"
    assert service.status().connected is True


@pytest.mark.anyio
async def test_connect_raises_timeout_when_no_connected_state_arrives() -> None:
    fake_system = FakeDroneSystem([FakeConnectionState(False)])
    service = DroneConnectionService(system_factory=lambda: fake_system)

    with pytest.raises(DroneConnectionTimeoutError):
        await service.connect("udp://:14540", timeout_seconds=1)

    assert service.status().connected is False


@pytest.mark.anyio
async def test_connect_raises_timeout_when_mavsdk_connect_hangs() -> None:
    fake_system = HangingDroneSystem([FakeConnectionState(True)])
    service = DroneConnectionService(system_factory=lambda: fake_system)

    with pytest.raises(DroneConnectionTimeoutError):
        await service.connect("udp://:14540", timeout_seconds=0.01)

    assert fake_system.connected_to == "udp://:14540"
    assert service.status().connected is False


@pytest.mark.anyio
async def test_disconnect_clears_connection_status() -> None:
    fake_system = FakeDroneSystem([FakeConnectionState(True)])
    service = DroneConnectionService(system_factory=lambda: fake_system)

    await service.connect("udp://:14540", timeout_seconds=1)
    status = await service.disconnect()

    assert status.connected is False
    assert status.system_address is None
