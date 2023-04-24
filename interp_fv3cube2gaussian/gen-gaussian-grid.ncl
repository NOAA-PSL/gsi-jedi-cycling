 in_file = "gaussian_grid_C96.nc4"
 inf = addfile( in_file, "r" )

 lat = inf->lat
 lon = inf->lon
 lev = inf->lev
 ilev = inf->ilev
 hyai = inf->hyai
 hybi = inf->hybi

;nlat = 192
;nlon = 384
 nlat = 384
 nlon = 768
 nlev = 127
 plev = 128

 out_file = "gaussian_grid_C192.nc4"
;create output netcdf file
 system( "/bin/rm -f " + out_file )
 outf = addfile( out_file, "c" )
 setfileoption ( outf, "DefineMode", True )

;define file global attributes
 globalAtt = True
 globalAtt@creation_date = systemfunc ( "date" )        
 globalAtt@comments = "Created Gaussian C192 lat-lon grid"
 fileattdef( outf, globalAtt )

;predefine the coordinate variables and their dimensionality
;note: to get an UNLIMITED record dimension, set the dimensionality
;to -1 and set the unlimited array to True.
 dimNames = (/"lon", "lat", "lev", "ilev" /)  
 dimSizes = (/nlon,  nlat,  nlev,  plev/) 
 dimUnlim = (/ False , False, False, False /)   
 filedimdef( outf, dimNames, dimSizes, dimUnlim )

;predefine the dimensionality of the variables, names and types
 filevardef( outf, "lon", typeof(lon) , getvardims(lon))
 filevardef( outf, "lat", typeof(lat) , getvardims(lat))
 filevardef( outf, "lev", typeof(lev) , getvardims(lev))
 filevardef( outf, "ilev", typeof(ilev) , getvardims(ilev))
 filevardef( outf, "hyai", typeof(hyai) , getvardims(hyai))
 filevardef( outf, "hybi", typeof(hybi) , getvardims(hybi))
 
 lev@units = "half-grid level numbers"
 ilev@units = "full-grid level numbers"
 hyai@units = "Pa"
 hybi@units = "1"

;create variable attributes  	
 filevarattdef( outf, "lon", lon )
 filevarattdef( outf, "lat", lat )
 filevarattdef( outf, "lev", lev )
 filevarattdef( outf, "ilev", ilev )
 filevarattdef( outf, "hyai", hyai )
 filevarattdef( outf, "hybi", hybi )

 setfileoption ( outf, "DefineMode", False )

;
 gau_info = gaus(nlat/2)   ; divide by 2 to get "per hemisphere"
 glat     = gau_info(:,0)  ; gaussian latitudes ( 1st dimension of gau_info)
 gwgt     = gau_info(:,1)  ; gaussian weights   ( 2nd dimension of gau_info) 

 glon = new((/nlon/), float)
 dlon = 360.0/nlon
 do n = 0, nlon-1
   glon(n) = n*dlon
 end do

 flat = tofloat(glat)

 print(glat)
 print(glon)

 outf->lon = (/glon/)
 outf->lat = (/flat/)
 outf->lev = (/lev/)
 outf->ilev = (/ilev/)
 outf->hyai = (/hyai/)
 outf->hybi = (/hybi/)

 print( "out file : " + out_file )

