import PyPDF2


def rotate(src, dest):
    pdf_in = open(src, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_in)
    pdf_writer = PyPDF2.PdfFileWriter()

    for pagenum in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagenum)
        page.rotateClockwise(180)
        pdf_writer.addPage(page)

    pdf_out = open(dest, 'wb')
    pdf_writer.write(pdf_out)
    pdf_out.close()
    pdf_in.close()
