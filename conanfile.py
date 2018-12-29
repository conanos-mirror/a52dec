from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os, shutil

class A52decConan(ConanFile):
    name = "a52dec"
    version = "0.7.4"
    description = "liba52 is a free library for decoding ATSC A/52 streams"
    url = "https://github.com/conanos/a52dec"
    homepage = "http://liba52.sourceforge.net/"
    license = "GPL-v2"
    win_projs = ["a52dec.sln","a52dec.vcxproj","liba52.vcxproj","libao.vcxproj"]
    exports = ["COPYING","liba52.def","shared/*"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url = 'http://liba52.sourceforge.net/files/{name}-{version}.tar.gz'
        tools.get(url.format(name =self.name, version =self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename( extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            shutil.copy2(os.path.join(self.source_folder,"liba52.def"), os.path.join(self.source_folder,self._source_subfolder,"vc++","liba52.def"))
            sln_folder = "shared" if self.options.shared else "static"
            for i in self.win_projs:
                shutil.copy2(os.path.join(self.source_folder,sln_folder,i), os.path.join(self.source_folder,self._source_subfolder,"vc++",i))

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({'LIBS' : "-lm"}):
        #        self.run("autoreconf -f -i")

        #        _args = ["--prefix=%s/builddir"%(os.getcwd()), "--with-pic", "--disable-silent-rules", "--enable-introspection"]
        #        if self.options.shared:
        #            _args.extend(['--enable-shared=yes','--enable-static=no'])
        #        else:
        #            _args.extend(['--enable-shared=no','--enable-static=yes'])

        #        autotools = AutoToolsBuildEnvironment(self)
        #        autotools.fpic = True
        #        autotools.configure(args=_args)
        #        autotools.make(args=["-j4"])
        #        autotools.install()
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"vc++")):
                msbuild = MSBuild(self)
                msbuild.build("a52dec.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})

    def package(self):
        if self.settings.os == 'Windows':
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join("vc++",platforms.get(str(self.settings.arch)),str(self.settings.build_type))
            self.copy("liba52.dll", dst=os.path.join(self.package_folder,"bin"),
                      src=os.path.join(self.build_folder,self._source_subfolder,output_rpath))
            self.copy("a52dec.exe", dst=os.path.join(self.package_folder,"bin"),
                      src=os.path.join(self.build_folder,self._source_subfolder,"vc++","Debug"))
            tools.mkdir(os.path.join(self.package_folder,"lib"))
            for suffix in [".lib",".exp",".ilk",".pdb"]:
                shutil.copy(os.path.join(self.build_folder,self._source_subfolder,output_rpath,"liba52"+suffix),
                            os.path.join(self.package_folder,"lib","a52"+suffix))
        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

