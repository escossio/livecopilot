from abc import ABC, abstractmethod
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class AudioCaptureBase(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    def is_live(self) -> bool:
        return False


class MockAudioCapture(AudioCaptureBase):
    def start(self) -> None:
        logger.info("audio_capture_start", extra={"event": "audio_capture_start", "mode": "mock"})

    def stop(self) -> None:
        logger.info("audio_capture_stop", extra={"event": "audio_capture_stop", "mode": "mock"})


class LiveAudioCapture(AudioCaptureBase):
    def start(self) -> None:
        logger.info("audio_capture_start", extra={"event": "audio_capture_start", "mode": "live"})

    def stop(self) -> None:
        logger.info("audio_capture_stop", extra={"event": "audio_capture_stop", "mode": "live"})

    def is_live(self) -> bool:
        return True


def get_audio_capture() -> AudioCaptureBase:
    mode = settings.capture_mode.lower()
    if mode == "live":
        return LiveAudioCapture()
    if mode != "mock":
        logger.info("audio_capture_unavailable", extra={"event": "audio_capture_unavailable", "mode": mode})
    return MockAudioCapture()
