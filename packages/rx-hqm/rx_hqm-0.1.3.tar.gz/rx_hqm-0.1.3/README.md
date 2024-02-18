# Installation

``` shell
pip install -e .
```
create symbolic links in the project root directory:

``` shell
ln -s /publicfs/ucas/user/qi/public/RK/high_q2_yield_study/data
ln -s /publicfs/ucas/user/qi/public/RK/high_q2_yield_study/root_sample
```

# Usage
## Mass window
This package provide the pdf in following mass window

+ (4500, 6000) MeV for electron
+ (5180, 5600) MeV for muon

**Use same mass window as this**, some parameters are mass-window dependent
## Get shape
available dataset: 2018, 2017, r2p1, r1
trigger:
+ electron mode: ETOS, GTIS
+ moun mode: MTOS

## systematic uncertainty related arguments
+ `systematic`
  + `nom`: nominal pdf
  + `sys1`: alternative pdf for systematic uncertainty study
+ `bts_index`: bootstrapping index for KDE pdfs.


``` python
#import the package
from hqm.model import get_part_reco
from hqm.model import get_Bu2Ksee_shape
from hqm.model import get_Bd2Ksee_shape
from hqm.model import get_signal_shape
from hqm.model import get_Bs2phiee_shape
from hqm.model import get_Bu2K1ee_shape
from hqm.model import get_Bu2K2ee_shape

# muon signal shape and constriaints
signal_shape_mm, constraints = get_signal_shape(dataset="2018", trigger="MTOS", parameter_name_prefix="prefix", systematic="nom")
#electron signal shape and constraints
signal_shape_ee, constraints = get_signal_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", systematic="nom")

#rare part-reco B0 -> K* ee
Bd2Ksee_shape = get_Bd2Ksee_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", bts_index=0)
#rare part-reco B+ -> K* ee
Bu2Ksee_shape = get_Bu2Ksee_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", bts_index=0)
#rare part-reco Bs -> phi ee
Bs2phiee_shape = get_Bs2phiee_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", bts_index=0)
#rare part-reco B+ -> K1 ee
Bu2K1ee_shape = get_Bu2K1ee_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", bts_index=0)
#rare part-reco B+ -> K2 ee
Bu2K2ee_shape = get_Bu2K2ee_shape(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", bts_index=0)


#resonant part-reco + psi2S K & ratio constraint
part_reco_shape, constraints = get_part_reco(dataset="2018", trigger="ETOS", parameter_name_prefix="prefix", systematic="nom", bts_index=0)
```



