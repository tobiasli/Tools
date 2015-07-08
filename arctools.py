# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
'''
-------------------------------------------------------------------------------
Name:       arctools
Purpose:    Module with powerful tools built on top of standard arcpy
            functionality.

Author:     Tobias Litherland

Created:    17.12.2014
Copyright:  (c) Tobias Litherland 2014, 2015

-------------------------------------------------------------------------------

 Milestones:
    02.06.2015  TL  Added method create_filled_contours, which creates filled
                    contours for a specified set of contour levels.
    01.06.2015  TL  Added handling of grouped dictionaries in dictToTable.
    05.03.2015  TL  Canceled development of changeFieldOrder. The operation
                    is too complex and prone to errors, and the manual job
                    for a given table is not that hard. Maybe.
    05.03.2015  TL  Added property overwriteExistingOutput which controls
                    whether errors are raised if output allready exists.
    05.03.2015  TL  Added history. Current methods are:
                        dictToTable
                        tableToDict
                        renameFields (new)
                        changeFieldOrder (new)

-------------------------------------------------------------------------------

 Future improvements:
    - Rewrite functions to agree with PEP8.
    - Add "sortField" argument to tableToDict to allow sorted output based on a
        field.
    - Objectify module so it accepts a pre-loaded arcpy instance.

-------------------------------------------------------------------------------
'''
import os
import re
import datetime
import arcpy
import time
from collections import OrderedDict,Counter

# Properties
overwriteExistingOutput = False #True allows methods to overwrite existing output.

