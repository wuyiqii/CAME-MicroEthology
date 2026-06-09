#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from .utils import robust_zscore, smooth_series, transition_count

DEFAULT_COLS=['orientation_heading_energy','morph_pose_energy','kin_linear_energy','microburst_energy','spectral_dynamics_energy','coordination_head_body_energy','slowfast_semantics_state_energy','stability_occlusion_contact_energy','boundary_delta_energy','boundary_mmd_energy']
PHASE={0:'stable',1:'intermediate-instability',2:'high-instability'}

def load_config(path):
    if not path: return {}
    with open(path,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}

def columns(df,cfg):
    cols=(cfg.get('instability_score',{}) or {}).get('columns',DEFAULT_COLS)
    cols=[c for c in cols if c in df.columns]
    if not cols: cols=[c for c in df.columns if c.endswith('_energy')]
    if not cols: cols=[c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in {'FrameNumber','group_id'}]
    if not cols: raise ValueError('No valid columns for CAME instability calculation.')
    return cols

def weights(cols,cfg):
    wcfg=(cfg.get('instability_score',{}) or {}).get('weights','uniform')
    if wcfg=='uniform' or wcfg is None: w=np.ones(len(cols),float)
    elif isinstance(wcfg,dict): w=np.array([float(wcfg.get(c,1.0)) for c in cols],float)
    elif isinstance(wcfg,list):
        w=np.ones(len(cols),float); w[:min(len(w),len(wcfg))]=[float(x) for x in wcfg[:min(len(w),len(wcfg))]]
    else: w=np.ones(len(cols),float)
    w=np.maximum(w,0); return w/w.sum() if w.sum()>0 else np.ones(len(cols))/len(cols)

def compute_dynamic_indices(df,cfg=None):
    cfg=cfg or {}; df=df.copy(); cols=columns(df,cfg); w=weights(cols,cfg)
    Z=[]
    for c in cols:
        z=np.nan_to_num(np.abs(robust_zscore(pd.to_numeric(df[c],errors='coerce').to_numpy(float))),nan=0,posinf=0,neginf=0); Z.append(z)
    Z=np.vstack(Z).T; I=Z@w
    df['I_t']=I; df['E_t']=np.sqrt(np.nanmean(Z*Z,axis=1))
    dZ=np.zeros_like(Z); dZ[1:]=np.abs(np.diff(Z,axis=0)) if len(df)>=2 else dZ[1:]
    df['B_t']=smooth_series(np.nanmax(dZ,axis=1),3)
    df['R_t']=smooth_series(np.abs(I-np.nanmedian(I[np.isfinite(I)])) if np.isfinite(I).any() else np.zeros_like(I),5)
    df['change_intensity']=smooth_series(np.abs(np.gradient(I)) if len(I)>1 else np.zeros_like(I),3)
    df.attrs['instability_columns']=cols; df.attrs['instability_weights']={c:float(x) for c,x in zip(cols,w)}
    return df

def thresholds(df,cfg,global_reference_csv=None):
    pcfg=(cfg.get('phase_decoding',{}) or {})
    if pcfg.get('threshold_mode','quantile')=='fixed': return float(pcfg['theta1']),float(pcfg['theta2'])
    vals=None
    if global_reference_csv:
        ref=pd.read_csv(global_reference_csv); ref=compute_dynamic_indices(ref,cfg) if 'I_t' not in ref.columns else ref; vals=ref['I_t'].to_numpy(float)
    else: vals=df['I_t'].to_numpy(float)
    vals=vals[np.isfinite(vals)]
    if vals.size==0: return 0.0,1.0
    t1=float(np.nanquantile(vals,float(pcfg.get('q1',0.60)))); t2=float(np.nanquantile(vals,float(pcfg.get('q2',0.85))))
    return (t1,t2 if t2>t1 else t1+1e-9)

def decode(df,t1,t2):
    df=df.copy(); I=df['I_t'].to_numpy(float); code=np.zeros(len(df),int); code[I>=t1]=1; code[I>=t2]=2
    df['phase_code']=code; df['phase_label']=[PHASE[int(c)] for c in code]; return df

