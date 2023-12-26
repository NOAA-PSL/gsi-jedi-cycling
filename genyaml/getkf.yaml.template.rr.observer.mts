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

time window:
  begin: '$(ATM_WINDOW_BEGIN)'
  end: $(ATM_WINDOW_END)

#increment variables: [ua, va, t, DZ, delp, ice_wat, liq_wat, sphum, o3mr]

background:
  date: $(ATM_WINDOW_CENTER)
  members from template:
    pattern: '%mem%'
    nmembers: 1
    zero padding: 3
    template:
      states:
      - AT_DATE_BGN: $(ATM_BGN_TIME)
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: $(BKGDIR)/MEMSTR/RESTART
        filename_core: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_core.res.nc
        filename_trcr: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_tracer.res.nc
        filename_sfcd: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.sfc_data.nc
        filename_sfcw: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_srf_wnd.res.nc
        filename_cplr: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.coupler.res
      - AT_DATE_MID: $(ATM_WINDOW_CENTER)
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
      - AT_DATE_END: $(ATM_END_TIME)
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: $(BKGDIR)/MEMSTR/RESTART
        filename_core: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_core.res.nc
        filename_trcr: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_tracer.res.nc
        filename_sfcd: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.sfc_data.nc
        filename_sfcw: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_srf_wnd.res.nc
        filename_cplr: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.coupler.res

control member:
  date: $(ATM_WINDOW_CENTER)
  members from template:
    pattern: '%mem%'
    nmembers: 1
    zero padding: 3
    template:
      states:
      - datetime: STAR_DATE_BGN
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: $(BKGDIR)/mem000/RESTART
        filename_core: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_core.res.nc
        filename_trcr: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_tracer.res.nc
        filename_sfcd: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.sfc_data.nc
        filename_sfcw: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.fv_srf_wnd.res.nc
        filename_cplr: $(ATM_BGN_YYYYMMDD).$(ATM_BGN_HH)0000.coupler.res
      - datetime: STAR_DATE_MID
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
      - datetime: STAR_DATE_END
        filetype: fms restart
        state variables: [ua,va,t,delp,DZ,sphum,ice_wat,liq_wat,o3mr,phis,
                          slmsk,sheleg,tsea,vtype,stype,vfrac,stc,smc,snwdph,
                          u_srf,v_srf,f10m]
        datapath: $(BKGDIR)/mem000/RESTART
        filename_core: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_core.res.nc
        filename_trcr: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_tracer.res.nc
        filename_sfcd: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.sfc_data.nc
        filename_sfcw: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.fv_srf_wnd.res.nc
        filename_cplr: $(ATM_END_YYYYMMDD).$(ATM_END_HH)0000.coupler.res

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
  states:
  - datadir: analysis/mean/mem%{member}%
    datetime: STAR_DATE_BGN
    filename: bgn.%{member}%
    filetype: auxgrid
    gridtype: gaussian
  - datadir: analysis/mean/mem%{member}%
    datetime: STAR_DATE_MID
    filename: mid.%{member}%
    filetype: auxgrid
    gridtype: gaussian
  - datadir: analysis/mean/mem%{member}%
    datetime: STAR_DATE_END
    filename: end.%{member}%
    filetype: auxgrid
    gridtype: gaussian

# Observing system
# ----------------
observations:
  observers:
  - !INC sondes.yaml
  - !INC amsua_n19.yaml
