# Background/anaysis geometry
# ---------------------------
geometry:
  fms initialization:
    namelist filename: Data/fv3files/fmsmpp.nml
    field table filename: Data/fv3files/field_table
  akbk: Data/fv3files/akbk127.nc4
  layout:
  - !ENV ${solver_layout_x}
  - !ENV ${solver_layout_y}
  npx: $(npx_ges)
  npy: $(npy_ges)
  npz: $(npz_ges)
  field metadata override: Data/fieldmetadata/gfs-restart.yaml

#window begin: '$(ATM_WINDOW_BEGIN)'
#window length: $(ATM_WINDOW_LENGTH)

time window:
  begin: $(ATM_WINDOW_BEGIN)
  end: $(ATM_WINDOW_END)

#increment variables: [ua, va, t, DZ, delp, ice_wat, liq_wat, sphum, o3mr]
increment variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                      slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                      u_srf,v_srf,f10m]

background:
  members from template:
    pattern: '%mem%'
    nmembers: $(NMEM_ENKF)
    zero padding: 3
    template:
      datetime: $(BKG_ISOTIME)
      states:
      - datetime: &date_bgn $(BKG_BGN)
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010418/mem%mem%/RESTART
        filename_core: 20220104.230000.fv_core.res.nc
        filename_trcr: 20220104.230000.fv_tracer.res.nc
        filename_sfcd: 20220104.230000.sfc_data.nc
        filename_sfcw: 20220104.230000.fv_srf_wnd.res.nc
        filename_cplr: 20220104.230000.coupler.res
      - datetime: &date_mid '2022-01-05T00:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: MEMSTR/INPUT
        filename_core: fv_core.res.nc
        filename_trcr: fv_tracer.res.nc
        filename_sfcd: sfc_data.nc
        filename_sfcw: fv_srf_wnd.res.nc
        filename_cplr: coupler.res
      - datetime: &date_end '2022-01-05T01:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010500/mem%mem%/RESTART
        filename_core: 20220105.010000.fv_core.res.nc
        filename_trcr: 20220105.010000.fv_tracer.res.nc
        filename_sfcd: 20220105.010000.sfc_data.nc
        filename_sfcw: 20220105.010000.fv_srf_wnd.res.nc
        filename_cplr: 20220105.010000.coupler.res

driver:
  read HX from disk: true
  do posterior observer: false
 #do test prints: true
  do test prints: false
  save posterior mean: true
  save posterior ensemble: false
  save prior mean: false
  save posterior mean increment: true
  save posterior ensemble increments: true
  update obs config with geometry info: true

local ensemble DA:
  solver: GETKF
  vertical localization:
    fraction of retained variance: .95
    lengthscale: 14
    lengthscale units: levels
  inflation:
    rtps: 0.85
    rtpp: 0.0
    mult: 1.0

# Analysis output
# ---------------
# for realistic output, use gfs filetype for output
# here we are using latlon for ease of visualisation
output ensemble increments:
  filetype: fms restart
  datapath: analysis/increment/mem%{member}%
  filename_core: fv_core.res.nc
  filename_trcr: fv_tracer.res.nc
  filename_sfcd: sfc_data.nc
  filename_sfcw: fv_srf_wnd.res.nc
  filename_cplr: coupler.res

output:
  states:
  - datadir: analysis/mean/mem%{member}%
    datetime: *date_bgn
    filename: bgn.%{member}%
    filetype: auxgrid
    gridtype: gaussian
  - datadir: analysis/mean/mem%{member}%
    datetime: *date_mid
    filename: mid.%{member}%
    filetype: auxgrid
    gridtype: gaussian
  - datadir: analysis/mean/mem%{member}%
    datetime: *date_end
    filename: end.%{member}%
    filetype: auxgrid
    gridtype: gaussian

output increment:
  filetype: auxgrid
  gridtype: gaussian
  filename: analysis/increment/xainc.

# Observing system
# ----------------
observations:
  observers:
  - !INC sondes.yaml
  - !INC amsua_n19.yaml
