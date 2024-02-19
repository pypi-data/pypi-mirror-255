from typing import List, Optional


class BaseTarget:
    Alias : str

    @staticmethod
    def keyword() -> str:
        return NotImplementedError()


class LinkableTarget(BaseTarget):

    # Linker executable to use
    Linker : str
    # Output from linker
    LinkerOutput : str
    # Options to pass to linker
    LinkerOptions : str
    # Libraries to link into DLL
    Libraries : List[str]
    # Secondary libraries to link into executable
    Libraries2 : List[str]
    # (optional) Link objects used to make libs instead of libs (default true)
    LinkerLinkObjects : Optional[str]
    # (optional) List of assembly resources to use with %3
    LinkerAssemblyResources : Optional[str]

    # (optional) Executable to run post-link to "stamp" executable in-place
    LinkerStampExe : Optional[str]
    # (optional) Arguments to pass to LinkerStampExe
    LinkerStampExeArgs : Optional[str]
    # (optional) Specify the linker type. Valid options include: 
    # auto, msvc, gcc, snc-ps3, clang-orbis, greenhills-exlr, codewarrior-ld
    # Default is 'auto' (use the linker executable name to detect)
    LinkerType : Optional[str]

    # (optional) Allow response files to be used if not auto-detected (default: false)
    LinkerAllowResponseFile : Optional[bool]
    # (optional) Force use of response files (default: false)
    LinkerForceResponseFile : Optional[bool]

    ###############################################
    # Additional options
    ###############################################

    # (optional) Force targets to be built before this DLL (Rarely needed,
    # but useful when DLL relies on externally generated files).
    PreBuildDependencies : List[str]
    # (optional) Environment variables to use for local build
    # If set, linker uses this environment
    # If not set, linker uses .Environment from your Settings node
    Environment: List[str]


class AppTarget(LinkableTarget):
    @staticmethod
    def keyword() -> str:
        return "Executable"


class DynLibTarget(LinkableTarget):
    @staticmethod
    def keyword() -> str:
        return "DLL"


class ObjTarget(BaseTarget):
    # (optional) Alias
    Alias : Optional[str]

    ###############################################
    # Options for compilation
    ###############################################

    # Compiler to use
    Compiler : str
    # Options for compiler
    CompilerOptions : str
    # Path to store intermediate objects
    CompilerOutputPath : str
    # (optional) Specify the file extension for generated objects (default .obj or .o)
    CompilerOutputExtension : Optional[str]
    # (optional) Append extension instead of replacing it (default: false)
    CompilerOutputKeepBaseExtension : Optional[bool]
    # (optional) Specify a prefix for generated objects (default none)
    CompilerOutputPrefix : Optional[str]

    ###############################################
    # Specify inputs for compilation
    ###############################################

    # (optional) Path to find files in
    CompilerInputPath : Optional[str]
    # (optional) Pattern(s) to use when finding files (default *.cpp)
    CompilerInputPattern : Optional[str]
    # (optional) Recurse into dirs when finding files (default true)
    CompilerInputPathRecurse : Optional[bool]
    # (optional) Path(s) to exclude from compilation
    CompilerInputExcludePath : Optional[str]
    # (optional) File(s) to exclude from compilation (partial, root-relative of full path)
    CompilerInputExcludedFiles : Optional[str]
    # (optional) Pattern(s) to exclude from compilation
    CompilerInputExcludePattern : Optional[str]
    # (optional) Explicit array of files to build
    CompilerInputFiles : Optional[List[str]]
    # (optional) Root path to use for .obj path generation for explicitly listed files
    CompilerInputFilesRoot : Optional[str]
    # (optional) Unity to build (or Unities)
    CompilerInputUnity : Optional[str]
    # (optional) Don't fail if no inputs are found
    CompilerInputAllowNoFiles : Optional[bool]
    # (optional) ObjectList(s) whos output should be used as an input
    CompilerInputObjectLists : Optional[str]

    # (optional) Allow caching of compiled objects if available (default true)
    AllowCaching : Optional[bool]
    # (optional) Allow distributed compilation if available (default true)
    AllowDistribution : Optional[bool]

    # (optional) Compiler to use for preprocessing
    Preprocessor : Optional[str]
    # (optional) Args to pass to compiler if using custom preprocessor
    PreprocessorOptions : Optional[str]

    # (optional) List of objects to be used with /FU
    CompilerForceUsing : Optional[str]

    ###############################################
    # (optional) Properties to control precompiled header use
    ###############################################

    # (optional) Precompiled header (.cpp) file to compile
    PCHInputFile : Optional[str]
    # (optional) Precompiled header compilation output
    PCHOutputFile : Optional[str]
    # (optional) Options for compiler for precompiled header
    PCHOptions : Optional[str]

    ###############################################
    # Additional options
    ###############################################

    # (optional) Force targets to be built before this library (Rarely needed,
    # but useful when a library relies on generated code).
    PreBuildDependencies : Optional[str]

    # (optional) Hide a target from -showtargets (default false)
    Hidden : Optional[bool]

    @staticmethod
    def keyword() -> str:
        return "ObjectList"


