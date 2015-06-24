~Version
VERS .              3.0       :CWLS LOG ASCII STANDARD - VERSION 3.0
WRAP .               NO       :ONE LINE PER DEPTH STEP
DLM  .            COMMA       :DELIMITING CHARACTER
PROG .       striplog.py      :LAS Program name and version
CREA . 2015/03/27 13:00       :LAS Creation date {YYYY/MM/DD hh:mm}

~Well
#MNEM .UNIT  DATA             DESCRIPTION
#---- ------ --------------   -----------------------------
STRT .M       280.000         :START DEPTH
STOP .M      1935.000         :STOP DEPTH
STEP .M      -999.2500        :STEP
NULL .       -999.2500        :NULL VALUE

WELL .       P-129                 :WELL
FLD  .       UNDEFINED             :FIELD
CTRY .       CA                    :COUNTRY

PROV .       NOVA SCOTIA           :PROVINCE
UWI  .                             :UNIQUE WELL ID
LIC  .       P-129                 :LICENSE NUMBER

~Parameter
#MNEM .UNIT  VALUE            DESCRIPTION
#---- ------ --------------   -----------------------------

#Required parameters
RUN  .        ONE             :RUN NUMBER
PDAT .        GL              :PERMANENT DATUM
APD  .M       -999.250        :ABOVE PERM DATUM
DREF .        KB              :DEPTH REFERENCE
EREF .M       -999.250        :ELEVATION OF DEPTH

#Remarks
R1   .                        :REMARK LINE 1
R2   .                        :REMARK LINE 2
R3   .                        :REMARK LINE 3

~Lithology_Parameter
LITH .   Striplog         : Lithology source          {S}
LITHD.   MD               : Lithology depth reference {S}

~Lithology_Definition
LITHT.M                   : Lithology top depth       {F}
LITHB.M                   : Lithology base depth      {F}
LITHD.                    : Lithology description     {S}