def dictToTable(dictionary, tablePath, table, method = 'insert', keyField = None, tableKey = None, fields = [],makeTable = False,featureClassType = '', spatialReference = ''):
    '''
    Method for taking a dictionary and writing the values to a given table
    assuming that dictionary keys and table fields match. Can also perform
    update/insert/delete operations according to the values of method.

    All sub-dictionaries in dictionary must have fields in the same order.

    To be able to handle feature klasses, the dictionary must contain a "SHAPE"
    or "SHAPE@[argument]" field.

    Input
        dictionary      dict/list Dictionary of dictionaries or list of
                                dictionaries which is inserted into table.
                                Assumes that key names and value types match table schema.
        tablePath       str     Path to the table that data is inserted
                                into.
        table           str     Assumes that key names and value types match
                                table schema.
        method          str     String defining operation performed on
                                table.
                                    insert = Append dictionary to table.
                                    update = Overwrite rows using dictionaryKey
                                             and tableKey to identify what rows
                                             to update.
                                    delete = Delete rows using dictionaryKey
                                             and tableKey to identify what rows
                                             to remove.
        keyField        str     Name of the field that contains unique id's
                                that are matched to the values of tableKey.
                                Data type of the field is arbitrary.
        tableKey        str     Name of the field that contains unique id's
                                that are matched to the values of
                                dictionaryKey. Data type of the field is
                                arbitrary. If left out it is assumed to be the
                                same as keyField.
        fields          list    List of fields from dictionary that should
                                be entered into table. If left empty method
                                will map all dictionary fields to table.
        makeTable       logic   True will recreate existing table according
                                to apparent data model of dictionary. False
                                will add to existing table, and fail if
                                table does not exist.
        featureClassType str    The type of feature class created. If empty,
                                queries the type property of the shape geometry.
        spatialReference bin    All valid identifiers of a spatial reference,
                                by name, ID or object.

    Output
        count           int     Report the numbers of rows written to the
                                table.
    '''

    arcpy.env.overwriteOutput = overwriteExistingOutput

    dictionaryKey = keyField
    if not tableKey: #If fields are the same, you only need to specify one key field.
        tableKey = dictionaryKey

    assert not (method == 'update' and not (dictionaryKey and tableKey))
    assert not (method == 'delete' and not (dictionaryKey and tableKey))
    assert dictionary

    shapeIdentification = '^shape(@\w*)?$'

    #Get the field names from the first list in the
    islist = False
    isdict = False
    isgroupeddict = False
    #Straight list of dictionaries:
    if isinstance(dictionary,list) and isinstance(dictionary[0],dict) and isinstance(dictionary,tuple):
        islist = True
        dictionaryFrame = dictionary[0]
    #Dictionary of dictionaries:
    elif (isinstance(dictionary,dict) or isinstance(dictionary,OrderedDict)) and (isinstance(dictionary.values()[0],dict) or isinstance(dictionary.values()[0],OrderedDict)):
        isdict = True
        dictionaryFrame = dictionary.values()[0]
    #Dictionary of grouped dictionaries (dictionary with a list of dictionaries that usually have a common attribute.
    elif (isinstance(dictionary,dict) or isinstance(dictionary,OrderedDict)) and (isinstance(dictionary.values()[0],list) or isinstance(dictionary.values()[0],tuple)) and (isinstance(dictionary.values()[0][0],dict) or isinstance(dictionary.values()[0][0],OrderedDict)):
        isgroupeddict = True
        dictionaryFrame = dictionary.values()[0][0]
    else:
        raise Exception('Unknown structure for input argument [dictionary].')

    dictionaryFields = dictionaryFrame.keys()

    #Convert dictionaries and grouped dictionaries to lists for entry as table rows:
    if isdict:
        dictionary = [row for row in dictionary.values()]
    if isgroupeddict:
        dictionary = [item for sublist in dictionary.values() for item in sublist]

    #Check integrity of fields, and create new dictionary containing only the selected fields.
    if fields:
        if isinstance(fields,str):
            fields = [fields]
        for field in fields:
            if not field in dictionaryFields:
                raise Exception('Field input %s is not present in dictionary.',field)

        dictionaryFields = fields

        dict2 = []
        for d in dictionary:
            dict2 += [{k:v for k,v in d.items() if k in dictionaryFields}]
        dictionary = dict2

    #Check if dictionary is a feature class
    featureClass = False
    for field in dictionaryFields:
        if re.findall(shapeIdentification,field.lower()):
            featureClass = True
            if not featureClassType:
                if hasattr(dictionaryFrame[field],'type'):
                    featureClassType = dictionaryFrame[field].type
                else:
                    raise Exception('featureClassType argument not passed, and input dictionary shape field %s does not have a type attribute' % field)

            if not spatialReference:
                if hasattr(dictionaryFrame[field],'spatialReference'):
                    spatialReference = dictionaryFrame[field].spatialReference
                else:
                    raise Exception('spatialReference argument not passed, and input dictionary shape field %s does not have a spatialReference attribute' % field)

    #Create table/feature class if makeTable == True.
    if makeTable:
        if arcpy.Exists(os.path.join(tablePath,table)) and overwriteExistingOutput:
            arcpy.Delete_management(os.path.join(tablePath,table))

        if featureClass:
            arcpy.CreateFeatureclass_management(tablePath,table,geometry_type = featureClassType, spatial_reference = spatialReference)
        else:
            arcpy.CreateTable_management(tablePath,table)

        #Loop through key/value pairs and create fields according to the contents
        #of the first item in the dictionary. Default field type is text if
        #nothing else is found.
        for k,v in dictionaryFrame.items():
            fieldType = 'TEXT'
            length = ''
            if re.findall(shapeIdentification,k):
                continue #Skip create field if shape.
            elif k == 'GLOBALID':
                fieldType = 'GUID'
            elif isinstance(v,int):
                fieldType = 'LONG'
            elif isinstance(v,str) or isinstance(v,unicode):
                if len(v) > length:
                    length = len(v)
            elif isinstance(v,float):
                fieldType = 'DOUBLE'
            elif isinstance(v,datetime.datetime):
                fieldType = 'DATE'
            try:
                arcpy.AddField_management(os.path.join(tablePath,table),k,fieldType,field_length = length)
            except:
                if k.lower() == 'objectid':
                    continue
                else:
                    Exception('Failed to create field %s of type %s in table %s',(k,fieldType,table))


    tableFieldNames = [field.name for field in arcpy.ListFields(os.path.join(tablePath,table))]

    operationCount = 0

    for field in dictionaryFields: #Get the fields from the first entry in the dictionary.
        if not field in tableFieldNames:
            Exception('Dictionary field %s is not present in table %s.',[field,table])

    if method == 'insert':
        with arcpy.da.InsertCursor(os.path.join(tablePath,table),dictionaryFields) as cursor:
            for d in dictionary:
                values = [d[key] for key in cursor.fields]
                operationCount += 1
                cursor.insertRow(values)

    elif method == 'update':
        with arcpy.da.UpdateCursor(os.path.join(tablePath,table),dictionaryFields) as cursor:
            for row in cursor:
                t = dict(zip(dictionaryFields,row))
                for d in dictionary:
                    if t[tableKey] == d[dictionaryKey]:
                        operationCount += 1
                        cursor.updateRow([d[key] for key in cursor.fields])

    elif method == 'delete':
        with arcpy.da.UpdateCursor(os.path.join(tablePath,table),dictionaryFields) as cursor:
            for row in cursor:
                t = dict(zip(dictionaryFields,row))
                for d in dictionary:
                    if t[tableKey] == d[dictionaryKey]:
                        operationCount += 1
                        cursor.deleteRow()
    else:
        Exception('Operation %s not valid. Valid options are "insert","update" and "delete".',method)

    return operationCount

