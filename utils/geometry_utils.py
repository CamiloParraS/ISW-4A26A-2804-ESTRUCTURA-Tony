import math


class GeometryUtils:
    @staticmethod
    def polar_to_cartesian(
        center_x: float, center_y: float, length: float, angle_degrees: float
    ) -> tuple[float, float]:
        """No preste Atencion en clases de Trigonometria para saber que pasa aqui"""
        angle = math.radians(angle_degrees - 90)
        return center_x + length * math.cos(angle), center_y + length * math.sin(angle)
