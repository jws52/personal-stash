"""make up some colormaps for your custom
check http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors

def custom_colors(word):	 
   darkblue='#0000A0'
   midnightblue='#151B54'
   bla='#313695'
   blb='#4575B4'
   blc='#74ADD1'
   bld='#ABD9E9'
   ble='#E0F3F8'
   blue1 = '#0000CC'
   blue2 = '#000099'
   turquoise='#43C6DB'
   lightblue='#ADDFFF'
   oceanblue='#2B65EC'
   gold='#FFD700'
   darkorange='#FF8C00'
   mustard='#FFDB58'
   saffron='#FBB917'
   cantaloupe='#FFA62F'
   Scarlet='#FF2400'
   orangered='#FF4500'
   redwine='#990012'
   burgundy='#8C001A'
   firebrick='#800517'
   darkred='#8B0000'
   if word =='verycold_to_verywarm':
      var = colors.LinearSegmentedColormap.from_list('my_cmap',[midnightblue,darkblue,'blue','white','red',redwine,burgundy],256)
      return var
   elif word == 'cold_to_warm':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',[midnightblue,darkblue,'blue',lightblue,\
       'white',Scarlet,'red',redwine,firebrick],256)
       return var
   elif word == 'avoid_green':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',[midnightblue,darkblue,blue1,'blue',oceanblue,lightblue,'white','yellow',saffron,'orange','red',redwine,burgundy],256)
       return var
   elif word == 'grads':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',[midnightblue,bla,blb,blc,bld,ble,gold,'orange',darkorange,orangered,'red',darkred],256)
       return var
   elif word == 'warm':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',[ble,'white',gold,'orange',darkorange,orangered,'red',darkred],256)
       print var
       return var
   elif word == 'separate':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',[midnightblue,turquoise,redwine,gold,blb,'orange',lightblue,darkorange,blue2,'red',mustard,darkred],256)
       return var
   elif word == 'default':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#fee090','#fdae61','#f46d43','#d73027','#a50026'],256)
#       var = colors.LinearSegmentedColormap.from_list('my_cmap',['#313695','#4575b4','#74add1','#abd9e9','#e0f3f8','#ffffbf','#fee090','#fdae61','#f46d43','#d73027','#a50026'],256)
       return var
   elif word == 'brown_to_green':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',['#8c510a','#bf812d','#dfc27d','#f6e8c3','#f5f5f5','#c7eae5','#80cdc1','#35978f','#01665e'],256)
       return var
   elif word == 'green_hue':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',['#f7fcf5','#e5f5e0','#c7e9c0','#a1d99b','#74c476','#41ab5d','#238b45','#006d2c','#00441b'],256)
       return var
   elif word == 'OrRd':
       var = colors.LinearSegmentedColormap.from_list('my_cmap',['#fef0d9','#fdd49e','#fdbb84','#fc8d59','#ef6548','#d7301f','#990000'],256)
       return var
   else:
      raise Exception, "Your choice is not yet specified - if you have an idea: add it to the code in colors_peer.py!"
   del var,darkblue,midnightblue,blue1,blue2,turquoise,lightblue,oceanblue,mustard,saffron,cantaloupe,redwine,burgundy

def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to 
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

