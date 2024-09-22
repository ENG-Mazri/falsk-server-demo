from flask import Flask, flash, request, redirect, url_for, Blueprint, render_template
from fileinput import filename
import ifcopenshell
import blueprints.ifc.processors.ifcMetaDataProcessor as MetaData
import ifcpatch
import utils.logger as Logger

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
    categories = request.form.get('category').split(',')
    file.save('assets/model.ifc')
    name = file.filename

    try:
        output = ifcpatch.execute({
            "input": "assets/model.ifc",
            "file": ifcopenshell.open("assets/model.ifc"),
            "recipe": "ExtractElements",
            "arguments": categories,
        })
        ifcpatch.write(output, "assets/output.ifc")
    
        Logger.success("Extracting finished!") 
    except Exception as error:
        Logger.error("Error when extracting from model :(")
    

    return 'Finished splitting...'


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