"""
Shared border-geometry helpers (added Development Log Entry 49).

Reproduces exactly what compute_border_distance.py does -- planar nearest
point on the Natural Earth India boundary lines (EPSG:4326 coordinates, the
same thing shapely's nearest_points does), then a geodesic WGS84 distance to
that point -- but can also restrict the boundary to one neighbouring country
(e.g. China only, so H3 measures proximity to the LAC rather than to the
open Bhutan/Nepal borders or the Myanmar border).

Uses geopandas/shapely/pyproj when they are installed. If they are not, it
falls back to a small pure-Python shapefile reader and Vincenty's inverse
formula, which agrees with pyproj.Geod to well under a metre. The fallback was
validated by reproducing every value of distance_to_border_km in
border_optics_master_villages_with_distance.csv (see compute_lac_distance.py).
"""

import math
import struct

import numpy as np

BOUNDARY_PATH = "data/raw/ne_10m_admin_0_boundary_lines_land/ne_10m_admin_0_boundary_lines_land"

# ---------------------------------------------------------------- reading


def _read_dbf(path):
    raw = open(path, "rb").read()
    n_records = struct.unpack("<I", raw[4:8])[0]
    header_len = struct.unpack("<H", raw[8:10])[0]
    record_len = struct.unpack("<H", raw[10:12])[0]
    fields, offset = [], 32
    while raw[offset] != 0x0D:
        name = raw[offset:offset + 11].split(b"\0")[0].decode("latin-1")
        length = raw[offset + 16]
        fields.append((name, length))
        offset += 32
    records = []
    for i in range(n_records):
        start = header_len + i * record_len + 1  # skip deletion flag
        rec, pos = {}, start
        for name, length in fields:
            rec[name] = raw[pos:pos + length].decode("utf-8", errors="replace").strip()
            pos += length
        records.append(rec)
    return records


def _read_shp_polylines(path):
    """Return a list (one per record) of lists of parts, each an (n, 2) lon/lat array."""
    raw = open(path, "rb").read()
    out, pos = [], 100
    while pos < len(raw):
        content_len = struct.unpack(">i", raw[pos + 4:pos + 8])[0] * 2
        rec = raw[pos + 8:pos + 8 + content_len]
        shape_type = struct.unpack("<i", rec[0:4])[0]
        if shape_type == 0:
            out.append([])
        else:
            num_parts, num_points = struct.unpack("<ii", rec[36:44])
            parts = list(struct.unpack(f"<{num_parts}i", rec[44:44 + 4 * num_parts]))
            pts_start = 44 + 4 * num_parts
            pts = np.frombuffer(rec[pts_start:pts_start + 16 * num_points], dtype="<f8").reshape(-1, 2)
            bounds = parts + [num_points]
            out.append([pts[bounds[k]:bounds[k + 1]] for k in range(num_parts)])
        pos += 8 + content_len
    return out


def load_india_segments():
    """List of dicts: {'other_country': str, 'parts': [ (n,2) arrays ]} for India-related lines."""
    records = _read_dbf(BOUNDARY_PATH + ".dbf")
    shapes = _read_shp_polylines(BOUNDARY_PATH + ".shp")
    segments = []
    for rec, parts in zip(records, shapes):
        left, right = rec.get("ADM0_LEFT"), rec.get("ADM0_RIGHT")
        if left == "India" or right == "India":
            other = right if left == "India" else left
            segments.append({"other_country": other, "parts": parts})
    return segments


def segment_arrays(segments, country=None):
    """Stack every 2-point line segment as (A, B) arrays, optionally for one neighbour only."""
    a_list, b_list, owner = [], [], []
    for i, seg in enumerate(segments):
        if country is not None and seg["other_country"] != country:
            continue
        for part in seg["parts"]:
            if len(part) < 2:
                continue
            a_list.append(part[:-1])
            b_list.append(part[1:])
            owner.extend([i] * (len(part) - 1))
    return np.vstack(a_list), np.vstack(b_list), np.array(owner)


# ---------------------------------------------------------------- geometry


def nearest_point_planar(lon, lat, A, B):
    """Planar (lon/lat degrees) nearest point on a set of segments -- same rule as shapely."""
    p = np.array([lon, lat])
    ab = B - A
    denom = (ab ** 2).sum(1)
    t = np.where(denom > 0, ((p - A) * ab).sum(1) / np.where(denom > 0, denom, 1), 0.0)
    t = np.clip(t, 0, 1)
    proj = A + ab * t[:, None]
    d2 = ((proj - p) ** 2).sum(1)
    k = int(np.argmin(d2))
    return proj[k], k


def _vincenty_m(lon1, lat1, lon2, lat2):
    a, f = 6378137.0, 1 / 298.257223563
    b = (1 - f) * a
    L = math.radians(lon2 - lon1)
    U1 = math.atan((1 - f) * math.tan(math.radians(lat1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(lat2)))
    sinU1, cosU1, sinU2, cosU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    for _ in range(200):
        sin_lam, cos_lam = math.sin(lam), math.cos(lam)
        sin_sig = math.sqrt((cosU2 * sin_lam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cos_lam) ** 2)
        if sin_sig == 0:
            return 0.0
        cos_sig = sinU1 * sinU2 + cosU1 * cosU2 * cos_lam
        sig = math.atan2(sin_sig, cos_sig)
        sin_alpha = cosU1 * cosU2 * sin_lam / sin_sig
        cos2_alpha = 1 - sin_alpha ** 2
        cos2_sm = cos_sig - 2 * sinU1 * sinU2 / cos2_alpha if cos2_alpha != 0 else 0.0
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        lam_prev = lam
        lam = L + (1 - C) * f * sin_alpha * (sig + C * sin_sig * (cos2_sm + C * cos_sig * (-1 + 2 * cos2_sm ** 2)))
        if abs(lam - lam_prev) < 1e-12:
            break
    u2 = cos2_alpha * (a ** 2 - b ** 2) / b ** 2
    A_ = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B_ = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    d_sig = B_ * sin_sig * (cos2_sm + B_ / 4 * (cos_sig * (-1 + 2 * cos2_sm ** 2)
                                                - B_ / 6 * cos2_sm * (-3 + 4 * sin_sig ** 2) * (-3 + 4 * cos2_sm ** 2)))
    return b * A_ * (sig - d_sig)


try:  # prefer pyproj (what compute_border_distance.py uses) when available
    from pyproj import Geod as _Geod

    _GEOD = _Geod(ellps="WGS84")

    def geodesic_m(lon1, lat1, lon2, lat2):
        return float(_GEOD.inv(lon1, lat1, lon2, lat2)[2])
except ImportError:  # pragma: no cover - exercised in environments without pyproj
    def geodesic_m(lon1, lat1, lon2, lat2):
        return _vincenty_m(lon1, lat1, lon2, lat2)


def distance_to_border_km(lon, lat, A, B, owner, segments):
    """Geodesic km to the planar-nearest point, plus the neighbouring country of that segment."""
    pt, k = nearest_point_planar(lon, lat, A, B)
    return geodesic_m(lon, lat, pt[0], pt[1]) / 1000.0, segments[owner[k]]["other_country"]
