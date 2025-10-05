import numpy as np
from netCDF4 import Dataset
import math

# --- MERRA-2 Grid Reference (Approximate) ---
LAT_MIN, LON_MIN = -90.0, -180.0
LAT_STEP, LON_STEP = 0.5, 0.625

def main():
    try:
        # User input for location
        lat = float(input("Enter latitude (e.g., 40.7): "))
        lon = float(input("Enter longitude (e.g., -74.0): "))

        # File paths (update if different)
        file_slv = r"C:\Users\ADMIN\Downloads\MERRA2_400.tavg1_2d_slv_Nx.20250901.nc4"
        file_flx = r"C:\Users\ADMIN\Downloads\MERRA2_400.tavg1_2d_flx_Nx.20250901.nc4"

        # Open datasets
        ds_slv = Dataset(file_slv, 'r')
        ds_flx = Dataset(file_flx, 'r')

        # Convert lat/lon to array indices
        lat_idx = round((lat - LAT_MIN) / LAT_STEP)
        lon_idx = round((lon - LON_MIN) / LON_STEP)

        # --- Extract SLV variables (temperature & wind components) ---
        temp_k = ds_slv.variables['T2M'][:, lat_idx, lon_idx]   # 2m air temperature
        u10 = ds_slv.variables['U10M'][:, lat_idx, lon_idx]     # 10m wind U component
        v10 = ds_slv.variables['V10M'][:, lat_idx, lon_idx]     # 10m wind V component

        # --- Extract FLX variables (precipitation & max wind) ---
        precip = ds_flx.variables['PRECTOT'][:, lat_idx, lon_idx]   # total precipitation
        wind_max_flx = ds_flx.variables['SPEEDMAX'][:, lat_idx, lon_idx]  # optional

        # Close datasets
        ds_slv.close()
        ds_flx.close()

        # --- Calculations ---
        temp_c = temp_k - 273.15
        wind_speed = np.sqrt(u10**2 + v10**2)   # FIXED: use **2 not *2
        precip_mm_day = precip * 86400  # convert m/s to mm/day

        tmax, tmin = np.nanmax(temp_c), np.nanmin(temp_c)
        wind_max = max(np.nanmax(wind_speed), np.nanmax(wind_max_flx))
        precip_avg = np.nanmean(precip_mm_day)

        # --- Thresholds for extremes ---
        thresholds = {"veryHotC": 35, "veryColdC": 0, "veryWindyMs": 12, "veryWetMm": 10}
        conditions = []
        if tmax > thresholds["veryHotC"]: conditions.append("Very Hot")
        if tmin < thresholds["veryColdC"]: conditions.append("Very Cold")
        if wind_max > thresholds["veryWindyMs"]: conditions.append("Very Windy")
        if precip_avg > thresholds["veryWetMm"]: conditions.append("Very Wet (Avg.)")

        # --- Print results ---
        print(f"\n--- Weather at ({lat}, {lon}) on 2025-09-01 ---")
        print(f"Temperature: {tmin:.1f}°C – {tmax:.1f}°C")
        print(f"Maximum wind speed: {wind_max:.1f} m/s")
        print(f"Average Total Precipitation: {precip_avg:.1f} mm/day")
        print("Extreme conditions detected:", ", ".join(conditions) if conditions else "None")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")


if __name__ == "__main__":
    main()
