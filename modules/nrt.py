# nrt
'''
Temp.

Contacts: 
Lewis Trotter: lewis.trotter@postgrad.curtin.edu.au
'''

# import required libraries
import os
import sys
import shutil
import datetime
import xarray as xr
import rasterio

sys.path.append('../../modules')
import cog_odc

sys.path.append('../../shared')
import arc, satfetcher, tools


def create_nrt_project(out_folder, out_filename):
    """
    Creates a new empty geodatabase with required features
    for nrt monitoring tools.
    
    Parameters
    ----------
    out_folder: str
        An output path for new project folder.
    out_filename: str
        An output filename for new project.
    """
    
    # notify
    print('Creating new monitoring project database...')
    
    # check inputs are not none and strings
    if out_folder is None or out_filename is None:
        raise ValueError('Blank folder or filename provided.')
    elif not isinstance(out_folder, str) or not isinstance(out_folder, str):
        raise TypeError('Folder or filename not strings.')
    
    # get full path
    out_filepath = os.path.join(out_folder, out_filename + '.gdb')
    
    # check folder exists
    if not os.path.exists(out_folder):
        raise ValueError('Requested folder does not exist.')
        
    # check file does not already exist
    if os.path.exists(out_filepath):
        raise ValueError('Requested file location arleady exists. Choose a different name.')
    
    # build project geodatbase
    out_filepath = arcpy.management.CreateFileGDB(out_folder, out_filename)
    
    
    # notify
    print('Generating database feature class...')
    
    # temporarily disable auto-visual of outputs
    arcpy.env.addOutputsToMap = False
    
    # create feature class and aus albers spatial ref sys
    srs = arcpy.SpatialReference(3577)
    out_feat = arcpy.management.CreateFeatureclass(out_path=out_filepath, 
                                                   out_name='monitoring_areas', 
                                                   geometry_type='POLYGON',
                                                   spatial_reference=srs)
    
    
    # notify
    print('Generating database domains...')
    
    # create platform domain
    arcpy.management.CreateDomain(in_workspace=out_filepath, 
                                  domain_name='dom_platforms', 
                                  domain_description='Platform name (Landsat or Sentinel)',
                                  field_type='TEXT', 
                                  domain_type='CODED')
    
    # generate coded values to platform domain
    dom_values = {'Landsat': 'Landsat', 'Sentinel': 'Sentinel'}
    for dom_value in dom_values:
        arcpy.management.AddCodedValueToDomain(in_workspace=out_filepath, 
                                               domain_name='dom_platforms', 
                                               code=dom_value, 
                                               code_description=dom_values.get(dom_value))
        
    # create index domain
    arcpy.management.CreateDomain(in_workspace=out_filepath, 
                                  domain_name='dom_indices', 
                                  domain_description='Vegetation index name',
                                  field_type='TEXT', 
                                  domain_type='CODED')
    
    # generate coded values to index domain
    dom_values = {'NDVI': 'NDVI', 'MAVI': 'MAVI', 'kNDVI': 'kNDVI'}
    for dom_value in dom_values:
        arcpy.management.AddCodedValueToDomain(in_workspace=out_filepath, 
                                               domain_name='dom_indices', 
                                               code=dom_value, 
                                               code_description=dom_values.get(dom_value))

    # create year domain
    arcpy.management.CreateDomain(in_workspace=out_filepath, 
                                  domain_name='dom_years', 
                                  domain_description='Training years (1980 - 2050)',
                                  field_type='LONG', 
                                  domain_type='RANGE')
    
    # generate range values to year domain
    arcpy.management.SetValueForRangeDomain(in_workspace=out_filepath, 
                                            domain_name='dom_years', 
                                            min_value=1980, 
                                            max_value=2050)
    
    # create boolean domain
    arcpy.management.CreateDomain(in_workspace=out_filepath, 
                                  domain_name='dom_boolean', 
                                  domain_description='Boolean (Yes or No)',
                                  field_type='TEXT', 
                                  domain_type='CODED')
    
    # generate coded values to boolean domain
    dom_values = {'Yes': 'Yes', 'No': 'No'}
    for dom_value in dom_values:
        arcpy.management.AddCodedValueToDomain(in_workspace=out_filepath, 
                                               domain_name='dom_boolean', 
                                               code=dom_value, 
                                               code_description=dom_values.get(dom_value))
        

    # notify
    print('Generating database fields...') 
    
    # add area id field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='area_id', 
                              field_type='TEXT', 
                              field_alias='Area ID',
                              field_length=200,
                              field_is_required='REQUIRED')
            
    # add platforms field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='platform', 
                              field_type='TEXT', 
                              field_alias='Platform',
                              field_length=20,
                              field_is_required='REQUIRED',
                              field_domain='dom_platforms')    
    
    # add s_year field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='s_year', 
                              field_type='LONG', 
                              field_alias='Start Year of Training Period',
                              field_is_required='REQUIRED',
                              field_domain='dom_years')
    
    # add e_year field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='e_year', 
                              field_type='LONG', 
                              field_alias='End Year of Training Period',
                              field_is_required='REQUIRED',
                              field_domain='dom_years')
    
    # add index field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='index', 
                              field_type='TEXT', 
                              field_alias='Vegetation Index',
                              field_length=20,
                              field_is_required='REQUIRED',
                              field_domain='dom_indices')
    
    # add alert field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='alert', 
                              field_type='TEXT', 
                              field_alias='Alert User',
                              field_length=20,
                              field_is_required='REQUIRED',
                              field_domain='dom_boolean')
    
    # add email field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='email', 
                              field_type='TEXT', 
                              field_alias='Email of User',
                              field_is_required='REQUIRED')
    
    # add last_run field to featureclass   
    arcpy.management.AddField(in_table=out_feat, 
                              field_name='last_run', 
                              field_type='DATE', 
                              field_alias='Last Run',
                              field_is_required='NON_REQUIRED')   
    
    # notify todo - delete if we dont want defaults
    print('Generating database defaults...')  
    
    # set default platform
    arcpy.management.AssignDefaultToField(in_table=out_feat, 
                                          field_name='platform',
                                          default_value='Landsat')   

    # set default index
    arcpy.management.AssignDefaultToField(in_table=out_feat, 
                                          field_name='index',
                                          default_value='MAVI')        

    # set default alert
    arcpy.management.AssignDefaultToField(in_table=out_feat, 
                                          field_name='alert',
                                          default_value='No')    
           
           
    # notify
    print('Creating NetCDF data folder...') 
    
    # create output folder
    out_nc_folder = os.path.join(out_folder, '{}_cubes'.format(out_filename))
    if os.path.exists(out_nc_folder):
        try:
            shutil.rmtree(out_nc_folder)
        except:
            raise ValueError('Could not delete {}'.format(out_nc_folder))

    # create new folder
    os.makedirs(out_nc_folder)
    
    
    # notify
    print('Adding data to current map...') 
    
    # enable auto-visual of outputs
    arcpy.env.addOutputsToMap = True
    
    try:
        # get active map, add feat
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        mp = aprx.activeMap
        mp.addDataFromPath(out_feat)
    
    except:
        arcpy.AddWarning('Could not find active map. Add monitor areas manually.')        
        
    # notify
    print('Created new monitoring project database successfully.')


