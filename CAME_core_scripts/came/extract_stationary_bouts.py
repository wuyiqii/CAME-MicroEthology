#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Optional, Dict, List
import numpy as np
import pandas as pd
import yaml

DEFAULT_CONTEXTS={
 'LAS':{'allowed_postures':['lying'],'allowed_zones':['Resting','Resting-overlap','Resting-other-overlap','resting']},
 'FAS':{'allowed_postures':['standing','other'],'allowed_zones':['Feeder','feeder','feeding']},
 'SAS':{'allowed_postures':['standing'],'allowed_zones':['Resting','Resting-overlap','Resting-other-overlap','resting']},
}

def load_config(path):
    if not path: return {}
    with open(path,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def normalise(df):
    df=df.copy()
    if 'FrameNumber' not in df.columns: df['FrameNumber']=np.arange(len(df),dtype=int)
    df['FrameNumber']=pd.to_numeric(df['FrameNumber'],errors='coerce').ffill().bfill().astype(int)
    if 'group_id' not in df.columns: df['group_id']='group0'
    if 'pred_ds_label' not in df.columns:
        df['pred_ds_label']=df['dynamics_label'].map({'stationary':'s','move':'d'}).fillna(df['dynamics_label']) if 'dynamics_label' in df.columns else 's'
    if 'posture' not in df.columns: df['posture']=df['posture_label'] if 'posture_label' in df.columns else 'unknown'
    if 'zone_label' not in df.columns:
        for c in ['zone_lable','context_label','zone']:
            if c in df.columns: df['zone_label']=df[c]; break
    if 'zone_label' not in df.columns: df['zone_label']='unknown'
    return df.sort_values(['group_id','FrameNumber']).reset_index(drop=True)

def extract_bouts(df, context_name='LAS', contexts=None, stationary_labels=None, min_duration_sec=10, fps=1.0):
    df=normalise(df); contexts=contexts or DEFAULT_CONTEXTS; stationary_labels=stationary_labels or ['s','stationary','static']
    if context_name not in contexts: raise ValueError(f'Unknown context {context_name}')
    ctx=contexts[context_name]
    st={str(x).strip().lower() for x in stationary_labels}; post={str(x).strip().lower() for x in ctx.get('allowed_postures',[])}; zones={str(x).strip().lower() for x in ctx.get('allowed_zones',[])}
    stationary=df['pred_ds_label'].astype(str).str.strip().str.lower().isin(st)
    posture_ok=df['posture'].astype(str).str.strip().str.lower().isin(post) if post else True
    zone_ok=df['zone_label'].astype(str).str.strip().str.lower().isin(zones) if zones else True
    df['came_context']=context_name; df['came_bout_gate']=(stationary & posture_ok & zone_ok).astype(bool)
    min_frames=max(1,int(round(float(min_duration_sec)*float(fps))))
    bouts=[]; frames=[]; n=0
    for gid,sub in df.groupby('group_id',sort=False):
        sub=sub.sort_values('FrameNumber'); gate=list(sub['came_bout_gate'].to_numpy(bool))+[False]; start=None
        for i,flag in enumerate(gate):
            if flag and start is None: start=i
            elif (not flag) and start is not None:
                end=i-1; length=end-start+1
                if length>=min_frames:
                    n+=1; seg=sub.iloc[start:end+1].copy(); bid=f'{context_name}_bout{n:04d}'; seg['bout_id']=bid; frames.append(seg)
                    bouts.append({'bout_id':bid,'context':context_name,'group_id':gid,'start_frame':int(seg['FrameNumber'].iloc[0]),'end_frame':int(seg['FrameNumber'].iloc[-1]),'duration_frames':len(seg),'duration_sec':len(seg)/max(float(fps),1e-9),'major_posture':seg['posture'].mode().iloc[0] if not seg['posture'].mode().empty else '', 'major_zone':seg['zone_label'].mode().iloc[0] if not seg['zone_label'].mode().empty else ''})
                start=None
    return pd.DataFrame(bouts), pd.concat(frames,ignore_index=True) if frames else pd.DataFrame(columns=list(df.columns)+['bout_id'])

def extract_bouts_for_file(input_csv,output_dir,context_name='LAS',config_path=None,fps=1.0,min_duration_sec=None):
    cfg=load_config(config_path); bcfg=cfg.get('stationary_bout',{}) if isinstance(cfg,dict) else {}
    contexts=bcfg.get('contexts',DEFAULT_CONTEXTS); stationary_labels=bcfg.get('stationary_labels',['s','stationary','static'])
    if min_duration_sec is None: min_duration_sec=float(bcfg.get('min_duration_sec',10))
    input_csv=Path(input_csv); output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    idx,frames=extract_bouts(pd.read_csv(input_csv),context_name,contexts,stationary_labels,min_duration_sec,fps)
    idx_path=output_dir/f'{input_csv.stem}_{context_name}_bout_index.csv'; frames_path=output_dir/f'{input_csv.stem}_{context_name}_bout_frames.csv'
    idx.to_csv(idx_path,index=False); frames.to_csv(frames_path,index=False)
    bd=output_dir/f'{input_csv.stem}_{context_name}_bouts'; bd.mkdir(exist_ok=True)
    if not frames.empty:
        for bid,sub in frames.groupby('bout_id',sort=False): sub.to_csv(bd/f'{bid}.csv',index=False)
    return idx_path,frames_path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output-dir',required=True); ap.add_argument('--context',default='LAS',choices=['LAS','FAS','SAS']); ap.add_argument('--config',default=None); ap.add_argument('--fps',type=float,default=1.0); ap.add_argument('--min-duration-sec',type=float,default=None)
    a=ap.parse_args(); idx,frm=extract_bouts_for_file(a.input,a.output_dir,a.context,a.config,a.fps,a.min_duration_sec); print(f'[CAME] Bout index: {idx}\n[CAME] Bout frames: {frm}')
if __name__=='__main__': main()
