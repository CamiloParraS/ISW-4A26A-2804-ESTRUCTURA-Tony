from __future__ import annotations

from datetime import datetime

from ui.helpers import SchedulerUtils


class ClockTabNavMixin:
    def _navigate(
        self,
        direction: int,
        *,
        cancel_local_nav: bool = True,
    ) -> None:
        if cancel_local_nav:
            self._cancel_local_navigation()

        if direction > 0:
            self._carousel.rotate_next(direction)
        else:
            self._carousel.rotate_prev(abs(direction))

        self._render_active_city(animate=True)

    def _cancel_local_navigation(self) -> None:
        SchedulerUtils.cancel_after_job(self, self._local_nav_job)
        self._local_nav_job = None
        self._local_nav_steps_remaining = 0
        self._local_nav_direction = 0

    def go_to_local(self) -> None:
        self._cancel_local_navigation()
        self._hover_direction = None
        self.clock.clear_preview()

        if not self._carousel.has_city("Local"):
            return

        offset = self._carousel.shortest_offset_to_city("Local")
        if offset == 0:
            return

        self._local_nav_direction = 1 if offset > 0 else -1
        self._local_nav_steps_remaining = abs(offset)
        self._run_local_navigation_step()

    def _run_local_navigation_step(self) -> None:
        self._local_nav_job = None
        if self._local_nav_steps_remaining <= 0 or self._local_nav_direction == 0:
            self._cancel_local_navigation()
            return

        self._navigate(self._local_nav_direction, cancel_local_nav=False)
        self._local_nav_steps_remaining -= 1

        if self._local_nav_steps_remaining > 0:
            self._local_nav_job = self.after(190, self._run_local_navigation_step)
        else:
            self._cancel_local_navigation()

    def on_shortcut_left(self) -> None:
        self._navigate(-1)

    def on_shortcut_right(self) -> None:
        self._navigate(1)

    def on_shortcut_local(self) -> None:
        self.go_to_local()

    def _on_arrow_hover(self, direction: int) -> None:
        self._hover_direction = direction
        self._sync_preview()

    def _on_arrow_leave(self, _event: object) -> None:
        self._hover_direction = None
        self.clock.clear_preview()

    def _sync_preview(self, utc_now: datetime | None = None) -> None:
        if self._hover_direction is None:
            self.clock.clear_preview()
            return

        now_utc = utc_now or self._utc_now_provider()
        preview_city = self._carousel.node_at_offset(self._hover_direction)
        preview_time = self._city_time(preview_city, now_utc)
        self.clock.set_preview_angles(self._angles_for_time(preview_time))
