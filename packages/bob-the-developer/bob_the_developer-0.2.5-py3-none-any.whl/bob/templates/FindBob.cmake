include(FetchContent)

FetchContent_Declare(
  bob-cmake
  GIT_REPOSITORY https://github.com/renemoll/bob-cmake.git
  GIT_TAG        origin/main
  GIT_SHALLOW    true
  SOURCE_DIR     ${CMAKE_BINARY_DIR}/bob-cmake
)

FetchContent_MakeAvailable(bob-cmake)

list(PREPEND CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}/bob-cmake")

#
# Todo: fetch a specific version
#
# FetchContent_Declare(
#   bob-cmake
#   URL https://github.com/renemoll/bob-cmake/archive/refs/tags/0.0.1.tar.gz
# )
# 