def tableToDict(table,sqlQuery = '', keyField = None, groupBy = None, fields = []):
    '''
    Method for creating a dictionary or a list from a table. With only 'table'
    as input, the method will return a list containing dictionaries for each
    table row, with keys matching the column names of the table. If keyField
    is passed, the method will return a dictionary using the values of column
    [keyField] as dictionary keys.

    If table is a feature class and fields is empty, the SHAPE@ token is used
    to return the entire geometry.

    Input
          table           str     Path to the table that is converted to a
                                  python dictionary.
          sqlQuery        str     SQL query to perform a selection of the data
                                  within the table.
          keyField        str     Name of column containing non-empty, unique
                                  values identifying each row. If non-unique,
                                  rows are grouped according to the values of
                                  this column.
          groupBy         str     Column name containing values that all rows
                                  are grouped by.
          fields          list    List of field names that should be included
                                  in dictionary. Default gets all fields.

    Output
          output          dict/list   Dictionary or list, depending on wether
                                      keyField is passed as an argument or
                                      not.
    '''

    arcpy.env.overwriteOutput = overwriteExistingOutput

    output = list()

    if keyField and groupBy:
        Exception('Method takes either keyField or groupBy, not both.')

    if keyField or groupBy:
        output = OrderedDict()

    if keyField:
        #Check if contents of field is unique:
        uniqueList = []
        with arcpy.da.SearchCursor(table,keyField,where_clause = sqlQuery) as cursor:
            for row in cursor:
                uniqueList += row
        if not len(set(uniqueList)) == len(uniqueList):
            Exception('When keyField is used as input, the column needs to have unique values. To group rows by the contents of a column, use groupBy.')


    if fields:
        if isinstance(fields,str):
            fields = [fields]
    else:
        fields = [field.name for field in arcpy.ListFields(table)]

        for index,field in enumerate(fields):
            if field.lower() == 'shape':
                fields[index] = field + '@'

    with arcpy.da.SearchCursor(table,fields,where_clause = sqlQuery) as cursor:
        for row in cursor:
            dictRow = OrderedDict(zip(fields,row))

            if keyField:
                output[dictRow[keyField]] = dictRow
            elif groupBy:
                if not output.has_key(dictRow[groupBy]):
                    output[dictRow[groupBy]] = []

                output[dictRow[groupBy]] += [dictRow]
            else:
                output += [dictRow]

    return output

def create_filled_contours(raster,output_feature_class,explicit_contour_list,create_complete_polygons = False,raster_edge_crop_distance = 10):

    '''
    Method for creating filled contours for a specified list of contours.

    NB: Method will only work if the DEM is +1 contour higher in elevation than
    values in the explicit_contour_list.

    Input
          raster                raster  Raster dataset for which the values are
                                        calculated.
          output_feature_class  f.class The feature class to store the output
                                        polygons.
          explicit_contour_list list/float    A list containing the specific levels of
                                        every contour or a value for a single contour.

    '''

    if not isinstance(explicit_contour_list,list):
        explicit_contour_list = [explicit_contour_list]

    # We want an immutable list, so we convert to a tuple:
    explicit_contour_list = tuple(explicit_contour_list)

    # Add an additional explicit_contour to list. The additional contour helps
    # with creating the polygons. The additional contour is +1 of the regular
    # contour intervals over the topmost contour.
    regular_delta = Counter([j-i for i, j in zip(explicit_contour_list[:-1], explicit_contour_list[1:])]).most_common(1)[0][0]

    explicit_contour_list = explicit_contour_list + (explicit_contour_list[-1]+regular_delta,)

    contour_line = r'in_memory\arctools_contour_line'
    fishnet_line= r'in_memory\arctools_fishnet_line'
    polygons_raw = r'in_memory\polygons_raw'
    polygon_raster_mean = r'in_memory\polygon_raster_mean'
    polygons = r'in_memory\polygons'
    contour_merge_line = r'in_memory\arctools_contour_merge_line'
    contour_merge_line_buffer = r'in_memory\contour_merge_line_buffer'
    buffer_centroid = r'in_memory\buffer_centroid'
    level_join_polygons = r'in_memory\arctools_level_join_polygons'
    level_lyr = 'level_lyr'


