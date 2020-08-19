.. to view each save, use Python restview -w PMUCal.rst PMUCal.rst

==============================
PMUCal Framework Documentation
==============================

Scripting and Running Tests
'''''''''''''''''''''''''''
When a single test is run (either by clicking the "One Test" button or via a Python Script, The SSM is sent a "RunTest" command and the list of modules i load order (Sync, Digitizer,FGen,Sensor,Analaysis).  The SSM then opens each of the loaded .ini files in order and builds a script out of the "Scriptlets" in each of the files.

The Scriptlets are run in the SSM.  When a "GetLoopScript" coomand is encountered, the SSM gathers all the [LoopScript] is loaded from .ini files in the order indicated by the parameters of the "GetLoopScript" call.

If for some reason a test is aborted (either becuase the "Abort" button was clicked or as a reaction to an error).  The [AbortScript] is loaded from the .ini files (in order) and run by the SSM.  Aloowing for a clean exit from the test.




PMU Conformity Configurations
'''''''''''''''''''''''''''''

Frequency Range
---------------

Plugins:
::::::::

Sync: Dyn3 PMU Cal
~~~~~~~~~~~~~~~~~~~
Clocks:
^^^^^^^
- FGenClk: PXI_Trig1, (TrigClk)
- SamplerClk: PXI_Trig4, (TrigClk)

Triggers: 
^^^^^^^^^
- PPS_Trigger: PXI_Trig3
- Digitizer_TrigTime: PXI_Trig6 (may no longer be used)
- FGen_Trigger: PXI_Trig2




FGen: PMU_Cal
~~~~~~~~~~~~~
Reference Clock
^^^^^^^^^^^^^^^
- source: PXI_Trig1

Triggers:
^^^^^^^^^
- Start: PXI_Trig2

Test Function .ini file: 50F0_50Fs_FreqRng.ini
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Digitizer: PMU Cal (Finite)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Trigger:
^^^^^^^^
- PXI_Trig3

Clock:
^^^^^^^
- Source: PXI_Trig4
- Sample Mode: Finite Samples
- Sync: PXI_Trig3 (PPS_Trigger) (may no longer be used)




Sensor: C37.118 PMU
~~~~~~~~~~~~~~~~~~~


Analysis: PMU (Finite)
~~~~~~~~~~~~~~~~~~~~~~
- Test Type: SteadyState
- Test Function .ini file: 50F0_50Fs_FreqRng.ini
- Test Duration: 5


Step Test
---------