~Lithology_Data | Lithology_Definition
  280.000,  299.986,  "Red, siltstone"                                
  299.986,  304.008,  "Grey, sandstone, vf-f"                         
  304.008,  328.016,  "Red, siltstone"                                
  328.016,  328.990,  "Limestone"                                     
  328.990,  330.007,  "Red, siltstone"                                
  330.007,  333.987,  "Limestone"                                     
  333.987,  338.983,  "Red, siltstone"                                
  338.983,  340.931,  "Limestone"                                     
  340.931,  345.927,  "Red, siltstone"                                
  345.927,  346.944,  "Limestone"                                     
  346.944,  414.946,  "Red, siltstone"                                
  414.946,  416.936,  "Grey, mudstone"                                
  416.936,  422.440,  "Red, heterolithic"                             
  422.440,  423.414,  "Grey, mudstone"                                
  423.414,  426.929,  "Red, heterolithic"                             
  426.929,  427.902,  "Grey, mudstone"                                
  427.902,  449.921,  "Anhydrite"                                     
  449.921,  452.927,  "Limestone"                                     
  452.927,  528.974,  "Red, heterolithic"                             
  528.974,  532.446,  "Anhydrite"                                     
  532.446,  537.485,  "Red, heterolithic"                             
  537.485,  539.983,  "Limestone"                                     
  539.983,  586.009,  "Red, heterolithic"                             
  586.009,  589.016,  "Limestone"                                     
  589.016,  591.006,  "Red, siltstone"                                
  591.006,  592.996,  "Limestone"                                     
  592.996,  594.012,  "Red, siltstone"                                
  594.012,  594.986,  "Limestone"                                     
  594.986,  615.014,  "Red, siltstone"                                
  615.014,  621.492,  "Anhydrite"                                     
  621.492,  639.996,  "Red, siltstone"                                
  639.996,  642.960,  "Anhydrite"                                     
  642.960,  645.966,  "Red, siltstone"                                
  645.966,  649.989,  "Anhydrite"                                     
  649.989,  652.487,  "Red, siltstone"                                
  652.487,  656.002,  "Anhydrite"                                     
  656.002,  669.975,  "Red, heterolithic"                             
  669.975,  674.971,  "Grey, sandstone, vf-f"                         
  674.971,  703.468,  "Anhydrite"                                     
  703.468,  703.976,  "Grey, sandstone, vf-f"                         
  703.976,  705.966,  "Anhydrite"                                     
  705.966,  707.448,  "Grey, sandstone, vf-f"                         
  707.448,  714.477,  "Anhydrite"                                     
  714.477,  715.451,  "Limestone"                                     
  715.451,  719.473,  "Anhydrite"                                     
  719.473,  724.470,  "Limestone"                                     
  724.470,  734.462,  "Anhydrite"                                     
  734.462,  735.436,  "Limestone"                                     
  735.436,  761.900,  "Anhydrite"                                     
  761.900,  764.907,  "Limestone"                                     
  764.907,  778.922,  "Anhydrite"                                     
  778.922,  779.938,  "Limestone"                                     
  779.938,  805.937,  "Anhydrite"                                     
  805.937,  809.959,  "Limestone"                                     
  809.959,  827.955,  "Red, sandstone, vf-f"                          
  827.955,  829.945,  "Grey, sandstone, vf-f"                         
  829.945,  838.921,  "Red, sandstone, vf-f"                          
  838.921,  840.954,  "Grey, sandstone, vf-f"                         
  840.954,  847.432,  "Red, sandstone, vf-f"                          
  847.432,  853.953,  "Grey, sandstone, vf-f"                         
  853.953,  859.966,  "Red, sandstone, vf-f"                          
  859.966,  862.930,  "Grey, sandstone, vf-f"                         
  862.930,  872.457,  "Red, sandstone, vf-f"                          
  872.457,  874.955,  "Grey, sandstone, vf-f"                         
  874.955,  878.935,  "Red, sandstone, vf-f"                          
  878.935,  880.925,  "Grey, sandstone, vf-f"                         
  880.925,  893.924,  "Red, sandstone, vf-f"                          
  893.924,  894.941,  "Grey, sandstone, vf-f"                         
  894.941,  905.950,  "Red, sandstone, vf-f"                          
  905.950,  918.949,  "Grey, sandstone, vf-f"                         
  918.949,  919.923,  "Red, mudstone"                                 
  919.923,  939.908,  "Grey, sandstone, vf-f"                         
  939.908,  947.403,  "Red, mudstone"                                 
  947.403,  955.914,  "Grey, sandstone, vf-f"                         
  955.914,  984.918,  "Red, sandstone, vf-f"                          
  984.918,  991.947,  "Grey, sandstone, vf-f"                         
  991.947, 1015.913,  "Red, sandstone, vf-f"                          
 1015.913, 1019.936,  "Grey, sandstone, vf-f"                         
 1019.936, 1134.938,  "Red, heterolithic"                             
 1134.938, 1137.436,  "Grey, sandstone, vf-f"                         
 1137.436, 1152.425,  "Grey, heterolithic"                            
 1152.425, 1154.924,  "Grey, sandstone, vf-f"                         
 1154.924, 1159.920,  "Grey, mudstone"                                
 1159.920, 1164.959,  "Grey, sandstone, vf-f"                         
 1164.959, 1201.966,  "Grey, heterolithic"                            
 1201.966, 1204.972,  "Grey, sandstone, f-m"                          
 1204.972, 1207.005,  "Grey, heterolithic"                            
 1207.005, 1210.011,  "Grey, sandstone, f-m"                          
 1210.011, 1217.506,  "Grey, heterolithic"                            
 1217.506, 1221.486,  "Grey, sandstone, f-m"                          
 1221.486, 1238.000,  "Grey, heterolithic"                            
 1238.000, 1246.002,  "Grey, sandstone, f-m"                          
 1246.002, 1252.481,  "Grey, mudstone"                                
 1252.481, 1262.982,  "Grey, sandstone, f-m"                          
 1262.982, 1272.509,  "Grey, heterolithic"                            
 1272.509, 1277.505,  "Grey, sandstone, f-m"                          
 1277.505, 1287.498,  "Grey, heterolithic"                            
 1287.498, 1294.019,  "Grey, sandstone, f-m"                          
 1294.019, 1304.012,  "Grey, mudstone"                                
 1304.012, 1309.008,  "Grey, sandstone, f-m"                          
 1309.008, 1332.000,  "Grey, heterolithic"                            
 1332.000, 1333.990,  "Grey, sandstone, f-m"                          
 1333.990, 1343.009,  "Grey, heterolithic"                            
 1343.009, 1349.996,  "Grey, sandstone, f-m"                          
 1349.996, 1357.490,  "Grey, heterolithic"                            
 1357.490, 1359.988,  "Grey, sandstone, f-m"                          
 1359.988, 1367.991,  "Grey, heterolithic"                            
 1367.991, 1369.981,  "Grey, sandstone, f-m"                          
 1369.981, 1374.978,  "Grey, mudstone"                                
 1374.978, 1377.010,  "Grey, sandstone, f-m"                          
 1377.010, 1393.524,  "Grey, heterolithic"                            
 1393.524, 1399.028,  "Grey, sandstone, f-m"                          
 1399.028, 1414.018,  "Grey, heterolithic"                            
 1414.018, 1425.027,  "Grey, sandstone, vf-f"                         
 1425.027, 1428.033,  "Grey, heterolithic"                            
 1428.033, 1435.019,  "Grey, sandstone, vf-f"                         
 1435.019, 1443.996,  "Grey, heterolithic"                            
 1443.996, 1448.992,  "Grey, sandstone, vf-f"                         
 1448.992, 1455.979,  "Grey, heterolithic"                            
 1455.979, 1458.985,  "Grey, sandstone, vf-f"                         
 1458.985, 1460.002,  "Grey, mudstone"                                
 1460.002, 1463.474,  "Grey, sandstone, vf-f"                         
 1463.474, 1482.020,  "Grey, heterolithic"                            
 1482.020, 1484.010,  "Grey, mudstone"                                
 1484.010, 1487.524,  "Grey, sandstone, vf-f"                         
 1487.524, 1489.049,  "Grey, mudstone"                                
 1489.049, 1491.081,  "Grey, sandstone, vf-f"                         
 1491.081, 1495.569,  "Grey, heterolithic"                            
 1495.569, 1507.552,  "Grey, sandstone, f-m"                          
 1507.552, 1515.089,  "Grey, heterolithic"                            
 1515.089, 1525.082,  "Grey, sandstone, f-m"                          
 1525.082, 1527.072,  "Grey, mudstone"                                
 1527.072, 1540.071,  "Grey, sandstone, f-m"                          
 1540.071, 1542.061,  "Grey, mudstone"                                
 1542.061, 1545.068,  "Grey, sandstone, f-m"                          
 1545.068, 1547.524,  "Grey, mudstone"                                
 1547.524, 1553.028,  "Grey, sandstone, f-m"                          
 1553.028, 1554.002,  "Grey, mudstone"                                
 1554.002, 1556.500,  "Grey, sandstone, f-m"                          
 1556.500, 1557.516,  "Grey, mudstone"                                
 1557.516, 1560.015,  "Grey, sandstone, f-m"                          
 1560.015, 1562.005,  "Grey, mudstone"                                
 1562.005, 1568.017,  "Grey, sandstone, f-m"                          
 1568.017, 1570.007,  "Grey, mudstone"                                
 1570.007, 1571.998,  "Grey, sandstone, f-m"                          
 1571.998, 1573.014,  "Grey, mudstone"                                
 1573.014, 1600.028,  "Grey, sandstone, f-m"                          
 1600.028, 1602.992,  "Grey, mudstone"                                
 1602.992, 1635.046,  "Grey, sandstone, f-m"                          
 1635.046, 1640.042,  "Grey, heterolithic"                            
 1640.042, 1644.530,  "Grey, sandstone, f-m"                          
 1644.530, 1648.045,  "Grey, mudstone"                                
 1648.045, 1655.539,  "Grey, sandstone, f-m"                          
 1655.539, 1657.572,  "Grey, mudstone"                                
 1657.572, 1675.102,  "Grey, sandstone, f-m"                          
 1675.102, 1677.092,  "Grey, mudstone"                                
 1677.092, 1698.559,  "Grey, sandstone, f-m"                          
 1698.559, 1700.084,  "Grey, mudstone"                                
 1700.084, 1713.040,  "Grey, sandstone, f-m"                          
 1713.040, 1715.031,  "Grey, mudstone"                                
 1715.031, 1733.534,  "Grey, sandstone, f-m"                          
 1733.534, 1734.550,  "Grey, mudstone"                                
 1734.550, 1737.049,  "Grey, sandstone, f-m"                          
 1737.049, 1738.531,  "Grey, mudstone"                                
 1738.531, 1742.045,  "Grey, sandstone, f-m"                          
 1742.045, 1743.019,  "Grey, mudstone"                                
 1743.019, 1756.018,  "Grey, sandstone, f-m"                          
 1756.018, 1770.034,  "Grey, mudstone"                                
 1770.034, 1784.049,  "Grey, sandstone, f-m"                          
 1784.049, 1784.557,  "Grey, mudstone"                                
 1784.557, 1797.514,  "Grey, sandstone, f-m"                          
 1797.514, 1800.520,  "Grey, mudstone"                                
 1800.520, 1836.511,  "Grey, sandstone, f-m"                          
 1836.511, 1837.019,  "Grey, mudstone"                                
 1837.019, 1841.000,  "Grey, sandstone, f-m"                          
 1841.000, 1842.016,  "Grey, mudstone"                                
 1842.016, 1847.986,  "Grey, sandstone, f-m"                          
 1847.986, 1849.002,  "Grey, mudstone"                                
 1849.002, 1853.956,  "Grey, sandstone, f-m"                          
 1853.956, 1858.445,  "Grey, mudstone"                                
 1858.445, 1873.942,  "Grey, sandstone, f-m"                          
 1873.942, 1892.446,  "Grey, mudstone"                                
 1892.446, 1898.967,  "Grey, sandstone, f-m"                          
 1898.967, 1904.471,  "Grey, mudstone"                                
 1904.471, 1935.000,  "Volcanic"
