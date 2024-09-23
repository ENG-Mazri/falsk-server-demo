from flask import Flask, flash, request, redirect, url_for, Blueprint, render_template, send_file
from fileinput import filename
import ifcopenshell
import blueprints.ifc.processors.ifcMetaDataProcessor as MetaData
import ifcpatch
import utils.logger as Logger
import numpy as np
import base64
import os
import zipfile
import utils.filesManager as FilesManager

ifc_bp = Blueprint("IFC BP", __name__, template_folder="templates")

@ifc_bp.route("/ifc")
def ifc(): 
    return 'Hi ifc...'

@ifc_bp.route("/exportIfc", methods=['POST'])
def exportHandler():
    
    file = request.files['file'] 
    file.save('assets/model.ifc')
    model = ifcopenshell.open('assets/model.ifc')

    metaDataProcessor = MetaData.IfcMetaDataProcessor(model)
    data = metaDataProcessor.getElemmentsByStorey()

    return data


@ifc_bp.route("/ifc/extract", methods=['POST'])
def extractHandler():
    
    file = request.files['file'] 
    category = request.form.get('category')
    file.save('assets/model.ifc')
    name = file.filename
    assets_path = os.path.join(os.getcwd(), "assets")

    # try:
    output = ifcpatch.execute({
        "input": "assets/model.ifc",
        "file": ifcopenshell.open("assets/model.ifc"),
        "recipe": "ExtractElements",
        "arguments": [category],
    })

    output.write("assets/output.ifc", zipped=False)

    f = open("assets/output.ifc", 'rb')
    blob_data = f.read()
    byte_array = bytearray(blob_data)
    # f = open("assets/output.ifc", 'rb')
    # data = np.frombuffer(f.read(), dtype=np.uint8)
    f.close()
    Logger.success("Extracting finished!")
    encoded_data = base64.b64encode(bytes(byte_array)) # Encode bytearray to base64
    FilesManager.deleteDirContent(assets_path)
    return encoded_data
    # return send_file("assets/output.ifc", download_name=name, mimetype='application/x-step', as_attachment=True)
    # except Exception as error:
    #     Logger.error("Error when extracting from model :(")


@ifc_bp.route("/ifc/split", methods=['POST'])
def splitHandler():
    
    file = request.files['file'] 
    filter = request.form.get('filter')
    file.save('assets/model.ifc')
    name = file.filename
    assets_path = os.path.join(os.getcwd(), "assets")
    # FilesManager.deleteDirContent(assets_path)
    # try:
    ifcpatch.execute({
        "input": "assets/model.ifc",
        "file": ifcopenshell.open("assets/model.ifc"),
        "recipe": "SplitByBuildingStorey",
        "arguments": [assets_path],
    })


    with zipfile.ZipFile('assets/stories.zip', 'w') as zipped_f:
        for filename in os.listdir(assets_path):
            if filename in ["model.ifc", "output.ifc", "stories.zip"]:
                continue

            file_path = os.path.join(assets_path, filename) 
            file = open(file_path, 'rb')
            blob_data = file.read()
            data = bytearray(blob_data)
            zipped_f.writestr(filename, data)
            file.close()

    # ifcpatch.write(output) 

    # output.write("assets/output.ifc", zipped=False)

    f = open("assets/stories.zip", 'rb')
    blob_data = f.read()
    byte_array = bytearray(blob_data)
    f.close()
    Logger.success("Splitting finished!")
    encoded_data = base64.b64encode(bytes(byte_array))
    
    FilesManager.deleteDirContent(assets_path)
    return encoded_data


@ifc_bp.route("/ifc/upgrade", methods=['POST'])
def upgradeHandler():
    
    file = request.files['file'] 
    to_schema = request.form.get('schema')
    file.save('assets/model.ifc')
    name = file.filename
    assets_path = os.path.join(os.getcwd(), "assets")

    try: 
        output = ifcpatch.execute({
            "input": "assets/model.ifc",
            "file": ifcopenshell.open("assets/model.ifc"),
            "recipe": "Migrate",
            "arguments": [to_schema],
        })

        ifcpatch.write(output, "assets/output.ifc")
    
        Logger.success("Upgradinging finished!")
    except Exception as error:
        Logger.error("Error when upgrading model :(")
    
    FilesManager.deleteDirContent(assets_path)
    return 'Finished...'



# f = open("assets/output.ifc", 'rb')
# data = np.frombuffer(f.read(), dtype=np.uint8)
# f.close()
