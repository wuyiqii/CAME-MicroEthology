#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import ast, re
from pathlib import Path
from typing import Sequence, List, Tuple, Dict
import numpy as np
import pandas as pd
MISSING_TOKENS = {"", "null", "none", "nan", "na", "n/a", "NULL", "None"}

def is_present(value: object) -> bool:
    if value is None: return False
    text = str(value).strip()
    return bool(text) and text.lower() not in {x.lower() for x in MISSING_TOKENS}

def robust_zscore(values: Sequence[float]) -> np.ndarray:
    arr=np.asarray(values,dtype=float); finite=np.isfinite(arr)
    if not finite.any(): return np.zeros_like(arr,dtype=float)
    med=np.nanmedian(arr[finite]); mad=np.nanmedian(np.abs(arr[finite]-med)); scale=1.4826*mad
    if not np.isfinite(scale) or scale<1e-9:
        std=np.nanstd(arr[finite]); scale=std if np.isfinite(std) and std>=1e-9 else 1.0
    return (arr-med)/scale

def minmax01(values: Sequence[float]) -> np.ndarray:
    arr=np.asarray(values,dtype=float); out=np.zeros_like(arr,dtype=float); finite=np.isfinite(arr)
    if not finite.any(): return out
    lo,hi=np.nanmin(arr[finite]),np.nanmax(arr[finite])
    if hi-lo<1e-12: return out
    out[finite]=(arr[finite]-lo)/(hi-lo); return out

def smooth_series(values: Sequence[float], window:int=3) -> np.ndarray:
    return pd.Series(np.asarray(values,dtype=float)).rolling(max(1,int(window)),center=True,min_periods=1).mean().to_numpy(dtype=float)

def parse_point(value: object) -> Tuple[float,float]:
    if not is_present(value): return np.nan,np.nan
    if isinstance(value,(list,tuple)) and len(value)>=2:
        try: return float(value[0]),float(value[1])
        except Exception: return np.nan,np.nan
    text=str(value).strip()
    try:
        obj=ast.literal_eval(text)
        if isinstance(obj,(list,tuple)) and len(obj)>=2: return float(obj[0]),float(obj[1])
    except Exception: pass
    text=text.replace('(','').replace(')','').replace('[','').replace(']','')
    parts=[p for p in re.split(r'[,\s]+',text) if p]
    if len(parts)>=2:
        try: return float(parts[0]),float(parts[1])
        except Exception: pass
    return np.nan,np.nan

def parse_polyline(value: object) -> List[Tuple[float,float]]:
    if not is_present(value): return []
    pts=[]
    for part in re.split(r'[|｜]',str(value).strip()):
        for token in part.split(';'):
            x,y=parse_point(token.strip())
            if np.isfinite(x) and np.isfinite(y): pts.append((x,y))
    return pts

def bbox_from_value(value:object)->Tuple[float,float,float,float]:
    pts=parse_polyline(value)
    if len(pts)<2: return np.nan,np.nan,np.nan,np.nan
    a=np.asarray(pts,float); return float(np.nanmin(a[:,0])),float(np.nanmin(a[:,1])),float(np.nanmax(a[:,0])),float(np.nanmax(a[:,1]))

def polygon_area(points):
    if len(points)<3: return np.nan
    a=np.asarray(points,float); x,y=a[:,0],a[:,1]
    return float(0.5*abs(np.dot(x,np.roll(y,-1))-np.dot(y,np.roll(x,-1))))

def polygon_perimeter(points, closed=True):
    if len(points)<2: return np.nan
    a=np.asarray(points,float); d=np.diff(a,axis=0); total=float(np.sum(np.sqrt(np.sum(d*d,axis=1))))
    if closed and len(points)>=3:
        q=a[0]-a[-1]; total+=float(np.sqrt(np.sum(q*q)))
    return total

def pca_orientation(points):
    if len(points)<2: return np.nan
    a=np.asarray(points,float); a=a[np.isfinite(a).all(axis=1)]
    if len(a)<2: return np.nan
    a=a-a.mean(axis=0,keepdims=True); cov=np.cov(a.T)
    if not np.isfinite(cov).all(): return np.nan
    vals,vecs=np.linalg.eigh(cov); v=vecs[:,int(np.argmax(vals))]
    return float(np.degrees(np.arctan2(v[1],v[0])))

def angle_diff_deg(a):
    arr=np.asarray(a,float); rad=np.unwrap(np.deg2rad(arr)); out=np.full_like(rad,np.nan,dtype=float)
    if len(rad)>=2: out[1:]=np.diff(rad)
    return np.rad2deg(out)

def transition_count(labels, exclude_self=True):
    labels=list(labels)
    return sum(1 for a,b in zip(labels[:-1],labels[1:]) if (not exclude_self) or a!=b)
