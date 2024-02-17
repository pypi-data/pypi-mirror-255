import os
import csv

INVALID_OUTPUT_FILE_MSG = "Invalid output file: {}"

def export_to_file(idx, lattice, output_dir=None):
    if output_dir is None:
        output_dir = "./"
    if not output_dir.endswith("/"):
        output_dir += "/"

    if not os.path.exists(output_dir):
        raise SystemExit(INVALID_OUTPUT_FILE_MSG.format(output_dir))

    hasse_lattice, concepts = lattice.hasse, lattice.concepts
    with open(f'{output_dir}{idx}_hasse.csv', 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        for l in hasse_lattice:
            writer.writerow(l)

    with open(f'{output_dir}{idx}_concepts_by_id.csv', 'w') as f:
        # create the csv writer
        writer = csv.writer(f)
        for c in concepts:
            str_c = str(c)
            try:
                idx = str_c.index('],')
            except ValueError:
                idx = str_c.index('},')
            str_1, str_2 = str_c[1:idx + 1], str_c[idx + 2:-1]
            writer.writerow([f'{c.hr_O()}', f'{c.hr_A()}'])
