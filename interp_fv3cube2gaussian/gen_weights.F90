!--------------------------------------------------------------------
PROGRAM gen_weights

   use namelist_module
   use tile_module
   use latlon_module
   use gaussian_module
   use fv_grid_utils_module

  !use mpi

   IMPLICIT NONE

   include 'mpif.h'

   type tiletype
      type(tilegrid), dimension(6) :: tile
   end type tiletype

   type(tilespec_type), dimension(6)    :: spec
   type(tiletype), dimension(max_types) :: types
   type(latlongrid)                     :: latlon
   type(gaussiangrid)                   :: gaussian
   type(fv_grid_type), dimension(6)     :: gridstruct

   integer :: i, n, nm
   logical :: last
   integer :: num_procs, myrank, ierr

   call read_namelist('input.nml')

   if(num_types < 1) then
      print *, 'num_types must great than 0. eg. must have at least 1 type.'
      stop 111
   end if

   print *, 'File: ', __FILE__, ', line: ', __LINE__

   if(use_gaussian_grid) then
      call initialize_gaussiangrid(gaussian_grid_file, &
                                   nlon, nlat, nlev, nilev, npnt, gaussian)
   else
      call initialize_latlongrid(nlon, nlat, npnt, latlon)
      print *, 'File: ', __FILE__, ', line: ', __LINE__
      print *, 'latlon%nlev: ', latlon%nlev, ', latlon%nlay: ', latlon%nlay
   end if

   call initialize_tilegrid(types(1)%tile, trim(griddirname), data_types(1))

   print *, 'File: ', __FILE__, ', line: ', __LINE__
   print *, 'generate_weights = ', generate_weights

   print *, 'File: ', __FILE__, ', line: ', __LINE__
   print *, 'use_gaussian_grid = ', use_gaussian_grid
   if(use_gaussian_grid) then
      call generate_weight4gaussian(types(1)%tile, gaussian)
      call write_gaussiangrid(gaussian, wgt_flnm)
   else
      call generate_weight(types(1)%tile, latlon)
      call write_latlongrid(latlon, wgt_flnm)
   end if

   print *, 'File: ', __FILE__, ', line: ', __LINE__

   do n = 1, num_types
      call finalize_tilegrid(types(n)%tile)
   end do

   print *, 'File: ', __FILE__, ', line: ', __LINE__

   if(use_gaussian_grid) then
      call finalize_gaussiangrid(gaussian)
   else
      call finalize_latlongrid(latlon)
   end if

   print *, 'File: ', __FILE__, ', line: ', __LINE__

END PROGRAM gen_weights

