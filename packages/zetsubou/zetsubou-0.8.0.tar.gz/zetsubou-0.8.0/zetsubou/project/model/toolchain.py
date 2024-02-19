from dataclasses import dataclass, fields
from typing import List, Optional
from abc import ABC, abstractmethod

from zetsubou.project.model.kind import ETargetKind
from zetsubou.project.model.toolchain_enums import ECompilerFamily, ELibrarianFamily, ELinkerFamily, ECppStandard
from zetsubou.project.model.toolchain_profile import IToolchainProfile
from zetsubou.utils.common import Version, filename_no_ext, fix_path


class ICompiler(ABC):
    @abstractmethod
    def output(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def cpp_to_str(cpp:ECppStandard) -> Optional[str]:
        pass

    @abstractmethod
    def cppstd(self, cpp:ECppStandard) -> str:
        pass

    @abstractmethod
    def include(self, value:str) -> str:
        pass

    @abstractmethod
    def system_include(self, value:str) -> str:
        pass

    @abstractmethod
    def define(self, value:str) -> str:
        pass


class ClangCompiler(ICompiler):
    def output(self) -> str:
        return '-o"%2" "%1" -c '

    @staticmethod
    def cpp_to_str(cpp:ECppStandard) -> Optional[str]:
        return {
            ECppStandard.cpp11  : 'c++11',
            ECppStandard.cpp14  : 'c++14',
            ECppStandard.cpp17  : 'c++17',
            ECppStandard.cpp20  : 'c++20',
            ECppStandard.cpp23  : 'c++2b',
            ECppStandard.latest : 'c++2b',
        }.get(cpp, None)

    def cppstd(self, cpp: ECppStandard) -> str:
        return f"-std={ClangCLCompiler.cpp_to_str(cpp)}"

    def include(self, value:str) -> str:
        return f"-I\"{fix_path(value)}\""

    def system_include(self, value: str) -> str:
        return f"-isystem\"{fix_path(value)}\""

    def define(self, value:str) -> str:
        return f"-D{value}"


class MSVCCompiler(ICompiler):
    def output(self) -> str:
        return '/c "%1" /Fo"%2" /experimental:external '

    @staticmethod
    def cpp_to_str(cpp:ECppStandard) -> Optional[str]:
        return {
            ECppStandard.cpp14  : 'c++14',
            ECppStandard.cpp17  : 'c++17',
            ECppStandard.cpp20  : 'c++20',
            ECppStandard.latest : 'latest',
        }.get(cpp, None)

    def cppstd(self, cpp: ECppStandard) -> str:
        return f"/std:{MSVCCompiler.cpp_to_str(cpp)} "

    def include(self, value:str) -> str:
        return f"/I\"{value}\""

    def system_include(self, value:str) -> str:
        return f"/external:I\"{value}\""

    def define(self, value:str) -> str:
        return f"/D{value}"


class ClangCLCompiler(MSVCCompiler):
    pass


class GCCCompiler(ClangCompiler):
    pass


def _pick_by_filename(entries, executable):
    filename = filename_no_ext(executable)
    for entry in entries:
        if filename in entry[1]:
            return entry[0]
    return None


def guess_compiler_family(compiler:str) -> Optional[ECompilerFamily]:
    return _pick_by_filename([
        (ECompilerFamily.MSVC,     ['cl']),
        (ECompilerFamily.CLANG,    ['clang', 'clang++']),
        (ECompilerFamily.CLANG_CL, ['clang-cl']),
        (ECompilerFamily.GCC,      ['gcc', 'g++']),
    ], compiler)


def get_compiler_by_family(family:ECompilerFamily) -> ICompiler:
    return {
        ECompilerFamily.MSVC : MSVCCompiler(),
        ECompilerFamily.CLANG : ClangCompiler(),
        ECompilerFamily.CLANG_CL : ClangCLCompiler(),
        ECompilerFamily.GCC : GCCCompiler(),
    }.get(family)


class ILibrarian(ABC):
    @abstractmethod
    def output(self) -> str:
        pass


class MSVC_Librarian(ILibrarian):
    def output(self) -> str:
        return '/OUT:"%2" "%1" '


class LLVM_Librarian(ILibrarian):
    def output(self) -> str:
        return 'rc "%2" "%1" '


class GCC_Librarian(LLVM_Librarian):
    pass


def guess_librarian_family(librarian:str) -> Optional[ELibrarianFamily]:
    return _pick_by_filename([
        (ELibrarianFamily.MSVC, ['lib']),
        (ELibrarianFamily.LLVM, ['llvm-ar']),
        (ELibrarianFamily.GCC,  ['ar']),
    ], librarian)


def get_librarian_by_family(family:ELibrarianFamily) -> ILibrarian:
    return {
        ELibrarianFamily.MSVC : MSVC_Librarian(),
        ELibrarianFamily.LLVM : LLVM_Librarian(),
        ELibrarianFamily.GCC : GCC_Librarian(),
    }.get(family)


class ILinker(ABC):
    @abstractmethod
    def output(self) -> str:
        pass

    @abstractmethod
    def target(self, target_kind: ETargetKind) -> str:
        pass

    @abstractmethod
    def link(self, value:str) -> str:
        pass

    @abstractmethod
    def dir(self, value:str) -> str:
        pass


class LINK_Linker(ILinker):
    def output(self) -> str:
        return '/OUT:"%2" "%1" '

    def target(self, target_kind: ETargetKind) -> str:
        if target_kind == ETargetKind.DYNAMIC_LIBRARY:
            return '/DLL '
        return ''

    def link(self, value: str) -> str:
        return value

    def dir(self, value: str) -> str:
        return f"/LIBPATH:\"{value}\""


class LD_Linker(ILinker):
    def output(self) -> str:
        return '"%1" -o "%2" '

    def target(self, target_kind: ETargetKind) -> str:
        if target_kind == ETargetKind.DYNAMIC_LIBRARY:
            return '--shared '
        return ''

    def link(self, value: str) -> str:
        return f"-l\"{value}\""

    def dir(self, value: str) -> str:
        return f"-L\"{fix_path(value)}\""


class LLD_LINK_Linker(LINK_Linker):
    pass


class LD_LLD_Linker(LD_Linker):
    pass


def guess_linker_family(linker:str) -> Optional[ELinkerFamily]:
    return _pick_by_filename([
        (ELinkerFamily.LINK,     ['link']),
        (ELinkerFamily.LLD_LINK, ['lld-link']),
        (ELinkerFamily.LD_LLD,   ['ld-lld']),
        (ELinkerFamily.LD,       ['ld']),
    ], linker)


def get_linker_by_family(family: ELinkerFamily) -> ILinker:
    return {
        ELinkerFamily.LINK : LINK_Linker(),
        ELinkerFamily.LLD_LINK : LLD_LINK_Linker(),
        ELinkerFamily.LD_LLD : LD_LLD_Linker(),
        ELinkerFamily.LD : LD_Linker(),
    }.get(family)


@dataclass
class ToolchainDefinition:
    name: str
    version : Version
    ide_version : Version
    vs_install_path : str
    arch : str

    i_compiler : ICompiler
    i_librarian : ILibrarian
    i_linker : ILinker

    # Toolset
    Toolset : List[str]

    # Directories added to PATH
    PathEnv: List[str]

    # Default include directories
    IncludeDirectories: List[str]

    # Additonal files copied with exe during distributed compilation
    RequiredFiles: List[str]

    # (optional) Additional files (usually dlls) required by the compiler.
    ExtraFiles: List[str]

    # Default defines
    Defines: List[str]



    # Compiler executable
    Compiler: str

    # Compiler flags
    CompilerOptions : str

    # Compiler family
    CompilerFamily: ECompilerFamily



    # Linker executable
    Linker: str

    # Linker family
    LinkerFamily : ELinkerFamily

    # Linker flags
    LinkerOptions : str

    # Paths with library files
    LinkerPaths : str



    # Librarian executable
    Librarian: str

    # Librarian family
    LibrarianFamily : ELibrarianFamily

    # Librarian flags
    LibrarianOptions : str



    @staticmethod
    def create(name:str, compiler_exe:str, librarian_exe:str, linker_exe:str,
     *, CompilerOptions: str = '', LibrarianOptions: str = '', LinkerOptions: str = '', **kwargs) -> Optional['ToolchainDefinition']:

        compiler_family = guess_compiler_family(compiler_exe)
        librarian_family = guess_librarian_family(librarian_exe)
        linker_family = guess_linker_family(linker_exe)

        i_compiler = get_compiler_by_family(compiler_family)
        i_librarian = get_librarian_by_family(librarian_family)
        i_linker = get_linker_by_family(linker_family)

        return ToolchainDefinition(
            name=name,

            i_compiler=i_compiler,
            Compiler=compiler_exe,
            CompilerFamily=compiler_family,
            CompilerOptions=i_compiler.output() + CompilerOptions,

            i_librarian=i_librarian,
            Librarian=librarian_exe,
            LibrarianFamily=librarian_family,
            LibrarianOptions=i_librarian.output() + LibrarianOptions,

            i_linker=i_linker,
            Linker=linker_exe,
            LinkerFamily=linker_family,
            LinkerOptions=i_linker.output() + LinkerOptions,

            **{ name : value for name, value in kwargs.items() }
        )

    def __hash__(self):
        return hash(self.name)

    def get_hidden_fields(self) -> List[str]:
        result = []
        for field in fields(ToolchainDefinition):
            if field.name.islower():
                result.append(field.name)
        return result


# The actual toolchain that can be used
@dataclass
class Toolchain:
    name: str
    profile: IToolchainProfile
    definition: ToolchainDefinition
    toolset: str

    def __hash__(self):
        return hash(self.name)