# checks, dtype, fillvalueto, fillvalue_from need doing, metadata
def sync_nrt_cube(out_nc, collections, bands, start_dt, end_dt, bbox, in_epsg=3577, slc_off=False, resolution=30, ds_existing=None, chunks={}):
    """
    Takes a path to a netcdf file, a start and end date, bounding box and
    obtains the latest satellite imagery from DEA AWS. If an existing
    dataset is provided, the metadata from that is used to define the
    coordinates, etc. This function is used to 'sync' existing cubes
    to the latest scene (time = now). New scenes are appended on to
    the existing cube and re-exported to a new file (overwrite).
    
    Parameters
    ----------
    in_feat: str
        A path to an existing monitoring areas gdb feature class.
    in_epsg: int
        A integer representing a specific epsg code for coordinate system.
      
    """
    
    # checks
    
    # notify
    print('Syncing cube for monitoring area: {}'.format(out_nc))

    # query stac endpoint
    items = cog_odc.fetch_stac_items_odc(stac_endpoint='https://explorer.sandbox.dea.ga.gov.au/stac', 
                                         collections=collections, 
                                         start_dt=start_dt, 
                                         end_dt=end_dt, 
                                         bbox=bbox,
                                         slc_off=slc_off,
                                         limit=250)

    # replace s3 prefix with https for each band - arcgis doesnt like s3
    items = cog_odc.replace_items_s3_to_https(items=items, 
                                              from_prefix='s3://dea-public-data', 
                                              to_prefix='https://data.dea.ga.gov.au')

    # construct an xr of items (lazy)
    ds = cog_odc.build_xr_odc(items=items,
                              bbox=bbox,
                              bands=bands,
                              crs=in_epsg,
                              resolution=resolution,
                              group_by='solar_day',
                              skip_broken_datasets=True,
                              like=ds_existing,
                              chunks=chunks)

    # prepare lazy ds with data type, type, time etc
    ds = cog_odc.convert_type(ds=ds, to_type='int16')  # input?
    ds = cog_odc.change_nodata_odc(ds=ds, orig_value=0, fill_value=-999)  # input?
    ds = cog_odc.fix_xr_time_for_arc_cog(ds)

    # return dataset instantly if new, else append
    if ds_existing is None:
        return ds
    else:
        # existing netcdf - append
        ds_new = ds_existing.combine_first(ds).copy(deep=True)

        # close everything safely
        ds.close()
        ds_existing.close()

        return ds_new

  
# todo - include provisional products too. finish meta
def get_satellite_params(platform=None):
    """
    Helper function to generate Landsat or Sentinel query information
    for quick use during NRT cube creation or sync only.
    
    Parameters
    ----------
    platform: str
        Name of a satellite platform, Landsat or Sentinel only.
    
    params
    """
    
    # check platform name
    if platform is None:
        raise ValueError('Must provide a platform name.')
    elif platform.lower() not in ['landsat', 'sentinel']:
        raise ValueError('Platform must be Landsat or Sentinel.')
        
    # set up dict
    params = {}
    
    # get porams depending on platform
    if platform.lower() == 'landsat':
        
        # get collections
        collections = [
            'ga_ls5t_ard_3', 
            'ga_ls7e_ard_3', 
            'ga_ls8c_ard_3']
        
        # get bands
        bands = [
            'nbart_red', 
            'nbart_green', 
            'nbart_blue', 
            'nbart_nir', 
            'nbart_swir_1', 
            'nbart_swir_2', 
            'oa_fmask']
        
        # get resolution
        resolution = 30
        
        # build dict
        params = {
            'collections': collections,
            'bands': bands,
            'resolution': resolution}
        
    else:
        
        # get collections
        collections = [
            's2a_ard_granule', 
            's2b_ard_granule']
        
        # get bands
        bands = [
            'nbart_red', 
            'nbart_green', 
            'nbart_blue', 
            'nbart_nir_1', 
            'nbart_swir_2', 
            'nbart_swir_3', 
            'fmask']
        
        # get resolution
        resolution = 10
        
        # build dict
        params = {
            'collections': collections,
            'bands': bands,
            'resolution': resolution}        
        
    return params
 