class StaticLibTarget(BaseTarget):

    ###############################################
    # Options for compilation
    ###############################################
    # Compiler to use
    Compiler : str
    # Options for compiler
    CompilerOptions : str
    # Path to store intermediate objects
    CompilerOutputPath : str
    # (optional) Specify the file extension for generated objects (default .obj or .o)
    CompilerOutputExtension : Optional[str]
    # (optional) Specify a prefix for generated objects (default none)
    CompilerOutputPrefix : Optional[str]

    ###############################################
    # Options for librarian
    ###############################################

    # Librarian to collect intermediate objects
    Librarian : str

    # Options for librarian
    LibrarianOptions : str

    # (optional) Specify the librarian type. Valid options include:
    # auto, msvc, ar, ar-orbis, greenhills-ax
    # Default is 'auto' (use the librarian executable name to detect)
    LibrarianType : Optional[str]

    # Output path for lib file
    LibrarianOutput : str

    # (optional) Additional inputs to merge into library
    LibrarianAdditionalInputs : Optional[str]

    # (optional) Allow response files to be used if not auto-detected (default: false)  
    LibrarianAllowResponseFile : Optional[bool]

    # (optional) Force use of response files (default: false)
    LibrarianForceResponseFile : Optional[bool]

    ###############################################
    # Specify inputs for compilation
    ###############################################
    # (optional) Path to find files in
    CompilerInputPath : Optional[str]

    # (optional) Pattern(s) to use when finding files (default *.cpp)
    CompilerInputPattern : Optional[List[str]]
    # (optional) Recurse into dirs when finding files (default true)
    CompilerInputPathRecurse : Optional[bool]
    # (optional) Path(s) to exclude from compilation
    CompilerInputExcludePath : Optional[List[str]]
    # (optional) File(s) to exclude from compilation (partial, root-relative of full path)
    CompilerInputExcludedFiles : Optional[List[str]]
    # (optional) Pattern(s) to exclude from compilation
    CompilerInputExcludePattern : Optional[List[str]]
    # (optional) Explicit array of files to build
    CompilerInputFiles : Optional[List[str]]
    # (optional) Root path to use for .obj path generation for explicitly listed files
    CompilerInputFilesRoot : Optional[str]
    # (optional) Unity to build (or Unities)
    CompilerInputUnity : Optional[List[str]] 
    # (optional) ObjectList(s) whos output should be used as an input
    CompilerInputObjectLists : Optional[List[str]] 

    ###############################################
    # Cache & Distributed compilation control
    ###############################################
    # (optional) Allow caching of compiled objects if available (default true)
    AllowCaching : Optional[bool]
    # (optional) Allow distributed compilation if available (default true)
    AllowDistribution : Optional[bool]

    ###############################################
    # Custom preprocessor support
    ###############################################

    # (optional) Compiler to use for preprocessing
    Preprocessor : Optional[str]
    # (optional) Args to pass to compiler if using custom preprocessor
    PreprocessorOptions : Optional[str]

    ###############################################
    # Additional compiler options
    ###############################################
    # (optional) List of objects to be used with /FU
    CompilerForceUsing : Optional[List[str]]

    ###############################################
    # (optional) Properties to control precompiled header use
    ###############################################

    # (optional) Precompiled header (.cpp) file to compile
    PCHInputFile : Optional[str]
    # (optional) Precompiled header compilation output
    PCHOutputFile : Optional[str]
    # (optional) Options for compiler for precompiled header
    PCHOptions : Optional[str]

    ###############################################
    # Additional options
    ###############################################

    # (optional) Force targets to be built before this library (Rarely needed,
    # but useful when a library relies on generated code).
    PreBuildDependencies : Optional[List[str]]

    # (optional) Environment variables to use for local build
    # If set, librarian uses this environment
    # If not set, librarian uses .Environment from your Settings node
    Environment : Optional[List[str]]

    # (optional) Hide a target from -showtargets (default false)
    Hidden : Optional[bool]

    @staticmethod
    def keyword() -> str:
        return "Library"
