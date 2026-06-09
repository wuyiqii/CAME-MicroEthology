#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Optional, Dict, List
import numpy as np
import pandas as pd
from .utils import bbox_from_value, parse_polyline, parse_point, polygon_area, polygon_perimeter, pca_orientation, angle_diff_deg, robust_zscore, smooth_series

DEFAULT_GROUP_MAP = {
 'kin_linear_energy':['speed_box','speed_mask','acc_box','acc_mask','head_speed','tail_speed','mid_speed'],
 'morph_pose_energy':['area_box_change_abs','area_mask_change_abs','box_aspect_ratio_change_abs','keypoints_distance_change_abs','polygon_perimeter_change_abs'],
 'orientation_heading_energy':['box_orientation_change_abs','mask_orientation_change_abs','kps_orientation_change_abs'],
 'coordination_head_body_energy':['head_tail_distance_change_abs','head_mid_distance_change_abs','tail_mid_distance_change_abs'],
 'microburst_energy':['jerk_box','jerk_mask','head_jerk','tail_jerk'],
 'stability_occlusion_contact_energy':['mask_discrepancy','mask_centroid_box_center_distance','area_mask_box_ratio_change_abs'],
 'spectral_dynamics_energy':['speed_box_rms','kps_orientation_change_abs_rms','area_mask_change_abs_rms'],
 'slowfast_semantics_state_energy':['sf_energy','sf_delta','sf_pca1'],
 'boundary_delta_energy':['speed_box','area_mask_change_abs','kps_orientation_change_abs','mask_discrepancy'],
 'boundary_mmd_energy':['sf_mmd','sf_mmd_4','sf_mmd_8','sf_mmd_16'],
}

def _normalise(df):
    df=df.copy()
    if 'FrameNumber' not in df.columns:
        df['FrameNumber']=np.arange(len(df),dtype=int)
    df['FrameNumber']=pd.to_numeric(df['FrameNumber'],errors='coerce').ffill().bfill().astype(int)
    if 'group_id' not in df.columns: df['group_id']='group0'
    if 'kps0_det' not in df.columns and 'kps0' in df.columns: df['kps0_det']=df['kps0']
    if 'kps1_det' not in df.columns and 'kps1' in df.columns: df['kps1_det']=df['kps1']
    if 'zone_label' not in df.columns:
        for c in ['zone_lable','context_label','zone']:
            if c in df.columns: df['zone_label']=df[c]; break
    if 'zone_label' not in df.columns: df['zone_label']='unknown'
    if 'posture' not in df.columns:
        df['posture']=df['posture_label'] if 'posture_label' in df.columns else 'unknown'
    return df.sort_values(['group_id','FrameNumber']).reset_index(drop=True)

def _add_geometry(df):
    df=df.copy(); boxes=np.asarray([bbox_from_value(v) for v in df.get('box',pd.Series([np.nan]*len(df)))],float)
    df['bbox_x1'],df['bbox_y1'],df['bbox_x2'],df['bbox_y2']=boxes[:,0],boxes[:,1],boxes[:,2],boxes[:,3]
    df['bbox_width']=df['bbox_x2']-df['bbox_x1']; df['bbox_height']=df['bbox_y2']-df['bbox_y1']
    df['center_x_box']=(df['bbox_x1']+df['bbox_x2'])/2; df['center_y_box']=(df['bbox_y1']+df['bbox_y2'])/2
    df['area_box']=df['bbox_width']*df['bbox_height']; df['box_aspect_ratio']=df['bbox_width']/df['bbox_height'].replace(0,np.nan)
    df['box_perimeter']=2*(df['bbox_width']+df['bbox_height']); df['box_orientation']=np.where(df['bbox_width']>=df['bbox_height'],0.0,90.0)
    masks=[parse_polyline(v) for v in df.get('mask',pd.Series([np.nan]*len(df)))]
    df['area_mask']=[polygon_area(p) for p in masks]; df['polygon_perimeter']=[polygon_perimeter(p) for p in masks]
    df['mask_orientation']=[pca_orientation(p) for p in masks]
    cents=[]
    for p in masks:
        if len(p)==0: cents.append((np.nan,np.nan))
        else:
            a=np.asarray(p,float); cents.append((float(np.nanmean(a[:,0])),float(np.nanmean(a[:,1]))))
    df['center_x_mask']=[p[0] for p in cents]; df['center_y_mask']=[p[1] for p in cents]
    df['area_mask_box_ratio']=df['area_mask']/df['area_box'].replace(0,np.nan)
    df['mask_centroid_box_center_distance']=np.sqrt((df['center_x_mask']-df['center_x_box'])**2+(df['center_y_mask']-df['center_y_box'])**2)
    df['mask_discrepancy']=df['mask_centroid_box_center_distance']/np.sqrt(df['area_box'].clip(lower=1))
    k0=[parse_point(v) for v in df.get('kps0_det',pd.Series([np.nan]*len(df)))]
    k1=[parse_point(v) for v in df.get('kps1_det',pd.Series([np.nan]*len(df)))]
    df['kps0_x']=[p[0] for p in k0]; df['kps0_y']=[p[1] for p in k0]; df['kps1_x']=[p[0] for p in k1]; df['kps1_y']=[p[1] for p in k1]
    df['kps_mid_x']=(df['kps0_x']+df['kps1_x'])/2; df['kps_mid_y']=(df['kps0_y']+df['kps1_y'])/2
    dx=df['kps0_x']-df['kps1_x']; dy=df['kps0_y']-df['kps1_y']
    df['keypoints_distance']=np.sqrt(dx*dx+dy*dy); df['kps_orientation']=np.degrees(np.arctan2(dy,dx))
    return df