#### Debug storage:
##    contour_line = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\arctools_contour_line'
##    fishnet_line= r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\arctools_fishnet_line'
##    polygons_raw = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\polygons_raw'
##    polygon_raster_mean = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\polygon_raster_mean'
##    polygons = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\polygons'
##    contour_merge_line = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\arctools_contour_merge_line'
##    contour_merge_line_buffer = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\contour_merge_line_buffer'
##    buffer_centroid = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\buffer_centroid'
##    level_join_polygons = r'M:\GIS_Data\Hydrology\Projects\Reservoir_profile_builder\data.gdb\arctools_level_join_polygons'
####


    print 'Create contours'
    arcpy.CheckOutExtension('Spatial')
    arcpy.sa.ContourWithBarriers(raster,contour_line,explicit_only = True, in_explicit_contours = explicit_contour_list)
    arcpy.CheckInExtension('Spatial')


    print 'Create fishnet'
    desc = arcpy.Describe(raster)
    XMin = desc.extent.XMin+desc.meanCellWidth
    XMax = desc.extent.XMax-desc.meanCellWidth
    YMin = desc.extent.YMin+desc.meanCellHeight
    YMax = desc.extent.YMax-desc.meanCellHeight
    arcpy.env.overwriteOutput = True
    arcpy.CreateFishnet_management(out_feature_class=fishnet_line, origin_coord='%0.4f %0.4f' % (XMin,YMin), y_axis_coord='%0.4f %0.4f' % (XMin,YMin+10), cell_width="0", cell_height="0", number_rows="1", number_columns="1", corner_coord='%0.4f %0.4f' % (XMax,YMax), labels="LABELS", template='%0.4f %0.4f %0.4f %0.4f' % (XMin,YMin,XMax,YMax), geometry_type="POLYLINE")
    arcpy.DefineProjection_management(fishnet_line,desc.spatialReference)

    print 'Merge'
    arcpy.env.overwriteOutput = True
    arcpy.Merge_management(inputs=';'.join([contour_line,fishnet_line]), output=contour_merge_line, field_mappings="""Contour "Contour" true true false 8 Double 0 0 ,First,#,%(contour_line)s,Contour,-1,-1;Type "Type" true true false 4 Long 0 0 ,First,#,%(contour_line)s,Type,-1,-1;;Shape_Length "Shape_Length" false true true 8 Double 0 0 ,First,#,%(contour_line)s,Shape_Length,-1,-1,%(fishnet_line)s,Shape_Length,-1,-1""" % {'fishnet_line':fishnet_line,'contour_line':contour_line})

    print 'Feature to polygon'
    arcpy.FeatureToPolygon_management(in_features=contour_merge_line, out_feature_class=polygons_raw, cluster_tolerance="", attributes="ATTRIBUTES", label_features="")

    arcpy.AddField_management(polygons_raw,'Contour','DOUBLE')

    poly_oid_name = arcpy.Describe(polygons_raw).OIDFieldName


    # Get the average elevation of each polygon, map these to their
    # corresponding contour elevation, and use the OBJECTID to map these back to
    # the polygon data. This process is 50x times faster than Spatial Join.
    print 'Zonal statistics'
    start = time.clock()
    arcpy.CheckOutExtension('Spatial')
    arcpy.gp.ZonalStatisticsAsTable_sa(polygons_raw, poly_oid_name, raster, polygon_raster_mean, "DATA", "MEAN")
    arcpy.CheckInExtension('Spatial')
    stop = time.clock()

    table_oid_name = arcpy.Describe(polygon_raster_mean).OIDFieldName

    table_dict = tableToDict(polygon_raster_mean,keyField = poly_oid_name + '_')

    bottom = explicit_contour_list[:-1]
    top = explicit_contour_list[1:]

    #Reclassify mean raster values to contour values:
    for k in table_dict:
        if table_dict[k]['MEAN'] > explicit_contour_list[-1]:
            table_dict[k]['MEAN'] = explicit_contour_list[-1]
            print 'nisse'
        elif table_dict[k]['MEAN'] < explicit_contour_list[0]:
            table_dict[k]['MEAN'] = explicit_contour_list[0]
            print 'troll'
        else:
            for b,t in zip(bottom,top):
                if table_dict[k]['MEAN']>=b and table_dict[k]['MEAN']<t:
                    table_dict[k]['MEAN'] = t
                    break

    #Insert contour values to polygon data:
    found_warning = False
    with arcpy.da.UpdateCursor(polygons_raw,[poly_oid_name,'Contour'])as cursor:
        for row in cursor:
            if not row[0] in table_dict:
                row[1] = None #Polygons that where too small to get a raster value from Zonal Statistics. Handled later.
                found_warning = True
            else:
                row[1] = table_dict[row[0]]['MEAN']
            cursor.updateRow(row)

    if found_warning:
        print 'WARNING: Some contours were too close together to be handled properly. Check Contour = None in resulting table.'

    print 'Homebrew Spatial Join: %0.2f seconds' % (stop-start)
    print 'Regular Spatial Join: %0.2f seconds' % 19473
    print 'Improvement: %0.0fx' % (19473/(stop-start))

    if isinstance(output_feature_class,arcpy.Geometry):
        return arcpy.CopyFeatures_management(polygons_raw,arcpy.Geometry())
    elif isinstance(output_feature_class,list):
        return tableToDict(polygons_raw) # Will pass output as a list when no keyField is passed as an argument.
    else:
        arcpy.CopyFeatures_management(polygons_raw,output_feature_class)

