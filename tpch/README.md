## TPC-H sqlite database generator

Execute `make` in this folder in order to generate a *tpch.db*.
The default is to generate a database that is only 10% (~125 MB) of the standard TPC-H one.
If you want to change the scale factor you can run make with a `SCALE` parameter.

    make SCALE="1"

If the parameter is set to `"1"` it will generate a full TPC-H database. 
