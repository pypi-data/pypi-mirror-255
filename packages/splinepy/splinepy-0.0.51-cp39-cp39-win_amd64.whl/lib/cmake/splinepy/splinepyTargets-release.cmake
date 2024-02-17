#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "splinepy::splinepy_python" for configuration "Release"
set_property(TARGET splinepy::splinepy_python APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(splinepy::splinepy_python PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/splinepy_python.lib"
  )

list(APPEND _cmake_import_check_targets splinepy::splinepy_python )
list(APPEND _cmake_import_check_files_for_splinepy::splinepy_python "${_IMPORT_PREFIX}/lib/splinepy_python.lib" )

# Import target "splinepy::splinepy" for configuration "Release"
set_property(TARGET splinepy::splinepy APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(splinepy::splinepy PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/splinepy.lib"
  )

list(APPEND _cmake_import_check_targets splinepy::splinepy )
list(APPEND _cmake_import_check_files_for_splinepy::splinepy "${_IMPORT_PREFIX}/lib/splinepy.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
