#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "casadi-kin-dyn::casadi-kin-dyn" for configuration "Release"
set_property(TARGET casadi-kin-dyn::casadi-kin-dyn APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(casadi-kin-dyn::casadi-kin-dyn PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libcasadi-kin-dyn.so.1.6.11"
  IMPORTED_SONAME_RELEASE "libcasadi-kin-dyn.so.1.6.11"
  )

list(APPEND _cmake_import_check_targets casadi-kin-dyn::casadi-kin-dyn )
list(APPEND _cmake_import_check_files_for_casadi-kin-dyn::casadi-kin-dyn "${_IMPORT_PREFIX}/lib/libcasadi-kin-dyn.so.1.6.11" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
