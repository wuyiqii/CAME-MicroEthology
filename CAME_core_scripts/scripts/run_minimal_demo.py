#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
from came.extract_visual_features import extract_features_for_file
from came.extract_stationary_bouts import extract_bouts_for_file
from came.run_came_dynamics import run_came_for_file

def infer_context(p:Path):
    n=p.name.lower()
    if 'fas' in n or 'feed' in n: return 'FAS'
    if 'sas' in n or 'stand' in n: return 'SAS'
    return 'LAS'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input-dir',required=True); ap.add_argument('--output-dir',required=True); ap.add_argument('--config',default='configs/came_minimal.yaml'); ap.add_argument('--fps',type=float,default=1.0); ap.add_argument('--context',default='auto',choices=['auto','LAS','FAS','SAS'])
    a=ap.parse_args(); inp=Path(a.input_dir); out=Path(a.output_dir); csvs=sorted(inp.glob('*.csv'))
    if not csvs: raise FileNotFoundError(f'No CSV files found in {inp}')
    for csv in csvs:
        ctx=infer_context(csv) if a.context=='auto' else a.context
        print(f'[CAME] {csv.name} context={ctx}')
        feat=out/'features'/f'{csv.stem}_features.csv'; extract_features_for_file(csv,feat,a.fps)
        _, bout_frames=extract_bouts_for_file(feat,out/'stationary_bouts',ctx,a.config,a.fps)
        if bout_frames.exists(): run_came_for_file(bout_frames,out/'came_dynamics',a.config,a.fps)
    print(f'[CAME] Done: {out}')
if __name__=='__main__': main()