def phase_segments(df,fps=1.0):
    if df.empty: return pd.DataFrame()
    df=df.copy();
    if 'bout_id' not in df.columns: df['bout_id']='bout0001'
    if 'FrameNumber' not in df.columns: df['FrameNumber']=np.arange(len(df))
    rows=[]
    for bid,sub in df.groupby('bout_id',sort=False):
        sub=sub.reset_index(drop=True); lab=sub['phase_label'].astype(str).tolist(); start=0
        for i in range(1,len(sub)+1):
            if i==len(sub) or lab[i]!=lab[start]:
                seg=sub.iloc[start:i]
                rows.append({'bout_id':bid,'phase_label':lab[start],'start_frame':int(seg['FrameNumber'].iloc[0]),'end_frame':int(seg['FrameNumber'].iloc[-1]),'duration_frames':len(seg),'duration_sec':len(seg)/max(float(fps),1e-9),'mean_I_t':seg['I_t'].mean(),'max_I_t':seg['I_t'].max(),'mean_B_t':seg['B_t'].mean(),'mean_R_t':seg['R_t'].mean(),'mean_E_t':seg['E_t'].mean()})
                start=i
    return pd.DataFrame(rows)

def summarize(df,segs,fps=1.0):
    if df.empty: return pd.DataFrame()
    df=df.copy();
    if 'bout_id' not in df.columns: df['bout_id']='bout0001'
    if 'FrameNumber' not in df.columns: df['FrameNumber']=np.arange(len(df))
    rows=[]
    for bid,sub in df.groupby('bout_id',sort=False):
        lab=sub['phase_label'].astype(str).tolist(); n=len(sub); counts=pd.Series(lab).value_counts(normalize=True); dur=n/max(float(fps),1e-9); trans=transition_count(lab,True)
        ss=segs[(segs['bout_id']==bid)&(segs['phase_label']=='stable')] if not segs.empty and 'bout_id' in segs.columns else pd.DataFrame(); longest=float(ss['duration_sec'].max()) if not ss.empty else 0.0
        rows.append({'bout_id':bid,'start_frame':int(sub['FrameNumber'].iloc[0]),'end_frame':int(sub['FrameNumber'].iloc[-1]),'duration_frames':n,'duration_sec':dur,'SP_occupancy':float(counts.get('stable',0)),'IIP_occupancy':float(counts.get('intermediate-instability',0)),'HIP_occupancy':float(counts.get('high-instability',0)),'IIP_HIP_ratio':float(counts.get('intermediate-instability',0)+counts.get('high-instability',0)),'transition_count':int(trans),'transition_density_per_min':float(trans/max(dur/60,1e-9)),'longest_SP_fraction':float(longest/max(dur,1e-9)),'mean_I_t':sub['I_t'].mean(),'max_I_t':sub['I_t'].max(),'mean_B_t':sub['B_t'].mean(),'max_B_t':sub['B_t'].max(),'mean_R_t':sub['R_t'].mean(),'mean_E_t':sub['E_t'].mean()})
    return pd.DataFrame(rows)

def run_came_dynamics(df,cfg=None,fps=1.0,global_reference_csv=None):
    cfg=cfg or {}; states=compute_dynamic_indices(df,cfg); t1,t2=thresholds(states,cfg,global_reference_csv); states=decode(states,t1,t2); segs=phase_segments(states,fps); desc=summarize(states,segs,fps)
    meta={'theta1':float(t1),'theta2':float(t2),'phase_rule':{'stable':'I_t < theta1','intermediate-instability':'theta1 <= I_t < theta2','high-instability':'I_t >= theta2'},'instability_columns':states.attrs.get('instability_columns',[]),'instability_weights':states.attrs.get('instability_weights',{})}
    return states,segs,desc,meta

def run_came_for_file(input_csv,output_dir,config_path=None,fps=1.0,global_reference_csv=None):
    cfg=load_config(config_path); input_csv=Path(input_csv); out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    states,segs,desc,meta=run_came_dynamics(pd.read_csv(input_csv),cfg,fps,global_reference_csv); stem=input_csv.stem
    paths={'frame_states':out/f'{stem}_frame_states.csv','phase_segments':out/f'{stem}_phase_segments.csv','bout_descriptors':out/f'{stem}_bout_descriptors.csv','thresholds':out/f'{stem}_thresholds.json'}
    states.to_csv(paths['frame_states'],index=False); segs.to_csv(paths['phase_segments'],index=False); desc.to_csv(paths['bout_descriptors'],index=False)
    with open(paths['thresholds'],'w',encoding='utf-8') as f: json.dump(meta,f,ensure_ascii=False,indent=2)
    return paths

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output-dir',required=True); ap.add_argument('--config',default=None); ap.add_argument('--fps',type=float,default=1.0); ap.add_argument('--global-reference-csv',default=None)
    a=ap.parse_args(); paths=run_came_for_file(a.input,a.output_dir,a.config,a.fps,a.global_reference_csv)
    for k,p in paths.items(): print(f'[CAME] {k}: {p}')
if __name__=='__main__': main()
