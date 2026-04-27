from __future__ import annotations

from datetime import datetime

from utils import ClockAngleUtils, ClockAngles


class ClockAnimator:
    def _init_animation_state(self) -> None:
        self._animation_job: str | None = None
        self._animation_step = 0
        self._animation_total_steps = 12
        self._animation_start_angles: ClockAngles | None = None
        self._animation_target_angles: ClockAngles | None = None
        self._animation_target_time: datetime | None = None
        self._animation_digital_text: str | None = None

    def animate_to_display(
        self,
        current_time: datetime,
        digital_text: str | None = None,
    ) -> None:
        self._cancel_job("_animation_job")

        if digital_text is None:
            digital_text = self._get_digital_from_cdll()

        self.digital_label.configure(text=digital_text)
        self._animation_target_time = current_time
        self._animation_digital_text = digital_text
        self._animation_start_angles = self._override_angles or self._base_angles()
        self._animation_target_angles = ClockAngleUtils.angles_for_datetime(
            current_time
        )
        self._animation_step = 0
        self._run_animation_frame()

    def _run_animation_frame(self) -> None:
        if (
            self._animation_start_angles is None
            or self._animation_target_angles is None
        ):
            return

        self._animation_step += 1
        progress = min(self._animation_step / self._animation_total_steps, 1.0)
        eased_progress = 1.0 - (1.0 - progress) ** 2

        self._override_angles = (
            self._interpolate_angle(
                self._animation_start_angles[0],
                self._animation_target_angles[0],
                eased_progress,
            ),
            self._interpolate_angle(
                self._animation_start_angles[1],
                self._animation_target_angles[1],
                eased_progress,
            ),
            self._interpolate_angle(
                self._animation_start_angles[2],
                self._animation_target_angles[2],
                eased_progress,
            ),
        )
        self._draw_clock()

        if progress < 1.0:
            self._animation_job = self.after(16, self._run_animation_frame)
            return

        target_time = self._animation_target_time
        digital_text = self._animation_digital_text

        self._animation_job = None
        self._override_angles = None

        if target_time is not None:
            self.set_display(target_time, digital_text=digital_text)

    @staticmethod
    def _interpolate_angle(start: float, target: float, progress: float) -> float:
        shortest = ((target - start + 180.0) % 360.0) - 180.0
        return start + shortest * progress
