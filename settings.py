class Settings:
    # Virtual resolution
    VIRTUAL_WIDTH = 1600
    VIRTUAL_HEIGHT = 900

    # Character
    PIO_FRAME_WIDTH = 26
    PIO_FRAME_HEIGHT = 26
    PIO_SCALE = 3
    PIO_ANIMATION_STEPS = 4
    PIO_ANIMATION_COOLDOWN = 160  # Faster animation
    PIO_SPEED = 16  # Increased speed

    # Group
    GROUP_FRAME_WIDTH = 144
    GROUP_FRAME_HEIGHT = 76
    GROUP_SCALE = 1
    GROUP_ANIMATION_COOLDOWN = 90  # Faster animation
    GROUP_ANIMATION_STEPS = 3
    GROUP_SPACING = 130
    SPAWN_INTERVAL = 4000  # (optional: spawn faster if desired)

    # Pathing/Floors
    GROUND_Y = 760
    SECOND_FLOOR_Y = 552
    SECOND_FLOOR_CURVE_Y = 583
    STAIRS_LEFT_GROUND_X = 650
    STAIRS_LEFT_SECOND_FLOOR_X = 500
    STAIRS_RIGHT_GROUND_X = 822
    STAIRS_RIGHT_SECOND_FLOOR_X = 973
    STAIRS_HORIZONTAL_MID_X = (500 + 975) / 2
    PATH_2F_LEFT_CURVE_X = 650
    PATH_2F_MIDDLE_X = 800
    PATH_2F_RIGHT_CURVE_X = 948

    # Right Stud Path
    STAIRS_RIGHT_GROUND_RSTUD_X = 800
    STAIRS_RIGHT_SECOND_FLOOR_RSTUD_X = 953
    PATH_2F_RIGHT_CURVE_RSTUD_X = 940
    SECOND_FLOOR_CURVE_STUD_Y = 580

    # Pointing System
    bg_color = (0, 0, 0, 0)