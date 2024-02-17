# Selection

This is a project holding scripts and code to apply selections.

## Setup

```bash
#Setup ROOT, etc
source /cvmfs/sft.cern.ch/lcg/views/setupViews.sh LCG_99 x86_64-centos7-gcc8-opt

#Clone and build library

git clone ssh://git@gitlab.cern.ch:7999/r_k/preselection.git
cd preselection
mkdir build
cd build
cmake ..
make
```

There will be two libraries built `lib/libpres.so` and `/lib/libselection.so`. They have to be loaded by ROOT everytime ROOT starts, this can be done by putting in `$HOME/.rootlogon.C`:

```c++
{
    TString root_version = gROOT->GetVersion();
    if (root_version == "6.22/06")
    {   
        gSystem->Load("/some/path/here/preselection/lib/libpres.so");
        gSystem->Load("/some/path/here/preselection/lib/libselection.so");
    }   
}
```

## Making selection JSON file

This file contains all the selection and it is made by:

```
python python/make_selection.py
```

## Reading the selection

The code below will read one and only one file with the analysis selection, located in:

```
/publicfs/ucas/user/campoverde/preselection/json/selection_v1.json
```

### python

Do:

```python

import read_selection as rs

selection = rs.get(quantity, trigger, q2bin=q2bin, year = year)
```

where the `python/` directory needs to be in the `PYTHONPATH`, (see 
<a href="https://gitlab.cern.ch/lhcb_ucas/general-computing/-/blob/master/python.md#user-content-pythonpath" target="_blank">this</a>).
To install (make symbolic link) the module to `$HOME/.local/python` run `./install.sh`. 

Finally, the arguments allowed are among:

```python

#The cuts are among:
['hlt1', 'hlt2']
['bdt', 'cascade', 'kinematics', 'mass', 'nspd', 'pid', 'q2', 'ghost']
['etos', 'gtis', 'xyecal', 'calo_rich'] #etos and gtis are the L0 trigger requirements for eTOS and gTIS!
['mtos', 'rich', 'acceptance', 'jpsi_misid'] #mtos is the L0 trigger requirement for mTOS

#Trigger is among:
['ETOS', 'HTOS', 'GTIS', 'MTOS']

#q2 bin is among:
['central', 'jpsi', 'psi2', 'high']

#Year is among:
['2011', '2012', '2015', '2016', '2017', '2018', 'r1', 'r2p1']

```
so, to extract the B mass cut for the `central` q2 bin in the mTOS category in 2016:

```python
cut = rs.get('mass', 'MTOS', 'central', '2016')
```

`'none'` can be used for cuts that do not depend on the specific variable, e.g.:

```python
rs.get('hlt1', 'ETOS', 'none', '2017')
```

because the `hlt1` requirement only changes with the year. **However the trigger is always needed** for safety reasons and to keep the code simple.

#### Reading truth matching strings

Witht the `python` script one can also read the truth matching strings doing:

```python
truth_str = rs.get_truth(event_type)
```

where `event_type` can be a string or integer.
### C++

To access the cuts the `libselection.so` needs to be loaded by the `$HOME/.rootlogon.C` as mentioned before and:

```c++
#include "/publicfs/ucas/user/campoverde/preselection/include/read_selection.h"

void test_read()
{
    auto val = read_selection::get("bdt", "ETOS", "central", "2011");
    auto vol = read_selection::get("bdt", "ETOS", "central", "2011");

    std::cout << val << std::endl;
    std::cout << vol << std::endl;
}
```

for instance, in order to read the `bdt` requirement in `ETOS` category for the `central` q2 bin in `2011`.

The include line would be replaced with the path to your local `read_selection.h` and with:

```c++
#include "read_selection.h"
```

if the `include` directory is added to the `CPLUS_INCLUDE_PATH` (see
<a href="https://gitlab.cern.ch/lhcb_ucas/general-computing/-/blob/master/cpp.md#user-content-include-paths" target="_blank">this</a>)
