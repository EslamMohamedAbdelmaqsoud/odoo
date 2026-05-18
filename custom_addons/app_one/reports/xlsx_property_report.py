from ast import literal_eval
from odoo import http
from odoo.http import request
import xlsxwriter
import io


# This controller defines an endpoint to generate and download an Excel report of properties based on their IDs.
class XlsxPropertyReport(http.Controller):

    @http.route("/property/excel/report/<string:property_ids>", type="http", auth="user")  # 1- handel endpoint
    # 2- methods to generate the report
    def download_property_excel_report(self, property_ids):

        properties = request.env["property"].browse(literal_eval(property_ids))
        output = io.BytesIO()  # 3- store the generated Excel file in memory
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})  # 4- create a new Excel workbook in memory
        worksheet = workbook.add_worksheet(
            "Properties")  # 5- add a new worksheet to the workbook with the name "Properties"
        # 6- define cell formats for the header
        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#D3D3D3", "border": 1, "align": "center", "valign": "vcenter"})
        string_format = workbook.add_format({"border": 1, "align": "center", "valign": "vcenter"})
        price_format = workbook.add_format(
            {"num_format": "$##,##00.00", "border": 1, "align": "center", "valign": "vcenter"})

        headers = ['Name', 'Email', 'Phone', 'Description', 'Data Availability', 'Postcode', 'Selling Price', 'Garden']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        row_num = 1
        for property_record in properties:
            worksheet.write(row_num, 0, property_record.name, string_format)
            worksheet.write(row_num, 1, property_record.email, string_format)
            worksheet.write(row_num, 2, property_record.phone, string_format)
            worksheet.write(row_num, 3, property_record.description, string_format)
            worksheet.write(row_num, 4, 'Yes' if property_record.data_availability else 'No', string_format)
            worksheet.write(row_num, 5, property_record.postcode, string_format)
            worksheet.write(row_num, 6, property_record.selling_price, price_format)
            worksheet.write(row_num, 7, 'Yes' if property_record.garden else 'No', string_format)
            row_num += 1

        workbook.close()  # close the workbook to finalize the Excel file and write it to the in-memory output
        output.seek(0)

        file_name = "Property Report.xlsx"  # define the name of the Excel file to be downloaded

        return request.make_response(
            output.getvalue(),
            headers=[
                ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("Content-Disposition", f"attachment; filename={file_name}")
            ]
        )

