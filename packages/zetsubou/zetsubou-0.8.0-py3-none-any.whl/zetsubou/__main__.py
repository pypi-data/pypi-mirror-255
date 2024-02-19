from sys import exit as sys_exit
from sys import argv as sys_argv
from typing import Callable, List, Optional
from .zetsubou import main as zet_main


# class ProfileScope:
#     scalene = None

#     def __init__(self, argv:List[str]):
#         profile_arg = '--profile'
#         if profile_arg in argv:
#             argv.remove(profile_arg)
#             from scalene import scalene_profiler
#             self.scalene = scalene_profiler.Scalene
            

#     def __enter__(self):
#         if self.scalene is not None:
#             #self.scalene.clear_mmap_data()
#             self.scalene.__stats.start_clock()
#             self.scalene.enable_signals()

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.scalene is not None:
#             self.scalene.disable_signals()
#             self.scalene.__stats.stop_clock()


# with ProfileScope(sys_argv[1:]):

sys_exit(zet_main(sys_argv[1:]))
