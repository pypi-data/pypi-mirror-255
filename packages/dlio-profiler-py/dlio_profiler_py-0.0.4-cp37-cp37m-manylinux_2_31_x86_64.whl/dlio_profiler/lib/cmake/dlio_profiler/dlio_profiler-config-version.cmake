#-----------------------------------------------------------------------------
# Version file for install directory
#-----------------------------------------------------------------------------
set(PACKAGE_VERSION 2.0.1)

if ("${PACKAGE_FIND_VERSION_MAJOR}" EQUAL 2)
    set(PACKAGE_VERSION_COMPATIBLE 1)
    if ("${PACKAGE_FIND_VERSION_PATCH}" EQUAL 1)
        set(PACKAGE_VERSION_EXACT 1)
    endif ()
endif ()
