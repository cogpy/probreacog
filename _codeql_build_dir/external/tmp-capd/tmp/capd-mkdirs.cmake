# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/src")
  file(MAKE_DIRECTORY "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/src")
endif()
file(MAKE_DIRECTORY
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/src/capd-build"
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/capd"
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/tmp"
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/capd-stamp"
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/download"
  "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/capd-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/capd-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/runner/work/probreacog/probreacog/_codeql_build_dir/external/tmp-capd/capd-stamp${cfgdir}") # cfgdir has leading slash
endif()
