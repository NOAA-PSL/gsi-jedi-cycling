# Background/anaysis geometry
# ---------------------------
geometry:
  fms initialization:
    namelist filename: Data/fv3files/fmsmpp.nml
    field table filename: Data/fv3files/field_table
  akbk: Data/fv3files/akbk127.nc4
  layout:
  - !ENV ${observer_layout_x}
  - !ENV ${observer_layout_y}
  npx: $(npx_ges)
  npy: $(npy_ges)
  npz: $(npz_ges)
  field metadata override: Data/fieldmetadata/gfs-restart.yaml

#window begin: '$(ATM_WINDOW_BEGIN)'
#window length: $(ATM_WINDOW_LENGTH)

time window:
  begin: '2022-01-04T22:00:00Z'
  end: '2022-01-05T01:00:00Z'

#increment variables: [ua, va, t, DZ, delp, ice_wat, liq_wat, sphum, o3mr]

background:
  date: '2022-01-05T00:00:00Z'
  members from template:
    pattern: '%mem%'
    nmembers: 1
    zero padding: 3
    template:
      states:
      - datetime: DATE_BGN '2022-01-04T23:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010418/MEMSTR/RESTART
        filename_core: 20220104.230000.fv_core.res.nc
        filename_trcr: 20220104.230000.fv_tracer.res.nc
        filename_sfcd: 20220104.230000.sfc_data.nc
        filename_sfcw: 20220104.230000.fv_srf_wnd.res.nc
        filename_cplr: 20220104.230000.coupler.res
      - datetime: DATE_MID '2022-01-05T00:00:00Z'
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
      - datetime: DATE_END '2022-01-05T01:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010500/MEMSTR/RESTART
        filename_core: 20220105.010000.fv_core.res.nc
        filename_trcr: 20220105.010000.fv_tracer.res.nc
        filename_sfcd: 20220105.010000.sfc_data.nc
        filename_sfcw: 20220105.010000.fv_srf_wnd.res.nc
        filename_cplr: 20220105.010000.coupler.res

control member:
  date: '2022-01-05T00:00:00Z'
  members from template:
    pattern: '%mem%'
    nmembers: 1
    zero padding: 3
    template:
      states:
      - datetime: DATE_BGN '2022-01-04T23:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010418/mem000/RESTART
        filename_core: 20220104.230000.fv_core.res.nc
        filename_trcr: 20220104.230000.fv_tracer.res.nc
        filename_sfcd: 20220104.230000.sfc_data.nc
        filename_sfcw: 20220104.230000.fv_srf_wnd.res.nc
        filename_cplr: 20220104.230000.coupler.res
      - datetime: DATE_MID '2022-01-05T00:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: mem000/INPUT
        filename_core: fv_core.res.nc
        filename_trcr: fv_tracer.res.nc
        filename_sfcd: sfc_data.nc
        filename_sfcw: fv_srf_wnd.res.nc
        filename_cplr: coupler.res
      - datetime: DATE_END '2022-01-05T01:00:00Z'
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: /work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022010500/mem000/RESTART
        filename_core: 20220105.010000.fv_core.res.nc
        filename_trcr: 20220105.010000.fv_tracer.res.nc
        filename_sfcd: 20220105.010000.sfc_data.nc
        filename_sfcw: 20220105.010000.fv_srf_wnd.res.nc
        filename_cplr: 20220105.010000.coupler.res

driver:
  read HX from disk: false
  do posterior observer: false
 #do test prints: true
  do test prints: false
  save posterior mean: false
  save posterior ensemble: false
  save prior mean: false
  save posterior mean increment: false
  save posterior ensemble increments: false
  update obs config with geometry info: false
  run as observer only: true
  use control member: true

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
output:
  filetype: auxgrid
  gridtype: gaussian
  filename: analysis/mean/mean.

# Observing system
# ----------------
observations:
  observers:
  - !INC sondes.yaml
  - !INC amsua_n19.yaml
