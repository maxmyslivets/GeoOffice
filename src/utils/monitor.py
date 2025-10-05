from screeninfo import get_monitors

def correct_window_position(left: int, top: int, width: int, height: int) -> tuple[int, int, int, int]:
    """
    Проверяет, попадает ли окно в область видимости мониторов.
    Если нет — возвращает координаты для центрирования окна на главном мониторе.

    :param left: Позиция окна слева
    :param top: Позиция окна сверху
    :param width: Ширина окна
    :param height: Высота окна
    :return: (left, top, width, height) — скорректированные координаты окна
    """
    monitors = get_monitors()

    # Проверка: окно частично на каком-либо мониторе
    def is_window_visible():
        for m in monitors:
            if not (
                left + width < m.x or
                left > m.x + m.width or
                top + height < m.y or
                top > m.y + m.height
            ):
                return True
        return False

    if is_window_visible():
        return left, top, width, height

    # Центрируем на главном мониторе (обычно m.x == 0 и m.y == 0)
    main = next((m for m in monitors if m.x == 0 and m.y == 0), monitors[0])
    new_left = main.x + (main.width - width) // 2
    new_top = main.y + (main.height - height) // 2

    return new_left, new_top, width, height
