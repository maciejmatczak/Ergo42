from invoke import task, Exit
import gerber
from textwrap import dedent


MOUNTING_HOLE_PRETTY = '/usr/share/kicad/modules/MountingHole.pretty'
MOUNTING_HOLE_NAME = 'MountingHole_2.2mm_M2_Pad'

BOARD_DRILL_FILE = '../ergo42/ergo42/ergo42.drl'
PLATE_DRILL_FILE = '../ergo42_pcb_case/plate/gerbers/plate.drl'
BOTTOM_DRILL_FILE = '../ergo42_pcb_case/bottom/gerbers/bottom.drl'
COVER_DRILL_FILE = '../ergo42_pcb_case/cover/gerbers/cover.drl'

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

        c.run(f'{ZIPPER} {project}/{PLOTS}/{project}.zip ./{project}/{PLOTS}/*')


def get_drills_of_dia(drill_file_path, diameter, normalize=True):
    drills = gerber.read(drill_file_path)

    tool = None
    for t in drills.tools:
        if drills.tools[t].diameter == diameter:
            tool = drills.tools[t]

    if not tool:
        raise Exit(f'Tool for diameter {diameter} not found!')

    hits = [hit for hit in drills.hits if hit.tool is tool]
    for hit in hits:
        hit.to_metric()

    coords = [hit.position for hit in hits]

    return normalize_coords(coords)


def normalize_coords(coords):
    origin = coords[0]
    for hole in coords:
        origin = min(origin, hole)

    xn, yn = origin
    for i, _ in enumerate(coords):
        x, y = coords[i]

        # hard coding decimal place precision
        coords[i] = (
            round(x - xn, 6),
            round(y - yn, 6)
        )

    return sorted(coords)


def verify_drills(spec):
    designs_holes = {}

    for slug, data in spec.items():
        holes = get_drills_of_dia(data['drill_file'], data['tool_diameter'])

        if 'filter_out_f' in data:
            holes = [h for h in holes if not data['filter_out_f'](h)]
            if holes[0] != (0, 0):
                holes = normalize_coords(holes)

        if len(holes) != data['holes_number']:
            raise Exit(dedent(f"""\
                Found {len(holes)} holes in {slug}, expected {data["holes_number"]}:
                {holes}
            """))

        designs_holes[slug] = sorted(holes)

    a, b = designs_holes.keys()
    if designs_holes[a] != designs_holes[b]:
        raise Exit(dedent(f"""\
            Holes did not match:
            {a} = {designs_holes[a]}
            {b} = {designs_holes[b]}
        """))

    print('PASS!')


@task()
def verify(c):
    print('Checking board vs plate drills...')
    spec = {
        'board': {
            'tool_diameter': 5,
            'holes_number': 5,
            'drill_file': BOARD_DRILL_FILE
        },
        'plate': {
            'tool_diameter': 2.2,
            'holes_number': 5,
            'drill_file': PLATE_DRILL_FILE
        }
    }
    verify_drills(spec)

    print('Checking board vs bottom drills...')
    spec = {
        'board': {
            'tool_diameter': 5,
            'holes_number': 5,
            'drill_file': BOARD_DRILL_FILE
        },
        'bottom': {
            'tool_diameter': 2.2,
            'holes_number': 5,
            'drill_file': BOTTOM_DRILL_FILE,
            'filter_out_f': lambda xy: xy[1] > 60  # holes above 60 are for cover
        }
    }
    verify_drills(spec)

    print('Checking bottom vs cover drills...')
    spec = {
        'bottom': {
            'tool_diameter': 2.2,
            'holes_number': 4,
            'drill_file': BOTTOM_DRILL_FILE,
            'filter_out_f': lambda xy: xy[1] < 60  # holes above 60 are for cover
        },
        'cover': {
            'tool_diameter': 2.2,
            'holes_number': 4,
            'drill_file': COVER_DRILL_FILE,
            'filter_out_f': lambda xy: 60 < xy[0] < 62  # middle cover hole for reset
        }
    }
    verify_drills(spec)


@task()
def circles2holes(c):
    for project in PROJECTS:
        c.run(
            f'python scripts/circles2holes.py {project}/{project}.kicad_pcb \
                {MOUNTING_HOLE_PRETTY} {MOUNTING_HOLE_NAME}'
        )
