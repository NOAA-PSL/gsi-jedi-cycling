correlated_observations::
! isis          method   kreq   kmult   type    cov_file
iasi_metop-c      2       0.0     1.0    sea     Rcov_iasicsea
iasi_metop-b      2       0.0     1.0    sea     Rcov_iasibsea
iasi_metop-c      2       0.0     1.0    land    Rcov_iasicland
iasi_metop-b      2       0.0     1.0    land    Rcov_iasibland
cris-fsr_n20      2       0.0     1.0    sea     Rcov_crisn20
cris-fsr_npp      2       0.0     1.0    sea     Rcov_crisnpp
::

met_guess::
!var     level    crtm_use    desc              orig_name
  ps        1      -1         surface_pressure     ps
  dpres   127      -1         pressure_thickness   dprse
  z         1      -1         geopotential_height  phis
  u       127       2         zonal_wind           u
  v       127       2         meridional_wind      v
  div     127      -1         zonal_wind           div
  vor     127      -1         meridional_wind      vor
  tv      127       2         virtual_temperature  tv
  q       127       2         specific_humidity    sphu
  oz      127       2         ozone                ozone
  cw      127      10         cloud_condensate     cw
  ql      127      12         cloud_liquid         ql 
  qi      127      12         cloud_ice            qi 
::

state_derivatives::
!var  level  src
 ps   1      met_guess
 u    127    met_guess
 v    127    met_guess
 tv   127    met_guess
 q    127    met_guess
 oz   127    met_guess
 cw   127    met_guess
 prse 128    met_guess
 dprse 127   met_guess
::

state_tendencies::
!var  levels  source
 u    127     met_guess
 v    127     met_guess
 tv   127     met_guess
 q    127     met_guess
 cw   127     met_guess
 oz   127     met_guess
 prse 128     met_guess
 dprse 127    met_guess
::

state_vector::  
!var     level  itracer source     funcof
 u       127      0     met_guess    u
 v       127      0     met_guess    v
 tv      127      0     met_guess    tv
 tsen    127      0     met_guess    tv,q
 q       127      1     met_guess    q
 oz      127      1     met_guess    oz
 ql      127      1     met_guess    ql 
 qi      127      1     met_guess    qi 
 prse    128      0     met_guess    prse
 dpres   127      0     met_guess    prse   
 ps        1      0     met_guess    prse
 sst       1      0     met_guess    sst
::


state_vector_efsoi::
!var     level  itracer source     funcof
 u       127      0     met_guess    u
 v       127      0     met_guess    v
 tv      127      0     met_guess    tv
 q       127      1     met_guess    q
 dpres   127      0     met_guess    prse   
 ps        1      0     met_guess    prse
::



control_vector_enkf::
!var     level  itracer as/tsfc_sdv  an_amp0   source  funcof
 u       127      0       1.00        -1.0     state    u,v
 v       127      0       1.00        -1.0     state    u,v
!ps        1      0       1.20        -1.0     state    prse
!pst       1      0       1.20        -1.0     state    prse,u,v
 tv      127      0       1.50        -1.0     state    tv
 q       127      1       1.50        -1.0     state    q
 oz      127      1       2.00        -1.0     state    oz
 dpres   127      0       1.00        -1.0     state    prse
!sst       1      0       1.00        -1.0     state    sst
!cw      127      1       1.00        -1.0     state    cw
!stl       1      0       3.00        -1.0     motley   sst
!sti       1      0       3.00        -1.0     motley   sst
::

control_vector::
!var     level  itracer as/tsfc_sdv  an_amp0   source  funcof
 sf      127      0       1.00        -1.0     state    u,v
 vp      127      0       1.00        -1.0     state    u,v
 ps        1      0       1.20        -1.0     state    prse
 dpres   127      0       1.00        -1.0     state    prse
 t       127      0       1.50        -1.0     state    tv
 q       127      1       1.50        -1.0     state    q
 oz      127      1       2.00        -1.0     state    oz
 sst       1      0       1.00        -1.0     state    sst
 cw      127      1       1.00        -1.0     state    cw
 stl       1      0       3.00        -1.0     motley   sst
 sti       1      0       3.00        -1.0     motley   sst
::

! Following table shows the use of all four prescribed trace gas data.
! To turn off any one of any combination of trace gas input, add "!"
! in the first column of that trace gas name.  To use all default
! trace gas profiles, just delete the following seven lines.
chem_guess::
!var     level  itracer crtm_use       type    orig_name
!ch4      64      1       2             n/a    ch4
 co2     127      1       0             n/a    co2
!co       64      1       2             n/a    co
!n2o      64      1       2             n/a    n2o
::
