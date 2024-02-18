import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Fundamental Config
currentfilepath = __file__

# config.txt path
motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
configpath = motherpath + "\\pymeili_resource\\config.txt"
def read_config(line):
    content = np.loadtxt(configpath, dtype=str)
    try:
        if content[line][0:5] == "-----":
            raise TypeError(f"\033[45m[pymeili inner Error]\033[0m Config file error: get line number: {line+1} is a split line.")
        else: raise Exception
    except Exception:
        if content[line] == "one": return 1
        elif content[line] == "zero": return 0
        # 判斷是否為布林值
        if content[line] == "True" or content[line] == "1": return True
        elif content[line] == "False" or content[line] == "0": return False
        # 判斷是否為數字
        try:
            return int(content[line])
        except:
            # 如果開頭為@，則替換成#
            if content[line][0] == "@": content[line] = "#"+content[line][1:]
            # 如果含有空格的字串，將空格換成_
            if "_" in content[line]:
                content[line] = content[line].replace("_", " ")
            return content[line]
            


def cmaplist(index):
    theme = read_config(18)
    # 如果index是list
    if type(index) == list:
        if read_config(1) == False:
            print('\033[44m[pymeili Info]\033[0m Detected self-defined colormap list.')
        return LinearSegmentedColormap.from_list('mycmap', index)
    else:
        #print(f'\033[44m[pymeili Info]\033[0m Detected colormap code index: {index}; theme is {theme}.')
        str(index)
        if index in ['-28','28','-27','-26','-25','-24','-23','-22','22','23','24','25','26','27','12','13','14','15','-12','-13','-14','-15','33','34','35','36','37','38','39','-33','-34','-35','-36','-37','-38','-39','43','44','45','46','47','48','49','-43','-44','-45','-46','-47','-48','-49','59','58','57','-57','-58','-59','-69','69','-79','79','-89','89','-99','99','-109','109','-119','119','-129','129', '-139', '139', '-149', '149', '-159', '159']:
            try:
                if theme == 'light':
                    if index == '15':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#47A7DE','#D5EDD5','#E08A16','#AB503B'])
                    if index == '14':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#47A7DE','#E08A16','#AB503B'])
                    if index == '13':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#D5EDD5','#AB503B'])
                    if index == '12':
                        return LinearSegmentedColormap.from_list('mycmap', ['#47A7DE','#E08A16'])

                    if index == '-15': # reversed 1
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#E08A16','#D5EDD5','#47A7DE','#454FB4'])
                    if index == '-14': # reversed 1 but 4 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#E08A16','#47A7DE','#454FB4'])
                    if index == '-13': # reversed 1 but 3 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#D5EDD5','#454FB4'])
                    if index == '-12': # reversed 1 but 2 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#E08A16','#47A7DE'])

                    if index == '28':
                        return LinearSegmentedColormap.from_list('mycmap', ['#D9EEFD','#FFFFFF','#FFFFFF','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E','#BB8263'])        
                    if index == '27':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E','#BB8263'])
                    if index == '26':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E'])
                    if index == '25':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F'])
                    if index == '24':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A'])
                    if index == '23':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4'])
                    if index == '22':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF'])

                    if index == '-28': # reversed 2
                        return LinearSegmentedColormap.from_list('mycmap', ['#BB8263','#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#FFFFFF','#FFFFFF','#D9EEFD']) 
                    if index == '-27': # reversed 2
                        return LinearSegmentedColormap.from_list('mycmap', ['#BB8263','#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE','#EEEEEE'])
                    if index == '-26': # reversed 2 but 6 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-25':
                        return LinearSegmentedColormap.from_list('mycmap', ['#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-24':
                        return LinearSegmentedColormap.from_list('mycmap', ['#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-23':
                        return LinearSegmentedColormap.from_list('mycmap', ['#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-22':
                        return LinearSegmentedColormap.from_list('mycmap', ['#F2CABF','#EEEEEE'])
                    
                    if index == '39':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438','#E9A82E','#EA6D0B','#D10C0F','#802523'])
                    if index == '38':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438','#E9A82E'])
                    if index == '37':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438'])
                    if index == '36':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE'])
                    if index == '35':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5'])
                    if index == '34':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED'])
                    if index == '33':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B'])
                    
                    if index == '-39': 
                        return LinearSegmentedColormap.from_list('mycmap', ['#802523','#D10C0F','#EA6D0B','#E9A82E','#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-38':
                        return LinearSegmentedColormap.from_list('mycmap', ['#E9A82E','#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-37':
                        return LinearSegmentedColormap.from_list('mycmap', ['#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-36':
                        return LinearSegmentedColormap.from_list('mycmap', ['#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-35':
                        return LinearSegmentedColormap.from_list('mycmap', ['#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-34':
                        return LinearSegmentedColormap.from_list('mycmap', ['#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-33':
                        return LinearSegmentedColormap.from_list('mycmap', ['#5E9C5B','#BCEDAC','#EEEEEE'])
                    
                    if index == '49': # 18色
                        return LinearSegmentedColormap.from_list('mycap', ['#2D889B','#5CA9BB','#86CAD7','#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402','#A164AA','#845098'])
                    if index == '48': # 16色
                        return LinearSegmentedColormap.from_list('mycap', ['#2D889B','#5CA9BB','#86CAD7','#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402'])
                    if index == '47': # 13色
                        return LinearSegmentedColormap.from_list('mycap', ['#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402'])
                    if index == '46': # 11色
                        return LinearSegmentedColormap.from_list('mycap', ['#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D'])
                    if index == '45': # 9色
                        return LinearSegmentedColormap.from_list('mycap', ['#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D'])
                    if index == '44': # 7色
                        return LinearSegmentedColormap.from_list('mycap', ['#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237'])
                    if index == '43': # 5色
                        return LinearSegmentedColormap.from_list('mycap', ['#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905'])
                    
                    if index == '-49':
                        return LinearSegmentedColormap.from_list('mycap', ['#845098','#A164AA','#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249','#86CAD7','#5CA9BB','#2D889B'])
                    if index == '-48':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249','#86CAD7','#5CA9BB','#2D889B'])
                    if index == '-47':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249'])
                    if index == '-46':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A'])
                    if index == '-45':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890'])
                    if index == '-44':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463'])
                    if index == '-43':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905'])
                    
                    if index == '59':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#CACACA','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801','#AA21A3','#DA2DD3','#FB39FA','#FED5FD'])
                    if index == '58':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801','#AA21A3','#DA2DD3','#FB39FA','#FED5FD'])
                    if index == '57':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801'])
                    
                    if index == '-59':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD','#9DFEFF','#EEEEEE'])
                    if index == '-58':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD','#9DFEFF'])
                    if index == '-57':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD'])

                    if index == '69':
                        return LinearSegmentedColormap.from_list('mycmap',['#CD6A1A','#E28637','#F3A760','#FFCD81','#FCE09C','#FFF4B7','#FAFAFA','#FAFAFA','#B4FFCB','#5CF0B0','#00BE9F','#41ACC9','#0071B4','#003559']) 
                    if index == '-69':
                        return LinearSegmentedColormap.from_list('mycmap',['#003559','#0071B4','#41ACC9','#00BE9F','#5CF0B0','#B4FFCB','#FAFAFA','#FAFAFA','#FFF4B7','#FCE09C','#FFCD81','#F3A760','#E28637','#CD6A1A'])                                            
                                                                        
                    if index == '79': #ECMWF Blue~Red
                        return LinearSegmentedColormap.from_list('mycmap',['#CBBEEC','#F295CD','#AE3E77','#7F116B','#6B22AB','#1240AF','#437AC4','#ADCAE5','#FFFFFF','#EBA4A0','#D75E5D','#AC1317','#6C0403','#BE5820','#E0A06E','#E3D8C9','#AC9D9B'])
                    if index == '-79':
                        return LinearSegmentedColormap.from_list('mycmap',['#AC9D9B','#E3D8C9','#E0A06E','#BE5820','#6C0403','#AC1317','#D75E5D','#EBA4A0','#FFFFFF','#ADCAE5','#437AC4','#1240AF','#6B22AB','#7F116B','#AE3E77','#F295CD','#CBBEEC'])
                    
                    if index == '89':
                        return LinearSegmentedColormap.from_list('mycmap',['#3A0300','#703922','#A56F44','#785732','#483C1F','#9A917F','#FFFFFF','#79B494','#3C9262','#1B696B','#0D507A','#354778','#724172'])
                    if index == '-89':
                        return LinearSegmentedColormap.from_list('mycmap',['#724172','#354778','#0D507A','#1B696B','#3C9262','#79B494','#FFFFFF','#9A917F','#483C1F','#785732','#A56F44','#703922','#3A0300'])

                    if index == '99':
                        return LinearSegmentedColormap.from_list('mycmap',['#8C5338','#CD6A1A','#E28637','#F3A760','#FFCD81','#FFF4B7','#EEEEEE','#EEEEEE','#B4FFCB','#56E0A5','#00BE9F','#41ACC9','#0071B4','#003559'])
                    if index == '-99':
                        return LinearSegmentedColormap.from_list('mycmap',['#003559','#0071B4','#41ACC9','#00BE9F','#56E0A5','#B4FFCB','#EEEEEE','#EEEEEE','#FFF4B7','#FFCD81','#F3A760','#E28637','#CD6A1A','#8C5338'])
                
                    if index == '109':
                        return LinearSegmentedColormap.from_list('mycmap',['#400000','#7D0204','#4B0077','#A401E6','#0102FB','#014BAA','#016EFF','#72B2D6','#97DAF4','#BEFFE8','#F5F5F5','#EFFDCA','#FEE183','#FB9001','#EF5E03','#E40004','#BB022E','#8A0220','#7A021C','#7A021C','#75021C'])
                    if index == '-109':
                        return LinearSegmentedColormap.from_list('mycmap',['#75021C','#7A021C','#7A021C','#8A0220','#BB022E','#E40004','#EF5E03','#FB9001','#FEE183','#EFFDCA','#F5F5F5','#BEFFE8','#97DAF4','#72B2D6','#016EFF','#014BAA','#0102FB','#A401E6','#4B0077','#7D0204','#400000'])
                    
                    if index == '119':
                        return LinearSegmentedColormap.from_list('mycmap',['#FFFFFF','#CECECE','#A1A1A1','#717171','#444444','#7747D0','#380C66','#7c0341'])
                    if index == '-119':
                        return LinearSegmentedColormap.from_list('mycmap',['#7c0341','#380C66','#7747D0','#444444','#717171','#A1A1A1','#CECECE','#FFFFFF'])
                    
                    if index == '129':
                        return LinearSegmentedColormap.from_list('mycmap',['#EDEDED','#BBF3AA','#FDFF04','#DA9E3A','#F45855','#800025'])
                    if index == '-129':
                        return LinearSegmentedColormap.from_list('mycmap',['#800025','#F45855','#DA9E3A','#FDFF04','#BBF3AA','#EDEDED'])
                    
                    if index == '139':
                        return LinearSegmentedColormap.from_list('mycmap',['#F8BAC5','#EB95DD','#DF71F4','#9157DB','#484FB8','#004693','#2874C6','#64B7F8','#8CE3F6','#F0F0F0','#FEEAA0','#FDB365','#EF633E','#C21C26','#BA4355','#F18DB2','#CB86A4','#98656C','#69452A'])
                    if index == '-139':
                        return LinearSegmentedColormap.from_list('mycmap',['#69452A','#98656C','#CB86A4','#F18DB2','#BA4355','#C21C26','#EF633E','#FDB365','#FEEAA0','#F0F0F0','#8CE3F6','#64B7F8','#2874C6','#004693','#484FB8','#9157DB','#DF71F4','#EB95DD','#F8BAC5'])
                
                    if index == '149':
                        return LinearSegmentedColormap.from_list('mycmap',['#D9BFED','#B28DE4','#071A91','#A5D4FB','#F5F5F5','#FF9C33','#790000','#FF0000','#F5A595'])
                    if index == '-149':
                        return LinearSegmentedColormap.from_list('mycmap',['#F5A595','#FF0000','#790000','#FF9C33','#F5F5F5','#A5D4FB','#071A91','#B28DE4','#D9BFED'])
                    
                    if index == '159':
                        return LinearSegmentedColormap.from_list('mycmap',['#C60042','#8A0001','#952C14','#9C431F','#A86E34','#DB9C1A','#FFDE00','#FFF980','#F0F0F0','#80F180','#00DC00','#00B64B','#009496','#00ACC1','#00D8FF','#6E92D2','#9379C3'])
                    if index == '-159':
                        return LinearSegmentedColormap.from_list('mycmap',['#9379C3','#6E92D2','#00D8FF','#00ACC1','#009496','#00B64B','#00DC00','#80F180','#F0F0F0','#FFF980','#FFDE00','#DB9C1A','#A86E34','#9C431F','#952C14','#8A0001','#C60042'])
                                                
                
                elif theme == 'dark':
                    if index == '15':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#47A7DE','#D5EDD5','#E08A16','#AB503B'])
                    if index == '14':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#47A7DE','#E08A16','#AB503B'])
                    if index == '13':
                        return LinearSegmentedColormap.from_list('mycmap', ['#454FB4','#D5EDD5','#AB503B'])
                    if index == '12':
                        return LinearSegmentedColormap.from_list('mycmap', ['#47A7DE','#E08A16'])

                    if index == '-15': # reversed 1
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#E08A16','#D5EDD5','#47A7DE','#454FB4'])
                    if index == '-14': # reversed 1 but 4 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#E08A16','#47A7DE','#454FB4'])
                    if index == '-13': # reversed 1 but 3 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#AB503B','#D5EDD5','#454FB4'])
                    if index == '-12': # reversed 1 but 2 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#E08A16','#47A7DE'])
                            
                    if index == '28':
                        return LinearSegmentedColormap.from_list('mycmap', ['#D9EEFD','#FFFFFF','#FFFFFF','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E','#BB8263'])        
                    if index == '27':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E','#BB8263'])
                    if index == '26':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F','#CF725E'])
                    if index == '25':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A','#DB997F'])
                    if index == '24':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4','#DCB29A'])
                    if index == '23':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF','#F1C9B4'])
                    if index == '22':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#F2CABF'])
                    
                    if index == '-28': # reversed 2
                        return LinearSegmentedColormap.from_list('mycmap', ['#BB8263','#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#FFFFFF','#FFFFFF','#D9EEFD']) 
                    if index == '-27': # reversed 2
                        return LinearSegmentedColormap.from_list('mycmap', ['#BB8263','#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-26': # reversed 2 but 6 colors
                        return LinearSegmentedColormap.from_list('mycmap', ['#CF725E','#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-25':
                        return LinearSegmentedColormap.from_list('mycmap', ['#DB997F','#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-24':
                        return LinearSegmentedColormap.from_list('mycmap', ['#DCB29A','#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-23':
                        return LinearSegmentedColormap.from_list('mycmap', ['#F1C9B4','#F2CABF','#EEEEEE'])
                    if index == '-22':
                        return LinearSegmentedColormap.from_list('mycmap', ['#F2CABF','#EEEEEE'])
                    
                    if index == '39':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438','#E9A82E','#EA6D0B','#D10C0F','#802523'])
                    if index == '38':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438','#E9A82E'])
                    if index == '37':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE','#760438'])
                    if index == '36':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5','#E90EDE'])
                    if index == '35':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED','#0C04D5'])
                    if index == '34':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B','#66B5ED'])
                    if index == '33':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#BCEDAC','#5E9C5B'])
                    
                    if index == '-39': 
                        return LinearSegmentedColormap.from_list('mycmap', ['#802523','#D10C0F','#EA6D0B','#E9A82E','#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-38':
                        return LinearSegmentedColormap.from_list('mycmap', ['#E9A82E','#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-37':
                        return LinearSegmentedColormap.from_list('mycmap', ['#760438','#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-36':
                        return LinearSegmentedColormap.from_list('mycmap', ['#E90EDE','#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-35':
                        return LinearSegmentedColormap.from_list('mycmap', ['#0C04D5','#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-34':
                        return LinearSegmentedColormap.from_list('mycmap', ['#66B5ED','#5E9C5B','#BCEDAC','#EEEEEE'])
                    if index == '-33':
                        return LinearSegmentedColormap.from_list('mycmap', ['#5E9C5B','#BCEDAC','#EEEEEE'])
                    
                    if index == '49': # 18色
                        return LinearSegmentedColormap.from_list('mycap', ['#2D889B','#5CA9BB','#86CAD7','#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402','#A164AA','#845098'])
                    if index == '48': # 16色
                        return LinearSegmentedColormap.from_list('mycap', ['#2D889B','#5CA9BB','#86CAD7','#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402'])
                    if index == '47': # 13色
                        return LinearSegmentedColormap.from_list('mycap', ['#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D','#B10239','#740402'])
                    if index == '46': # 11色
                        return LinearSegmentedColormap.from_list('mycap', ['#0E9249','#31A054','#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D'])
                    if index == '45': # 9色
                        return LinearSegmentedColormap.from_list('mycap', ['#61BA6A','#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237','#ED175D'])
                    if index == '44': # 7色
                        return LinearSegmentedColormap.from_list('mycap', ['#99CF7B','#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905','#F05237'])
                    if index == '43': # 5色
                        return LinearSegmentedColormap.from_list('mycap', ['#CAE890','#EFEA98','#EFC463','#EB9D39','#DE7905'])
                    if index == '-49':
                        return LinearSegmentedColormap.from_list('mycap', ['#845098','#A164AA','#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249','#86CAD7','#5CA9BB','#2D889B'])
                    if index == '-48':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249','#86CAD7','#5CA9BB','#2D889B'])
                    if index == '-47':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A','#31A054','#0E9249'])
                    if index == '-46':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890','#99CF7B','#61BA6A'])
                    if index == '-45':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463','#EFEA98','#CAE890'])
                    if index == '-44':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905','#EB9D39','#EFC463'])
                    if index == '-43':
                        return LinearSegmentedColormap.from_list('mycap', ['#740402','#B10239','#ED175D','#F05237','#DE7905'])
                    
                    if index == '59':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#CACACA','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801','#AA21A3','#DA2DD3','#FB39FA','#FED5FD'])
                    if index == '58':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801','#AA21A3','#DA2DD3','#FB39FA','#FED5FD'])
                    if index == '57':
                        return LinearSegmentedColormap.from_list('mycmap', ['#EEEEEE','#9DFEFF','#01D1FD','#00A5FD','#0177FD','#26A41C','#00FB30','#FDFD32','#FFD329','#FFA71F','#FFA71F','#DA2304','#AA1801'])
                    
                    if index == '-59':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD','#9DFEFF','#EEEEEE'])
                    if index == '-58':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD','#9DFEFF'])
                    if index == '-57':
                        return LinearSegmentedColormap.from_list('mycmap', ['#FED5FD','#FB39FA','#DA2DD3','#AA21A3','#AA1801','#DA2304','#FFA71F','#FFA71F','#FFD329','#FDFD32','#00FB30','#26A41C','#0177FD','#00A5FD','#01D1FD'])


                    if index == '69':
                        return LinearSegmentedColormap.from_list('mycmap',['#CD6A1A','#E28637','#F3A760','#FFCD81','#FCE09C','#FFF4B7','#FAFAFA','#FAFAFA','#B4FFCB','#5CF0B0','#00BE9F','#41ACC9','#0071B4','#003559']) 
                    if index == '-69':
                        return LinearSegmentedColormap.from_list('mycmap',['#003559','#0071B4','#41ACC9','#00BE9F','#5CF0B0','#B4FFCB','#FAFAFA','#FAFAFA','#FFF4B7','#FCE09C','#FFCD81','#F3A760','#E28637','#CD6A1A'])                                            
                                                                        
                    if index == '79': #ECMWF Blue~Red
                        return LinearSegmentedColormap.from_list('mycmap',['#CBBEEC','#F295CD','#AE3E77','#7F116B','#6B22AB','#1240AF','#437AC4','#ADCAE5','#FFFFFF','#EBA4A0','#D75E5D','#AC1317','#6C0403','#BE5820','#E0A06E','#E3D8C9','#AC9D9B'])
                    if index == '-79':
                        return LinearSegmentedColormap.from_list('mycmap',['#AC9D9B','#E3D8C9','#E0A06E','#BE5820','#6C0403','#AC1317','#D75E5D','#EBA4A0','#FFFFFF','#ADCAE5','#437AC4','#1240AF','#6B22AB','#7F116B','#AE3E77','#F295CD','#CBBEEC'])
                    
                    if index == '89':
                        return LinearSegmentedColormap.from_list('mycmap',['#3A0300','#703922','#A56F44','#785732','#483C1F','#9A917F','#FFFFFF','#79B494','#3C9262','#1B696B','#0D507A','#354778','#724172'])
                    if index == '-89':
                        return LinearSegmentedColormap.from_list('mycmap',['#724172','#354778','#0D507A','#1B696B','#3C9262','#79B494','#FFFFFF','#9A917F','#483C1F','#785732','#A56F44','#703922','#3A0300'])

                    if index == '99':
                        return LinearSegmentedColormap.from_list('mycmap',['#8C5338','#CD6A1A','#E28637','#F3A760','#FFCD81','#FFF4B7','#EEEEEE','#EEEEEE','#B4FFCB','#56E0A5','#00BE9F','#41ACC9','#0071B4','#003559'])
                    if index == '-99':
                        return LinearSegmentedColormap.from_list('mycmap',['#003559','#0071B4','#41ACC9','#00BE9F','#56E0A5','#B4FFCB','#EEEEEE','#EEEEEE','#FFF4B7','#FFCD81','#F3A760','#E28637','#CD6A1A','#8C5338'])
                
                    if index == '109':
                        return LinearSegmentedColormap.from_list('mycmap',['#400000','#7D0204','#4B0077','#A401E6','#0102FB','#014BAA','#016EFF','#72B2D6','#97DAF4','#BEFFE8','#F5F5F5','#EFFDCA','#FEE183','#FB9001','#EF5E03','#E40004','#BB022E','#8A0220','#7A021C','#7A021C','#75021C'])
                    if index == '-109':
                        return LinearSegmentedColormap.from_list('mycmap',['#75021C','#7A021C','#7A021C','#8A0220','#BB022E','#E40004','#EF5E03','#FB9001','#FEE183','#EFFDCA','#F5F5F5','#BEFFE8','#97DAF4','#72B2D6','#016EFF','#014BAA','#0102FB','#A401E6','#4B0077','#7D0204','#400000'])
                    
                    if index == '119':
                        return LinearSegmentedColormap.from_list('mycmap',['#FFFFFF','#CECECE','#A1A1A1','#717171','#444444','#7747D0','#380C66','#7c0341'])
                    if index == '-119':
                        return LinearSegmentedColormap.from_list('mycmap',['#7c0341','#380C66','#7747D0','#444444','#717171','#A1A1A1','#CECECE','#FFFFFF'])
                
                    if index == '129':
                        return LinearSegmentedColormap.from_list('mycmap',['#EDEDED','#BBF3AA','#FDFF04','#DA9E3A','#F45855','#800025'])
                    if index == '-129':
                        return LinearSegmentedColormap.from_list('mycmap',['#800025','#F45855','#DA9E3A','#FDFF04','#BBF3AA','#EDEDED'])       

                    if index == '139':
                        return LinearSegmentedColormap.from_list('mycmap',['#F8BAC5','#EB95DD','#DF71F4','#9157DB','#484FB8','#004693','#2874C6','#64B7F8','#8CE3F6','#F0F0F0','#FEEAA0','#FDB365','#EF633E','#C21C26','#BA4355','#F18DB2','#CB86A4','#98656C','#69452A'])
                    if index == '-139':
                        return LinearSegmentedColormap.from_list('mycmap',['#69452A','#98656C','#CB86A4','#F18DB2','#BA4355','#C21C26','#EF633E','#FDB365','#FEEAA0','#F0F0F0','#8CE3F6','#64B7F8','#2874C6','#004693','#484FB8','#9157DB','#DF71F4','#EB95DD','#F8BAC5'])
                
                    if index == '149':
                        return LinearSegmentedColormap.from_list('mycmap',['#D9BFED','#B28DE4','#071A91','#A5D4FB','#F5F5F5','#FF9C33','#790000','#FF0000','#F5A595'])
                    if index == '-149':
                        return LinearSegmentedColormap.from_list('mycmap',['#F5A595','#FF0000','#790000','#FF9C33','#F5F5F5','#A5D4FB','#071A91','#B28DE4','#D9BFED'])
                    
                    if index == '159':
                        return LinearSegmentedColormap.from_list('mycmap',['#C60042','#8A0001','#952C14','#9C431F','#A86E34','#DB9C1A','#FFDE00','#FFF980','#F0F0F0','#80F180','#00DC00','#00B64B','#009496','#00ACC1','#00D8FF','#6E92D2','#9379C3'])
                    if index == '-159':
                        return LinearSegmentedColormap.from_list('mycmap',['#9379C3','#6E92D2','#00D8FF','#00ACC1','#009496','#00B64B','#00DC00','#80F180','#F0F0F0','#FFF980','#FFDE00','#DB9C1A','#A86E34','#9C431F','#952C14','#8A0001','#C60042'])
                                        
            except: # TypeError: invalid index
                raise TypeError(f"\033[41m[pymeili Error]\033[0m Invalid cmap index: {index}")
        else: 
            return index

