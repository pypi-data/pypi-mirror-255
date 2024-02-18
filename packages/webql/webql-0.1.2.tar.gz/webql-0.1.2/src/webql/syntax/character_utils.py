def is_white_space(code: int) -> bool:
    """
    WhiteSpace ::
      - "Horizontal Tab"
      - "Space"
    """
    return code == 9 or code == 32  # Horizontal Tab or Space


def is_digit(code: int) -> bool:
    """
    Digit :: one of
      - `0` `1` `2` `3` `4` `5` `6` `7` `8` `9`
    """
    return 48 <= code <= 57  # '0' through '9'


def is_letter(code: int) -> bool:
    """
    Letter :: one of
      - `A` `B` `C` `D` `E` `F` `G` `H` `I` `J` `K` `L` `M`
      - `N` `O` `P` `Q` `R` `S` `T` `U` `V` `W` `X` `Y` `Z`
      - `a` `b` `c` `d` `e` `f` `g` `h` `i` `j` `k` `l` `m`
      - `n` `o` `p` `q` `r` `s` `t` `u` `v` `w` `x` `y` `z`
    """
    return (97 <= code <= 122) or (65 <= code <= 90)  # 'a'-'z' or 'A'-'Z'


def is_identifier_start(code: int) -> bool:
    """
    NameStart ::
      - Letter
      - `_`
    """
    return is_letter(code) or code == 95  # '_' underscore


def is_identifier_continue(code: int) -> bool:
    """
    NameContinue ::
      - Letter
      - Digit
      - `_`
    """
    return is_letter(code) or is_digit(code) or code == 95  # '_' underscore
