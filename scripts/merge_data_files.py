"""
Usage: python merge_data_files.py <gaps file> <variants file> <line offset> <number of line to read>
"""
import sys
import os
import csv


def gapline2sentence(gap_line):
    tokens = gap_line.split()
    ngap = int(tokens[0])
    gap_start = sum(len(t) for t in tokens[1:ngap + 1]) + ngap
    gap_end = gap_start + len(tokens[ngap + 1])
    sentence = gap_line.split(' ', 1)[1]
    return sentence, gap_start, gap_end


def main():
    gap_file = sys.argv[1]
    var_file = sys.argv[2]
    start_line = int(sys.argv[3])
    n_lines = int(sys.argv[4])

    outf = os.path.join(os.path.split(gap_file)[0],
                        "{}.{}.{}.ln{}.s{}.csv".format(
                            os.path.split(gap_file)[1].split('.')[0],
                            gap_file.split('.')[-2],
                            var_file.split('.')[-3],
                            start_line, n_lines))

    gapf = open(gap_file, encoding='utf-8')
    varf = open(var_file, encoding='utf-8')
    with open(outf, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow("sentence gap_start gap_end variants".split())
        for i, gap_line in enumerate(gapf):
            if i < start_line - 1:
                varf.readline()
                continue
            if i >= n_lines + start_line - 1:
                break
            sentence, gap_start, gap_end = gapline2sentence(gap_line.rstrip())
            variants = varf.readline().rstrip().split()[:4]
            writer.writerow([sentence, gap_start, gap_end, ",".join(variants)])
    print("Saved file", outf)


if __name__ == "__main__":
    main()
