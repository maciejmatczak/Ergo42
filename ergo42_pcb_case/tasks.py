from invoke import task


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
