~Version
VERS .              3.0       :CWLS LOG ASCII STANDARD - VERSION 3.0
WRAP .               NO       :ONE LINE PER DEPTH STEP
DLM  .            COMMA       :DELIMITING CHARACTER
PROG .       striplog.py      :LAS Program name and version
CREA . 2015/03/27 12:53       :LAS Creation date {YYYY/MM/DD hh:mm}

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
  280.000,  282.000,  "Red, siltstone, very fine"                     
  282.000,  299.500,  "Brown, interbeds, sandstone, fine"             
  299.500,  315.000,  "Red, stringers, siltstone, very fine"          
  315.000,  328.000,  "Red, stringers, siltstone, very fine"          
  328.000,  340.000,  "Siltstone"                                     
  340.000,  360.000,  "Red, stringers, siltstone, very fine"          
  360.000,  373.000,  "Red, siltstone, very fine"                     
  373.000,  381.000,  "Red, stringers, siltstone, very fine"          
  381.000,  400.000,  "Red, siltstone, very fine"                     
  400.000,  412.000,  "Red, siltstone, very fine"                     
  412.000,  416.000,  "Light grey, shale"                             
  416.000,  420.000,  "Red, siltstone, very fine"                     
  420.000,  427.500,  "Light grey, shale"                             
  427.500,  439.500,  "White, anhydrite"                              
  439.500,  454.000,  "White, stringers, anhydrite"                   
  454.000,  458.000,  "Red, siltstone, very fine"                     
  458.000,  475.000,  "Red brown, interbeds, siltstone, very fine"    
  475.000,  495.000,  "Red brown, stringers, siltstone, very fine"    
  495.000,  507.000,  "Red brown, stringers, siltstone, very fine"    
  507.000,  510.000,  "Light, shale"                                  
  510.000,  514.500,  "Siltstone"                                     
  514.500,  517.500,  "Shale"                                         
  517.500,  520.000,  "Siltstone"                                     
  520.000,  525.000,  "Light grey, stringers, sandstone, very fine"   
  525.000,  532.000,  "White, stringers, anhydrite"                   
  532.000,  545.500,  "Dark grey, limestone"                          
  545.500,  565.000,  "Red, stringers, siltstone, very fine"          
  565.000,  585.500,  "Red, stringers, siltstone, very fine"          
  585.500,  588.000,  "Red, interbedded, siltstone, very fine"        
  588.000,  615.000,  "Red, stringers, siltstone, very fine"          
  615.000,  620.000,  "White, stringers, anhydrite"                   
  620.000,  645.000,  "Red, stringers, siltstone, very fine"          
  645.000,  655.000,  "Red, stringers, siltstone, very fine"          
  655.000,  675.000,  "Red, siltstone, very fine"                     
  675.000,  680.000,  "Dark grey, interbedded, siltstone"             
  680.000,  685.000,  "White, sandstone, fine"                        
  685.000,  701.500,  "White, stringers, anhydrite"                   
  701.500,  702.500,  "Sandy, anhydrite anhydrite"                    
  702.500,  703.500,  "White, sandstone, fine"                        
  703.500,  710.000,  "White, minor, anhydrite"                       
  710.000,  725.000,  "White, minor, anhydrite"                       
  725.000,  750.000,  "White, minor, anhydrite"                       
  750.000,  765.000,  "White, minor, anhydrite"                       
  765.000,  785.000,  "White, minor, anhydrite"                       
  785.000,  807.000,  "White, minor, anhydrite"                       
  807.000,  809.500,  "Dark grey, limestone limestone"                
  809.500,  826.000,  "Red, interbedded, sandstone siltstone, fine"   
  826.000,  842.000,  "Red, minor, siltstone"                         
  842.000,  855.000,  "Red, interbedded, sandstone siltstone, fine"   
  855.000,  860.000,  "Grey, sandstone, grains"                       
  860.000,  878.000,  "Red, minor, siltstone, very fine"              
  878.000,  882.000,  "Grey, sandstone, fine"                         
  882.000,  890.000,  "Red, minor, siltstone, very fine"              
  890.000,  890.500,  "Sandstone"                                     
  890.500,  910.000,  "Red, minor, siltstone, very fine"              
  910.000,  925.000,  "White, interbeds, sandstone, fine"             
  925.000,  943.000,  "White, interbeds, sandstone, fine"             
  943.000,  947.500,  "Light greenish, shale"                         
  947.500,  956.500,  "White, interbeds, sandstone, fine"             
  956.500,  963.500,  "Grey, interbedded, shale"                      
  963.500,  970.000,  "Red, siltstone"                                
  970.000,  985.000,  "Red, siltstone"                                
  985.000, 1000.000,  "Red, siltstone"                                
 1000.000, 1014.500,  "Red, siltstone"                                
 1014.500, 1020.000,  "White, interbeds, sandstone, fine"             
 1020.000, 1028.000,  "Interbedded, siltstone"                        
 1028.000, 1034.000,  "Red, siltstone"                                
 1034.000, 1042.000,  "Interbedded, siltstone"                        
 1042.000, 1050.000,  "Grey, shale, very fine"                        
 1050.000, 1060.000,  "Grey, interbedded, shale, very fine"           
 1060.000, 1080.000,  "Grey, interbedded, siltstone, very fine"       
 1080.000, 1091.500,  "Grey, interbedded, siltstone, very fine"       
 1091.500, 1097.500,  "Grey, shale, very fine"                        
 1097.500, 1110.500,  "Grey, interbedded, siltstone, very fine"       
 1110.500, 1115.000,  "Grey, interbedded, siltstone, very fine"       
 1115.000, 1125.000,  "Grey, shale, very fine"                        
 1125.000, 1145.000,  "Grey, shale, very fine"                        
 1145.000, 1160.000,  "Grey, shale, very fine"                        
 1160.000, 1165.000,  "White, sandstone, fine"                        
 1165.000, 1188.000,  "White, sandstone, fine"                        
 1188.000, 1204.000,  "White, sandstone, fine"                        
 1204.000, 1215.000,  "White, sandstone, fine"                        
 1215.000, 1234.500,  "White, sandstone, fine"                        
 1234.500, 1240.000,  "Grey, shale"                                   
 1240.000, 1246.500,  "White, sandstone, fine"                        
 1246.500, 1253.000,  "Grey, shale"                                   
 1253.000, 1279.500,  "White, sandstone, fine"                        
 1279.500, 1291.000,  "Grey, shale"                                   
 1291.000, 1294.000,  "Sandstone"                                     
 1294.000, 1305.000,  "Grey, shale"                                   
 1305.000, 1316.000,  "Grey, shale"                                   
 1316.000, 1333.000,  "White, sandstone, fine"                        
 1333.000, 1340.000,  "Grey, shale"                                   
 1340.000, 1349.000,  "White, sandstone, fine"                        
 1349.000, 1353.500,  "Shale"                                         
 1353.500, 1370.500,  "White, sandstone, fine"                        
 1370.500, 1374.000,  "Grey, shale"                                   
 1374.000, 1380.000,  "White, sandstone, fine"                        
 1380.000, 1384.000,  "Shale"                                         
 1384.000, 1395.000,  "White, sandstone, fine"                        
 1395.000, 1410.000,  "White, sandstone, fine"                        
 1410.000, 1440.000,  "White, sandstone, fine"                        
 1440.000, 1450.000,  "Black, shale"                                  
 1450.000, 1465.000,  "White, interbedded, sandstone, fine"           
 1465.000, 1483.500,  "White, interbedded, sandstone, fine"           
 1483.500, 1486.500,  "White, sandstone sandstone, fine"              
 1486.500, 1488.000,  "Black, sandstone"                              
 1488.000, 1488.500,  "Black, shale"                                  
 1488.500, 1490.500,  "Sandstone"                                     
 1490.500, 1492.000,  "Dark, sandstone"                               
 1492.000, 1494.000,  "Black, shale"                                  
 1494.000, 1495.500,  "White, shale, fine"                            
 1495.500, 1503.000,  "Sandstone"                                     
 1503.000, 1504.000,  "Shale"                                         
 1504.000, 1512.500,  "White, sandstone, fine"                        
 1512.500, 1518.000,  "White, sandstone, fine"                        
 1518.000, 1540.000,  "White, sandstone, fine"                        
 1540.000, 1542.000,  "Black, shale"                                  
 1542.000, 1553.000,  "White, sandstone, fine"                        
 1553.000, 1554.000,  "Black, fragments, shale"                       
 1554.000, 1556.500,  "Sandstone"                                     
 1556.500, 1558.500,  "Black, fragments, sandstone"                   
 1558.500, 1561.000,  "White, sandstone, fine"                        
 1561.000, 1571.000,  "Sandstone"                                     
 1571.000, 1579.500,  "White, sandstone, fine"                        
 1579.500, 1587.000,  "White, sandstone, fine"                        
 1587.000, 1594.500,  "White, sandstone, fine"                        
 1594.500, 1610.000,  "White, sandstone, fine"                        
 1610.000, 1625.000,  "White, sandstone, fine"                        
 1625.000, 1635.000,  "White, sandstone, fine"                        
 1635.000, 1648.000,  "White, interbedded, sandstone, fine"           
 1648.000, 1665.500,  "White, sandstone, fine"                        
 1665.500, 1667.000,  "Black, sandstone"                              
 1667.000, 1680.000,  "White, sandstone, fine"                        
 1680.000, 1695.000,  "White, sandstone, fine"                        
 1695.000, 1702.500,  "White, sandstone, fine"                        
 1702.500, 1715.000,  "Interbedded, sandstone"                        
 1715.000, 1725.000,  "White, sandstone, fine"                        
 1725.000, 1740.000,  "White, sandstone, fine"                        
 1740.000, 1756.500,  "White, sandstone, fine"                        
 1756.500, 1770.500,  "White, sandstone, fine"                        
 1770.500, 1790.000,  "White, sandstone, fine"                        
 1790.000, 1800.000,  "White, sandstone, fine"                        
 1800.000, 1815.000,  "White, sandstone, fine"                        
 1815.000, 1830.000,  "White, sandstone, fine"                        
 1830.000, 1845.000,  "White, sandstone, fine"                        
 1845.000, 1860.500,  "White, sandstone, fine"                        
 1860.500, 1882.500,  "White, sandstone, fine"                        
 1882.500, 1883.500,  "Dark grey, shale"                              
 1883.500, 1888.000,  "Sandstone"                                     
 1888.000, 1889.500,  "Dark grey, shale"                              
 1889.500, 1901.500,  "Sandstone"                                     
 1901.500, 1905.500,  "Grey, interbedded, shale"                      
 1905.500, 1911.500,  "White, sandstone, fine"                        
 1911.500, 1935.000,  "Light greenish, minor"
