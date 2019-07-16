from invoke import task, Exit
import gerber
from textwrap import dedent


BOARD_DRILLS = '../ergo42/ergo42/ergo42.drl'
COVER_DRILLS = '../ergo42_pcb_case/cover/gerbers/cover.drl'
PLATE_DRILLS = '../ergo42_pcb_case/plate/gerbers/plate.drl'

PROJECTS = ['bottom', 'cover', 'plate']
PLOTS = 'gerbers'
ZIPPER = '7z a'


@task
def clean(c):
    for project in PROJECTS:
        c.run(f'rm -rf {project}/{PLOTS}')


@task(clean)
def plot(c):
    for project in PROJECTS:
        c.run(f'python scripts/plot.py {project}/{project}.kicad_pcb {project}/{PLOTS}')

        c.run(f'{ZIPPER} {project}/{PLOTS}/{project}.zip {project}/{PLOTS}/*')


def get_drills_of_dia(drill_file_path, diameter, normalize=True):
    drills = gerber.read(drill_file_path)

    tool = None
    for t in drills.tools:
        if drills.tools[t].diameter == diameter:
            tool = drills.tools[t]

    if not tool:
        raise Exit('Standoff tool not found!')

    hits = [hit for hit in drills.hits if hit.tool is tool]
    for hit in hits:
        hit.to_metric()
    coords = [hit.position for hit in hits]

    origin = coords[0]
    for hole in coords:
        origin = min(origin, hole)

    xn, yn = origin
    for i, _ in enumerate(coords):
        x, y = coords[i]
        coords[i] = (x - xn, y - yn)

    return coords


@task()
def verify(c):
    board_standoff_holes = get_drills_of_dia(BOARD_DRILLS, 5)

    if len(board_standoff_holes) != 5:
        raise Exit(f'Found {len(board_standoff_holes)} holes in board, expected 5')

    plate_standoff_holes = get_drills_of_dia(PLATE_DRILLS, 2.35)

    if len(plate_standoff_holes) != 5:
        raise Exit(f'Found {len(board_standoff_holes)} holes in cover, expected 5')

    if sorted(board_standoff_holes) != sorted(plate_standoff_holes):
        raise Exit(dedent(f"""\
            Holes did not match:
            board = {sorted(board_standoff_holes)}
            plate = {sorted(plate_standoff_holes)}
        """))
