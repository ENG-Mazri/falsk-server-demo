from flask import Flask, flash, request, redirect, url_for, Blueprint, render_template, send_file
from fileinput import filename
import ifcopenshell
import blueprints.ifc.processors.ifcMetaDataProcessor as MetaData
import ifcpatch
import utils.logger as Logger
import numpy as np
import base64
import os

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
    assets_path = os.path.join(os.getcwd(), "assets").replace("\\", "/")
    # try:
    output = ifcpatch.execute({
        "input": "assets/model.ifc",
        "file": ifcopenshell.open("assets/model.ifc"),
        "recipe": "SplitByBuildingStorey",
        "arguments": [assets_path],
    })

    # ifcpatch.write(output)

    # output.write("assets/output.ifc", zipped=False)

    f = open("assets/output.ifc", 'rb')
    blob_data = f.read()
    byte_array = bytearray(blob_data)
    f.close()
    Logger.success("Extracting finished!")
    encoded_data = base64.b64encode(bytes(byte_array))
    return encoded_data


@ifc_bp.route("/ifc/upgrade", methods=['POST'])
def upgradeHandler():
    
    file = request.files['file'] 
    to_schema = request.form.get('schema')
    file.save('assets/model.ifc')
    name = file.filename

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
    

    return 'Finished...'





# f = open("assets/output.ifc", 'rb')
# data = np.frombuffer(f.read(), dtype=np.uint8)
# f.close()
