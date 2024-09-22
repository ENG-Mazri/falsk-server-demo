from flask import Flask, flash, request, redirect, url_for, Blueprint, render_template
from fileinput import filename
import ifcopenshell
import blueprints.ifc.processors.ifcMetaDataProcessor as MetaData


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