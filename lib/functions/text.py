import pygame


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface: pygame.Surface = font.render(word, False, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.


def strfdelta_round(tdelta, round_period='second'):
    """timedelta to string,  use for measure running time
    attend period from days downto smaller period, round to minimum period
    omit zero value period
    """
    period_names = ('day', 'hour', 'minute', 'second', 'millisecond')
    if round_period not in period_names:
        raise Exception(f'round_period "{round_period}" invalid, should be one of {",".join(period_names)}')
    period_seconds = (86400, 3600, 60, 1, 1 / pow(10, 3))
    period_desc = ('d', 'h', 'm', 's', 'ms')
    round_i = period_names.index(round_period)

    s = ''
    remainder = tdelta.total_seconds()
    for i in range(len(period_names)):
        q, remainder = divmod(remainder, period_seconds[i])
        if int(q) > 0:
            if not len(s) == 0:
                s += ' '
            s += f'{q:.0f}{period_desc[i]}'
        if i == round_i:
            break
        if i == round_i + 1:
            s += f'{remainder}{period_desc[round_i]}'
            break

    return s
