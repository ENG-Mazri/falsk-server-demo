from flask import Flask, flash, request, redirect, url_for, Blueprint, render_template, send_file
from fileinput import filename
import ifcopenshell
import blueprints.ifc.processors.ifcMetaDataProcessor as MetaData
import ifcpatch
import utils.logger as Logger
import numpy as np


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

    output.write("assets/output.ifczip", zipped=True)

    Logger.success("Extracting finished!") 
    return send_file("assets/output.ifczip", download_name=name, mimetype='application/zip', as_attachment=True)
    # except Exception as error:
    #     Logger.error("Error when extracting from model :(")


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
