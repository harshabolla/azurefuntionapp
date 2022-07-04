import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient

from .response_header import rh
from ..config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, CUSTOM_MODEL_ID

endpoint = FORM_RECOGNIZER_ENDPOINT
credential = AzureKeyCredential(FORM_RECOGNIZER_KEY)
form_recognizer_client = FormRecognizerClient(endpoint, credential)

model_id = CUSTOM_MODEL_ID


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method == "POST":
        f = req.files.get('File')
        file_uid = req.form['FileUID']
        logging.info("[Processing....]")
		##blob connection
        #connect_str="DefaultEndpointsProtocol=https;AccountName=bhttpnlobtrigger;AccountKey=gcfY1+pW9sLsT0GKlV77T1rJ5LMesD1rv1NyvpoBPaqB/6rVGQ9xcMzT9BpUYOnMlaCB52fzjQuR+AStNVgkHA==;EndpointSuffix=core.windows.net"
        #container="pdfstorage"
        
        ##writing to blob storage:
        #blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        #blob_client = blob_service_client.get_blob_client(container=container,blob = f.filename)
        #blob_client.upload_blob(f,overwrite=True)
        #logging.info('File Stored Successful')
        ## Reading the file
        #with open(path, "rb") as fd:
        #    form = fd.read()
        poller = form_recognizer_client.begin_recognize_custom_forms(model_id=model_id, form=f)
        result = poller.result()
        rh['FileUID'] = file_uid

        for recognized_form in result:
            for name, field in recognized_form.fields.items():
                bb_list = []
                try:
                    for i in range(4):
                        for j in range(2):
                            bb_list.append(field.value_data.bounding_box[i][j])
                except:
                    bb_list = [0,0,0,0,0,0,0,0]
                if name == "Name":
                    try:
                        rh["ExtractedFileData"][0]['EntityName'] = "OptionHolder"
                        rh["ExtractedFileData"][0]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][0]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][0]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][0]['EntityName'] = "OptionHolder"
                        rh["ExtractedFileData"][0]['EntityValue'] = ""
                        rh["ExtractedFileData"][0]['PageNumber'] = ""
                        rh["ExtractedFileData"][0]['boundingBox'] = bb_list

                elif name == "NoPerformanceGranted":
                    try:
                        rh["ExtractedFileData"][1]['EntityName'] = "OptionsGranted"
                        rh["ExtractedFileData"][1]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][1]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][1]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][1]['EntityName'] = "OptionsGranted"
                        rh["ExtractedFileData"][1]['EntityValue'] = ""
                        rh["ExtractedFileData"][1]['PageNumber'] = ""
                        rh["ExtractedFileData"][1]['boundingBox'] = bb_list

                elif name == "Date":
                    try:
                        rh["ExtractedFileData"][2]['EntityName'] = "GrantDate"
                        rh["ExtractedFileData"][2]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][2]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][2]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][2]['EntityName'] = "GrantDate"
                        rh["ExtractedFileData"][2]['EntityValue'] = ""
                        rh["ExtractedFileData"][2]['PageNumber'] = ""
                        rh["ExtractedFileData"][2]['boundingBox'] = bb_list

                elif name == "VestingPeroid":
                    try:
                        rh["ExtractedFileData"][3]['EntityName'] = "VestingEndDate"
                        rh["ExtractedFileData"][3]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][3]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][3]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][3]['EntityName'] = "VestingEndDate"
                        rh["ExtractedFileData"][3]['EntityValue'] = ""
                        rh["ExtractedFileData"][3]['PageNumber'] = ""
                        rh["ExtractedFileData"][3]['boundingBox'] = bb_list

                elif name == "OfferDeclineOrAccept":
                    try:
                        rh["ExtractedFileData"][4]['EntityName'] = "VestingCommencementDate"
                        rh["ExtractedFileData"][4]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][4]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][4]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][4]['EntityName'] = "VestingCommencementDate"
                        rh["ExtractedFileData"][4]['EntityValue'] = ""
                        rh["ExtractedFileData"][4]['PageNumber'] = ""
                        rh["ExtractedFileData"][4]['boundingBox'] = bb_list

                elif name == "empID":
                    logging.info("empID")
                    try:
                        rh["ExtractedFileData"][5]['EntityName'] = "EmployeeId"
                        rh["ExtractedFileData"][5]['EntityValue'] = field.value_data.text
                        rh["ExtractedFileData"][5]['PageNumber'] = field.value_data.page_number
                        rh["ExtractedFileData"][5]['boundingBox'] = bb_list
                    except:
                        rh["ExtractedFileData"][5]['EntityName'] = "EmployeeId"
                        rh["ExtractedFileData"][5]['EntityValue'] = ""
                        rh["ExtractedFileData"][5]['PageNumber'] =  ""
                        rh["ExtractedFileData"][5]['boundingBox'] = bb_list

        return func.HttpResponse(
            json.dumps(rh),
            mimetype="application/json",
        )
