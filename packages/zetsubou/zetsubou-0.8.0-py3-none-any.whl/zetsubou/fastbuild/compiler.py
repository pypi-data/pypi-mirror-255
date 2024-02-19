from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Compiler:
    Executable : str
    ExtraFiles : List[str] = field(default_factory=list)

    CompilerFamily : str = 'auto'
    AllowDistribution : bool = True
    ExecutableRootPath : Optional[str] = None
    SimpleDistributionMode : Optional[bool] = None
    CustomEnvironmentVariables : Optional[List[str]] = field(default_factory=list)
    ClangRewriteIncludes : Optional[bool] = None
    ClangGCCUpdateXLanguageArg : Optional[bool] = None
    VS2012EnumBugFix : Optional[bool] = None
    Environment : Optional[List[str]] = field(default_factory=list)
    AllowResponseFile : Optional[bool] = None
    ForceResponseFile : Optional[bool] = None

    UseLightCache_Experimental : Optional[bool] = None
    UseRelativePaths_Experimental : Optional[bool] = None
    SourceMapping_Experimental : Optional[bool] = None
    ClangFixupUnity_Disable : Optional[bool] = None

    @staticmethod
    def keyword() -> str:
        return "Compiler"