def changeFieldOrder(table,newTable,orderedFieldList):
    '''
    This method can reorder the fields in a table. All fields in
    orderedFieldList must exist in the table, and the method then changes the
    order of the table fields in accordance with the list.

    orderedFieldList does not have to contain all the fields in the table; the
    fields not specified will be moved to the head of the list.

    Input:
        table               str         path specifying the table or feature
                                        class.
        orderedFieldList    list(str)   names of existing fields in table.

    Output:
        newFieldList        list(str)   new complete list of field names in
                                        table.


    The way to handle this would be to make a new table with the correct fields,
    and copy all the data to the new table with a field mapping.
    '''

    shapeIdentification = '^shape(@\w*)?$'

    desc = arcpy.Describe(table)
    desc.hasM
    desc.hasZ
    desc.shapeType
    desc.featureType

    arcpy.env.overwriteOutput = overwriteExistingOutput

    fields = arcpy.ListFields(table)

    fieldCheck = False
    if isinstance(orderedFieldList[0],arcpy.Field):
        fieldCheck = True

    for of in orderedFieldList:
        if fieldCheck:
            name = of.name
        else:
            name = of
        if not name in [f.name for f in fields]:
            raise Exception('Field %s not found in table %s' % (of.name,table))

    newFields = []
    for of in orderedFieldList:
        if fieldCheck:
            name = of.name
        else:
            name = of
        for f in fields:
            if f.name == name:
                newFields += [f]

    if desc.datatype == u'FeatureClass':
        arcpy.CreateFeatureclass_management(os.path.realpath(newTable),os.path.basename(newTable),geometry_type=desc.shapeType,has_m=desc.hasM,has_z=desc.hasZ,spatial_reference=desc.spatialReference)
    else:
        arcpy.CreateTable_management(os.path.realpath(newTable),os.path.basename(newTable))


    for nf in newFields:
        if not nf.name.lower() == 'objectid':
            arcpy.AddField_management(newTable,nf.name,nf.type,)

    #CONTINUE HERE



def renameFields(table,newTable,fieldMappingDict):
    '''
    Method for batch-renaming fields in a table.

    For easy of coding, this method uses dictToTable and tableToDict in
    sequence, renaming the keys in the dictionary in between the operations.

    Input:
        table               str         path specifying the table or feature
                                        class to rename fields in.
        newTable            str         path specifying the resulting table or
                                        feature class. Can be the same as input
                                        table. In that case, input table is
                                        deleted before write operation.
        fieldMappingDict    dict(str)   dictionary with key/value pairs
                                        representing current/new field names.

    Output:
        newFieldList        list(str)   new complete list of field names in
                                        table.
    '''

    arcpy.env.overwriteOutput = overwriteExistingOutput

    old = tableToDict(table)

    new = []
    for row in old:
        new += [OrderedDict()]
        for k,v in row.items():
            if k in fieldMappingDict:
                k = fieldMappingDict[k]
            new[-1][k] = v

    if overwriteExistingOutput or table == newTable:
        try:
            arcpy.Delete_management(newTable)
        except:
            pass

    dictToTable(new, os.path.split(newTable)[0], os.path.split(newTable)[1], method = 'insert', makeTable = True)



if __name__ == '__main__':
    print('Module run from file. Test commencing.')

    overwriteExistingOutput = True
    path = 'M:\\GIS_Data\\Hydrology\\Personal_folders\\Tobias\\arctools_test\\arc_test.gdb'
    old = 'test'
    new = 'test2'
    fieldMapping = {'b':'second_field','nisse':'fjes'}

    a = tableToDict(os.path.join(path,old))
    print('Before rename:')
    print a

    print('\nField mapping:')
    print(fieldMapping)

    renameFields(os.path.join(path,old),os.path.join(path,new),fieldMapping)

    b = tableToDict(os.path.join(path,new))
    print('\nAfter rename')
    print(b)