from typing import List, Optional
from dataclasses import dataclass


class AdditionalSolutionOptions:
    # (optional) Project(s) set to build when "Build Solution" is selected
    SolutionBuildProject   : Optional[List[str]]
    # (optional) Project(s) set deploy
    SolutionDeployProjects : Optional[List[str]]

@dataclass
class SolutionConfigs(AdditionalSolutionOptions):
    # Platform(s) (default "Win32", "x64")
    Platform : str
    # Config(s) (default "Debug", "Release")
    Config : List[str]
    # (optional) Solution Config
    SolutionConfig : Optional[str]
    # (optional) Solution Platform
    SolutionPlatform : Optional[str]

@dataclass
class SolutionFolders:
    # Folder path in Solution
    Path : str
    # (optional) Project(s) to include in this folder
    Projects : Optional[List[str]]
    # (optional) Solution Item(s) (files) to include in this folder
    Items : Optional[List[str]]

@dataclass
class SolutionDependencies:
    # Project(s) to specify dependencies for
    Projects : List[str]
    # Project(s) the above projects depend on
    Dependencies : List[str]


class VSSolution(AdditionalSolutionOptions):
    # (optional) Alias
    Alias : Optional[str]

    ###############################################
    # Basic options
    ###############################################

    # Path to Solution file to be generated
    SolutionOutput : str
    # (optional) Project(s) to include in Solution
    SolutionProjects : Optional[List[str]]
    # (optional) Solution configurations (see below)
    SolutionConfigs : Optional[List[SolutionConfigs]]

    ###############################################
    # Folders
    ###############################################

    # (optional) Folders to organize projects (see below)
    SolutionFolders : Optional[List[SolutionFolders]]

    ###############################################
    # Advanced options
    ###############################################

    # (optional) Project dependency information (see above)
    SolutionDependencies : Optional[List[SolutionDependencies]]

    ###############################################
    # Version Info  
    ###############################################

    # (optional) Version of Solution (default "14.0.22823.1" VS2015 RC)
    SolutionVisualStudioVersion : Optional[str]
    # (optional) Min version of Solution (default "10.0.40219.1" VS2010 Express)
    SolutionMinimumVisualStudioVersion : Optional[str]

    @staticmethod
    def keyword() -> str:
        return "VSSolution"