def _add_motion(df,fps=1.0):
    df=df.copy(); g='group_id'
    def speed(x,y,out):
        dx=df.groupby(g,sort=False)[x].diff(); dy=df.groupby(g,sort=False)[y].diff(); df[out]=np.sqrt(dx*dx+dy*dy)*fps
    for x,y,out in [('center_x_box','center_y_box','speed_box'),('center_x_mask','center_y_mask','speed_mask'),('kps0_x','kps0_y','head_speed'),('kps1_x','kps1_y','tail_speed'),('kps_mid_x','kps_mid_y','mid_speed')]: speed(x,y,out)
    for s,a,j in [('speed_box','acc_box','jerk_box'),('speed_mask','acc_mask','jerk_mask'),('head_speed','head_acc','head_jerk'),('tail_speed','tail_acc','tail_jerk')]:
        df[a]=df.groupby(g,sort=False)[s].diff().abs()*fps; df[j]=df.groupby(g,sort=False)[a].diff().abs()*fps
    for c in ['area_box','area_mask','box_aspect_ratio','box_perimeter','polygon_perimeter','keypoints_distance','area_mask_box_ratio']:
        df[f'{c}_change_abs']=df.groupby(g,sort=False)[c].diff().abs()
    df['head_mid_distance']=np.sqrt((df['kps0_x']-df['kps_mid_x'])**2+(df['kps0_y']-df['kps_mid_y'])**2)
    df['tail_mid_distance']=np.sqrt((df['kps1_x']-df['kps_mid_x'])**2+(df['kps1_y']-df['kps_mid_y'])**2)
    df['head_tail_distance_change_abs']=df.groupby(g,sort=False)['keypoints_distance'].diff().abs()
    df['head_mid_distance_change_abs']=df.groupby(g,sort=False)['head_mid_distance'].diff().abs()
    df['tail_mid_distance_change_abs']=df.groupby(g,sort=False)['tail_mid_distance'].diff().abs()
    for c in ['box_orientation','mask_orientation','kps_orientation']:
        parts=[]
        for _,sub in df.groupby(g,sort=False): parts.append(pd.Series(np.abs(angle_diff_deg(sub[c].to_numpy(float))),index=sub.index))
        df[f'{c}_change_abs']=pd.concat(parts).sort_index() if parts else np.nan
    for c in ['speed_box','kps_orientation_change_abs','area_mask_change_abs']:
        if c in df.columns:
            df[f'{c}_rms']=df.groupby(g,sort=False)[c].transform(lambda s: s.rolling(3,min_periods=1,center=True).apply(lambda x: float(np.sqrt(np.nanmean(np.asarray(x)**2))),raw=False))
    return df.ffill().bfill()

def _energy_groups(df, group_map=DEFAULT_GROUP_MAP):
    df=df.copy()
    for out,cols in group_map.items():
        avail=[c for c in cols if c in df.columns]
        if not avail: df[out]=0.0; continue
        zs=[]
        for c in avail:
            z=np.nan_to_num(np.abs(robust_zscore(pd.to_numeric(df[c],errors='coerce').to_numpy(float))),nan=0.0,posinf=0.0,neginf=0.0)
            zs.append(z)
        df[out]=smooth_series(np.nanmean(np.vstack(zs),axis=0),3)
    return df

def extract_features(df:pd.DataFrame,fps:float=1.0)->pd.DataFrame:
    return _energy_groups(_add_motion(_add_geometry(_normalise(df)),fps=fps))

def extract_features_for_file(input_csv,output_csv,fps=1.0):
    input_csv=Path(input_csv); output_csv=Path(output_csv); output_csv.parent.mkdir(parents=True,exist_ok=True)
    out=extract_features(pd.read_csv(input_csv),fps=fps); out.to_csv(output_csv,index=False); return output_csv

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output',required=True); ap.add_argument('--fps',type=float,default=1.0)
    a=ap.parse_args(); print(f'[CAME] Feature CSV saved to: {extract_features_for_file(a.input,a.output,a.fps)}')
if __name__=='__main__': main()
