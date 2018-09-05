#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class ProtobufConan(ConanFile):
    name = "protobuf"
    version = "3.5.1"
    url = "https://github.com/bincrafters/conan-protobuf"
    homepage = "https://github.com/protocolbuffers/protobuf"
    author = "Bincrafters <bincrafters@gmail.com>"
    description = "Conan.io recipe for Google Protocol Buffers"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    settings = "os", "arch", "compiler", "build_type"
    short_paths=True
    options = {
        "shared": [True, False],
        "with_zlib": [True, False],
        "build_tests": [True, False],
        "build_binaries": [True, False],
        "static_rt": [True, False],
        "fPIC": [True, False],
    }
    default_options = (
        "with_zlib=False", "build_tests=False",
        "static_rt=True", "build_binaries=True",
        "shared=False", "fPIC=True")

    def configure(self):
        # Todo: re-enable shared builds when issue resolved
        if self.options.shared == True:
            raise ConanException("Shared builds not currently supported, see github issue: https://github.com/google/protobuf/issues/2502")
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11]@conan/stable")
        if self.options.build_tests:
            self.requires("gtest/[>=1.7.0]@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = "lib"
        cmake.definitions["protobuf_BUILD_TESTS"] = self.options.build_tests
        cmake.definitions["protobuf_BUILD_PROTOC_BINARIES"] = self.options.build_binaries
        cmake.definitions["protobuf_MSVC_STATIC_RUNTIME"] = self.options.static_rt
        cmake.definitions["protobuf_WITH_ZLIB"] = self.options.with_zlib
        # TODO: option 'shared' not enabled  cmake.definitions["protobuf_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()
        if self.options.build_tests:
            self.run("ctest")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")

            if self._is_clang_x86():
                self.cpp_info.libs.append("atomic")

        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines = ["PROTOBUF_USE_DLLS"]
