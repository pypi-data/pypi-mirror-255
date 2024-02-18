set(BRAHMA_FOUND TRUE)

# Include directories
set(BRAHMA_INCLUDE_DIRS "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-cpython-310/dlio_profiler/include")
if (NOT IS_DIRECTORY "${BRAHMA_INCLUDE_DIRS}")
    set(BRAHMA_FOUND FALSE)
endif ()
get_filename_component(BRAHMA_ROOT_DIR ${BRAHMA_INCLUDE_DIRS}/.. ABSOLUTE)
set(BRAHMA_LIBRARY_PATH "/home/runner/work/dlio-profiler/dlio-profiler/build/lib.linux-x86_64-cpython-310/dlio_profiler/lib")
link_directories(${BRAHMA_LIBRARY_PATH})
set(BRAHMA_LIBRARIES brahma)
set(BRAHMA_DEFINITIONS "")
if (NOT TARGET brahma)
  include(${CMAKE_CURRENT_LIST_DIR}/brahma-targets.cmake)
endif()
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(brahma
            REQUIRED_VARS BRAHMA_FOUND BRAHMA_INCLUDE_DIRS BRAHMA_LIBRARIES)
