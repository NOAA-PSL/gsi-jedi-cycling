!--------------------------------------------------------------------
PROGRAM single_fv3interp

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
   character(len=1024)                  :: outfullname

   integer :: i, n, nm
   logical :: last

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
   end if

   do n = 1, num_types
      if(1 == nm) then
         do i = 1, 6
            types(n)%tile(i)%initialized = .false.
         end do
      end if

      call initialize_tilegrid(types(n)%tile, trim(indirname), trim(data_types(n)))

      if(trim(data_types(n)) == 'fv_core.res.tile') then
         latlon%nlev = types(n)%tile(1)%nz
      else if(trim(data_types(n)) == 'sfc_data.tile') then
         latlon%nlay = types(n)%tile(1)%nz
      end if
   end do

   print *, 'File: ', __FILE__, ', line: ', __LINE__

   print *, 'File: ', __FILE__, ', line: ', __LINE__
   print *, 'wgt_flnm: ', trim(wgt_flnm)

   if(use_gaussian_grid) then
      call read_weights4gaussian(gaussian, wgt_flnm)
   else
      call read_weights(latlon, wgt_flnm)
   end if

  !print *, 'File: ', __FILE__, ', line: ', __LINE__
  !print *, 'num_types: ', num_types

   do n = 1, num_types
      last = (n == num_types)
     !print *, 'n = ', n
     !print *, 'last = ', last
      
      write(outfullname, fmt='(3a)') trim(outdirname), '/', trim(output_flnm)
      if(use_gaussian_grid) then
         call generate_header4gaussian(n, types(n)%tile, gaussian, &
                                 trim(data_types(n)), outfullname, last)
         call interp2gaussiangrid(trim(data_types(n)), spec, gridstruct, &
                                  types(n)%tile, gaussian)
      else
         call generate_header(n, types(n)%tile, latlon, &
                              trim(data_types(n)), output_flnm, last)
         call interp2latlongrid(trim(data_types(n)), spec, gridstruct, &
                                types(n)%tile, latlon)
      end if
   end do

   print *, 'File: ', __FILE__, ', line: ', __LINE__

!  do n = 1, 6
!     call grid_utils_exit(gridstruct(n))
!  end do

  !print *, 'File: ', __FILE__, ', line: ', __LINE__

   do n = 1, num_types
      call finalize_tilegrid(types(n)%tile)
   end do

  !print *, 'File: ', __FILE__, ', line: ', __LINE__

   if(use_gaussian_grid) then
      call finalize_gaussiangrid(gaussian)
   else
      call finalize_latlongrid(latlon)
   end if

   print *, 'File: ', __FILE__, ', line: ', __LINE__

END PROGRAM single_fv3interp

