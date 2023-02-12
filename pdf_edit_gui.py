import os
import argparse
import codecs
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import DecodedStreamObject, EncodedStreamObject, NameObject
import PySimpleGUI as sg  


def replace_text(content):
    lines = content.splitlines()

    result = ""
    in_text = False
    repair_in_next_line=False
    date_correct=''

    for line in lines:
        if line == "BT":
            in_text = True

        elif line == "ET":
            in_text = False

        elif in_text:
            cmd = line[-2:]
            if cmd.lower() == 'tj':
                replaced_line = line
                line_real=line[1:-4]
                if repair_in_next_line:
                    replaced_line = replaced_line.replace(line_real, date_correct)
                    repair_in_next_line=False
                if line_real.startswith('0027006900570058005000030059005C005600570044005900480051004C0044001D'):
                    date_correct=line_real[72:]
                    print(date_correct)
                if line_real.startswith('002701160044001D'):
                    repair_in_next_line=True                

                result += replaced_line + "\n"
            else:
                result += line + "\n"
            continue

        result += line + "\n"

    return result


def process_data(object):
    data = object.getData()
    decoded_data = data.decode()

    replaced_data = replace_text(decoded_data)

    encoded_data = replaced_data.encode()
    if object.decodedSelf is not None:
        object.decodedSelf.setData(encoded_data)
    else:
        object.setData(encoded_data)





if __name__ == "__main__":
    
    sg.theme("Dark Grey 13")
    layout = [[sg.Text("Vyberte súbor: "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Konvertuj", key='-SUBMIT-')],[sg.Text('Vyberte faktúru, na ktorej chcete opraviť dátum.',key='-OUTPUT-')]]
    window = sg.Window('PDF editor', layout, size=(600,150))

    while True:
        event, values = window.read()
        if ((event == sg.WIN_CLOSED)): # if user closes window or clicks cancel
            break
        if event == '-SUBMIT-':

            pdf = PdfFileReader(values['-IN-'])
            writer = PdfFileWriter()

            for page_number in range(0, pdf.getNumPages()):

                page = pdf.getPage(page_number)
                contents = page.getContents()

                if isinstance(contents, DecodedStreamObject) or isinstance(contents, EncodedStreamObject):
                    process_data(contents)
                elif len(contents) > 0:
                    for obj in contents:
                        if isinstance(obj, DecodedStreamObject) or isinstance(obj, EncodedStreamObject):
                            streamObj = obj.getObject()
                            process_data(streamObj)

                # Force content replacement
                page[NameObject("/Contents")] = contents.decodedSelf
                writer.addPage(page)

            with open((values['-IN-'])[:-4] + ".result.pdf", 'wb') as out_file:
                writer.write(out_file)
            window['-OUTPUT-'].update('Opravená faktúra sa uložila ako '+ (values['-IN-'])[:-4] + '.result.pdf')
            window.refresh()
    window.close()