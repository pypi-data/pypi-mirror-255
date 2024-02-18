#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "brahma" for configuration "RelWithDebInfo"
set_property(TARGET brahma APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(brahma PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-cpython-310/dlio_profiler/lib/libbrahma.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libbrahma.so"
  )

list(APPEND _cmake_import_check_targets brahma )
list(APPEND _cmake_import_check_files_for_brahma "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-cpython-310/dlio_profiler/lib/libbrahma.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
