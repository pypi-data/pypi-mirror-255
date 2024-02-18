#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "cpp-logger" for configuration "RelWithDebInfo"
set_property(TARGET cpp-logger APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(cpp-logger PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.7/dlio_profiler/lib/libcpp-logger.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libcpp-logger.so"
  )

list(APPEND _cmake_import_check_targets cpp-logger )
list(APPEND _cmake_import_check_files_for_cpp-logger "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.7/dlio_profiler/lib/libcpp-logger.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
