import shapefile as shp
import geopandas as gpd

def create_patches (n_x: int, n_y: int, file_directory: str):
    """
    create and saves a shapefile of a grid of polygons

    Parameters
    ----------
    n_x: int
        number of polygons in the x-axis
    n_y: int
        number of polygons in the y-axis
    file_directory: str
        the full directory of the saved file (must end in .shp)
    
    Returns
    -------
    geopandas object
        the geopandas objec read from the saved shapefile
    """
    try:
        w = shp.Writer(rf'{file_directory}')
        w.autoBalance = 1
        w.field('id')
        w.field('i')
        w.field('j')
        id = 0
        x = 0
        y = 0
        dist = 0

        for j in range(n_y):
            x = 0
            y += 1
            for i in range(n_x):
                id += 1
                x += 1
                vertices = []
                parts = []
                vertices.append([i + dist, j + dist])
                vertices.append([i + dist + 1, j + dist])
                vertices.append([i + dist + 1, j + dist + 1])
                vertices.append([i + dist, j + dist + 1])
                parts.append(vertices)
                w.poly(parts)
                w.record(id= id, i= x, j= y)
        
        w.close()
        temp = gpd.read_file(rf'{file_directory}')
        temp['id'] = [int(temp.at[a, 'id']) for a in range(len(temp.index))]
        temp['i'] = [int(temp.at[a, 'i']) for a in range(len(temp.index))]
        temp['j'] = [int(temp.at[a, 'j']) for a in range(len(temp.index))]
        return(temp)
    except:
        if file_directory[-3:] != 'shp':
            print("Error: file directory string does not end in .shp")
        else:
            print("Error: an issue with the input parameters")

