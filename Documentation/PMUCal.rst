.. to view each save, use Python restview -w PMUCal.rst PMUCal.rst

==============================
PMUCal Framework Documentation
==============================

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

