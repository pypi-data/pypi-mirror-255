#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dlio_profiler" for configuration "Release"
set_property(TARGET dlio_profiler APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dlio_profiler PROPERTIES
  IMPORTED_LOCATION_RELEASE "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.8/dlio_profiler/lib/libdlio_profiler.so"
  IMPORTED_SONAME_RELEASE "libdlio_profiler.so"
  )

list(APPEND _cmake_import_check_targets dlio_profiler )
list(APPEND _cmake_import_check_files_for_dlio_profiler "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.8/dlio_profiler/lib/libdlio_profiler.so" )

# Import target "dlio_profiler_preload" for configuration "Release"
set_property(TARGET dlio_profiler_preload APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dlio_profiler_preload PROPERTIES
  IMPORTED_LOCATION_RELEASE "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.8/dlio_profiler/lib/libdlio_profiler_preload.so"
  IMPORTED_SONAME_RELEASE "libdlio_profiler_preload.so"
  )

list(APPEND _cmake_import_check_targets dlio_profiler_preload )
list(APPEND _cmake_import_check_files_for_dlio_profiler_preload "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-3.8/dlio_profiler/lib/libdlio_profiler_preload.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
