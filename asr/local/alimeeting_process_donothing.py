# -*- coding: utf-8 -*-
"""
Process the textgrid files
"""
import argparse
import codecs
from distutils.util import strtobool
from pathlib import Path
import textgrid
import pdb

class Segment(object):
    def __init__(self, uttid, spkr, stime, etime, text):
        self.uttid = uttid
        self.spkr = spkr
        self.stime = round(stime, 2)
        self.etime = round(etime, 2)
        self.text = text

    def change_stime(self, time):
        self.stime = time

    def change_etime(self, time):
        self.etime = time


def get_args():
    parser = argparse.ArgumentParser(description="process the textgrid files")
    parser.add_argument("--path", type=str, required=True, help="Data path")
    parser.add_argument(
        "--mars",
        type=strtobool,
        default=False,
        help="Whether to process mars data set.",
    )
    args = parser.parse_args()
    return args

def main(args):
    wav_scp = codecs.open(Path(args.path) / "wav.scp", "r", "utf-8")
    textgrid_flist = codecs.open(Path(args.path) / "textgrid.flist", "r", "utf-8")

    # get the path of textgrid file for each utterance
    utt2textgrid = {}
    for line in textgrid_flist:
        path = Path(line.strip())
        uttid = path.stem
        utt2textgrid[uttid] = path

    # parse the textgrid file for each utterance
    all_segments = []
    for line in wav_scp:
        uttid = line.strip().split(" ")[0]
        uttid_part=uttid
        if args.mars == True:
            uttid_list = uttid.split("_")
            uttid_part= uttid_list[0]+"_"+uttid_list[1]
        if uttid_part not in utt2textgrid:
            print("%s doesn't have transcription" % uttid)
            continue

        segments = []
        tg = textgrid.TextGrid.fromFile(utt2textgrid[uttid_part])
        for i in range(tg.__len__()):
            for j in range(tg[i].__len__()):
                if tg[i][j].mark:
                    segments.append(
                        Segment(
                            uttid,
                            tg[i].name,
                            tg[i][j].minTime,
                            tg[i][j].maxTime,
                            tg[i][j].mark.strip(),
                        )
                    )

        segments = sorted(segments, key=lambda x: x.stime)
        all_segments += segments

    wav_scp.close()
    textgrid_flist.close()

    segments_file = codecs.open(Path(args.path) / "segments_all", "w", "utf-8")
    utt2spk_file = codecs.open(Path(args.path) / "utt2spk_all", "w", "utf-8")
    text_file = codecs.open(Path(args.path) / "text_all", "w", "utf-8")

    for i in range(len(all_segments)):
        utt_name = "%s-%s-%07d-%07d" % (
            all_segments[i].uttid,
            all_segments[i].spkr,
            all_segments[i].stime * 100,
            all_segments[i].etime * 100,
        )

        segments_file.write(
            "%s %s %.2f %.2f\n"
            % (
                utt_name,
                all_segments[i].uttid,
                all_segments[i].stime,
                all_segments[i].etime,
            )
        )
        utt2spk_file.write(
            "%s %s-%s\n" % (utt_name, all_segments[i].uttid, all_segments[i].spkr)
        )
        text_file.write("%s %s\n" % (utt_name, all_segments[i].text))

    segments_file.close()
    utt2spk_file.close()
    text_file.close()


if __name__ == "__main__":
    args = get_args()
    main(args)
